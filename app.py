"""Streamlit mock workflow for DevPath Agent."""

import json
from pathlib import Path
from typing import Any

import streamlit as st

from devpath.agent_workflow import (
    WorkflowInput,
    run_career_strategy_agent_workflow,
    run_career_strategy_tool_calling_workflow,
    run_career_strategy_workflow,
)
from devpath.core.config import get_app_config
from devpath.services.export_service import export_markdown_report
from devpath.services.file_service import load_json_file, load_text_file
from devpath.services.github_service import (
    convert_github_repos_to_projects,
    fetch_public_github_repositories,
    is_github_username_provided,
    is_valid_github_username,
    normalize_github_username,
)
from devpath.tool_router import ADK_MCP_RUNTIME_BACKEND, DIRECT_BACKEND, list_tool_backends


ROOT_DIR = Path(__file__).parent
SAMPLE_JOB_PATH = ROOT_DIR / "data" / "sample_job_posting.txt"
SAMPLE_PROFILE_PATH = ROOT_DIR / "data" / "sample_profile.json"
SAMPLE_PROJECTS_PATH = ROOT_DIR / "data" / "sample_projects.json"

TARGET_ROLES = [
    "Junior Frontend React Developer",
    "Junior Frontend Developer",
    "Junior .NET Developer",
    "Junior Unity Developer",
    "Junior C# Developer",
    "Junior Python Developer",
    "Junior Backend Developer",
    "Junior QA Engineer",
    "Backend Developer Intern",
]
CUSTOM_TARGET_ROLE = "Custom role"

STANDARD_WORKFLOW = "Standard workflow"
FULL_AGENT_WORKFLOW = "Full agent workflow"
TOOL_CALLING_WORKFLOW = "Gemini/ADK tool-calling agent"


def main() -> None:
    """Render the DevPath Agent polished mock workflow."""

    st.set_page_config(page_title="DevPath Agent", page_icon="🧭", layout="wide")
    initialize_session_state()

    apply_page_styles()
    render_header()
    render_sidebar()
    render_demo_preset()

    st.markdown("## Input Workspace")
    with st.container(border=True):
        job_text, job_source_url = render_job_posting_section()

    with st.container(border=True):
        profile, cv_text = render_candidate_profile_section()
        target_role = render_target_role_section()
        profile["target_roles"] = [target_role]

    with st.container(border=True):
        projects = render_portfolio_section()

    with st.container(border=True):
        settings = render_analysis_settings_section()

    st.divider()
    if st.button("Generate Career Strategy", type="primary", use_container_width=True):
        handle_generate_report(job_text, profile, projects, cv_text, settings, job_source_url)

    if "report" in st.session_state:
        render_results_tabs(
            st.session_state.report,
            st.session_state.get("projects", projects),
            st.session_state.get("analysis_settings", settings),
        )


def initialize_session_state() -> None:
    """Create editable input defaults once per Streamlit session."""

    defaults = {
        "job_text": "",
        "job_source_url": "",
        "sample_job_loaded": False,
        "sample_profile_loaded": False,
        "target_role_preset": "Junior Frontend React Developer",
        "custom_target_role": "",
        "experience_level": "Junior",
        "profile_summary": "",
        "skills_text": "",
        "education": "",
        "languages_text": "",
        "location_preference": "",
        "cv_text": "",
        "github_username": "",
        "github_projects": [],
        "github_repos": [],
        "manual_projects_json": "",
        "portfolio_source": "Local sample projects",
        "analysis_mode": "Gemini-assisted summary",
        "tool_backend": DIRECT_BACKEND,
        "analysis_workflow": TOOL_CALLING_WORKFLOW,
        "output_style": "Concise",
        "demo_scenario_ready": False,
        "latest_exported_path": "",
        "latest_export_preview": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def apply_page_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container { padding-top: 2rem; max-width: 1180px; }
        div[data-testid="stMetric"] {
            background: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.28);
            border-radius: 0.5rem;
            padding: 0.75rem;
        }
        div[data-testid="stMetric"] * {
            color: var(--text-color) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.title("DevPath Agent")
    st.subheader("AI Career Copilot for Junior Software Developers")
    st.markdown(
        "Analyze a job posting, match it with your profile and portfolio, "
        "and generate an evidence-based career strategy."
    )
    st.caption(
        "Deterministic scoring · GitHub evidence · ADK-style agent workflow · "
        "MCP tools · Gemini-assisted insights · Markdown export"
    )


def render_demo_preset() -> None:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        if st.button("Load sample React frontend scenario", use_container_width=True):
            load_demo_scenario()
    with col_b:
        if st.session_state.demo_scenario_ready or st.session_state.job_text:
            st.success("Demo scenario ready: sample React job, profile, local portfolio, and tool-calling workflow.")
        else:
            st.info("Use the sample scenario for the fastest offline demo, or paste your own inputs.")


def load_demo_scenario() -> None:
    try:
        st.session_state.job_text = load_text_file(SAMPLE_JOB_PATH)
        sample_profile = load_json_file(SAMPLE_PROFILE_PATH)
        if isinstance(sample_profile, dict):
            set_profile_fields(sample_profile)
    except (FileNotFoundError, ValueError) as exc:
        st.error(f"Could not load demo scenario: {exc}")
        return

    st.session_state.job_source_url = ""
    st.session_state.sample_job_loaded = True
    st.session_state.sample_profile_loaded = True
    st.session_state.portfolio_source = "Local sample projects"
    st.session_state.analysis_workflow = TOOL_CALLING_WORKFLOW
    st.session_state.analysis_mode = "Gemini-assisted summary"
    st.session_state.tool_backend = DIRECT_BACKEND
    st.session_state.output_style = "Concise"
    st.session_state.cv_text = sample_cv_context()
    st.session_state.demo_scenario_ready = True


def render_sidebar() -> None:
    with st.sidebar:
        st.header("Capstone Demo")
        st.markdown(
            "**Status:** Capstone demo ready  \n"
            "**Track fit:** Concierge Agents  \n"
            "**Default:** Gemini/ADK tool-calling, React sample data, safe fallback"
        )

        st.divider()
        st.subheader("Workflow")
        st.markdown(
            "1. Load demo scenario\n"
            "2. Generate career strategy\n"
            "3. Show score, evidence, gaps\n"
            "4. Show agent trace and runtime\n"
            "5. Export Markdown"
        )

        st.divider()
        st.subheader("Security")
        st.warning("Do not paste secrets, passwords, private tokens, or sensitive personal data.")

        with st.expander("Planned later"):
            st.markdown(
                "- Live ADK runtime exploration\n"
                "- GitHub source-code evidence mapping\n"
                "- Kaggle writeup and video script"
            )


def render_job_posting_section() -> tuple[str, str]:
    st.header("1. Job Posting")
    st.caption("Use a real or sample junior developer job description.")

    load_sample = st.checkbox(
        "Load sample job",
        value=False,
        help="Loads data/sample_job_posting.txt once, then leaves the text editable.",
    )
    if load_sample and not st.session_state.sample_job_loaded:
        try:
            st.session_state.job_text = load_text_file(SAMPLE_JOB_PATH)
            st.session_state.sample_job_loaded = True
        except FileNotFoundError as exc:
            st.error(f"Missing sample job posting: {exc}")
    elif not load_sample:
        st.session_state.sample_job_loaded = False

    job_text = st.text_area(
        "Paste job posting",
        key="job_text",
        height=240,
        placeholder="Paste a job posting or load the sample posting.",
    )
    job_source_url = st.text_input(
        "Optional job source URL",
        key="job_source_url",
        placeholder="https://example.com/jobs/junior-dotnet-developer",
    )
    return job_text, job_source_url


def render_candidate_profile_section() -> tuple[dict[str, Any], str]:
    st.header("2. Candidate Profile")
    st.caption("Review the candidate summary used for matching.")

    load_sample = st.checkbox(
        "Load sample profile",
        value=False,
        help="Loads data/sample_profile.json once, then leaves the fields editable.",
    )
    if load_sample and not st.session_state.sample_profile_loaded:
        try:
            sample_profile = load_json_file(SAMPLE_PROFILE_PATH)
            if not isinstance(sample_profile, dict):
                st.error("Sample profile JSON must contain one profile object.")
            else:
                set_profile_fields(sample_profile)
                st.session_state.sample_profile_loaded = True
        except (FileNotFoundError, ValueError) as exc:
            st.error(f"Could not load sample profile: {exc}")
    elif not load_sample:
        st.session_state.sample_profile_loaded = False

    col_a, col_b = st.columns(2)
    with col_a:
        experience_level = st.text_input("Experience level", key="experience_level")
        education = st.text_input("Education", key="education")
        location_preference = st.text_input("Location preference", key="location_preference")
    with col_b:
        skills_text = st.text_area(
            "Skills",
            key="skills_text",
            height=120,
            placeholder="C#, .NET, WPF, Unity, SQLite, EF Core, Git, MVVM",
            help="Separate skills with commas or new lines.",
        )
        languages_text = st.text_area(
            "Languages",
            key="languages_text",
            height=120,
            placeholder="English B1-B2, German A1, Ukrainian Native",
            help="Separate languages with commas or new lines.",
        )
    profile_summary = st.text_area(
        "Summary",
        key="profile_summary",
        height=90,
        placeholder="Short candidate summary, focus area, or positioning statement.",
    )

    st.markdown("#### Optional CV Context")
    st.warning("Do not paste secrets, passwords, private tokens, or sensitive personal data.")
    st.caption(
        "CV context is passed through privacy masking and used as additional report context. "
        "Deterministic scoring still comes from job, profile, and portfolio evidence."
    )
    cv_text = st.text_area(
        "Optional CV context",
        key="cv_text",
        height=120,
        placeholder="Optional non-sensitive CV context for the demo.",
        help="This text stays local unless Gemini-assisted mode is selected and a local API key is configured.",
    )

    profile = {
        "target_roles": [],
        "experience_level": experience_level.strip(),
        "skills": split_editable_list(skills_text),
        "languages": split_editable_list(languages_text),
        "education": education.strip(),
        "location_preference": location_preference.strip(),
        "summary": profile_summary.strip(),
    }
    return profile, cv_text


def render_portfolio_section() -> list[dict[str, Any]]:
    st.header("3. Portfolio")
    st.caption("Use local sample projects, paste manual portfolio JSON, or import public GitHub repository metadata.")
    source = st.radio(
        "Portfolio source",
        ["Local sample projects", "Manual JSON input", "GitHub public repositories"],
        horizontal=True,
        key="portfolio_source",
    )

    if source == "Manual JSON input":
        st.caption("Paste a JSON array of portfolio projects. This avoids GitHub API/rate-limit dependency for judge tests.")
        if st.button("Use React frontend sample JSON", use_container_width=True):
            st.session_state.manual_projects_json = sample_manual_projects_json()
        manual_json = st.text_area(
            "Portfolio projects JSON",
            key="manual_projects_json",
            height=260,
            placeholder='[{"name": "Project", "summary": "What it does", "technologies": ["Python", "SQL"]}]',
            help="Expected fields: name, summary or description, technologies, optional url.",
        )
        parsed = parse_manual_projects_json(manual_json)
        if parsed["ok"]:
            projects = parsed["projects"]
            st.success(f"Loaded {len(projects)} manual portfolio project(s).")
            render_project_cards(projects)
            return projects
        if manual_json.strip():
            st.error(parsed["error"])
            st.warning("Manual portfolio JSON is selected, so no fallback portfolio will be used until the JSON is fixed.")
            return []
        st.info("Paste portfolio JSON or click the sample button. No manual projects are loaded yet.")
        return []

    if source == "GitHub public repositories":
        username = st.text_input("GitHub username", key="github_username", placeholder="octocat")
        st.caption(
            "Only public repository metadata is imported. No token, private repos, cloning, or source-code download is used."
        )
        col_a, col_b = st.columns([1, 2])
        with col_a:
            fetch_clicked = st.button("Fetch public repositories", use_container_width=True)
        with col_b:
            max_repos = st.slider("Maximum repositories", min_value=1, max_value=30, value=10)

        if fetch_clicked:
            fetch_github_projects(username, max_repos=max_repos)

        github_projects = st.session_state.get("github_projects", [])
        if github_projects:
            st.success(f"Imported {len(github_projects)} public GitHub repositories.")
            render_github_repo_table(st.session_state.get("github_repos", []))
            render_project_cards(github_projects)
            return github_projects

        st.info("No GitHub repositories imported yet. The app is using local sample projects as fallback.")

    projects = load_sample_projects()
    if projects:
        render_project_cards(projects)
    return projects


def parse_manual_projects_json(raw_json: str) -> dict[str, Any]:
    """Parse and normalize manual portfolio project JSON from the UI."""

    if not raw_json.strip():
        return {"ok": False, "projects": [], "error": "Manual portfolio JSON is empty."}
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        return {"ok": False, "projects": [], "error": f"Invalid portfolio JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}."}
    if not isinstance(payload, list):
        return {"ok": False, "projects": [], "error": "Portfolio JSON must be an array of project objects."}

    projects: list[dict[str, Any]] = []
    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            return {"ok": False, "projects": [], "error": f"Project #{index} must be a JSON object."}
        name = str(item.get("name", "")).strip()
        if not name:
            return {"ok": False, "projects": [], "error": f"Project #{index} is missing a non-empty 'name' field."}
        summary = str(item.get("summary") or item.get("description") or "").strip()
        technologies = normalize_manual_project_technologies(item.get("technologies", []))
        project = dict(item)
        project["name"] = name
        project["summary"] = summary
        project["technologies"] = technologies
        project["source"] = "manual"
        projects.append(project)
    return {"ok": True, "projects": projects, "error": ""}


def normalize_manual_project_technologies(value: Any) -> list[str]:
    if isinstance(value, str):
        raw_items = value.replace("\n", ",").split(",")
    elif isinstance(value, list | tuple | set):
        raw_items = list(value)
    else:
        raw_items = []
    technologies: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        technology = str(item).strip()
        if technology and technology.lower() not in seen:
            seen.add(technology.lower())
            technologies.append(technology)
    return technologies


def sample_manual_projects_json() -> str:
    projects = [
        {
            "name": "TaskBoard React Dashboard",
            "summary": (
                "React and TypeScript task management dashboard with reusable components, filters, "
                "responsive layout, and REST API integration mock."
            ),
            "technologies": ["React", "TypeScript", "JavaScript", "HTML", "CSS", "REST API", "Git", "Tailwind CSS"],
            "url": "https://github.com/example/taskboard-react",
        },
        {
            "name": "Weather UI App",
            "summary": (
                "Responsive weather app built with JavaScript, HTML, CSS, API fetching, loading states, "
                "error handling, and mobile-friendly layout."
            ),
            "technologies": ["JavaScript", "HTML", "CSS", "REST API", "Git"],
            "url": "https://github.com/example/weather-ui",
        },
        {
            "name": "Portfolio Website",
            "summary": (
                "Personal portfolio website with project case studies, responsive design, accessibility improvements, "
                "and Figma-based visual planning."
            ),
            "technologies": ["HTML", "CSS", "JavaScript", "Responsive Design", "Figma", "Git"],
            "url": "https://github.com/example/frontend-portfolio",
        },
    ]
    return json.dumps(projects, indent=2)


def fetch_github_projects(username: str, max_repos: int) -> None:
    normalized_username = normalize_github_username(username)
    if not is_github_username_provided(normalized_username):
        st.warning("Enter a GitHub username before fetching public repositories.")
        return
    if not is_valid_github_username(normalized_username):
        st.error("Invalid GitHub username. Use only letters, numbers, or hyphens.")
        return

    try:
        repos = fetch_public_github_repositories(normalized_username, max_repos=max_repos)
        projects = convert_github_repos_to_projects(repos)
    except (ValueError, RuntimeError) as exc:
        st.error(f"Could not import public GitHub repositories: {exc}")
        return

    st.session_state.github_repos = repos
    st.session_state.github_projects = projects
    if not projects:
        st.warning("No public non-fork, non-archived repositories were found for this username.")


def render_github_repo_table(repos: list[dict[str, Any]]) -> None:
    if not repos:
        return

    rows = [
        {
            "Repository": repo.get("name", ""),
            "Language": repo.get("language", ""),
            "Topics": ", ".join(repo.get("topics", [])),
            "Stars": repo.get("stars", 0),
            "Forks": repo.get("forks", 0),
            "Is fork": repo.get("fork", False),
            "Archived": repo.get("archived", False),
            "Pushed": repo.get("pushed_at", ""),
            "URL": repo.get("html_url", ""),
        }
        for repo in repos
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_target_role_section() -> str:
    st.subheader("Candidate Target Role")
    preset = st.selectbox(
        "Role preset",
        [*TARGET_ROLES, CUSTOM_TARGET_ROLE],
        key="target_role_preset",
        help="Used as the candidate target role when the career strategy is generated.",
    )
    if preset != CUSTOM_TARGET_ROLE:
        return preset

    custom_role = st.text_input(
        "Custom target role",
        key="custom_target_role",
        placeholder="Junior Python Developer, Data Analyst Intern, Frontend Developer...",
        help="Use this when the role is not covered by the presets.",
    )
    return custom_role.strip() or "Junior Software Developer"


def render_analysis_settings_section() -> dict[str, Any]:
    st.header("AI Agent Demo Settings")
    st.caption("Capstone-ready defaults: Gemini/ADK tool-calling, optional Gemini narrative, deterministic scoring.")

    app_config = get_app_config()
    selected_workflow = st.session_state.get("analysis_workflow", TOOL_CALLING_WORKFLOW)
    col_a, col_b, col_c = st.columns(3)
    workflow_label = {
        TOOL_CALLING_WORKFLOW: "Tool-calling",
        FULL_AGENT_WORKFLOW: "Full",
        STANDARD_WORKFLOW: "Standard",
    }.get(selected_workflow, "Full")
    col_a.metric("Agent workflow", workflow_label)
    col_b.metric("Gemini narrative", "Ready" if app_config.gemini_enabled else "Fallback")
    col_c.metric("Score source", "Deterministic")

    if app_config.gemini_enabled:
        st.success("Gemini is configured for narrative insights. Match scores and evidence remain deterministic.")
    else:
        st.info(
            "Gemini-assisted mode is selected by default. Add GOOGLE_API_KEY locally for AI narrative insights; "
            "without it, the demo continues with the deterministic agent report."
        )

    with st.expander("Runtime details for judges", expanded=False):
        analysis_workflow = st.selectbox(
            "Demo workflow",
            [TOOL_CALLING_WORKFLOW, FULL_AGENT_WORKFLOW, STANDARD_WORKFLOW],
            key="analysis_workflow",
            format_func=format_workflow_option,
            help=(
                "Choose the visible execution style for the demo. The capstone mode uses Gemini/ADK tool-calling "
                "with MCP-aware tool traces and safe deterministic fallbacks."
            ),
        )

        if analysis_workflow == TOOL_CALLING_WORKFLOW:
            analysis_mode = "Gemini-assisted summary"
            tool_backend = ADK_MCP_RUNTIME_BACKEND
            st.selectbox(
                "Gemini behavior",
                ["Structured extraction + narrative writers"],
                index=0,
                disabled=True,
                help=(
                    "Gemini extracts structured job/profile/CV context and enhances narrative sections when "
                    "GOOGLE_API_KEY is configured. The score and evidence stay deterministic."
                ),
            )
            st.selectbox(
                "Tool route",
                ["MCP runtime first -> local MCP registry -> direct deterministic fallback"],
                index=0,
                disabled=True,
                help=(
                    "This route is fixed for the capstone tool-calling demo so judges can see MCP participation "
                    "and fallback behavior in the Runtime tab."
                ),
            )
            st.info(
                "Capstone agent mode locks the backend route to MCP runtime first. "
                "The Runtime tab will show each tool call, backend used, fallback status, and warnings."
            )
        else:
            analysis_mode = st.selectbox(
                "Narrative mode",
                ["Gemini-assisted summary", "Mock deterministic mode"],
                key="analysis_mode",
                format_func=format_analysis_mode_option,
                help=(
                    "Gemini adds optional narrative insights when an API key is configured. "
                    "The numeric score, evidence, gaps, and recommendations are still built from deterministic logic."
                ),
            )
            tool_backend = st.selectbox(
                "Deterministic tool backend",
                list_tool_backends(),
                key="tool_backend",
                format_func=format_tool_backend_option,
                help=(
                    "Used by Standard and Full workflows. For the capstone tool-calling workflow, the route is "
                    "locked to MCP runtime first with local fallbacks."
                ),
            )
            st.caption(
                "These controls are available for comparing the baseline deterministic routes. "
                "Use the capstone agent mode for the clearest ADK/MCP/Gemini demonstration."
            )

        output_style = st.selectbox("Output style", ["Concise", "Detailed"], key="output_style")

        st.caption(
            "Application drafts and interview prep are always included in the capstone demo so judges can see the "
            "full career-copilot workflow."
        )

    return {
        "analysis_mode": analysis_mode,
        "tool_backend": tool_backend,
        "analysis_workflow": analysis_workflow,
        "output_style": output_style,
        "include_cover_letter": True,
        "include_interview_prep": True,
    }


def format_workflow_option(value: str) -> str:
    labels = {
        TOOL_CALLING_WORKFLOW: "Capstone agent mode: Gemini/ADK tool-calling + MCP trace",
        FULL_AGENT_WORKFLOW: "ADK-style deterministic multi-agent workflow",
        STANDARD_WORKFLOW: "Baseline deterministic workflow",
    }
    return labels.get(value, value)


def format_analysis_mode_option(value: str) -> str:
    labels = {
        "Gemini-assisted summary": "Gemini narrative insights with safe fallback",
        "Mock deterministic mode": "Deterministic narrative only",
    }
    return labels.get(value, value)


def format_tool_backend_option(value: str) -> str:
    labels = {
        DIRECT_BACKEND: "Direct deterministic services",
        "Local MCP-style tools": "Local MCP-style tool registry",
        ADK_MCP_RUNTIME_BACKEND: "Experimental MCP runtime route",
    }
    return labels.get(value, value)


def handle_generate_report(
    job_text: str,
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
    cv_text: str,
    settings: dict[str, Any],
    job_source_url: str,
) -> None:
    if not job_text.strip():
        st.error("Please provide a job posting before generating a career strategy.")
        return
    if not profile_has_content(profile):
        st.error("Please load or enter a candidate profile before generating a career strategy.")
        return
    if not projects:
        st.error("Please load portfolio projects before generating a career strategy.")
        return

    workflow_input = WorkflowInput(
        job_text=job_text,
        profile=profile,
        projects=projects,
        cv_text=cv_text,
        target_role=(profile.get("target_roles") or ["Junior Software Developer"])[0],
        output_style=settings["output_style"],
        analysis_mode=settings.get("analysis_mode", "Mock deterministic mode"),
        tool_backend=settings.get("tool_backend", DIRECT_BACKEND),
    )
    warnings: list[str] = []
    if settings.get("analysis_workflow") == TOOL_CALLING_WORKFLOW:
        try:
            result = run_career_strategy_tool_calling_workflow(workflow_input)
        except Exception:
            warnings.append(
                "Gemini/ADK tool-calling workflow could not be used. Falling back to full deterministic agent workflow."
            )
            result = run_career_strategy_agent_workflow(workflow_input)
    elif settings.get("analysis_workflow") == FULL_AGENT_WORKFLOW:
        try:
            result = run_career_strategy_agent_workflow(workflow_input)
        except Exception:
            warnings.append("Full agent workflow could not be used. Falling back to standard deterministic workflow.")
            result = run_career_strategy_workflow(workflow_input)
    else:
        result = run_career_strategy_workflow(workflow_input)

    report = result.report
    if job_source_url.strip():
        report["job_analysis"]["job_source_url"] = job_source_url.strip()

    for warning in [*warnings, *result.warnings]:
        st.warning(warning)
    if result.mode_used == "Gemini-assisted summary":
        st.success("Gemini-assisted career insights generated. Deterministic score fields were unchanged.")

    st.session_state.report = report
    st.session_state.projects = projects
    st.session_state.analysis_settings = settings
    st.session_state.latest_exported_path = ""
    st.session_state.latest_export_preview = ""
    st.success("Career strategy generated.")


def render_results_tabs(report: dict[str, Any], projects: list[dict[str, Any]], settings: dict[str, Any]) -> None:
    st.divider()
    st.header("Results Dashboard")
    render_results_dashboard(report)

    tabs = st.tabs(
        [
            "Overview",
            "Evidence",
            "Gaps",
            "Action Plan",
            "Application",
            "Interview",
            "Runtime",
            "Export",
        ]
    )

    with tabs[0]:
        render_job_analysis_tab(
            report["job_analysis"],
            report.get("gemini_insights", {}),
            report.get("gemini_summary") or report.get("ai_summary", ""),
        )
        render_profile_match_tab(report["profile_match"], report["skill_gaps"])
    with tabs[1]:
        render_portfolio_evidence_tab(report["portfolio_evidence"], projects)
    with tabs[2]:
        render_skill_gaps_tab(report["skill_gaps"])
    with tabs[3]:
        render_preparation_plan_tab(report["preparation_plan"])
    with tabs[4]:
        render_application_drafts_tab(report["application_drafts"], settings["include_cover_letter"])
    with tabs[5]:
        render_interview_prep_tab(report["interview_prep"], settings["include_interview_prep"])
    with tabs[6]:
        render_agent_workflow_trace(report)
        render_tool_calling_trace(report.get("tool_call_trace", []))
        render_workflow_runtime(report.get("runtime_route", {}))
    with tabs[7]:
        render_export_tab(report)


def render_results_dashboard(report: dict[str, Any]) -> None:
    profile_match = report.get("profile_match", {})
    skill_gaps = report.get("skill_gaps", {})
    portfolio_evidence = report.get("portfolio_evidence", {})
    strong_matches = profile_match.get("strong_matches", [])
    prioritized_gaps = skill_gaps.get("prioritized_gaps", [])
    evidence_by_skill = profile_match.get("evidence_by_skill", {})
    next_action = _recommended_next_action(prioritized_gaps, report.get("preparation_plan", {}))

    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Match Score", f"{profile_match.get('overall_score', 0)}/100")
    col_b.metric("Top Strengths", str(len(strong_matches)))
    col_c.metric("Priority Gaps", str(len(prioritized_gaps)))
    col_d.metric("Evidence Items", str(sum(len(items) for items in evidence_by_skill.values())))

    st.info(f"Recommended next action: {next_action}")
    if portfolio_evidence.get("github_evidence"):
        st.caption("GitHub Repository Evidence is available in the Evidence tab.")
    if st.session_state.get("latest_exported_path"):
        st.success(f"Latest Markdown export: {st.session_state.latest_exported_path}")


def _recommended_next_action(prioritized_gaps: list[dict[str, Any]], preparation_plan: dict[str, Any]) -> str:
    if prioritized_gaps:
        return str(prioritized_gaps[0].get("recommendation", "Address the highest-priority skill gap."))
    seven_day_plan = preparation_plan.get("7_day_plan", [])
    if seven_day_plan:
        return str(seven_day_plan[0])
    return "Polish portfolio evidence and prepare concise project stories."


def render_workflow_runtime(runtime_route: dict[str, Any]) -> None:
    if not runtime_route:
        st.info("Workflow Runtime: no runtime metadata available for this report.")
        return

    requested_backend = runtime_route.get("requested_tool_backend") or runtime_route.get("tool_backend", "Unknown")
    backend_used = runtime_route.get("tool_backend", "Unknown")
    mcp_runtime_used = bool(runtime_route.get("mcp_runtime_used"))
    experimental = bool(runtime_route.get("experimental"))
    fallback_used = bool(runtime_route.get("fallback_used"))
    selected_tools = runtime_route.get("selected_tools") or []
    notes = runtime_route.get("notes") or []

    if fallback_used:
        st.warning(f"One or more tool calls used fallback. Deterministic report backend: `{backend_used}`.")
    elif experimental and mcp_runtime_used:
        st.info("Experimental ADK-MCP runtime route succeeded for selected tools.")
    else:
        st.success("Stable deterministic runtime used.")

    with st.expander("Workflow Runtime", expanded=False):
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Backend selected", str(requested_backend))
        col_b.metric("Backend used", str(backend_used))
        col_c.metric("MCP runtime used", "Yes" if mcp_runtime_used else "No")

        col_d, col_e = st.columns(2)
        col_d.metric("Experimental route", "Yes" if experimental else "No")
        col_e.metric("Fallback used", "Yes" if fallback_used else "No")

        st.markdown("**Selected tools:**")
        render_bullets(selected_tools, "No runtime tools were selected for this backend.")
        st.markdown("**Notes:**")
        render_bullets(notes, "No runtime notes available.")


def render_agent_workflow_trace(report: dict[str, Any]) -> None:
    agent_workflow = report.get("agent_workflow", {})
    agent_trace = report.get("agent_trace", [])
    if not agent_workflow and not agent_trace:
        return

    st.info("Full ADK-style deterministic orchestration was used.")
    with st.expander("Agent Workflow Trace", expanded=True):
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Scoring source", str(agent_workflow.get("scoring_source", "deterministic")))
        llm_modification = bool(agent_workflow.get("llm_score_modification", False))
        col_b.metric("LLM score modification", "Enabled" if llm_modification else "Disabled")
        col_c.metric("Agent stages", str(len(agent_trace) or len(agent_workflow.get("agents", []))))

        st.markdown(f"**Agent orchestration:** {agent_workflow.get('orchestration', 'Full agent workflow')}")
        st.caption("Trace entries show metadata only. Raw private inputs and secrets are not displayed.")

        if not agent_trace:
            render_bullets(agent_workflow.get("agents", []), "No serialized agent trace available.")
            return

        for step in agent_trace:
            status = str(step.get("status", "completed"))
            icon = agent_status_icon(status, step.get("warnings", []))
            agent_name = step.get("agent_name", "agent")
            summary = step.get("summary", "No summary available.")
            st.markdown(f"**{icon} {agent_name}** - {summary}")
            with st.expander(f"Details: {agent_name}", expanded=False):
                tools_used = step.get("tools_used", [])
                st.markdown("**Tools used:**")
                render_bullets(tools_used, "No tools recorded for this stage.")
                warnings = step.get("warnings", [])
                if warnings:
                    st.markdown("**Warnings:**")
                    render_bullets(warnings, "No warnings.")


def render_tool_calling_trace(tool_call_trace: list[dict[str, Any]]) -> None:
    if not tool_call_trace:
        return

    st.info("Gemini/ADK tool-calling mode used visible MCP-aware tool calls.")
    with st.expander("AI Tool-Calling Trace", expanded=True):
        completed = sum(1 for step in tool_call_trace if step.get("status") == "completed")
        fallback = sum(1 for step in tool_call_trace if step.get("fallback_used"))
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Tool calls", str(len(tool_call_trace)))
        col_b.metric("Completed", str(completed))
        col_c.metric("Fallback steps", str(fallback))
        st.caption("Trace shows metadata only. Raw job text, CV text, secrets, and API keys are not displayed.")

        for index, step in enumerate(tool_call_trace, start=1):
            status = str(step.get("status", "completed"))
            warnings = step.get("warnings", [])
            icon = agent_status_icon(status, warnings)
            tool_name = step.get("tool_name", "tool")
            backend = step.get("backend_used", "Unknown backend")
            title = f"{index}. {icon} {tool_name} via {backend}"
            st.markdown(f"**{title}**")
            with st.expander(f"Details: {tool_name} #{index}", expanded=False):
                st.markdown(f"**Agent:** {step.get('agent_name', 'agent')}")
                st.markdown(f"**Status:** {status}")
                st.markdown(f"**Input summary:** {step.get('input_summary', 'No input summary available.')}")
                st.markdown(f"**Output summary:** {step.get('output_summary', 'No output summary available.')}")
                st.markdown(f"**Fallback used:** {'Yes' if step.get('fallback_used') else 'No'}")
                if warnings:
                    st.markdown("**Warnings:**")
                    render_bullets(warnings, "No warnings.")


def agent_status_icon(status: str, warnings: list[str]) -> str:
    normalized = status.lower()
    if normalized == "failed":
        return "✗"
    if warnings or normalized in {"warning", "fallback"}:
        return "!"
    return "✓"


def render_job_analysis_tab(
    job_analysis: dict[str, Any],
    gemini_insights: dict[str, Any] | None = None,
    gemini_summary: str = "",
) -> None:
    st.subheader("Job Analysis")
    st.markdown(job_analysis.get("detected_focus", "No job analysis available."))

    render_gemini_insights(gemini_insights or {}, gemini_summary)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        render_summary_card("Detected role", job_analysis.get("target_role", "Unknown"))
    col_b.metric("Output style", job_analysis.get("output_style", "Concise"))
    col_c.metric("CV context", "Yes" if job_analysis.get("cv_context_provided") else "No")

    if job_analysis.get("job_source_url"):
        st.markdown(f"**Source URL:** {job_analysis['job_source_url']}")


def render_gemini_insights(gemini_insights: dict[str, Any], gemini_summary: str = "") -> None:
    if not gemini_insights and not gemini_summary:
        return

    if not isinstance(gemini_insights, dict):
        gemini_insights = {}

    st.markdown("### Gemini-assisted Career Strategy")
    st.caption("Gemini improves the narrative explanation only. The numeric score and evidence are deterministic.")

    career_summary = gemini_insights.get("career_summary") or gemini_summary
    st.markdown("#### AI Career Strategy Summary")
    if career_summary:
        st.info(career_summary)
    else:
        st.write("No Gemini career summary available yet.")

    st.markdown("#### Top 3 Application Actions")
    render_numbered(gemini_insights.get("top_actions", []), "No Gemini action items available yet.")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Best Portfolio Evidence to Mention")
        render_bullets(
            gemini_insights.get("portfolio_positioning", []),
            "No Gemini portfolio positioning available yet.",
        )
    with col_b:
        st.markdown("#### Skill Gap Strategy")
        render_bullets(gemini_insights.get("skill_gap_strategy", []), "No Gemini gap strategy available yet.")

    st.markdown("#### Interview Focus Areas")
    render_bullets(gemini_insights.get("interview_focus", []), "No Gemini interview focus areas available yet.")


def render_profile_match_tab(profile_match: dict[str, Any], skill_gaps: dict[str, Any]) -> None:
    st.subheader("Profile Match")
    score = int(profile_match.get("overall_score", 0))
    st.metric("Overall match score", f"{score}/100")
    st.progress(score / 100)
    st.write(profile_match.get("explanation", "No explanation available."))

    st.markdown("### Category Score Breakdown")
    category_scores = profile_match.get("category_scores", {})
    columns = st.columns(3)
    for index, (name, value) in enumerate(category_scores.items()):
        with columns[index % 3]:
            st.metric(name.replace("_", " ").title(), f"{value}")
    render_category_details(profile_match.get("category_details", {}), category_scores)

    match_col, partial_col, gap_col = st.columns(3)
    with match_col:
        st.markdown("### Strong Matches")
        render_bullets(profile_match.get("strong_matches", []), "No strong matches detected yet.")
    with partial_col:
        st.markdown("### Partial Matches")
        render_bullets(profile_match.get("partial_matches", []), "No partial matches detected yet.")
    with gap_col:
        st.markdown("### Missing Skills")
        missing_skills = skill_gaps.get("missing_skills") or profile_match.get("missing_skills", [])
        render_bullets(missing_skills, "No major required skill gaps detected.")

    st.markdown("### Evidence by Skill")
    render_evidence_by_skill(profile_match.get("evidence_by_skill", {}))


def render_portfolio_evidence_tab(portfolio_evidence: dict[str, Any], projects: list[dict[str, Any]]) -> None:
    st.subheader("Portfolio Evidence")
    st.write(portfolio_evidence.get("summary", "No portfolio summary available."))
    with st.expander("Suggested evidence points", expanded=True):
        render_bullets(portfolio_evidence.get("suggested_evidence_points", []), "No evidence points available.")
    st.markdown("### Portfolio Evidence Map")
    render_evidence_by_skill(portfolio_evidence.get("evidence_by_skill", {}), project_only=True)
    render_github_evidence(portfolio_evidence.get("github_evidence", []))
    render_project_cards(projects)


def render_skill_gaps_tab(skill_gaps: dict[str, Any]) -> None:
    st.subheader("Skill Gaps")
    st.write(skill_gaps.get("message", "No skill gap analysis available."))
    gap_narrative = skill_gaps.get("llm_gap_narrative", {})
    has_enhanced_narrative = has_enhanced_section(gap_narrative, ("summary", "gap_explanations"))
    render_llm_gap_narrative(gap_narrative)

    missing_skills = skill_gaps.get("missing_skills", [])
    priority_items = skill_gaps.get("priority", [])
    prioritized_gaps = skill_gaps.get("prioritized_gaps", [])

    if has_content(missing_skills) or has_content(priority_items):
        gap_col, priority_col = st.columns(2)
        with gap_col:
            st.markdown("### Missing Skills")
            render_bullets(missing_skills, "No required missing skills detected.")
        with priority_col:
            st.markdown("### Priority")
            render_bullets(priority_items, "Keep strengthening portfolio evidence.")

    if prioritized_gaps:
        if has_enhanced_narrative:
            with st.expander("Deterministic gap details", expanded=False):
                render_prioritized_gaps(prioritized_gaps, use_expanders=False)
        else:
            st.markdown("### Prioritized Gaps And Recommendations")
            render_prioritized_gaps(prioritized_gaps)
    elif not has_enhanced_narrative and not has_content(missing_skills) and not has_content(priority_items):
        st.info("No required gaps were detected. Keep strengthening portfolio evidence.")


def render_preparation_plan_tab(preparation_plan: dict[str, Any]) -> None:
    st.subheader("Preparation Plan")
    action_plan = preparation_plan.get("llm_enhanced_plan", {})
    has_enhanced_plan = has_enhanced_section(
        action_plan,
        (
            "summary",
            "7_day_plan",
            "14_day_plan",
            "30_day_roadmap",
            "portfolio_tasks",
            "study_tasks",
            "interview_drills",
            "done_criteria",
        ),
    )
    render_llm_action_plan(action_plan)

    if has_enhanced_plan:
        with st.expander("Deterministic fallback plan", expanded=False):
            render_deterministic_preparation_plan(preparation_plan)
        return

    render_deterministic_preparation_plan(preparation_plan)


def render_deterministic_preparation_plan(preparation_plan: dict[str, Any]) -> None:
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        render_plan_block("7-Day Plan", preparation_plan.get("7_day_plan", []))
    with col_b:
        render_plan_block("14-Day Plan", preparation_plan.get("14_day_plan", []))
    with col_c:
        render_plan_block("30-Day Roadmap", preparation_plan.get("30_day_roadmap", []))


def render_application_drafts_tab(application_drafts: dict[str, Any], include_cover_letter: bool) -> None:
    st.subheader("Application Drafts")
    enhanced_drafts = application_drafts.get("llm_enhanced_drafts", {})
    has_enhanced_drafts = has_enhanced_section(
        enhanced_drafts,
        (
            "cover_letter_draft",
            "recruiter_message_draft",
            "cv_bullets",
            "project_positioning",
            "what_to_emphasize",
            "what_to_avoid",
            "application_checklist",
        ),
    )
    render_llm_application_drafts(enhanced_drafts)

    if has_enhanced_drafts:
        with st.expander("Deterministic fallback drafts", expanded=False):
            render_deterministic_application_drafts(application_drafts, include_cover_letter)
        return

    render_deterministic_application_drafts(application_drafts, include_cover_letter)


def render_deterministic_application_drafts(
    application_drafts: dict[str, Any],
    include_cover_letter: bool,
) -> None:
    if not include_cover_letter:
        st.info("Cover letter drafts were disabled in analysis settings.")
    else:
        st.markdown("### Cover Letter Draft")
        st.code(application_drafts.get("cover_letter_draft", ""), language="markdown")

    st.markdown("### Recruiter Message Draft")
    st.code(application_drafts.get("recruiter_message_draft", ""), language="markdown")


def render_interview_prep_tab(interview_prep: dict[str, Any], include_interview_prep: bool) -> None:
    st.subheader("Interview Prep")
    if not include_interview_prep:
        st.info("Interview prep was disabled in analysis settings.")
        return
    enhanced_prep = interview_prep.get("llm_enhanced_prep", {})
    has_enhanced_prep = has_enhanced_section(
        enhanced_prep,
        (
            "focus_summary",
            "questions",
            "practice_focus",
            "technical_questions",
            "behavioral_questions",
            "project_story_prompts",
            "weak_area_drills",
            "answer_guidance",
        ),
    )
    render_llm_interview_prep(enhanced_prep)

    if has_enhanced_prep:
        with st.expander("Deterministic fallback interview prep", expanded=False):
            render_deterministic_interview_prep(interview_prep)
        return

    render_deterministic_interview_prep(interview_prep)


def render_deterministic_interview_prep(interview_prep: dict[str, Any]) -> None:
    st.markdown("### Interview Questions")
    for index, question in enumerate(interview_prep.get("questions", []), start=1):
        st.markdown(f"{index}. {question}")

    st.markdown("### Practice Focus")
    render_bullets(interview_prep.get("practice_focus", []), "No practice focus available.")


def render_llm_gap_narrative(gap_narrative: dict[str, Any]) -> None:
    if not gap_narrative:
        return
    with st.expander("Gemini-enhanced gap narrative", expanded=True):
        summary = gap_narrative.get("summary")
        if summary:
            st.write(summary)
        for item in gap_narrative.get("gap_explanations", []):
            skill = item.get("skill", "Gap")
            st.markdown(f"**{skill}**")
            if item.get("explanation"):
                st.write(item["explanation"])
            if item.get("next_step"):
                st.markdown(f"**Next step:** {item['next_step']}")


def render_llm_action_plan(action_plan: dict[str, Any]) -> None:
    if not action_plan:
        return
    with st.expander("Gemini-enhanced action plan", expanded=True):
        if action_plan.get("summary"):
            st.write(action_plan["summary"])
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            render_plan_block("Enhanced 7-Day Plan", action_plan.get("7_day_plan", []))
        with col_b:
            render_plan_block("Enhanced 14-Day Plan", action_plan.get("14_day_plan", []))
        with col_c:
            render_plan_block("Enhanced 30-Day Roadmap", action_plan.get("30_day_roadmap", []))
        detail_col_a, detail_col_b = st.columns(2)
        with detail_col_a:
            if action_plan.get("portfolio_tasks"):
                st.markdown("### Portfolio Tasks")
                render_bullets(action_plan.get("portfolio_tasks", []), "No portfolio tasks available.")
            if action_plan.get("study_tasks"):
                st.markdown("### Focused Study Tasks")
                render_bullets(action_plan.get("study_tasks", []), "No study tasks available.")
        with detail_col_b:
            if action_plan.get("interview_drills"):
                st.markdown("### Interview Drills")
                render_bullets(action_plan.get("interview_drills", []), "No interview drills available.")
            if action_plan.get("done_criteria"):
                st.markdown("### Done Criteria")
                render_bullets(action_plan.get("done_criteria", []), "No done criteria available.")


def render_llm_application_drafts(application: dict[str, Any]) -> None:
    if not application:
        return
    with st.expander("Gemini-enhanced application drafts", expanded=True):
        if application.get("cover_letter_draft"):
            st.markdown("### Enhanced Cover Letter")
            st.code(application["cover_letter_draft"], language="markdown")
        if application.get("recruiter_message_draft"):
            st.markdown("### Enhanced Recruiter Message")
            st.code(application["recruiter_message_draft"], language="markdown")
        if application.get("cv_bullets"):
            st.markdown("### Suggested CV Bullets")
            render_bullets(application.get("cv_bullets", []), "No CV bullets available.")
        col_a, col_b = st.columns(2)
        with col_a:
            if application.get("project_positioning"):
                st.markdown("### Project Positioning")
                render_bullets(application.get("project_positioning", []), "No project positioning available.")
            if application.get("what_to_emphasize"):
                st.markdown("### What To Emphasize")
                render_bullets(application.get("what_to_emphasize", []), "No emphasis points available.")
        with col_b:
            if application.get("what_to_avoid"):
                st.markdown("### What To Avoid")
                render_bullets(application.get("what_to_avoid", []), "No avoid-list items available.")
            if application.get("application_checklist"):
                st.markdown("### Application Checklist")
                render_bullets(application.get("application_checklist", []), "No checklist items available.")


def render_llm_interview_prep(interview: dict[str, Any]) -> None:
    if not interview:
        return
    with st.expander("Gemini-enhanced interview prep", expanded=True):
        if interview.get("focus_summary"):
            st.write(interview["focus_summary"])
        if interview.get("questions"):
            st.markdown("### Enhanced Questions")
            for index, question in enumerate(interview.get("questions", []), start=1):
                st.markdown(f"{index}. {question}")
        if interview.get("technical_questions"):
            st.markdown("### Technical Questions With Answer Focus")
            render_question_guides(interview.get("technical_questions", []))
        if interview.get("behavioral_questions"):
            st.markdown("### Behavioral Questions With Story Focus")
            render_question_guides(interview.get("behavioral_questions", []))
        col_a, col_b = st.columns(2)
        with col_a:
            if interview.get("project_story_prompts"):
                st.markdown("### Project Story Prompts")
                render_bullets(interview.get("project_story_prompts", []), "No project story prompts available.")
            if interview.get("weak_area_drills"):
                st.markdown("### Weak-Area Drills")
                render_bullets(interview.get("weak_area_drills", []), "No weak-area drills available.")
        with col_b:
            if interview.get("answer_guidance"):
                st.markdown("### Answer Guidance")
                render_bullets(interview.get("answer_guidance", []), "No answer guidance available.")
        if interview.get("practice_focus"):
            st.markdown("### Enhanced Practice Focus")
            render_bullets(interview.get("practice_focus", []), "No enhanced practice focus available.")


def render_export_tab(report: dict[str, Any]) -> None:
    st.subheader("Export")
    st.info(report.get("privacy_notice", "Review personal details before exporting."))
    st.caption("The exported Markdown report is saved locally in outputs/. Generated reports are ignored by Git.")

    if st.button("Export Markdown Report"):
        try:
            exported_path = export_markdown_report(report)
            preview = Path(exported_path).read_text(encoding="utf-8")
            st.session_state.latest_exported_path = exported_path
            st.session_state.latest_export_preview = preview
        except OSError as exc:
            st.error(f"Could not export Markdown report: {exc}")

    if st.session_state.get("latest_exported_path"):
        st.success(f"Markdown report exported: {st.session_state.latest_exported_path}")
        with st.expander("Markdown preview"):
            st.code(st.session_state.get("latest_export_preview", ""), language="markdown")


def render_category_details(category_details: dict[str, Any], category_scores: dict[str, Any]) -> None:
    if not category_details:
        if not category_scores:
            st.info("No category score details available yet.")
        return

    for key, detail in category_details.items():
        label = key.replace("_", " ").title()
        earned = detail.get("earned", category_scores.get(key, 0))
        max_score = detail.get("max", "")
        reason = detail.get("reason", "No reason provided.")
        score_label = f"{earned} / {max_score}" if max_score != "" else str(earned)
        with st.expander(f"{label}: {score_label}"):
            render_reason_lines(str(reason))


def render_summary_card(label: str, value: Any) -> None:
    with st.container(border=True):
        st.caption(label)
        st.markdown(f"**{value}**")


def render_reason_lines(reason: str) -> None:
    lines = split_reason_lines(reason)
    if not lines:
        st.write("Reason: No reason provided.")
        return

    st.markdown(f"**Reason:** {lines[0]}")
    for line in lines[1:]:
        st.markdown(line)


def split_reason_lines(reason: str) -> list[str]:
    normalized = reason.strip()
    if not normalized:
        return []
    for marker in ("Missing or weak", "Required skills without"):
        normalized = normalized.replace(f". {marker}", f".\n{marker}")
    return [line.strip() for line in normalized.splitlines() if line.strip()]


def render_evidence_by_skill(evidence_by_skill: dict[str, list[str]], project_only: bool = False) -> None:
    if not evidence_by_skill:
        st.info("No skill evidence available yet.")
        return

    visible_evidence: dict[str, list[str]] = {}
    for skill, sources in evidence_by_skill.items():
        filtered_sources = [source for source in sources if not project_only or source.startswith("Project: ")]
        if filtered_sources:
            visible_evidence[skill] = filtered_sources

    if not visible_evidence:
        st.info("No project-based skill evidence available yet.")
        return

    for skill, sources in sorted(visible_evidence.items()):
        with st.expander(skill):
            render_bullets(sources, "No evidence sources listed.")


def render_prioritized_gaps(prioritized_gaps: list[dict[str, Any]], use_expanders: bool = True) -> None:
    if not prioritized_gaps:
        st.info("No prioritized gaps detected. Keep strengthening the evidence already present.")
        return

    for gap in prioritized_gaps:
        priority = gap.get("priority", "Priority")
        skill = gap.get("skill", "Unknown skill")
        reason = gap.get("reason", "No reason provided.")
        recommendation = gap.get("recommendation", "No recommendation provided.")
        title = f"{priority} Priority: {skill}"
        if not use_expanders:
            st.markdown(f"#### {title}")
            if priority.lower() == "high":
                st.warning(reason)
            else:
                st.info(reason)
            st.markdown(f"**Recommendation:** {recommendation}")
            continue
        with st.expander(title, expanded=priority.lower() == "high"):
            if priority.lower() == "high":
                st.warning(reason)
            else:
                st.info(reason)
            st.markdown(f"**Recommendation:** {recommendation}")


def render_project_cards(projects: list[dict[str, Any]]) -> None:
    st.markdown("### Projects")
    for project in projects:
        name = project.get("name", "Portfolio project")
        technologies = project.get("technologies", [])
        stack = ", ".join(technologies) or "No stack listed"
        summary = project.get("summary") or project.get("description") or "No description available."
        evidence_line = build_project_evidence_line(technologies, summary)

        with st.expander(name, expanded=False):
            st.markdown(f"**Stack:** {stack}")
            st.write(summary)
            if project.get("url"):
                st.markdown(f"**URL:** {project['url']}")
            if project.get("source") == "github":
                github = project.get("github", {})
                topics = ", ".join(github.get("topics", [])) or "No topics"
                st.markdown(
                    f"**GitHub metadata:** language `{github.get('language') or 'Unknown'}`, "
                    f"topics `{topics}`, stars `{github.get('stars', 0)}`, forks `{github.get('forks', 0)}`"
                )
                st.caption(
                    f"Repository signals: fork={github.get('fork', False)}, "
                    f"archived={github.get('archived', False)}, pushed={github.get('pushed_at', 'Unknown')}"
                )
            st.caption(evidence_line)
            highlights = project.get("highlights", [])
            if highlights:
                st.markdown("**Highlights:**")
                render_bullets(highlights, "No highlights listed.")


def render_github_evidence(github_evidence: list[dict[str, Any]]) -> None:
    if not github_evidence:
        return

    st.markdown("### GitHub Repository Evidence")
    for evidence in github_evidence:
        title = evidence.get("project_name", "GitHub repository")
        with st.expander(title, expanded=False):
            if evidence.get("project_url"):
                st.markdown(f"**URL:** {evidence['project_url']}")
            st.markdown(f"**Language:** {evidence.get('language') or 'Unknown'}")
            st.markdown(f"**Topics:** {', '.join(evidence.get('topics', [])) or 'No topics'}")
            st.markdown(f"**Matched skills:** {', '.join(evidence.get('matched_skills', [])) or 'No direct skill matches'}")
            signals = evidence.get("signals", {})
            st.markdown(
                "**Signals:** "
                f"stars={signals.get('stars', 0)}, forks={signals.get('forks', 0)}, "
                f"recently_updated={signals.get('recently_updated', False)}, "
                f"archived={signals.get('archived', False)}, fork={signals.get('fork', False)}"
            )
            render_bullets(evidence.get("evidence_notes", []), "No GitHub evidence notes available.")


def has_content(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        return any(has_content(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(has_content(item) for item in value)
    return bool(value)


def has_enhanced_section(section: Any, keys: tuple[str, ...]) -> bool:
    if not isinstance(section, dict):
        return False
    return any(has_content(section.get(key)) for key in keys)


def render_plan_block(title: str, items: list[str]) -> None:
    st.markdown(f"### {title}")
    render_bullets(items, "No plan items available.")


def render_bullets(items: list[str], empty_message: str) -> None:
    if not items:
        st.write(empty_message)
        return
    for item in items:
        st.markdown(f"- {item}")


def render_numbered(items: list[str], empty_message: str) -> None:
    if not items:
        st.write(empty_message)
        return
    for index, item in enumerate(items, start=1):
        st.markdown(f"{index}. {item}")


def render_question_guides(items: list[dict[str, Any]]) -> None:
    if not items:
        st.write("No guided questions available.")
        return
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            st.markdown(f"{index}. {item}")
            continue
        question = item.get("question", "Interview question")
        answer_focus = item.get("answer_focus", "")
        st.markdown(f"{index}. **{question}**")
        if answer_focus:
            st.caption(f"Answer focus: {answer_focus}")


def build_project_evidence_line(technologies: list[str], summary: str) -> str:
    evidence_keywords = ["C#", ".NET", "WPF", "SQLite", "Unity", "Git", "ASP.NET Core", "REST API"]
    combined = " ".join([*technologies, summary]).lower()
    matches = [keyword for keyword in evidence_keywords if keyword.lower() in combined]
    if not matches:
        return "Portfolio evidence: add clearer technology, outcome, and role evidence."
    return f"Portfolio evidence: demonstrates {', '.join(matches)} experience."


def load_sample_projects() -> list[dict[str, Any]]:
    try:
        projects = load_json_file(SAMPLE_PROJECTS_PATH)
    except (FileNotFoundError, ValueError) as exc:
        st.error(f"Could not load sample projects: {exc}")
        return []
    if not isinstance(projects, list):
        st.error("Sample projects JSON must contain a list of projects.")
        return []
    return projects


def set_profile_fields(profile: dict[str, Any]) -> None:
    target_roles = profile.get("target_roles", [])
    primary_role = str(target_roles[0]) if target_roles else "Junior Frontend React Developer"
    if primary_role in TARGET_ROLES:
        st.session_state.target_role_preset = primary_role
        st.session_state.custom_target_role = ""
    else:
        st.session_state.target_role_preset = CUSTOM_TARGET_ROLE
        st.session_state.custom_target_role = primary_role
    st.session_state.experience_level = str(profile.get("experience_level", ""))
    st.session_state.skills_text = ", ".join(profile.get("skills", []))
    st.session_state.education = str(profile.get("education", ""))
    st.session_state.languages_text = ", ".join(profile.get("languages", []))
    st.session_state.location_preference = str(profile.get("location_preference", ""))
    st.session_state.profile_summary = str(profile.get("summary", ""))


def sample_cv_context() -> str:
    return (
        "Junior frontend developer with hands-on experience building React and JavaScript projects. "
        "Created a React dashboard using TypeScript, reusable components, responsive layouts, and REST API integration. "
        "Built additional projects with HTML, CSS, Git, API fetching, and mobile-friendly UI design. "
        "Comfortable communicating in English and preparing for junior frontend roles."
    )


def split_editable_list(value: str) -> list[str]:
    normalized = value.replace("\n", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def profile_has_content(profile: dict[str, Any]) -> bool:
    return any(
        [
            profile.get("experience_level"),
            profile.get("skills"),
            profile.get("education"),
            profile.get("languages"),
            profile.get("location_preference"),
        ]
    )


if __name__ == "__main__":
    main()

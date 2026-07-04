"""Streamlit mock workflow for DevPath Agent."""

from pathlib import Path
from typing import Any

import streamlit as st

from devpath.agent_workflow import WorkflowInput, run_career_strategy_workflow
from devpath.services.export_service import export_markdown_report
from devpath.services.file_service import load_json_file, load_text_file
from devpath.services.github_service import (
    convert_github_repos_to_projects,
    fetch_public_github_repositories,
    is_github_username_provided,
    is_valid_github_username,
    normalize_github_username,
)
from devpath.tool_router import DIRECT_BACKEND, list_tool_backends


ROOT_DIR = Path(__file__).parent
SAMPLE_JOB_PATH = ROOT_DIR / "data" / "sample_job_posting.txt"
SAMPLE_PROFILE_PATH = ROOT_DIR / "data" / "sample_profile.json"
SAMPLE_PROJECTS_PATH = ROOT_DIR / "data" / "sample_projects.json"

TARGET_ROLES = [
    "Junior .NET Developer",
    "Junior Unity Developer",
    "Junior C# Developer",
    "Backend Developer Intern",
]


def main() -> None:
    """Render the DevPath Agent polished mock workflow."""

    st.set_page_config(page_title="DevPath Agent", page_icon="🧭", layout="wide")
    initialize_session_state()

    render_header()
    render_sidebar()

    with st.container(border=True):
        job_text, job_source_url = render_job_posting_section()

    with st.container(border=True):
        profile = render_candidate_profile_section()

    with st.container(border=True):
        projects = render_portfolio_section()

    with st.container(border=True):
        target_role = render_target_role_section()
        profile["target_roles"] = [target_role]

    with st.container(border=True):
        cv_text = render_cv_section()

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
        "experience_level": "Junior",
        "skills_text": "",
        "education": "",
        "languages_text": "",
        "location_preference": "",
        "github_username": "",
        "github_projects": [],
        "github_repos": [],
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def render_header() -> None:
    st.title("DevPath Agent")
    st.subheader("AI Career Copilot for Junior Software Developers")
    st.markdown(
        "Analyze a job posting, compare it with your profile and portfolio, "
        "and generate a focused career preparation plan."
    )
    st.info(
        "Mock deterministic mode remains the default. Gemini-assisted summaries are optional "
        "and only run when selected with an API key configured.",
        icon="🧭",
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.header("DevPath MVP")
        st.markdown(
            "**Project status:** Step 7A - GitHub public repository import foundation  \n"
            "**Mode:** local deterministic mock  \n"
            "**External API calls:** disabled by default except explicit GitHub public import  \n"
            "**Data source:** sample files or public GitHub repo metadata  \n"
            "**ADK agent skeleton:** available  \n"
            "**ADK runtime routing:** planned"
        )

        st.divider()
        st.subheader("Workflow")
        st.markdown(
            "1. Load or paste a job posting\n"
            "2. Review candidate profile\n"
            "3. Review portfolio projects\n"
            "4. Choose target role\n"
            "5. Add optional CV context\n"
            "6. Adjust analysis settings\n"
            "7. Generate and export report"
        )

        st.divider()
        st.subheader("Security")
        st.warning("Do not paste secrets, passwords, private tokens, or sensitive personal data.")

        with st.expander("Planned later"):
            st.markdown(
                "- Google ADK root agent\n"
                "- MCP server tools\n"
                "- GitHub repo evidence mapping"
            )


def render_job_posting_section() -> tuple[str, str]:
    st.header("1. Job Posting")
    st.caption("Load the sample posting or paste a junior developer role you want to analyze.")

    load_sample = st.checkbox(
        "Load sample job posting",
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
        "Job posting text",
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


def render_candidate_profile_section() -> dict[str, Any]:
    st.header("2. Candidate Profile")
    st.caption("Keep this lightweight for the MVP: simple editable text fields are enough.")

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

    return {
        "target_roles": [],
        "experience_level": experience_level.strip(),
        "skills": split_editable_list(skills_text),
        "languages": split_editable_list(languages_text),
        "education": education.strip(),
        "location_preference": location_preference.strip(),
    }


def render_portfolio_section() -> list[dict[str, Any]]:
    st.header("3. Portfolio Source")
    st.caption("Use local sample projects or import public GitHub repository metadata as portfolio evidence.")
    source = st.radio("Portfolio source", ["Local sample projects", "GitHub public repositories"], horizontal=True)

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
            "Stars": repo.get("stars", 0),
            "Forks": repo.get("forks", 0),
            "Pushed": repo.get("pushed_at", ""),
            "URL": repo.get("html_url", ""),
        }
        for repo in repos
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_target_role_section() -> str:
    st.header("4. Target Role")
    return st.selectbox(
        "Target role",
        TARGET_ROLES,
        help="Used as the profile target role when the mock report is generated.",
    )


def render_cv_section() -> str:
    st.header("5. Optional CV Context")
    st.warning("Do not paste sensitive personal data, API keys, passwords, or private information.")
    return st.text_area(
        "Paste optional CV text",
        height=150,
        placeholder="Optional CV text for mock context.",
        help="This text stays local in the mock MVP and is only passed to the deterministic report builder.",
    )


def render_analysis_settings_section() -> dict[str, Any]:
    st.header("6. Analysis Settings")
    analysis_mode = st.selectbox("Analysis mode", ["Mock deterministic mode", "Gemini-assisted summary"])
    tool_backend = st.selectbox(
        "Tool backend",
        list_tool_backends(),
        index=0,
        help=(
            "Local MCP-style tools use the MCP registry in-process. Experimental ADK-MCP runtime tools "
            "start a local MCP stdio runtime for selected tools and fall back safely if unavailable."
        ),
    )
    st.caption(
        "Direct Python services: stable deterministic backend. "
        "Local MCP-style tools: uses MCP-style local wrappers without runtime transport. "
        "Experimental ADK-MCP runtime tools: starts local MCP stdio runtime for selected tools and falls back safely if unavailable."
    )
    output_style = st.selectbox("Output style", ["Concise", "Detailed"])
    include_cover_letter = st.checkbox("Include cover letter draft", value=True)
    include_interview_prep = st.checkbox("Include interview prep", value=True)
    return {
        "analysis_mode": analysis_mode,
        "tool_backend": tool_backend,
        "output_style": output_style,
        "include_cover_letter": include_cover_letter,
        "include_interview_prep": include_interview_prep,
    }


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
    result = run_career_strategy_workflow(workflow_input)
    report = result.report
    if job_source_url.strip():
        report["job_analysis"]["job_source_url"] = job_source_url.strip()

    for warning in result.warnings:
        st.warning(warning)
    if result.mode_used == "Gemini-assisted summary":
        st.success("Gemini-assisted career insights generated. Deterministic score fields were unchanged.")

    st.session_state.report = report
    st.session_state.projects = projects
    st.session_state.analysis_settings = settings
    st.success("Career strategy generated.")


def render_results_tabs(report: dict[str, Any], projects: list[dict[str, Any]], settings: dict[str, Any]) -> None:
    st.divider()
    st.header("7. Results")
    st.caption("Review the mock analysis, then export a Markdown report when the result looks useful.")
    render_workflow_runtime(report.get("runtime_route", {}))

    tabs = st.tabs(
        [
            "Job Analysis",
            "Profile Match",
            "Portfolio Evidence",
            "Skill Gaps",
            "Preparation Plan",
            "Application Drafts",
            "Interview Prep",
            "Export",
        ]
    )

    with tabs[0]:
        render_job_analysis_tab(
            report["job_analysis"],
            report.get("gemini_insights", {}),
            report.get("gemini_summary") or report.get("ai_summary", ""),
        )
    with tabs[1]:
        render_profile_match_tab(report["profile_match"], report["skill_gaps"])
    with tabs[2]:
        render_portfolio_evidence_tab(report["portfolio_evidence"], projects)
    with tabs[3]:
        render_skill_gaps_tab(report["skill_gaps"])
    with tabs[4]:
        render_preparation_plan_tab(report["preparation_plan"])
    with tabs[5]:
        render_application_drafts_tab(report["application_drafts"], settings["include_cover_letter"])
    with tabs[6]:
        render_interview_prep_tab(report["interview_prep"], settings["include_interview_prep"])
    with tabs[7]:
        render_export_tab(report)


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
        st.warning("Workflow Runtime: fallback was used. The report was generated with direct deterministic services.")
    elif experimental and mcp_runtime_used:
        st.info("Workflow Runtime: experimental ADK-MCP runtime route succeeded for selected tools.")
    else:
        st.success("Workflow Runtime: stable deterministic route used.")

    with st.expander("Workflow Runtime", expanded=True):
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


def render_job_analysis_tab(
    job_analysis: dict[str, Any],
    gemini_insights: dict[str, Any] | None = None,
    gemini_summary: str = "",
) -> None:
    st.subheader("Job Analysis")
    st.markdown(job_analysis.get("detected_focus", "No job analysis available."))

    render_gemini_insights(gemini_insights or {}, gemini_summary)

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Detected role", job_analysis.get("target_role", "Unknown"))
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
    render_project_cards(projects)


def render_skill_gaps_tab(skill_gaps: dict[str, Any]) -> None:
    st.subheader("Skill Gaps")
    st.write(skill_gaps.get("message", "No skill gap analysis available."))

    gap_col, priority_col = st.columns(2)
    with gap_col:
        st.markdown("### Missing Skills")
        render_bullets(skill_gaps.get("missing_skills", []), "No required missing skills detected.")
    with priority_col:
        st.markdown("### Priority")
        render_bullets(skill_gaps.get("priority", []), "Keep strengthening portfolio evidence.")

    st.markdown("### Prioritized Gaps And Recommendations")
    render_prioritized_gaps(skill_gaps.get("prioritized_gaps", []))


def render_preparation_plan_tab(preparation_plan: dict[str, Any]) -> None:
    st.subheader("Preparation Plan")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        render_plan_block("7-Day Plan", preparation_plan.get("7_day_plan", []))
    with col_b:
        render_plan_block("14-Day Plan", preparation_plan.get("14_day_plan", []))
    with col_c:
        render_plan_block("30-Day Roadmap", preparation_plan.get("30_day_roadmap", []))


def render_application_drafts_tab(application_drafts: dict[str, Any], include_cover_letter: bool) -> None:
    st.subheader("Application Drafts")
    if not include_cover_letter:
        st.info("Cover letter drafts were disabled in analysis settings.")
    else:
        st.markdown("### Cover Letter Draft")
        st.text_area(
            "Cover letter draft",
            value=application_drafts.get("cover_letter_draft", ""),
            height=260,
            label_visibility="collapsed",
        )

    st.markdown("### Recruiter Message Draft")
    st.text_area(
        "Recruiter message draft",
        value=application_drafts.get("recruiter_message_draft", ""),
        height=160,
        label_visibility="collapsed",
    )


def render_interview_prep_tab(interview_prep: dict[str, Any], include_interview_prep: bool) -> None:
    st.subheader("Interview Prep")
    if not include_interview_prep:
        st.info("Interview prep was disabled in analysis settings.")
        return

    st.markdown("### Interview Questions")
    for index, question in enumerate(interview_prep.get("questions", []), start=1):
        st.markdown(f"{index}. {question}")

    st.markdown("### Practice Focus")
    render_bullets(interview_prep.get("practice_focus", []), "No practice focus available.")


def render_export_tab(report: dict[str, Any]) -> None:
    st.subheader("Export")
    st.info(report.get("privacy_notice", "Review personal details before exporting."))
    st.caption("The exported Markdown report is saved locally in outputs/. Generated reports are ignored by Git.")

    if st.button("Export Markdown Report"):
        try:
            exported_path = export_markdown_report(report)
            st.success(f"Markdown report exported: {exported_path}")
            preview = Path(exported_path).read_text(encoding="utf-8")
            with st.expander("Markdown preview"):
                st.code(preview, language="markdown")
        except OSError as exc:
            st.error(f"Could not export Markdown report: {exc}")


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
            st.write(f"Reason: {reason}")


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


def render_prioritized_gaps(prioritized_gaps: list[dict[str, Any]]) -> None:
    if not prioritized_gaps:
        st.info("No prioritized gaps detected. Keep strengthening the evidence already present.")
        return

    for gap in prioritized_gaps:
        priority = gap.get("priority", "Priority")
        skill = gap.get("skill", "Unknown skill")
        reason = gap.get("reason", "No reason provided.")
        recommendation = gap.get("recommendation", "No recommendation provided.")
        title = f"{priority} Priority: {skill}"
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
        summary = project.get("summary", "No description available.")
        evidence_line = build_project_evidence_line(technologies, summary)

        with st.expander(name, expanded=False):
            st.markdown(f"**Stack:** {stack}")
            st.write(summary)
            st.caption(evidence_line)
            highlights = project.get("highlights", [])
            if highlights:
                st.markdown("**Highlights:**")
                render_bullets(highlights, "No highlights listed.")


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
    st.session_state.experience_level = str(profile.get("experience_level", ""))
    st.session_state.skills_text = ", ".join(profile.get("skills", []))
    st.session_state.education = str(profile.get("education", ""))
    st.session_state.languages_text = ", ".join(profile.get("languages", []))
    st.session_state.location_preference = str(profile.get("location_preference", ""))


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

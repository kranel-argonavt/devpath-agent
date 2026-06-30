"""Streamlit mock workflow for DevPath Agent Step 1C."""

from pathlib import Path
from typing import Any

import streamlit as st

from devpath.core.report_builder import create_mock_report
from devpath.services.export_service import export_markdown_report
from devpath.services.file_service import load_json_file, load_text_file
from devpath.services.github_service import is_github_username_provided


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
    """Render the DevPath Agent mock workflow."""

    st.set_page_config(page_title="DevPath Agent", page_icon="🧭", layout="wide")
    initialize_session_state()

    render_header()
    render_sidebar()

    job_text, job_source_url = render_job_posting_section()
    target_role = render_target_role_section()
    profile = render_candidate_profile_section(target_role)
    projects = render_portfolio_section()
    cv_text = render_cv_section()
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
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def render_header() -> None:
    st.title("DevPath Agent")
    st.subheader("AI Career Copilot for Junior Software Developers")
    st.caption(
        "Mock mode: this version uses deterministic local logic. Gemini, ADK, MCP, "
        "and GitHub API integration will be added later."
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.header("Project Status")
        st.write("Status: Step 1C - Streamlit mock workflow")
        st.write("Data source: local sample files")
        st.write("AI mode: mock / deterministic")
        st.write("External API calls: disabled")

        st.header("Workflow Steps")
        st.markdown(
            "- Add job posting\n"
            "- Review candidate profile\n"
            "- Select portfolio source\n"
            "- Generate mock career strategy\n"
            "- Export Markdown report"
        )

        st.header("Security Note")
        st.info("Use sample data for demos. Do not paste secrets, passwords, API keys, or private personal data.")

        st.header("Planned Features")
        st.markdown(
            "- Gemini-assisted analysis\n"
            "- Google ADK root agent\n"
            "- MCP server tools\n"
            "- GitHub repository evidence\n"
            "- Rich Streamlit workflow"
        )


def render_job_posting_section() -> tuple[str, str]:
    st.header("1. Job Posting")
    load_sample = st.checkbox("Load sample job posting", value=False)
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
        height=260,
        placeholder="Paste a job posting or load the sample posting.",
    )
    job_source_url = st.text_input(
        "Optional job source URL",
        key="job_source_url",
        placeholder="https://example.com/jobs/junior-dotnet-developer",
    )
    return job_text, job_source_url


def render_target_role_section() -> str:
    st.header("2. Target Role")
    return st.selectbox("Target role", TARGET_ROLES)


def render_candidate_profile_section(target_role: str) -> dict[str, Any]:
    st.header("3. Candidate Profile")
    load_sample = st.checkbox("Load sample profile", value=False)
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
            height=130,
            placeholder="C#, .NET, WPF, Unity, SQLite, EF Core, Git, MVVM",
        )
        languages_text = st.text_area(
            "Languages",
            key="languages_text",
            height=130,
            placeholder="English B1-B2, German A1, Ukrainian Native",
        )

    return {
        "target_roles": [target_role],
        "experience_level": experience_level.strip(),
        "skills": split_editable_list(skills_text),
        "languages": split_editable_list(languages_text),
        "education": education.strip(),
        "location_preference": location_preference.strip(),
    }


def render_portfolio_section() -> list[dict[str, Any]]:
    st.header("4. Portfolio Source")
    source = st.radio("Portfolio source", ["Local sample projects", "GitHub public repositories"], horizontal=True)

    if source == "GitHub public repositories":
        username = st.text_input("GitHub username", placeholder="octocat")
        if is_github_username_provided(username):
            st.success(f"GitHub username provided: {username.strip()}")
        else:
            st.warning("Enter a GitHub username to validate the placeholder input.")
        st.info(
            "GitHub API integration will be implemented in a later step. "
            "For now, the app uses local sample projects as fallback."
        )

    projects = load_sample_projects()
    if projects:
        render_project_cards(projects)
    return projects


def render_cv_section() -> str:
    st.header("5. Optional CV Text")
    st.warning("Do not paste sensitive personal data, API keys, passwords, or private information.")
    return st.text_area("Paste optional CV text", height=180, placeholder="Optional CV text for mock context.")


def render_analysis_settings_section() -> dict[str, Any]:
    st.header("6. Analysis Settings")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        output_style = st.selectbox("Output style", ["Concise", "Detailed"])
    with col_b:
        include_cover_letter = st.checkbox("Include cover letter draft", value=True)
    with col_c:
        include_interview_prep = st.checkbox("Include interview prep", value=True)
    return {
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

    report = create_mock_report(
        job_text=job_text,
        profile=profile,
        projects=projects,
        cv_text=cv_text,
        output_style=settings["output_style"],
    )
    if job_source_url.strip():
        report["job_analysis"]["job_source_url"] = job_source_url.strip()

    st.session_state.report = report
    st.session_state.projects = projects
    st.session_state.analysis_settings = settings
    st.success("Career strategy generated in mock mode.")


def render_results_tabs(report: dict[str, Any], projects: list[dict[str, Any]], settings: dict[str, Any]) -> None:
    st.divider()
    st.header("Career Strategy Results")
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
        render_job_analysis_tab(report["job_analysis"])
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


def render_job_analysis_tab(job_analysis: dict[str, Any]) -> None:
    st.subheader("Job Analysis")
    st.write(job_analysis.get("detected_focus", "No job analysis available."))
    st.write(f"Target role: {job_analysis.get('target_role', 'Unknown')}")
    st.write(f"Output style: {job_analysis.get('output_style', 'Concise')}")
    if job_analysis.get("job_source_url"):
        st.markdown(f"Source URL: {job_analysis['job_source_url']}")
    st.write(f"CV context provided: {'Yes' if job_analysis.get('cv_context_provided') else 'No'}")


def render_profile_match_tab(profile_match: dict[str, Any], skill_gaps: dict[str, Any]) -> None:
    st.subheader("Profile Match")
    score = int(profile_match.get("overall_score", 0))
    st.metric("Overall match score", f"{score}/100")
    st.progress(score / 100)

    st.markdown("### Category Scores")
    category_scores = profile_match.get("category_scores", {})
    columns = st.columns(3)
    for index, (name, value) in enumerate(category_scores.items()):
        with columns[index % 3]:
            st.metric(name.replace("_", " ").title(), value)

    st.markdown("### Strong Matches")
    st.write(profile_match.get("strong_matches", []) or "No strong matches detected yet.")

    st.markdown("### Partial Matches")
    st.write(profile_match.get("partial_matches", []) or "No partial matches detected yet.")

    st.markdown("### Missing Skills")
    st.write(skill_gaps.get("missing_skills", []) or "No major required skill gaps detected.")

    st.markdown("### Explanation")
    st.write(profile_match.get("explanation", "No explanation available."))


def render_portfolio_evidence_tab(portfolio_evidence: dict[str, Any], projects: list[dict[str, Any]]) -> None:
    st.subheader("Portfolio Evidence")
    st.write(portfolio_evidence.get("summary", "No portfolio summary available."))
    st.markdown("### Suggested Evidence Points")
    st.write(portfolio_evidence.get("suggested_evidence_points", []))
    render_project_cards(projects)


def render_skill_gaps_tab(skill_gaps: dict[str, Any]) -> None:
    st.subheader("Skill Gaps")
    st.write(skill_gaps.get("message", "No skill gap analysis available."))
    st.markdown("### Missing Skills")
    st.write(skill_gaps.get("missing_skills", []) or "No required missing skills detected.")
    st.markdown("### Priority")
    st.write(skill_gaps.get("priority", []) or "Keep strengthening portfolio evidence.")


def render_preparation_plan_tab(preparation_plan: dict[str, Any]) -> None:
    st.subheader("Preparation Plan")
    render_plan_block("7-Day Plan", preparation_plan.get("7_day_plan", []))
    render_plan_block("14-Day Plan", preparation_plan.get("14_day_plan", []))
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
    for question in interview_prep.get("questions", []):
        st.markdown(f"- {question}")

    st.markdown("### Practice Focus")
    st.write(interview_prep.get("practice_focus", []))


def render_export_tab(report: dict[str, Any]) -> None:
    st.subheader("Export")
    st.info(report.get("privacy_notice", "Review personal details before exporting."))
    if st.button("Export Markdown Report"):
        try:
            exported_path = export_markdown_report(report)
            st.success(f"Markdown report exported: {exported_path}")
            preview = Path(exported_path).read_text(encoding="utf-8")
            with st.expander("Markdown preview"):
                st.code(preview, language="markdown")
        except OSError as exc:
            st.error(f"Could not export Markdown report: {exc}")


def render_project_cards(projects: list[dict[str, Any]]) -> None:
    st.markdown("### Projects")
    for project in projects:
        name = project.get("name", "Portfolio project")
        technologies = ", ".join(project.get("technologies", [])) or "No stack listed"
        summary = project.get("summary", "No description available.")
        with st.expander(name, expanded=False):
            st.markdown(f"**Stack:** {technologies}")
            st.write(summary)
            highlights = project.get("highlights", [])
            if highlights:
                st.markdown("**Highlights:**")
                for highlight in highlights:
                    st.markdown(f"- {highlight}")


def render_plan_block(title: str, items: list[str]) -> None:
    st.markdown(f"### {title}")
    if not items:
        st.write("No plan items available.")
        return
    for item in items:
        st.markdown(f"- {item}")


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

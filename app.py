import json
import streamlit as st

from agent.pipeline import run_review_pipeline


# Page config
st.set_page_config(
    page_title="AI Code Review Agent",
    page_icon="🤖",
    layout="wide"
)

# Title
st.title("🤖 AI Code Review Agent")

st.markdown("""
Analyze GitHub repositories using:
- AST-based semantic parsing
- AI-powered code review
- Confidence-scored issue detection
""")

# GitHub URL input
repo_url = st.text_input(
    "Enter GitHub Repository URL",
    placeholder="https://github.com/user/repository"
)

# Run button
if st.button("Run AI Review"):

    if not repo_url.strip():

        st.warning("Please enter a GitHub repository URL.")

    else:

        with st.spinner("Running AI code review pipeline..."):

            try:

                results = run_review_pipeline(repo_url)

                st.success("Review completed successfully!")

                st.divider()

                # Display results
                for result in results:

                    function_name = result["function"]
                    file_name = result["file"]
                    function_type = result["type"]
                    issues = result["issues"]

                    with st.expander(
                        f"{function_name} ({function_type})"
                    ):

                        st.markdown(f"**File:** `{file_name}`")

                        if not issues:

                            st.success("No issues found.")

                        else:

                            for issue in issues:

                                severity = issue["severity"]
                                confidence = issue["confidence"]

                                if severity == "high":
                                    badge = "🔴 HIGH"

                                elif severity == "medium":
                                    badge = "🟠 MEDIUM"

                                else:
                                    badge = "🟢 LOW"

                                st.markdown(f"### {badge}")
                                st.markdown(
                                    f"**Issue:** {issue['title']}"
                                )

                                st.markdown(
                                    f"**Description:** {issue['description']}"
                                )

                                st.markdown(
                                    f"**Suggestion:** {issue['suggestion']}"
                                )

                                st.markdown(
                                    f"**Confidence:** {confidence}%"
                                )

                                st.progress(confidence / 100)

                                st.divider()

                # Download JSON report
                st.download_button(
                    label="Download Review Report",
                    data=json.dumps(results, indent=2),
                    file_name="review_report.json",
                    mime="application/json"
                )

            except Exception as e:

                st.error(f"Error: {e}")
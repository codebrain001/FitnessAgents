import streamlit as st
import os

def setup_page():
    # Add page title, page icon, and wide layout
    st.set_page_config(
        page_title="Outputs Viewer",
        page_icon="📄",
        layout="wide",
        menu_items={
            'Report a bug': "https://github.com/codebrain001/FitnessAgents/issues",
            'About': "## The focus of the project is to develop a fitness-oriented multi-agent system where AI agents collaborate to achieve personalized fitness goals"
        }
    )

def load_file_to_display(file_path):
    if file_path.endswith('.md'):
        with open(file_path, 'r') as file:
            return file.read()
    else:
        return "Unsupported file format."

def main():
    setup_page()
    st.header('Generated Fitness Plan and Related Outputs')
    st.subheader('Results Derived from the Personalized Fitness Plan Generator')

    base_path = 'src/tools/data/outputs'  # Adjust the path as necessary

    files = [
        "health_report_analysis.md",
        "nutrition_plan.md",
        "user_persona.md",
        "wellbeing_plan.md",
        "workout_plan.md"
    ]

    for file_name in files:
        file_path = os.path.join(base_path, file_name)
        if os.path.exists(file_path):
            with st.expander(file_name):
                content = load_file_to_display(file_path)
                if file_name.endswith('.md'):
                    st.markdown(content)
                else:
                    st.write(content)
        else:
            st.warning(f"{file_name} does not exist in the specified path.")

if __name__ == "__main__":
    if st.session_state['workflow_completed'] == True or not None:
        main()
    else:
        st.error("No outputs found. Please ensure the agentic workflow is completed.")
        st.info('Please generate your fitness plan on the home page. Once the plan is generated, return to this page to view the results.', icon="ℹ️")
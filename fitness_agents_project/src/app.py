
import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging
import nest_asyncio
import json
import time

from agents import Agents
from tools.toolset import Toolset
from tools.query_engine_tool import MedicalReportRagPipeline
from tasks import AgentTasks

from utils import StreamToExpander
import streamlit as st
from streamlit_date_picker import date_range_picker, PickerType
from crewai import Crew, Process

from langchain_openai import ChatOpenAI

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

dotenv_path = 'src/.env'
# Load the .env file
load_dotenv(dotenv_path)

model_name = os.getenv("OPENAI_MODEL_NAME")

input_dir = "src/tools/data/inputs"

def setup_page():
    st.set_page_config(
        page_title="Fitness Agents",
        page_icon="🏠",
        layout="wide",
        menu_items={
            'Report a bug': "https://github.com/codebrain001/FitnessAgents/issues",
            'About': "## The focus of the project is to develop a fitness-oriented multi-agent system where AI agents collaborate to achieve personalized fitness goals"
        }
    )

def main_page():
    st.title("Personalized Fitness Plan Generator")
    st.write("Create a fitness plan tailored to your preferences and goals.")

    # User Demographics
    with st.expander("User Demographics"):
        age = st.number_input("Enter your age", min_value=10, max_value=100, value=st.session_state.get('age', 25))
        st.session_state['age'] = age
        gender = st.radio("Select your gender", options=["Male", "Female"], index=["Male", "Female"].index(st.session_state.get('gender', "Male")))
        st.session_state['gender'] = gender
        fitness_level = st.selectbox("What is your current fitness level?", options=["Beginner", "Intermediate", "Advanced"], index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.get('fitness_level', "Beginner")))
        st.session_state['fitness_level'] = fitness_level

    with st.expander("Health Information"):
        conditions = st.text_input("Do you have any pre-existing conditions or injuries?", value=st.session_state.get('conditions', ''))
        st.session_state['conditions'] = conditions
        # Or upload upload documents
        medical_report = st.file_uploader(label="Upload medical reports", type=["doc", "docx", "txt", "pdf", "mp4", "mp3"], accept_multiple_files=True) 
        st.session_state['medical_report'] = medical_report
        if medical_report:
            st.session_state['medical_report_uploaded_status'] = True
            
            save_uploaded_files_path = "src/tools/data/inputs/"
            for uploaded_file in medical_report:
                save_path = os.path.join(save_uploaded_files_path, uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.toast(f"Uploaded and saved: {uploaded_file.name}")
        else:
            st.session_state['medical_report_uploaded_status'] = False
        weight = st.number_input("Enter your weight (kg)", min_value=30, max_value=200, value=st.session_state.get('weight', 70), step=1)
        st.session_state['weight'] = weight
        height = st.number_input("Enter your height (cm)", min_value=100, max_value=250, value=st.session_state.get('height', 170), step=1)
        st.session_state['height'] = height

    with st.expander("Workout Preferences"):
        workout_time = st.radio("When do you prefer to workout?", options=["Morning", "Afternoon", "Evening"], index=["Morning", "Afternoon", "Evening"].index(st.session_state.get('workout_time', "Morning")))
        st.session_state['workout_time'] = workout_time
        workout_location = st.selectbox("Where do you prefer to workout?", options=["At home", "Gym", "Outdoor"], index=["At home", "Gym", "Outdoor"].index(st.session_state.get('workout_location', "At home")))
        st.session_state['workout_location'] = workout_location

    with st.expander("Dietary Preferences"):
        dietary_restrictions = st.multiselect(
            "Do you have any dietary restrictions or preferences?",
            options=["Vegetarian", "Vegan", "Keto", "Paleo", "Gluten-Free", "Dairy-Free", "Low-Carb", "None"],
            default=st.session_state.get('dietary_restrictions', [])
        )
        st.session_state['dietary_restrictions'] = dietary_restrictions

    with st.expander("Fitness Goal and Plan Details"):
        st.markdown("### Select the Date Range for Your Fitness Plan")
        # Default start and end dates
        default_start = datetime.now()
        default_end = datetime.now() + timedelta(days=7)
        refresh_value = timedelta(days=1)
        #  Date Range Picker
        date_range_string = date_range_picker(picker_type=PickerType.date,
                                    start=default_start, end=default_end,
                                    key='date_range_picker',
                                    refresh_button={'is_show': True, 'button_name': 'Refresh Last 1 Days',
                                                    'refresh_value': refresh_value})
        if date_range_string:
            st.session_state['plan_start_date'], st.session_state['plan_end_date'] = date_range_string
    
    intensity = st.selectbox("Select the intensity of your fitness plan", options=["Easy", "Intermediate", "Hard"], index=["Easy", "Intermediate", "Hard"].index(st.session_state.get('intensity', "Easy")))
    st.session_state['intensity'] = intensity
    daily_goal = st.text_area("Describe your fitness goal and current feelings", value=st.session_state.get('daily_goal', ''))
    st.session_state['daily_goal'] = daily_goal

    # Generate Plan Button
    button_clicked = st.button("Generate Fitness Plan")
    if button_clicked:
        st.session_state['workflow_completed'] = False 
        fitness_details = {
            "age": st.session_state['age'],
            "gender": st.session_state['gender'],
            "fitness_level": st.session_state['fitness_level'],
            "conditions": st.session_state['conditions'],
            "medical_report_uploaded_status": st.session_state['medical_report_uploaded_status'],
            "weight": st.session_state['weight'],
            "height": st.session_state['height'],
            "workout_time": st.session_state['workout_time'],
            "workout_location": st.session_state['workout_location'],
            "dietary_restrictions": st.session_state['dietary_restrictions'],
            "plan_start_date": st.session_state['plan_start_date'],
            "plan_end_date": st.session_state['plan_end_date'],
            "intensity": st.session_state['intensity'],
            "daily_goal": st.session_state['daily_goal']
        }

        # Convert the dictionary to a JSON string and save it to a file
        json_filename = "src/tools/data/fitness_details.json"
        with open(json_filename, "w") as json_file:
            json.dump(fitness_details, json_file, indent=4)

        st.success("Preference and goals received!")

        # Directly initiate the agentic crew after saving the JSON
        with st.spinner("Initiating Fitness Agents...Please wait for process to complete"):
            time.sleep(5)  
        fitness_crew = create_agentic_crew()
        start_time = time.time()
        st.info('Agentic Workflow Execution started...', icon="1️⃣")
        with st.status("🤖 **Agents at work...**", state="running", expanded=True) as status:
            with st.container(height=500, border=False):
                sys.stdout = StreamToExpander(st)
                result = fitness_crew.kickoff()
            status.update(label="✅ Requirement Analysis and Specification Successful!",
                          state="complete", expanded=False)
        st.subheader('View Agentic Workflow Outputs', anchor=False, divider="rainbow")
        st.info("This section allows you to view the outputs of the agentic workflow. Click the link below to access the Output Viewer Page.")
        st.page_link("pages/1_outputs_viewer.py", label="Output Viewer", icon="1️⃣")

        end_time = time.time()
        elapsed_time = end_time - start_time
        # Remove uploaded input document(s)
        for file_name in os.listdir(input_dir):
            file_path = os.path.join(input_dir, file_name)
            try:
                os.remove(file_path)
                st.toast("Uploaded document(s) removed from App.")
            except Exception as e:
                st.error(f'Failed to delete {file_path}. Reason: {e}')
    
        st.info(f"Time executed: {elapsed_time:.2f} seconds", icon="1️⃣")

        st.session_state['workflow_completed'] = True

def create_agentic_crew():
    tool_set = Toolset()
    query_engine_tools = MedicalReportRagPipeline(document_dir=input_dir)
    agents = Agents(tool_set, query_engine_tools)
    data_ingestion_and_interpretation_agent = agents.data_ingestion_and_interpretation_agent()
    health_monitoring_agent = agents.health_monitoring_agent()
    wellbeing_agent = agents.wellbeing_agent()
    fitness_coach_agent = agents.fitness_coach_agent()
    nutritionist_agent = agents.nutritionist_agent()

    agent_tasks = AgentTasks(
        data_ingestion_and_interpretation_agent,
        health_monitoring_agent,
        wellbeing_agent,
        fitness_coach_agent,
        nutritionist_agent,
    )

    data_ingestion_task = agent_tasks.create_data_ingestion_task()
    health_monitoring_task = agent_tasks.create_health_monitoring_task()
    wellbeing_task = agent_tasks.create_wellbeing_task()
    fitness_coach_task = agent_tasks.create_fitness_coach_task()
    nutritionist_task = agent_tasks.create_nutritionist_task()
    

    fitness_crew = Crew(
        agents = [
            data_ingestion_and_interpretation_agent,
            health_monitoring_agent,
            wellbeing_agent,
            fitness_coach_agent,
            nutritionist_agent,
        ],
        tasks = [
            data_ingestion_task,
            health_monitoring_task,
            wellbeing_task,
            fitness_coach_task,
            nutritionist_task,
        ],
        verbose=True,
        memory=True,
        process=Process.hierarchical,
        manager_llm=ChatOpenAI(model=model_name)
    )
    
    return fitness_crew

def main():
    setup_page()
    main_page()

if __name__ == "__main__":
    main()
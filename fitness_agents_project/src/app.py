
import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging
import nest_asyncio

from utils import StreamToExpander
import streamlit as st
from streamlit_date_picker import date_range_picker, PickerType

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


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
        age = st.number_input("Enter your age", min_value=10, max_value=100, value=25)
        gender = st.radio("Select your gender", options=["Male", "Female"])
        fitness_level = st.selectbox("What is your current fitness level?", options=["Beginner", "Intermediate", "Advanced"])

    with st.expander("Health Information"):
        conditions = st.text_input("Do you have any pre-existing conditions or injuries?")
        weight = st.number_input("Enter your weight (kg)", min_value=30, max_value=200, value=70, step=1)
        height = st.number_input("Enter your height (cm)", min_value=100, max_value=250, value=170, step=1)

    with st.expander("Workout Preferences"):
        workout_time = st.radio("When do you prefer to workout?", options=["Morning", "Afternoon", "Evening"])
        workout_location = st.selectbox("Where do you prefer to workout?", options=["At home", "Gym", "Outdoor"])

    with st.expander("Dietary Preferences (Optional)"):
        dietary_restrictions = st.multiselect(
            "Do you have any dietary restrictions or preferences?",
            options=["Vegetarian", "Vegan", "Keto", "Paleo", "Gluten-Free", "Dairy-Free", "Low-Carb", "None"]
        )

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
            plan_start_date, plan_end_date = date_range_string
            
        intensity = st.selectbox("Select the intensity of your fitness plan", options=["Easy", "Intermediate", "Hard"])
        daily_goal = st.text_area("What is your fitness goal")

    # Generate Plan Button
    if st.button("Generate Fitness Plan"):
        fitness_details = {
            "age": age,
            "gender": gender,
            "fitness_level": fitness_level,
            "conditions": conditions,
            "weight": weight,
            "height": height,
            "workout_time": workout_time,
            "workout_location": workout_location,
            "dietary_restrictions": dietary_restrictions,
            "plan_start_date": plan_start_date,
            "plan_end_date": plan_end_date,
            "intensity": intensity,
            "daily_goal": daily_goal
        }

        st.success("Preference and goals received!")
        return fitness_details


def main():
    setup_page()
    main_page()

if __name__ == "__main__":
    main()
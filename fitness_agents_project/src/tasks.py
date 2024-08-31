import os
from crewai import Task

class AgentTasks:
    def __init__(
            self,
            data_ingestion_and_interpretation_agent,
            health_monitoring_agent,
            wellbeing_agent,
            fitness_coach_agent,
            nutritionist_agent,
        ):
        self.data_ingestion_and_interpretation_agent = data_ingestion_and_interpretation_agent
        self.health_monitoring_agent = health_monitoring_agent
        self.wellbeing_agent = wellbeing_agent
        self.fitness_coach_agent = fitness_coach_agent
        self.nutritionist_agent = nutritionist_agent
        self.base_output_path = f'src/tools/data/outputs'

    
    def create_data_ingestion_task(self):
        return Task(
            description=(
                "Collect and understand the user fitness plan requirements from the application UI. "
                "Based on the inputs received, create a structured document that defines a detailed user persona. "
                "This persona should capture the user's fitness goals, preferences, and any constraints or special considerations."
            ),
            expected_output=(
                "Produce a structured document titled 'User Persona' that provides a rich context that includes "
                "demographics information, fitness profile, workout preferences, dietary considerations, goal setting and plan duration. "
            ),
            agent=self.data_ingestion_and_interpretation_agent,
            output_file=f'{self.base_output_path}/user_persona.md',
        )

    def create_health_monitoring_task(self):
        return Task(
            description=(
                "Analyze and interpret health and fitness data collected from the user's Apple Watch, providing personalized insights and recommendations based on their user persona and goals."
                "This includes analyzing key health metrics, identifying trends and patterns, and offering actionable advice."
            ),
            expected_output=(
                "Generate a health report with the following sections:\n"
                "1. **Health Metrics Summary**\n"
                "2. **Health Trend Analysis**\n"
                "3. **Personalized Recommendations**\n"
                "4. **Alerts and Warnings** (If any)\n"
            ),
            agent=self.health_monitoring_agent,
            output_file=f'{self.base_output_path}/health_report_analysis.md',
        )
    
    def create_wellbeing_task(self):
        return Task(
            description=(
                "Curate personalized music or podcast recommendations that align with the user's fitness goals, derived from their current mental state or mood when possible from Spotify. "
                "Additionally, offer tailored recovery advice to support overall well-being, including strategies for both mental and physical recovery."
            ),
            expected_output=(
                "Produce a personalized wellbeing plan that includes:\n"
                "1. **Music/Podcast Recommendations**:\n"
                "2. **Recovery Recommendations**:\n"
            ),
            agent=self.wellbeing_agent,
            output_file=f'{self.base_output_path}/wellbeing_plan.md',
        )
    
    def create_fitness_coach_task(self):
        return Task(
            description=(
            "Design and implement personalized workout plans that align with the user’s fitness level and goals, current health state, targeted focus areas and the respective plan start and end date. "
            "Ensure the workouts are effective, safe, and adaptable to environmental conditions and other external factors. "
            "Include relevant YouTube video links for exercise demonstrations."
            ),
            expected_output=(
                "Create a personalized workout plan document that includes:\n"
                "1. **Workout Schedule**:\n"
                "2. **Exercise Breakdown**:\n"
                "3. **Safety Guidelines**:\n"
                "4. **Location and Environmental Adjustments**:\n"
            ),
            agent=self.fitness_coach_agent,
            output_file=f'{self.base_output_path}/workout_plan.md',
        )

    def create_nutritionist_task(self):
        return Task(
            description=(
                "Develop and manage tailored nutrition plans that align with the user’s fitness level and goals, dietary preferences, health requirements and the respective plan start and end date.  "
                "Provide evidence-based nutritional advice that supports the user’s fitness and wellness objectives."
            ),
            expected_output=(
                "Produce a comprehensive nutrition plan that includes:\n"
                "1. **Meal Plans**:\n"
                "2. **Nutritional Advice**:\n"
                "3. **Supplement Guidance (if applicable)**:\n"
                "4. **Shopping List**:\n"
            ),
            agent=self.nutritionist_agent,
            output_file=f'{self.base_output_path}/nutrition_plan.md',
        )


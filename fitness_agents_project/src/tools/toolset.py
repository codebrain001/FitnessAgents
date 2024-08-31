import os
from dotenv import load_dotenv

from crewai_tools import (
    SerperDevTool,
    WebsiteSearchTool, 
    YoutubeVideoSearchTool, 
    FileReadTool, 
    PGSearchTool
)

from composio_crewai import ComposioToolSet, Action
from crewai_tools import ComposioTool
from crewai_tools import LlamaIndexTool

from llama_index.tools.arxiv import ArxivToolSpec

# dotenv_path = '../../.env'
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
# Load the .env file
load_dotenv(dotenv_path)

# Access the environment variables
database_url = os.getenv('DATABASE_URL')

class Toolset:
    """
    A class to intialize some tools
    """
    def __init__(self):
        """
        Initialize all the search and scraping tools.
        """
        self.search_tool = self.create_search_tool()
        self.website_rag_tool = self.create_website_rag_tool()
        self.youtube_searcth_tool = self.create_youtube_search_tool()
        self.json_file_reader_tool = self.create_json_file_reader_tool()
        self.pg_rag_tool = self.create_pg_rag_tool()
        self.calendar_tool = self.create_calendar_tool()
        self.weather_tool = self.create_weather_tool()
        # self.spotify_tool = self.create_spotify_tool()

    def create_search_tool(self):
        """
        Create a general search tool using SerperDevTool.

        Returns:
            SerperDevTool: An instance of SerperDevTool for general search.
        """
        return SerperDevTool()

    def create_website_rag_tool(self):
        """
        Create a tool to scrape websites.

        Returns:
            ScrapeWebsiteTool: An instance of ScrapeWebsiteTool for scraping websites.
        """
        return WebsiteSearchTool()
    
    def create_youtube_search_tool(self):
        """
        Create a tool to search for videos on youtube.

        Returns:
            YoutubeVideoSearchTool: An instance of YoutubeVideoSearchTool to perform semantic searches within Youtube videos.
        """
        return YoutubeVideoSearchTool()
    
    def create_json_file_reader_tool(self):
        """
        Create a tool to read the JSON file input recevied from the App UI

        returns:
            FileReadTool: An instance of FileReadTool facilitating file reading and content retrieval
        """
        return FileReadTool(file_path='src/tools/data/fitness_details.json')
    
    def create_pg_rag_tool(self):
        """
        Create a tool for semantic searches within PostgreSQL database tables.

        Returns:
            PGSearchTool: An instance of PGSearchTool to conduct a semantic search on a table within a PostgreSQL database.
        """
        return PGSearchTool(
            db_uri=str(database_url), table_name='health_data'
        )
    
    def create_calendar_tool(self):
        """
        Create a tool to create a new event in a Google Calendar.

        Returns:
            Composio Action instance for creating a new Google Calendar event
        """
        action = Action.GOOGLECALENDAR_CREATE_EVENT
        google_calendar_tool = ComposioTool.from_action(action)
        return google_calendar_tool

    def create_weather_tool(self):
        """
        Create a tool to query the OpenWeatherMap API.

        Returns:
            Composio Action instance for OpenWeatherMap API.
        """
        action = Action.WEATHERMAP_WEATHER
        weather_tool = ComposioTool.from_action(action)
        return weather_tool
    
    # def create_spotify_tool(self):
    #     """
    #     Create a tool to get recommendation from spotify

    #     Returns:
    #         Composio Action instance for Spotify recommendation
    #     """
    #     action = Action.SPOTIFY_GET_RECOMMENDATIONS
    #     spotify_reccommendation_tool = ComposioTool.from_action(action)
    #     return spotify_reccommendation_tool
    

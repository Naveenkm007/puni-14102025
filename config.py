import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Notion Integration
    NOTION_TOKEN = os.getenv('NOTION_TOKEN', '')
    NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID', '')
    
    # Weather API
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
    
    # Flask Settings
    FLASK_HOST = os.getenv('FLASK_HOST', 'localhost')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'task_planner.db')
    
    # Task Settings
    DEFAULT_WORK_START_HOUR = int(os.getenv('DEFAULT_WORK_START_HOUR', 9))
    DEFAULT_WORK_END_HOUR = int(os.getenv('DEFAULT_WORK_END_HOUR', 17))
    DEFAULT_BREAK_DURATION = int(os.getenv('DEFAULT_BREAK_DURATION', 15))
    DEFAULT_TASK_LENGTH = int(os.getenv('DEFAULT_TASK_LENGTH', 60))
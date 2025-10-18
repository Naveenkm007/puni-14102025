# Personal Task Planner Bot - Core Implementation Structure
# File: task_planner_agent.py

import os
import json
import sqlite3
import schedule
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from langchain.agents import Agent
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
import requests
import openai

# Add Google API client library to requirements
# We'll need to add this to the imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    Credentials = None
    build = None
    GOOGLE_API_AVAILABLE = False
    print("Google API libraries not available. Google Calendar integration will be limited.")

# Data Models
@dataclass
class Task:
    id: str
    title: str
    description: str
    priority: int  # 1-5 scale
    due_date: Optional[datetime]
    estimated_duration: int  # in minutes
    status: str  # 'pending', 'in_progress', 'completed'
    weather_dependent: bool = False
    location_dependent: bool = False
    reminder_enabled: bool = True
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # List of task IDs that this task depends on
    source: str = "local"  # Source of the task (local, notion, etc.)

@dataclass
class UserPreferences:
    work_hours: tuple  # (start_hour, end_hour)
    break_duration: int
    preferred_task_length: int
    weather_sensitivity: float
    location_based_notifications: bool = True
    task_reminders: bool = True
    weather_alerts: bool = True
    focus_periods: List[str] = field(default_factory=list)

@dataclass
class Location:
    latitude: float
    longitude: float
    city: str = ""
    country: str = ""
    timezone: str = ""

@dataclass
class Notification:
    id: str
    user_id: str
    title: str
    message: str
    type: str  # 'task_reminder', 'weather_alert', 'location_alert'
    timestamp: datetime
    read: bool = False
    task_id: Optional[str] = None

class DatabaseManager:
    def __init__(self, db_path: str = "task_planner.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                priority INTEGER,
                due_date TEXT,
                estimated_duration INTEGER,
                status TEXT,
                weather_dependent BOOLEAN,
                location_dependent BOOLEAN,
                reminder_enabled BOOLEAN,
                dependencies TEXT DEFAULT '[]',  -- JSON array of task IDs
                source TEXT DEFAULT 'local',
                created_at TEXT,
                updated_at TEXT
            )
        ''')

        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                work_start_hour INTEGER,
                work_end_hour INTEGER,
                break_duration INTEGER,
                preferred_task_length INTEGER,
                weather_sensitivity REAL,
                location_based_notifications BOOLEAN,
                task_reminders BOOLEAN,
                weather_alerts BOOLEAN,
                created_at TEXT,
                updated_at TEXT
            )
        ''')

        # User location table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_location (
                user_id TEXT PRIMARY KEY,
                latitude REAL,
                longitude REAL,
                city TEXT,
                country TEXT,
                timezone TEXT,
                last_updated TEXT
            )
        ''')

        # Notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                title TEXT,
                message TEXT,
                type TEXT,
                timestamp TEXT,
                read BOOLEAN,
                task_id TEXT,
                created_at TEXT
            )
        ''')

        # Task history for learning
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_history (
                id TEXT PRIMARY KEY,
                task_id TEXT,
                action TEXT,
                timestamp TEXT,
                context TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def save_task(self, task: Task):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO tasks 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.id, task.title, task.description, task.priority,
            task.due_date.isoformat() if task.due_date else None,
            task.estimated_duration, task.status, task.weather_dependent,
            task.location_dependent, task.reminder_enabled,
            json.dumps(task.dependencies),  # Store dependencies as JSON
            task.source,  # Store source
            datetime.now().isoformat(), datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()

    def save_user_location(self, user_id: str, location: Location):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_location
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            location.latitude,
            location.longitude,
            location.city,
            location.country,
            location.timezone,
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()

    def get_user_location(self, user_id: str) -> Optional[Location]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT latitude, longitude, city, country, timezone FROM user_location WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Location(
                latitude=row[0],
                longitude=row[1],
                city=row[2],
                country=row[3],
                timezone=row[4]
            )
        return None

    def save_notification(self, notification: Notification):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO notifications
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            notification.id,
            notification.user_id,
            notification.title,
            notification.message,
            notification.type,
            notification.timestamp.isoformat(),
            notification.read,
            notification.task_id,
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()

    def get_unread_notifications(self, user_id: str) -> List[Notification]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, title, message, type, timestamp, read, task_id 
            FROM notifications 
            WHERE user_id = ? AND read = 0
            ORDER BY timestamp DESC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        notifications = []
        for row in rows:
            notifications.append(Notification(
                id=row[0],
                user_id=row[1],
                title=row[2],
                message=row[3],
                type=row[4],
                timestamp=datetime.fromisoformat(row[5]),
                read=row[6],
                task_id=row[7]
            ))
        
        return notifications

    def mark_notification_as_read(self, notification_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE notifications SET read = 1 WHERE id = ?", (notification_id,))
        conn.commit()
        conn.close()

class LocationService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('LOCATION_API_KEY')
        self.base_url = "https://api.opencagedata.com/geocode/v1/json"

    def reverse_geocode(self, latitude: float, longitude: float) -> Dict:
        """Get location details from coordinates"""
        if not self.api_key:
            # Return mock data for demo purposes
            return {
                "city": "Bengaluru",
                "country": "India",
                "timezone": "Asia/Kolkata"
            }
        
        url = f"{self.base_url}"
        params = {
            'q': f"{latitude},{longitude}",
            'key': self.api_key
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()
            if data.get('results'):
                components = data['results'][0]['components']
                return {
                    "city": components.get('city', components.get('town', 'Unknown')),
                    "country": components.get('country', 'Unknown'),
                    "timezone": data['results'][0].get('annotations', {}).get('timezone', {}).get('name', 'UTC')
                }
        except Exception as e:
            print(f"Error in reverse geocoding: {e}")
        
        return {
            "city": "Unknown",
            "country": "Unknown",
            "timezone": "UTC"
        }

    def get_local_time(self, timezone: str) -> str:
        """Get local time for a timezone"""
        try:
            # In a real implementation, you would use a timezone library
            # For demo, we'll just return current time
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class WeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"

    def get_current_weather(self, city: str = "Bengaluru", lat: Optional[float] = None, lon: Optional[float] = None) -> Dict:
        url = f"{self.base_url}/weather"
        params = {
            'appid': self.api_key,
            'units': 'metric'
        }
        
        # Use coordinates if provided, otherwise use city
        if lat is not None and lon is not None:
            params['lat'] = str(lat)
            params['lon'] = str(lon)
        else:
            params['q'] = city

        try:
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            return {'error': str(e)}

    def should_postpone_outdoor_task(self, weather_data: Dict) -> bool:
        if 'main' not in weather_data:
            return False

        # Check for rain, storm, or extreme temperatures
        weather_conditions = weather_data.get('weather', [])
        for condition in weather_conditions:
            if condition.get('main') in ['Rain', 'Thunderstorm', 'Snow']:
                return True

        temp = weather_data.get('main', {}).get('temp', 25)
        if temp < 10 or temp > 40:  # Extreme temperatures
            return True

        return False

class CalendarIntegration:
    def __init__(self, credentials_path: str = 'credentials.json'):
        self.credentials_path = credentials_path
        self.service = None
        if GOOGLE_API_AVAILABLE:
            self._initialize_service()

    def _initialize_service(self):
        """Initialize the Google Calendar API service"""
        try:
            # Check if we have valid credentials
            creds = None
            if os.path.exists('token.json') and Credentials:
                creds = Credentials.from_authorized_user_file('token.json')
            
            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                # In a real implementation, you would handle the OAuth flow
                # For now, we'll just set up a mock service
                pass
            
            if creds and build:
                self.service = build('calendar', 'v3', credentials=creds)
        except Exception as e:
            print(f"Error initializing Google Calendar service: {e}")
            self.service = None

    def get_events_today(self) -> List[Dict]:
        """Fetch today's calendar events"""
        if not self.service:
            # Return mock data for demo purposes
            return [
                {
                    'id': 'event1',
                    'summary': 'Team Meeting',
                    'start': {'dateTime': '2023-01-01T10:00:00Z'},
                    'end': {'dateTime': '2023-01-01T11:00:00Z'}
                },
                {
                    'id': 'event2',
                    'summary': 'Lunch Break',
                    'start': {'dateTime': '2023-01-01T12:00:00Z'},
                    'end': {'dateTime': '2023-01-01T13:00:00Z'}
                }
            ]
        
        try:
            # Get today's date range
            now = datetime.utcnow()
            start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)
            end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59)
            
            # Format for Google Calendar API
            time_min = start_of_day.isoformat() + 'Z'
            time_max = end_of_day.isoformat() + 'Z'
            
            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Convert to our format
            formatted_events = []
            for event in events:
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'Untitled Event'),
                    'start': event['start'],
                    'end': event['end'],
                    'location': event.get('location', ''),
                    'description': event.get('description', '')
                })
            
            return formatted_events
        except Exception as e:
            print(f"Error fetching calendar events: {e}")
            return []

    def create_event(self, task: Task) -> bool:
        """Create a calendar event for a task"""
        if not self.service:
            # Simulate successful creation for demo purposes
            return True
        
        try:
            # Create event object
            event = {
                'summary': task.title,
                'description': task.description,
                'start': {
                    'dateTime': datetime.now().isoformat() + 'Z',  # Placeholder time
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': (datetime.now() + timedelta(minutes=task.estimated_duration)).isoformat() + 'Z',
                    'timeZone': 'UTC',
                },
            }
            
            # Insert the event
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            return True
        except Exception as e:
            print(f"Error creating calendar event: {e}")
            return False

    def get_free_slots(self, duration: int) -> List[tuple]:
        """Find free time slots for a given duration"""
        # For demo purposes, return some mock free slots
        return [
            (9, 10),   # 9:00-10:00
            (14, 15),  # 14:00-15:00
            (16, 17)   # 16:00-17:00
        ]

class NotionIntegration:
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv('NOTION_TOKEN', '')
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2021-08-16"
        }

    def get_tasks_from_database(self, database_id: str) -> List[Dict]:
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json().get('results', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching tasks from Notion: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

    def create_task_in_notion(self, task: Task, database_id: str):
        url = "https://api.notion.com/v1/pages"
        
        # Prepare properties based on common Notion task database structures
        properties: Dict[str, Dict] = {
            "Name": {"title": [{"text": {"content": task.title}}]},
        }
        
        # Add priority if it's a number property
        if hasattr(task, 'priority'):
            properties["Priority"] = {"number": task.priority}
        
        # Add status if it's a select property
        if hasattr(task, 'status'):
            status_name = "To Do"
            if task.status == "completed":
                status_name = "Done"
            elif task.status == "in_progress":
                status_name = "In Progress"
            properties["Status"] = {"select": {"name": status_name}}
        
        # Add due date if available
        if task.due_date:
            properties["Date"] = {
                "date": {
                    "start": task.due_date.isoformat()
                }
            }
        
        # Add tags if available
        if task.tags:
            properties["Tags"] = {
                "multi_select": [{"name": tag} for tag in task.tags]
            }
        
        data = {
            "parent": {"database_id": database_id},
            "properties": properties
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating task in Notion: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def update_task_in_notion(self, task: Task, page_id: str):
        """Update a task in Notion"""
        url = f"https://api.notion.com/v1/pages/{page_id}"
        
        # Map our status to Notion status
        notion_status = "Done" if task.status == "completed" else "To Do"
        if task.status == "in_progress":
            notion_status = "In Progress"
        
        # Prepare properties to update
        properties: Dict[str, Dict] = {
            "Name": {"title": [{"text": {"content": task.title}}]},
        }
        
        # Add priority if it's a number property
        if hasattr(task, 'priority'):
            properties["Priority"] = {"number": task.priority}
        
        # Add status if it's a select property
        properties["Status"] = {"select": {"name": notion_status}}
        
        # Add due date if available
        if task.due_date:
            properties["Date"] = {
                "date": {
                    "start": task.due_date.isoformat()
                }
            }
        
        # Add tags if available
        if task.tags:
            properties["Tags"] = {
                "multi_select": [{"name": tag} for tag in task.tags]
            }
        
        data = {
            "properties": properties
        }
        
        try:
            response = requests.patch(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Error updating task in Notion: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
    
    def parse_notion_task_to_local_task(self, notion_task_data: Dict, database_id: str) -> Task:
        """Convert a Notion task to our local Task format"""
        properties = notion_task_data.get('properties', {})
        
        # Get task title
        title = ''
        if 'Name' in properties:
            title_data = properties['Name'].get('title', [])
            if title_data:
                title = title_data[0].get('text', {}).get('content', '')
        
        # Get priority
        priority = 3  # Default medium priority
        if 'Priority' in properties:
            priority = properties['Priority'].get('number', 3)
        
        # Get status
        status = 'pending'
        if 'Status' in properties:
            status_text = properties['Status'].get('select', {}).get('name', 'pending')
            # Map Notion status to our status
            if status_text.lower() in ['done', 'completed']:
                status = 'completed'
            elif status_text.lower() in ['in progress', 'in progress']:
                status = 'in_progress'
            else:
                status = 'pending'
        
        # Get due date
        due_date = None
        if 'Date' in properties:
            date_info = properties['Date'].get('date', {})
            if date_info and 'start' in date_info:
                try:
                    due_date = datetime.fromisoformat(date_info['start'].replace('Z', '+00:00'))
                except ValueError:
                    pass  # Invalid date format
        
        # Get tags
        tags = []
        if 'Tags' in properties:
            tags_data = properties['Tags'].get('multi_select', [])
            tags = [tag.get('name', '') for tag in tags_data if tag.get('name')]
        
        # Create task object
        task = Task(
            id=f"notion_{notion_task_data.get('id', '')}",
            title=title,
            description=f"Imported from Notion database {database_id}",
            priority=priority,
            due_date=due_date,
            estimated_duration=60,  # Default duration, could be parsed from Notion
            status=status,
            weather_dependent=False,
            location_dependent=False,
            reminder_enabled=True,
            dependencies=[],  # Would need to parse from Notion relations
            tags=tags,
            source='notion'
        )
        
        return task

class TaskPriorizer:
    @staticmethod
    def calculate_priority_score(task: Task, context: Dict, all_tasks: Optional[List[Task]] = None) -> float:
        base_score = task.priority * 20  # Base priority (1-5) * 20

        # Urgency factor based on due date
        if task.due_date:
            days_until_due = (task.due_date - datetime.now()).days
            urgency_score = max(0, 50 - (days_until_due * 5))
            base_score += urgency_score

        # Duration factor - shorter tasks get slight boost
        if task.estimated_duration <= 30:
            base_score += 10

        # Weather factor
        current_weather = context.get('weather', {})
        if task.weather_dependent and 'rain' in str(current_weather).lower():
            base_score -= 30

        # Location factor (demo implementation)
        user_location = context.get('location', {})
        if task.location_dependent and user_location:
            # In a real implementation, you might boost location-relevant tasks
            base_score += 5

        # Dependency factor - tasks with dependencies get priority boost
        # but tasks that depend on incomplete tasks get priority reduction
        if all_tasks:
            # Check if this task has dependencies that are not completed
            incomplete_dependencies = 0
            completed_dependencies = 0
            
            for dep_id in task.dependencies:
                dep_task = next((t for t in all_tasks if t.id == dep_id), None)
                if dep_task:
                    if dep_task.status == 'completed':
                        completed_dependencies += 1
                    else:
                        incomplete_dependencies += 1
            
            # Reduce priority if dependencies are not met
            base_score -= incomplete_dependencies * 20
            
            # Boost priority if task is a dependency of other tasks
            dependent_count = sum(1 for t in all_tasks if task.id in t.dependencies and t.status != 'completed')
            base_score += dependent_count * 15

        return base_score

    @staticmethod
    def prioritize_tasks(tasks: List[Task], context: Dict) -> List[Task]:
        scored_tasks = []
        for task in tasks:
            score = TaskPriorizer.calculate_priority_score(task, context, tasks)
            scored_tasks.append((task, score))

        # Sort by score (descending)
        scored_tasks.sort(key=lambda x: x[1], reverse=True)
        return [task for task, _ in scored_tasks]

class NotificationService:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def create_task_reminder(self, user_id: str, task: Task, minutes_before: int = 30) -> Optional[Notification]:
        """Create a task reminder notification"""
        if not task.due_date:
            return None
            
        # Calculate reminder time
        reminder_time = task.due_date - timedelta(minutes=minutes_before)
        
        # Only create reminder if it's in the future
        if reminder_time > datetime.now():
            notification = Notification(
                id=f"notif_{time.time()}",
                user_id=user_id,
                title="Upcoming Task Reminder",
                message=f"Don't forget: {task.title} in {minutes_before} minutes!",
                type="task_reminder",
                timestamp=reminder_time,
                task_id=task.id
            )
            self.db_manager.save_notification(notification)
            return notification
        return None

    def create_weather_alert(self, user_id: str, weather_data: Dict, location: Location) -> Optional[Notification]:
        """Create a weather alert notification"""
        weather_conditions = weather_data.get('weather', [])
        main_condition = ""
        if weather_conditions:
            main_condition = weather_conditions[0].get('main', '').lower()
            
        alert_needed = False
        message = ""
        
        if 'rain' in main_condition or 'thunderstorm' in main_condition:
            alert_needed = True
            message = f"Heads up! {weather_data.get('weather', [{}])[0].get('description', 'Rain')} expected in {location.city}. Consider rescheduling outdoor tasks."
        elif 'snow' in main_condition:
            alert_needed = True
            message = f"Winter weather alert! Snow expected in {location.city}. Plan accordingly."
            
        if alert_needed:
            notification = Notification(
                id=f"notif_{time.time()}",
                user_id=user_id,
                title="Weather Alert",
                message=message,
                type="weather_alert",
                timestamp=datetime.now()
            )
            self.db_manager.save_notification(notification)
            return notification
        return None

    def create_location_alert(self, user_id: str, location: Location, context: str) -> Optional[Notification]:
        """Create a location-based alert notification"""
        notification = Notification(
            id=f"notif_{time.time()}",
            user_id=user_id,
            title="Location-based Alert",
            message=f"You've entered a new area: {location.city}, {location.country}. {context}",
            type="location_alert",
            timestamp=datetime.now()
        )
        self.db_manager.save_notification(notification)
        return notification

class AgenticPlanner:
    def __init__(self):
        self.llm = OpenAI(temperature=0.3)
        self.memory = ConversationBufferMemory()
        self.db_manager = DatabaseManager()
        self.notification_service = NotificationService(self.db_manager)
        self.location_service = LocationService()
        self.weather_service = WeatherService(os.getenv('WEATHER_API_KEY', ''))
        self.calendar = CalendarIntegration('credentials.json')
        self.notion = NotionIntegration(os.getenv('NOTION_TOKEN', ''))
        self.analytics = ProductivityAnalytics()
    
    def configure_notion(self, token: str):
        """Configure Notion integration with a token"""
        self.notion.token = token
        self.notion.headers['Authorization'] = f'Bearer {token}'
    
    def fetch_notion_tasks(self, database_id: str, user_id: str = "default_user") -> str:
        """Fetch tasks from Notion and integrate them into the task planner"""
        try:
            # Get tasks from Notion
            notion_tasks_data = self.notion.get_tasks_from_database(database_id)
            
            # Convert Notion tasks to our Task format
            notion_tasks = []
            for notion_task_data in notion_tasks_data:
                # Parse Notion task to local task format
                task = self.notion.parse_notion_task_to_local_task(notion_task_data, database_id)
                notion_tasks.append(task)
                
                # Save to database
                self.db_manager.save_task(task)
            
            return f"Successfully imported {len(notion_tasks)} tasks from Notion database {database_id}"
            
        except Exception as e:
            return f"Error importing tasks from Notion: {str(e)}"
    
    def fetch_calendar_events_as_tasks(self, user_id: str = "default_user") -> str:
        """Fetch calendar events and convert them to tasks"""
        try:
            # Get events from calendar
            calendar_events = self.calendar.get_events_today()
            
            # Convert calendar events to tasks
            calendar_tasks = []
            for event in calendar_events:
                # Create task from event
                start_time = event.get('start', {}).get('dateTime')
                end_time = event.get('end', {}).get('dateTime')
                
                # Calculate duration if both times are available
                estimated_duration = 60  # Default duration
                if start_time and end_time:
                    try:
                        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                        estimated_duration = int((end_dt - start_dt).total_seconds() / 60)
                    except ValueError:
                        pass  # Use default duration if parsing fails
                
                task = Task(
                    id=f"calendar_{event.get('id', '')}",
                    title=event.get('summary', 'Calendar Event'),
                    description=event.get('description', f"Calendar event: {event.get('summary', 'Untitled Event')}"),
                    priority=2,  # Low priority for calendar events
                    due_date=None,  # Would need to parse from event date
                    estimated_duration=estimated_duration,
                    status='pending',
                    weather_dependent=False,
                    location_dependent=False,
                    reminder_enabled=True,
                    dependencies=[],
                    tags=['calendar'],
                    source='calendar'
                )
                
                calendar_tasks.append(task)
                
                # Save to database
                self.db_manager.save_task(task)
            
            return f"Successfully imported {len(calendar_tasks)} events from calendar as tasks"
            
        except Exception as e:
            return f"Error importing calendar events: {str(e)}"
    
    def sync_task_to_notion(self, task: Task, database_id: str) -> str:
        """Sync a task's completion status back to Notion"""
        try:
            # Extract Notion page ID from task ID (assuming it's in the format notion_page_id)
            if task.id.startswith('notion_'):
                page_id = task.id[7:]  # Remove 'notion_' prefix
                success = self.notion.update_task_in_notion(task, page_id)
                if success:
                    return f"Task '{task.title}' synced to Notion"
                else:
                    return f"Failed to sync task '{task.title}' to Notion"
            else:
                # If it's not a Notion task, we might want to create it in Notion
                # For now, we'll just simulate the sync
                return f"Task '{task.title}' synced to Notion database {database_id}"
        except Exception as e:
            return f"Error syncing task to Notion: {str(e)}"
    
    def sync_task_completion(self, task: Task, database_id: str) -> str:
        """Sync task completion status to Notion if it's a Notion task"""
        if task.source == 'notion':
            return self.sync_task_to_notion(task, database_id)
        return "Task is not from Notion, no sync needed"

    def process_user_command(self, command: str, user_id: str = "default_user") -> str:
        # Check for analytics/report requests
        lower_command = command.lower()
        if 'report' in lower_command or 'analytics' in lower_command or 'insights' in lower_command:
            return self.generate_productivity_report(user_id)
        
        # Check for Notion integration requests
        if 'notion' in lower_command or 'import' in lower_command:
            if 'import' in lower_command or 'fetch' in lower_command:
                # Extract database ID from command
                # In a real implementation, you would parse this from the command
                database_id = "example_database_id"  # Placeholder
                return self.fetch_notion_tasks(database_id, user_id)
            else:
                return "To import tasks from Notion, please provide a command like 'Import tasks from Notion database [database_id]'. You'll need to set up Notion integration with a valid token and database ID."
        
        # Use LLM to parse natural language command
        prompt = f'''
        Parse this user command and extract task information:
        Command: "{command}"

        Extract:
        - Task title
        - Priority (1-5)
        - Due date (if mentioned)
        - Estimated duration
        - Weather dependency
        - Location dependency (if task is location-specific)
        - Reminder preference (enabled/disabled)
        - Dependencies (list of task titles that this task depends on)

        Return as JSON.
        '''

        response = self.llm(prompt)
        try:
            task_data = json.loads(response)
            return self.create_and_schedule_task(task_data, user_id)
        except:
            return "I couldn't understand that command. Please try again."

    def create_and_schedule_task(self, task_data: Dict, user_id: str = "default_user") -> str:
        # Get existing tasks to resolve dependencies
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks_data = cursor.fetchall()
        conn.close()
        
        existing_tasks = [self._row_to_task(row) for row in tasks_data]
        
        # Resolve dependencies from task titles to task IDs
        dependencies = []
        dependency_titles = task_data.get('dependencies', [])
        if dependency_titles:
            for dep_title in dependency_titles:
                # Find task by title
                dep_task = next((t for t in existing_tasks if t.title.lower() == dep_title.lower()), None)
                if dep_task:
                    dependencies.append(dep_task.id)
        
        # Create task from parsed data
        task = Task(
            id=str(time.time()),
            title=task_data.get('title', ''),
            description=task_data.get('description', ''),
            priority=task_data.get('priority', 3),
            due_date=task_data.get('due_date'),
            estimated_duration=task_data.get('duration', 60),
            status='pending',
            weather_dependent=task_data.get('weather_dependent', False),
            location_dependent=task_data.get('location_dependent', False),
            reminder_enabled=task_data.get('reminder_enabled', True),
            dependencies=dependencies,
            source='local'
        )

        # Get context for decision making
        user_location = self.db_manager.get_user_location(user_id)
        weather = {}
        if user_location:
            weather = self.weather_service.get_current_weather(
                lat=user_location.latitude, 
                lon=user_location.longitude
            )
        else:
            weather = self.weather_service.get_current_weather()

        calendar_events = self.calendar.get_events_today()

        context = {
            'weather': weather,
            'location': user_location,
            'calendar_events': calendar_events,
            'current_time': datetime.now()
        }

        # Apply intelligent scheduling
        if task.weather_dependent and self.weather_service.should_postpone_outdoor_task(weather):
            return f"Task '{task.title}' postponed due to weather. I'll suggest an indoor alternative."

        # Save to database and create calendar event
        self.db_manager.save_task(task)
        self.calendar.create_event(task)

        # Create notification if enabled
        if task.reminder_enabled:
            self.notification_service.create_task_reminder(user_id, task)

        # Add location context to response
        location_msg = ""
        if user_location:
            location_msg = f" (taking into account your location in {user_location.city})"

        return f"Task '{task.title}' has been scheduled successfully!{location_msg}"

    def update_user_location(self, user_id: str, latitude: float, longitude: float):
        """Update user's location in the database"""
        location_details = self.location_service.reverse_geocode(latitude, longitude)
        location = Location(
            latitude=latitude,
            longitude=longitude,
            city=location_details.get('city', 'Unknown'),
            country=location_details.get('country', 'Unknown'),
            timezone=location_details.get('timezone', 'UTC')
        )
        self.db_manager.save_user_location(user_id, location)
        return location

    def generate_daily_plan(self, user_id: str = "default_user") -> str:
        # Get all pending tasks
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE status='pending'")
        tasks_data = cursor.fetchall()
        conn.close()

        # Convert to Task objects and prioritize
        tasks = [self._row_to_task(row) for row in tasks_data]
        
        # Get user context
        user_location = self.db_manager.get_user_location(user_id)
        weather = {}
        if user_location:
            weather = self.weather_service.get_current_weather(
                lat=user_location.latitude, 
                lon=user_location.longitude
            )
        else:
            weather = self.weather_service.get_current_weather()

        context = {
            'weather': weather,
            'location': user_location,
            'calendar_events': self.calendar.get_events_today()
        }

        prioritized_tasks = TaskPriorizer.prioritize_tasks(tasks, context)

        # Generate plan summary
        location_info = ""
        if user_location:
            location_info = f" for {user_location.city}"
        
        plan_summary = f"📅 Today's Optimized Plan{location_info}:\n\n"
        for i, task in enumerate(prioritized_tasks[:5], 1):
            plan_summary += f"{i}. {task.title} (Priority: {task.priority})\n"

        return plan_summary

    def generate_productivity_report(self, user_id: str = "default_user") -> str:
        # Get all tasks
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks_data = cursor.fetchall()
        conn.close()

        # Convert to Task objects
        tasks = [self._row_to_task(row) for row in tasks_data]
        
        # Get user preferences
        # For now, we'll create default preferences
        user_preferences = UserPreferences(
            work_hours=(9, 17),
            break_duration=15,
            preferred_task_length=60,
            weather_sensitivity=0.5
        )
        
        # Generate analytics report
        report_data = self.analytics.generate_productivity_report(tasks, user_preferences)
        
        # Format the report
        report = f"📊 Productivity Report\n\n"
        report += f"Total Tasks: {report_data['total_tasks']}\n"
        report += f"Completed: {report_data['completed_tasks']}\n"
        report += f"Pending: {report_data['pending_tasks']}\n"
        report += f"Completion Rate: {report_data['completion_rate']}%\n\n"
        
        report += "Priority Breakdown:\n"
        for priority, stats in report_data['priority_stats'].items():
            report += f"  Priority {priority}: {stats['completed']}/{stats['total']} ({stats['completion_rate']:.1f}%)\n"
        
        report += f"\nTasks Completed This Week: {report_data['tasks_completed_this_week']}\n\n"
        
        if report_data['insights']:
            report += "💡 Insights:\n"
            for insight in report_data['insights']:
                report += f"  • {insight}\n"
        
        return report

    def _row_to_task(self, row) -> Task:
        # Parse dependencies from JSON string
        dependencies = []
        source = "local"  # Default source
        
        if len(row) > 10 and row[9]:  # Check if dependencies column exists and is not empty
            try:
                dependencies = json.loads(row[9])
            except:
                dependencies = []
        
        # Check if source column exists
        if len(row) > 11:
            source = row[10] if row[10] else "local"
        
        return Task(
            id=row[0], title=row[1], description=row[2],
            priority=row[3], due_date=row[4], estimated_duration=row[5],
            status=row[6], weather_dependent=row[7], location_dependent=row[8],
            dependencies=dependencies, source=source
        )

class ProductivityAnalytics:
    @staticmethod
    def generate_productivity_report(tasks: List[Task], user_preferences: UserPreferences) -> Dict:
        """Generate a productivity report based on task completion and user patterns"""
        completed_tasks = [task for task in tasks if task.status == 'completed']
        pending_tasks = [task for task in tasks if task.status != 'completed']
        
        # Calculate completion rate
        completion_rate = len(completed_tasks) / len(tasks) * 100 if tasks else 0
        
        # Calculate average task duration
        avg_duration = sum(task.estimated_duration for task in completed_tasks) / len(completed_tasks) if completed_tasks else 0
        
        # Calculate productivity by priority
        priority_stats = {}
        for priority in range(1, 6):
            priority_tasks = [task for task in tasks if task.priority == priority]
            completed_priority = [task for task in priority_tasks if task.status == 'completed']
            priority_stats[priority] = {
                'total': len(priority_tasks),
                'completed': len(completed_priority),
                'completion_rate': len(completed_priority) / len(priority_tasks) * 100 if priority_tasks else 0
            }
        
        # Calculate productivity trends
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        
        # Find tasks completed in the last week
        recent_completed = [
            task for task in completed_tasks 
            if task.due_date and week_ago <= task.due_date <= today
        ]
        
        # Productivity insights
        insights = []
        if completion_rate < 50:
            insights.append("Your task completion rate is below 50%. Consider breaking larger tasks into smaller, manageable chunks.")
        elif completion_rate > 80:
            insights.append("Great job! Your task completion rate is excellent. Keep up the good work!")
            
        if avg_duration > user_preferences.preferred_task_length:
            insights.append(f"On average, your tasks take longer than your preferred duration of {user_preferences.preferred_task_length} minutes. Consider adjusting your estimates.")
            
        # Priority insights
        low_priority_completion = priority_stats.get(1, {}).get('completion_rate', 0)
        high_priority_completion = priority_stats.get(5, {}).get('completion_rate', 0)
        
        if low_priority_completion > high_priority_completion:
            insights.append("You're completing more low-priority tasks than high-priority ones. Consider focusing on high-priority tasks first.")
        
        return {
            'total_tasks': len(tasks),
            'completed_tasks': len(completed_tasks),
            'pending_tasks': len(pending_tasks),
            'completion_rate': round(completion_rate, 2),
            'average_duration': round(avg_duration, 2),
            'priority_stats': priority_stats,
            'tasks_completed_this_week': len(recent_completed),
            'insights': insights
        }
    
    @staticmethod
    def generate_visualization_data(tasks: List[Task]) -> Dict:
        """Generate data for visualization charts"""
        # Task status distribution
        status_counts = {
            'completed': len([t for t in tasks if t.status == 'completed']),
            'pending': len([t for t in tasks if t.status == 'pending']),
            'in_progress': len([t for t in tasks if t.status == 'in_progress'])
        }
        
        # Priority distribution
        priority_counts = {}
        for i in range(1, 6):
            priority_counts[i] = len([t for t in tasks if t.priority == i])
        
        # Completion trend over time (simplified)
        completion_trend = []
        today = datetime.now()
        for i in range(7):
            date = today - timedelta(days=i)
            completed_on_date = len([
                t for t in tasks 
                if t.status == 'completed' and t.due_date 
                and t.due_date.date() == date.date()
            ])
            completion_trend.append({
                'date': date.strftime('%Y-%m-%d'),
                'completed': completed_on_date
            })
        
        return {
            'status_distribution': status_counts,
            'priority_distribution': priority_counts,
            'completion_trend': completion_trend
        }

class MotivationalQuoteService:
    @staticmethod
    def get_daily_quote() -> str:
        try:
            response = requests.get("https://api.quotable.io/random")
            data = response.json()
            return f'"{data["content"]}" - {data["author"]}'
        except:
            return '"The way to get started is to quit talking and begin doing." - Walt Disney'

# Scheduling and Background Tasks
def schedule_daily_planning():
    planner = AgenticPlanner()
    plan = planner.generate_daily_plan()
    print("Daily plan generated:", plan)

def schedule_weather_check():
    weather_service = WeatherService(os.getenv('WEATHER_API_KEY', ''))
    weather = weather_service.get_current_weather()
    print("Weather checked:", weather.get('weather', [{}])[0].get('description', 'Unknown'))

# Set up scheduled tasks
schedule.every().day.at("06:00").do(schedule_daily_planning)
schedule.every().hour.do(schedule_weather_check)

# Main execution function
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    # Initialize the agentic planner
    planner = AgenticPlanner()

    # Example usage
    result = planner.process_user_command("Add buy groceries to my tasks for this evening, high priority")
    print(result)

    # Generate daily plan
    daily_plan = planner.generate_daily_plan()
    print(daily_plan)

    # Start background scheduler (uncomment for production)
    # run_scheduler()
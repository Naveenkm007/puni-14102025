# Personal Task Planner Bot with Notion and Google Calendar Integration

This is an enhanced version of the Personal Task Planner Bot that includes Notion and Google Calendar integration capabilities.

## Features

- Task management with priority levels
- Weather-aware task scheduling
- Location-based task recommendations
- Task dependencies and blocking
- Productivity analytics and reporting
- **Notion integration** - Import tasks from Notion and sync completion status
- **Google Calendar integration** - Import events from Google Calendar as tasks

## Notion Integration

To use the Notion integration features:

1. Create a Notion integration in your Notion workspace
2. Share your task database with the integration
3. Provide the database ID and integration token to the application

### How It Works

1. **Import Tasks**: Click the "Import Notion Tasks" button to fetch tasks from your Notion database
2. **Task Sync**: When you complete a Notion task in this app, it will sync the completion status back to Notion
3. **Source Tracking**: Imported tasks are clearly marked with a cloud icon

## Google Calendar Integration

To use the Google Calendar integration features:

1. Set up Google Calendar API credentials in your Google Cloud Console
2. Download the credentials JSON file
3. Place the credentials file in the application directory

### How It Works

1. **Import Events**: Click the "Import Calendar Events" button to fetch today's events from Google Calendar
2. **Event Conversion**: Calendar events are converted to tasks in the task planner
3. **Source Tracking**: Imported events are clearly marked with a calendar icon

### API Endpoints

- `POST /api/notion/import` - Import tasks from Notion
- `POST /api/calendar/import` - Import events from Google Calendar
- `POST /api/notion/sync` - Sync task completion to Notion
- `GET /api/tasks` - Get all tasks
- `POST /api/tasks/<task_id>/complete` - Mark a task as completed

## Setup

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your environment variables by copying `.env.example` to `.env` and filling in your values:
   ```bash
   cp .env.example .env
   ```
   
   Then edit the `.env` file with your actual credentials:
   - `NOTION_TOKEN` - Your Notion integration token
   - `NOTION_DATABASE_ID` - Your Notion database ID
   - `WEATHER_API_KEY` - Your OpenWeatherMap API key (optional)
   - `GOOGLE_CALENDAR_CREDENTIALS_PATH` - Path to your Google Calendar credentials file (defaults to `credentials.json`)

3. For Google Calendar integration:
   - Set up Google Calendar API credentials in the Google Cloud Console
   - Download the credentials JSON file
   - Place it in the application directory as `credentials.json` (or specify a different path in your `.env` file)

4. Run the Flask API:
   ```bash
   python api.py
   ```

5. Open `index.html` in your browser to use the application

## Usage

- Use the chat interface to add tasks, request reports, or import from Notion/Calendar
- Click "Import Notion Tasks" to fetch tasks from your Notion database
- Click "Import Calendar Events" to fetch events from Google Calendar
- Click "Generate Productivity Report" to see analytics
- Toggle task completion with the checkboxes
- Tasks imported from Notion are clearly marked with a cloud icon
- Events imported from Google Calendar are clearly marked with a calendar icon

## Development

The application consists of:
- `index.html` - Main UI
- `style.css` - Styling
- `app.js` - Frontend logic
- `task_planner_bot_implementation.py` - Backend logic
- `api.py` - Flask API for integrations

## Future Enhancements

- Real-time Notion API integration
- Two-way sync for task updates
- Support for more Notion properties
- Task creation in Notion from the app
- Real Google Calendar API integration with OAuth flow
- Event creation in Google Calendar from the app
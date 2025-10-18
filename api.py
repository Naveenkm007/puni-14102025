from flask import Flask, jsonify, request
from task_planner_bot_implementation import AgenticPlanner
from config import Config
import os

app = Flask(__name__)
planner = AgenticPlanner()

# Configure the planner with environment variables
if Config.NOTION_TOKEN:
    planner.notion.token = Config.NOTION_TOKEN
    planner.notion.headers['Authorization'] = f'Bearer {Config.NOTION_TOKEN}'

@app.route('/api/notion/import', methods=['POST'])
def import_notion_tasks():
    """Import tasks from Notion"""
    data = request.get_json()
    database_id = data.get('database_id')
    user_id = data.get('user_id', 'default_user')
    
    if not database_id:
        return jsonify({'error': 'Database ID is required'}), 400
    
    # Set the Notion token if provided
    notion_token = data.get('notion_token')
    if notion_token:
        planner.notion.token = notion_token
        planner.notion.headers['Authorization'] = f'Bearer {notion_token}'
    
    result = planner.fetch_notion_tasks(database_id, user_id)
    return jsonify({'message': result})

@app.route('/api/calendar/import', methods=['POST'])
def import_calendar_events():
    """Import events from Google Calendar as tasks"""
    data = request.get_json()
    user_id = data.get('user_id', 'default_user')
    
    result = planner.fetch_calendar_events_as_tasks(user_id)
    return jsonify({'message': result})

@app.route('/api/notion/sync', methods=['POST'])
def sync_task_to_notion():
    """Sync a task to Notion"""
    data = request.get_json()
    task_data = data.get('task')
    database_id = data.get('database_id')
    
    if not task_data or not database_id:
        return jsonify({'error': 'Task data and database ID are required'}), 400
    
    # In a real implementation, you would convert the task_data to a Task object
    # and then call planner.sync_task_to_notion(task, database_id)
    
    return jsonify({'message': f'Task synced to Notion database {database_id}'})

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    # In a real implementation, you would fetch tasks from the database
    # For now, we'll return a sample response
    return jsonify({
        'tasks': [
            {
                'id': 1,
                'title': 'Sample Task',
                'description': 'This is a sample task',
                'priority': 3,
                'status': 'pending'
            }
        ]
    })

@app.route('/api/tasks/<task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """Mark a task as completed"""
    # In a real implementation, you would update the task in the database
    return jsonify({'message': f'Task {task_id} marked as completed'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
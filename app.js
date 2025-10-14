// Application Data
const appData = {
  tasks: [
    {
      id: 1,
      title: "Prepare presentation slides",
      description: "Create slides for client meeting",
      priority: "High",
      duration: "90 min",
      completed: false,
      weather_dependent: false,
      dependencies: []
    },
    {
      id: 2,
      title: "Gym workout",
      description: "Cardio and strength training",
      priority: "Medium",
      duration: "60 min",
      completed: false,
      weather_dependent: true,
      dependencies: []
    },
    {
      id: 3,
      title: "Buy groceries",
      description: "Weekly grocery shopping",
      priority: "Medium",
      duration: "45 min",
      completed: false,
      weather_dependent: true,
      dependencies: []
    },
    {
      id: 4,
      title: "Code review",
      description: "Review team's pull requests",
      priority: "High",
      duration: "30 min",
      completed: true,
      weather_dependent: false,
      dependencies: []
    },
    {
      id: 5,
      title: "Call mom",
      description: "Weekly check-in call",
      priority: "Low",
      duration: "20 min",
      completed: false,
      weather_dependent: false,
      dependencies: []
    },
    {
      id: 6,
      title: "Update project documentation",
      description: "Add API documentation",
      priority: "Medium",
      duration: "75 min",
      completed: false,
      weather_dependent: false,
      dependencies: []
    }
  ],
  tomorrowTasks: [
    {
      id: 7,
      title: "Team standup meeting",
      description: "Daily team sync at 9am",
      priority: "High",
      duration: "30 min",
      completed: false,
      weather_dependent: false,
      dependencies: []
    },
    {
      id: 8,
      title: "Gym workout",
      description: "Indoor exercises due to rain forecast",
      priority: "Medium",
      duration: "60 min",
      completed: false,
      weather_dependent: true,
      dependencies: [7]  // Depends on team standup
    },
    {
      id: 9,
      title: "Client presentation",
      description: "Present finalized slides to client",
      priority: "High",
      duration: "120 min",
      completed: false,
      weather_dependent: false,
      dependencies: [1]  // Depends on preparing slides
    },
    {
      id: 10,
      title: "Lunch with Sarah",
      description: "Catch up meeting at downtown cafe",
      priority: "Low",
      duration: "90 min",
      completed: false,
      weather_dependent: true,
      dependencies: []
    },
    {
      id: 11,
      title: "Email follow-ups",
      description: "Reply to pending client emails",
      priority: "Medium",
      duration: "45 min",
      completed: false,
      weather_dependent: false,
      dependencies: [9]  // Depends on client presentation
    },
    {
      id: 12,
      title: "Update project documentation",
      description: "Update documentation based on client feedback",
      priority: "Medium",
      duration: "90 min",
      completed: false,
      weather_dependent: false,
      dependencies: [9]  // Depends on client presentation
    }
  ],
  weather: {
    condition: "Partly Cloudy",
    temperature: "24°C",
    icon: "⛅",
    description: "Light rain expected this evening"
  },
  location: {
    city: "Unknown",
    country: "Unknown",
    latitude: null,
    longitude: null
  },
  quotes: [
    {
      text: "The way to get started is to quit talking and begin doing.",
      author: "Walt Disney"
    },
    {
      text: "Success is not final, failure is not fatal: it is the courage to continue that counts.",
      author: "Winston Churchill"
    },
    {
      text: "The future belongs to those who believe in the beauty of their dreams.",
      author: "Eleanor Roosevelt"
    },
    {
      text: "Your time is limited, don't waste it living someone else's life.",
      author: "Steve Jobs"
    },
    {
      text: "The only way to do great work is to love what you do.",
      author: "Steve Jobs"
    }
  ],
  chatMessages: [
    {
      type: "user",
      text: "Add gym workout for 7am tomorrow",
      timestamp: "10:30 AM"
    },
    {
      type: "bot",
      text: "I've scheduled your gym workout for 7am tomorrow. Since there's a chance of rain, I recommend indoor exercises. The task has been added to your calendar.",
      timestamp: "10:30 AM"
    },
    {
      type: "user",
      text: "What's my priority task right now?",
      timestamp: "10:32 AM"
    },
    {
      type: "bot",
      text: "Your highest priority task is 'Prepare presentation slides' - it's due today and estimated to take 90 minutes. I've found a 2-hour free slot this afternoon.",
      timestamp: "10:32 AM"
    }
  ],
  notifications: {
    enabled: false,
    permission: 'default', // 'default', 'granted', 'denied'
    upcomingTaskReminder: true,
    weatherAlerts: true,
    locationBasedAlerts: true
  },
  notion: {
    connected: false,
    tasks: [],
    databaseId: ''
  }
};

// Application State
let currentView = 'today';
let currentQuoteIndex = 0;
let notificationInterval = null;

// DOM Elements
const elements = {
  currentDate: document.getElementById('currentDate'),
  weatherIcon: document.getElementById('weatherIcon'),
  weatherTemp: document.getElementById('weatherTemp'),
  weatherCondition: document.getElementById('weatherCondition'),
  quoteText: document.getElementById('quoteText'),
  quoteAuthor: document.getElementById('quoteAuthor'),
  refreshQuoteBtn: document.getElementById('refreshQuoteBtn'),
  sectionTitle: document.getElementById('sectionTitle'),
  toggleViewBtn: document.getElementById('toggleViewBtn'),
  progressFill: document.getElementById('progressFill'),
  progressText: document.getElementById('progressText'),
  tasksList: document.getElementById('tasksList'),
  chatMessages: document.getElementById('chatMessages'),
  chatInput: document.getElementById('chatInput'),
  sendBtn: document.getElementById('sendBtn'),
  // Notification settings elements
  notificationsToggle: document.getElementById('notificationsToggle'),
  taskRemindersToggle: document.getElementById('taskRemindersToggle'),
  weatherAlertsToggle: document.getElementById('weatherAlertsToggle'),
  locationAlertsToggle: document.getElementById('locationAlertsToggle'),
  testNotificationBtn: document.getElementById('testNotificationBtn'),
  // Theme toggle elements
  themeToggleBtn: document.getElementById('themeToggleBtn'),
  themeToggleText: document.getElementById('themeToggleText')
};

// Initialize Application
function initApp() {
  updateDateTime();
  getLocation(); // Get user's location
  updateWeatherWidget();
  updateQuote();
  loadTasks();
  loadChatMessages();
  updateProgress();
  initNotifications(); // Initialize notification system
  setupNotificationSettings(); // Setup notification settings UI
  
  // Set up event listeners
  setupEventListeners();
  
  // Update time every minute
  setInterval(updateDateTime, 60000);
  
  // Add sample dependency message
  setTimeout(() => {
    addBotMessage("💡 Tip: Try clicking the 'Generate Productivity Report' button to see your productivity insights!");
  }, 3000);
}

// Apply theme immediately when page loads
(function() {
  const savedTheme = localStorage.getItem('theme');
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
  
  // Apply theme with a slight delay to ensure CSS is loaded
  setTimeout(() => {
    document.documentElement.setAttribute('data-color-scheme', theme);
  }, 10);
})();

// Update current date and time
function updateDateTime() {
  const now = new Date();
  const options = {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  };
  elements.currentDate.textContent = now.toLocaleDateString('en-US', options);
}

// Get user's location
function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      position => {
        appData.location.latitude = position.coords.latitude;
        appData.location.longitude = position.coords.longitude;
        // Get city and country from coordinates using reverse geocoding
        reverseGeocode(position.coords.latitude, position.coords.longitude);
      },
      error => {
        console.error("Error getting location:", error);
        // Use default location if geolocation fails
        appData.location.city = "Bengaluru";
        appData.location.country = "India";
        updateLocationDisplay();
      }
    );
  } else {
    console.log("Geolocation is not supported by this browser.");
    appData.location.city = "Bengaluru";
    appData.location.country = "India";
    updateLocationDisplay();
  }
}

// Reverse geocode to get city and country from coordinates
function reverseGeocode(lat, lon) {
  // In a real implementation, you would use a geocoding service like:
  // fetch(`https://api.openweathermap.org/geo/1.0/reverse?lat=${lat}&lon=${lon}&limit=1&appid=YOUR_API_KEY`)
  // For this demo, we'll simulate the response
  setTimeout(() => {
    // Simulate API response with a default location
    appData.location.city = "Bengaluru";
    appData.location.country = "India";
    updateLocationDisplay();
    updateWeatherForLocation(lat, lon);
  }, 1000);
}

// Update location display in the UI
function updateLocationDisplay() {
  const locationElement = document.getElementById('locationInfo');
  if (locationElement) {
    const locationText = locationElement.querySelector('.location-text');
    if (locationText) {
      locationText.textContent = `${appData.location.city}, ${appData.location.country}`;
    }
  }
}

// Update weather based on location
function updateWeatherForLocation(lat, lon) {
  // In a real implementation, you would fetch weather data for the location
  // For this demo, we'll keep the existing weather data but indicate it's location-based
  console.log(`Weather updated for location: ${lat}, ${lon}`);
}

// Update weather widget
function updateWeatherWidget() {
  elements.weatherIcon.textContent = appData.weather.icon;
  elements.weatherTemp.textContent = appData.weather.temperature;
  elements.weatherCondition.textContent = appData.weather.condition;
  
  // Add location context to weather description
  if (appData.location.city !== "Unknown") {
    appData.weather.description = `Light rain expected this evening in ${appData.location.city}`;
  }
}

// Update motivational quote
function updateQuote() {
  const quote = appData.quotes[currentQuoteIndex];
  elements.quoteText.textContent = `"${quote.text}"`;
  elements.quoteAuthor.textContent = `— ${quote.author}`;
}

// Fetch tasks from Notion
function fetchNotionTasks() {
  // In a real implementation, this would make an API call to your backend
  addBotMessage("Connecting to Notion and importing tasks...");
  
  // For demo purposes, we'll simulate fetching Notion tasks with a delay
  setTimeout(() => {
    // Sample Notion tasks
    const notionTasks = [
      {
        id: 'notion-1',
        title: 'Notion Task: Review project proposal',
        description: 'Review the Q3 project proposal document',
        priority: 'High',
        duration: '45 min',
        completed: false,
        weather_dependent: false,
        dependencies: [],
        source: 'notion'
      },
      {
        id: 'notion-2',
        title: 'Notion Task: Update team documentation',
        description: 'Update the team onboarding documentation',
        priority: 'Medium',
        duration: '60 min',
        completed: false,
        weather_dependent: false,
        dependencies: [],
        source: 'notion'
      }
    ];
    
    appData.notion.tasks = notionTasks;
    appData.notion.connected = true;
    
    // Add bot message to notify user
    addBotMessage(`✅ Successfully imported ${notionTasks.length} tasks from Notion!`);
    
    // Reload tasks to include Notion tasks
    loadTasks();
    
    // In a real implementation, you would make an API call like this:
    /*
    fetch('/api/notion/import', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        database_id: 'your_notion_database_id',
        notion_token: 'your_notion_token'
      })
    })
    .then(response => response.json())
    .then(data => {
      addBotMessage(data.message);
      // Reload tasks after successful import
      loadTasks();
    })
    .catch(error => {
      addBotMessage(`❌ Error importing Notion tasks: ${error.message}`);
    });
    */
  }, 1500);
}

// Load and display tasks
function loadTasks() {
  let tasks = currentView === 'today' ? appData.tasks : appData.tomorrowTasks;
  
  // Include Notion tasks if connected
  if (appData.notion.connected && currentView === 'today') {
    tasks = [...tasks, ...appData.notion.tasks];
  }
  
  elements.tasksList.innerHTML = '';
  
  tasks.forEach(task => {
    const taskElement = createTaskElement(task);
    elements.tasksList.appendChild(taskElement);
  });
  
  updateProgress();
}

// Create task element
function createTaskElement(task) {
  const taskDiv = document.createElement('div');
  taskDiv.className = `task-item ${task.completed ? 'completed' : ''} ${task.source === 'notion' ? 'notion-task' : ''}`;
  taskDiv.dataset.taskId = task.id;
  
  // Check if task has unmet dependencies
  const allTasks = [...appData.tasks, ...appData.tomorrowTasks, ...appData.notion.tasks];
  const hasUnmetDependencies = task.dependencies && task.dependencies.length > 0 && 
    !task.dependencies.every(depId => {
      const depTask = allTasks.find(t => t.id === depId);
      return depTask && depTask.completed;
    });
  
  // Add lock icon if task has unmet dependencies
  const lockIcon = hasUnmetDependencies ? '<i class="fas fa-lock dependency-lock" title="Task has unmet dependencies"></i>' : '';
  
  // Add Notion icon if it's a Notion task
  const notionIcon = task.source === 'notion' ? '<i class="fas fa-cloud" title="Imported from Notion"></i>' : '';
  
  taskDiv.innerHTML = `
    <div class="task-checkbox ${task.completed ? 'checked' : ''}" onclick="toggleTask(${task.id})">
      ${task.completed ? '<i class="fas fa-check"></i>' : ''}
    </div>
    <div class="task-content">
      <div class="task-header">
        <h4 class="task-title">${task.title} ${lockIcon} ${notionIcon}</h4>
        <span class="task-priority ${task.priority.toLowerCase()}">${task.priority}</span>
      </div>
      <p class="task-description">${task.description}</p>
      <div class="task-meta">
        <span class="task-duration">
          <i class="fas fa-clock"></i>
          ${task.duration}
        </span>
        ${task.weather_dependent ? '<i class="fas fa-cloud-rain weather-dependent" title="Weather dependent"></i>' : ''}
        ${task.dependencies && task.dependencies.length > 0 ? `<span class="task-dependencies" title="${task.dependencies.length} dependencies"><i class="fas fa-link"></i> ${task.dependencies.length}</span>` : ''}
        ${task.source === 'notion' ? `<span class="task-source" title="Imported from Notion"><i class="fas fa-cloud"></i></span>` : ''}
      </div>
    </div>
  `;
  
  return taskDiv;
}

// Toggle task completion
function toggleTask(taskId) {
  // Find task in all collections
  let task = null;
  let taskCollection = null;
  
  // Check in today's tasks
  task = appData.tasks.find(t => t.id === taskId);
  if (task) taskCollection = appData.tasks;
  
  // Check in tomorrow's tasks
  if (!task) {
    task = appData.tomorrowTasks.find(t => t.id === taskId);
    if (task) taskCollection = appData.tomorrowTasks;
  }
  
  // Check in Notion tasks
  if (!task) {
    task = appData.notion.tasks.find(t => t.id === taskId);
    if (task) taskCollection = appData.notion.tasks;
  }
  
  if (task && taskCollection) {
    // Check if task has unmet dependencies
    const allTasks = [...appData.tasks, ...appData.tomorrowTasks, ...appData.notion.tasks];
    const hasUnmetDependencies = task.dependencies && task.dependencies.length > 0 && 
      !task.dependencies.every(depId => {
        const depTask = allTasks.find(t => t.id === depId);
        return depTask && depTask.completed;
      });
    
    if (hasUnmetDependencies && !task.completed) {
      addBotMessage(`You cannot complete "${task.title}" yet because it depends on other tasks that are not completed.`);
      return;
    }
    
    task.completed = !task.completed;
    loadTasks();
    
    // Add bot response for task completion
    if (task.completed) {
      addBotMessage(`Great job completing "${task.title}"! Keep up the momentum.`);
      
      // Check if any dependent tasks can now be unlocked
      const dependentTasks = allTasks.filter(t => t.dependencies.includes(taskId) && !t.completed);
      if (dependentTasks.length > 0) {
        const taskNames = dependentTasks.map(t => t.title).join(', ');
        addBotMessage(`The following tasks are now unlocked: ${taskNames}`);
      }
      
      // If it's a Notion task, in a real implementation we would sync back to Notion
      if (task.source === 'notion') {
        addBotMessage(`_SYNCED completion status to Notion.`);
        // In a real implementation, you would make an API call like this:
        /*
        fetch(`/api/tasks/${task.id}/complete`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          }
        })
        .then(response => response.json())
        .then(data => {
          addBotMessage(data.message);
        })
        .catch(error => {
          addBotMessage(`❌ Error syncing to Notion: ${error.message}`);
        });
        */
      }
    } else {
      addBotMessage(`I've marked "${task.title}" as incomplete. Don't worry, you can tackle it when you're ready.`);
      
      // If it's a Notion task, in a real implementation we would sync back to Notion
      if (task.source === 'notion') {
        addBotMessage(`_SYNCED status update to Notion.`);
        // In a real implementation, you would make an API call like this:
        /*
        fetch(`/api/tasks/${task.id}/complete`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          }
        })
        .then(response => response.json())
        .then(data => {
          addBotMessage(data.message);
        })
        .catch(error => {
          addBotMessage(`❌ Error syncing to Notion: ${error.message}`);
        });
        */
      }
    }
  }
}

// Update progress bar
function updateProgress() {
  let tasks = currentView === 'today' ? appData.tasks : appData.tomorrowTasks;
  
  // Include Notion tasks if connected
  if (appData.notion.connected && currentView === 'today') {
    tasks = [...tasks, ...appData.notion.tasks];
  }
  
  const completedTasks = tasks.filter(task => task.completed).length;
  const totalTasks = tasks.length;
  const percentage = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
  
  elements.progressFill.style.width = `${percentage}%`;
  elements.progressText.textContent = `${percentage}% Complete (${completedTasks}/${totalTasks} tasks)`;
}

// Load chat messages
function loadChatMessages() {
  elements.chatMessages.innerHTML = '';
  
  appData.chatMessages.forEach(message => {
    const messageElement = createMessageElement(message);
    elements.chatMessages.appendChild(messageElement);
  });
  
  scrollChatToBottom();
}

// Create message element
function createMessageElement(message) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${message.type}`;
  
  messageDiv.innerHTML = `
    ${message.text}
    <div class="message-time">${message.timestamp}</div>
  `;
  
  return messageDiv;
}

// Add bot message
function addBotMessage(text) {
  const now = new Date();
  const timestamp = now.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
  
  const message = {
    type: 'bot',
    text: text,
    timestamp: timestamp
  };
  
  appData.chatMessages.push(message);
  
  const messageElement = createMessageElement(message);
  elements.chatMessages.appendChild(messageElement);
  scrollChatToBottom();
}

// Add user message
function addUserMessage(text) {
  const now = new Date();
  const timestamp = now.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
  
  const message = {
    type: 'user',
    text: text,
    timestamp: timestamp
  };
  
  appData.chatMessages.push(message);
  
  const messageElement = createMessageElement(message);
  elements.chatMessages.appendChild(messageElement);
  scrollChatToBottom();
}

// Process chat input (add notification-related responses)
function processChatInput(input) {
  const lowerInput = input.toLowerCase();
  
  // Simple AI responses based on keywords
  if (lowerInput.includes('add') && lowerInput.includes('task')) {
    return "I'd be happy to help you add a new task! However, in this demo version, task management is simulated. In the full version, I would integrate with your calendar and task management systems to add this automatically.";
  } else if (lowerInput.includes('add') && lowerInput.includes('task')) {
    if (lowerInput.includes('depend') || lowerInput.includes('after')) {
      return "I can help you add a task with dependencies! In the full version, I would parse the dependency relationship and link tasks accordingly. For example, you could say 'Add task Update project documentation that depends on Client presentation'.";
    }
    return "I'd be happy to help you add a new task! However, in this demo version, task management is simulated. In the full version, I would integrate with your calendar and task management systems to add this automatically.";
  } else if (lowerInput.includes('notion') || lowerInput.includes('import')) {
    if (lowerInput.includes('connect') || lowerInput.includes('setup')) {
      return "To connect your Notion account, you would need to provide your Notion integration token and database ID. In the full version, I would securely store these credentials and sync your tasks between Notion and this application.";
    } else {
      // Trigger Notion import
      fetchNotionTasks();
      return "I'm importing your tasks from Notion now. This may take a moment...";
    }
  } else if (lowerInput.includes('priority') || lowerInput.includes('important')) {
    const highPriorityTasks = appData.tasks.filter(task => task.priority === 'High' && !task.completed);
    if (highPriorityTasks.length > 0) {
      return `Your highest priority task right now is "${highPriorityTasks[0].title}" - ${highPriorityTasks[0].description}. It's estimated to take ${highPriorityTasks[0].duration}.`;
    } else {
      return "Great news! You've completed all your high-priority tasks for today. You can focus on medium and low priority items.";
    }
  } else if (lowerInput.includes('weather')) {
    return `Today's weather is ${appData.weather.condition} with a temperature of ${appData.weather.temperature}. ${appData.weather.description} I've already considered this for your outdoor tasks.`;
  } else if (lowerInput.includes('schedule') || lowerInput.includes('calendar')) {
    return "I can help you optimize your schedule! Based on your current tasks and calendar, I recommend tackling high-priority items during your most productive hours. Would you like me to suggest a specific time block?";
  } else if (lowerInput.includes('tomorrow')) {
    return "Tomorrow looks busy! You have several important tasks including your client presentation. I've already rescheduled your gym workout indoors due to the rain forecast. Need me to adjust anything else?";
  } else if (lowerInput.includes('help')) {
    return "I'm here to help you manage your tasks efficiently! I can help you prioritize tasks, check weather conditions, add new items to your schedule, and provide insights about your productivity. Just ask me anything about your tasks or schedule!";
  } else if (lowerInput.includes('where am i') || lowerInput.includes('my location')) {
    return `You are currently in ${appData.location.city}, ${appData.location.country}. I use this information to provide location-specific weather updates and plan tasks accordingly.`;
  } else if (lowerInput.includes('location')) {
    return `Your location is set to ${appData.location.city}, ${appData.location.country}. I use this to provide localized weather information and suggest appropriate tasks based on your area.`;
  } else if (lowerInput.includes('notification') || lowerInput.includes('alert')) {
    if (lowerInput.includes('enable') || lowerInput.includes('turn on')) {
      if (!("Notification" in window)) {
        return "Unfortunately, your browser doesn't support notifications.";
      }
      
      if (Notification.permission === 'denied') {
        return "Notification permission has been denied. Please enable notifications in your browser settings.";
      }
      
      requestNotificationPermission();
      return "I'm requesting permission to send you notifications. Please check your browser for the permission request.";
    } else if (lowerInput.includes('disable') || lowerInput.includes('turn off')) {
      appData.notifications.enabled = false;
      // Update UI
      if (elements.notificationsToggle) {
        elements.notificationsToggle.checked = false;
      }
      return "Notifications have been disabled. You can re-enable them at any time by asking me to turn notifications on.";
    } else if (lowerInput.includes('test')) {
      if (appData.notifications.enabled) {
        showNotification(
          'Test Notification', 
          'This is a test notification from your Personal Task Planner Bot!',
          {
            icon: 'https://via.placeholder.com/48x48/33808D/FFFFFF?text=🔔'
          }
        );
        return "I've sent you a test notification. Did you receive it?";
      } else {
        return "Notifications are currently disabled. Please enable them first to receive test notifications.";
      }
    } else {
      const status = appData.notifications.enabled ? 'enabled' : 'disabled';
      return `Notifications are currently ${status}. I can send you reminders for upcoming tasks, weather alerts, and location-based notifications. Would you like to change this setting?`;
    }
  } else if (lowerInput.includes('report') || lowerInput.includes('analytics') || lowerInput.includes('insights')) {
    // Generate productivity report
    const allTasks = [...appData.tasks, ...appData.tomorrowTasks];
    const completedTasks = allTasks.filter(task => task.completed);
    const pendingTasks = allTasks.filter(task => !task.completed);
    const completionRate = allTasks.length > 0 ? Math.round((completedTasks.length / allTasks.length) * 100) : 0;
    
    // Priority breakdown
    const priorityStats = {};
    ['High', 'Medium', 'Low'].forEach(priority => {
      const priorityTasks = allTasks.filter(task => task.priority === priority);
      const completedPriority = priorityTasks.filter(task => task.completed);
      priorityStats[priority] = {
        total: priorityTasks.length,
        completed: completedPriority.length,
        rate: priorityTasks.length > 0 ? Math.round((completedPriority.length / priorityTasks.length) * 100) : 0
      };
    });
    
    // Dependency information
    const tasksWithDependencies = allTasks.filter(task => task.dependencies && task.dependencies.length > 0);
    const blockedTasks = allTasks.filter(task => {
      return task.dependencies && task.dependencies.length > 0 && 
        !task.dependencies.every(depId => {
          const depTask = allTasks.find(t => t.id === depId);
          return depTask && depTask.completed;
        });
    });
    
    let report = `📊 Productivity Report:\n\n`;
    report += `Total Tasks: ${allTasks.length}\n`;
    report += `Completed: ${completedTasks.length}\n`;
    report += `Pending: ${pendingTasks.length}\n`;
    report += `Completion Rate: ${completionRate}%\n\n`;
    
    report += `Priority Breakdown:\n`;
    Object.keys(priorityStats).forEach(priority => {
      const stats = priorityStats[priority];
      report += `  ${priority}: ${stats.completed}/${stats.total} (${stats.rate}%)\n`;
    });
    
    report += `\nDependencies:\n`;
    report += `  Tasks with dependencies: ${tasksWithDependencies.length}\n`;
    report += `  Blocked tasks: ${blockedTasks.length}\n\n`;
    
    if (completionRate < 50) {
      report += `💡 Insight: Your completion rate is below 50%. Consider breaking larger tasks into smaller ones.\n`;
    } else if (completionRate > 80) {
      report += `💡 Insight: Great job! Your completion rate is excellent.\n`;
    }
    
    if (blockedTasks.length > 0) {
      report += `⚠️  Warning: You have ${blockedTasks.length} tasks that are blocked by uncompleted dependencies.\n`;
    }
    
    return report;
  } else {
    return "I understand you're looking for assistance with your tasks. I'm constantly learning and adapting to help you better. In the full version, I'd have access to your complete calendar, task history, and preferences to provide more personalized responses.";
  }
}

// Send chat message
function sendMessage() {
  const input = elements.chatInput.value.trim();
  
  if (input) {
    addUserMessage(input);
    elements.chatInput.value = '';
    
    // Simulate bot thinking time
    setTimeout(() => {
      const response = processChatInput(input);
      addBotMessage(response);
    }, 1000);
  }
}

// Scroll chat to bottom
function scrollChatToBottom() {
  elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

// Toggle between today and tomorrow views
function toggleView() {
  if (currentView === 'today') {
    currentView = 'tomorrow';
    elements.sectionTitle.textContent = "Tomorrow's Tasks";
    elements.toggleViewBtn.textContent = "View Today's Tasks";
  } else {
    currentView = 'today';
    elements.sectionTitle.textContent = "Today's Tasks";
    elements.toggleViewBtn.textContent = "View Tomorrow's Plan";
  }
  
  loadTasks();
}

// Refresh quote
function refreshQuote() {
  currentQuoteIndex = (currentQuoteIndex + 1) % appData.quotes.length;
  updateQuote();
  
  // Add rotation animation to refresh button
  elements.refreshQuoteBtn.style.transform = 'rotate(360deg)';
  setTimeout(() => {
    elements.refreshQuoteBtn.style.transform = 'rotate(0deg)';
  }, 300);
}

// Setup event listeners
function setupEventListeners() {
  // Refresh quote button
  elements.refreshQuoteBtn.addEventListener('click', refreshQuote);
  
  // Toggle view button
  elements.toggleViewBtn.addEventListener('click', toggleView);
  
  // Send message button
  elements.sendBtn.addEventListener('click', sendMessage);
  
  // Analytics button
  const analyticsBtn = document.getElementById('analyticsBtn');
  if (analyticsBtn) {
    analyticsBtn.addEventListener('click', () => {
      const report = processChatInput('show productivity report');
      addBotMessage(report);
      
      // Show analytics panel
      const analyticsPanel = document.getElementById('analyticsPanel');
      if (analyticsPanel) {
        analyticsPanel.style.display = 'block';
        
        // Scroll to analytics panel
        analyticsPanel.scrollIntoView({ behavior: 'smooth' });
        
        // Generate simple charts
        generateSimpleCharts();
      }
    });
  }
  
  // Close analytics button
  const closeAnalyticsBtn = document.getElementById('closeAnalyticsBtn');
  if (closeAnalyticsBtn) {
    closeAnalyticsBtn.addEventListener('click', () => {
      const analyticsPanel = document.getElementById('analyticsPanel');
      if (analyticsPanel) {
        analyticsPanel.style.display = 'none';
      }
    });
  }
  
  // Notion import button
  const notionBtn = document.getElementById('notionBtn');
  if (notionBtn) {
    notionBtn.addEventListener('click', () => {
      addBotMessage("Connecting to Notion and importing tasks...");
      fetchNotionTasks();
    });
  }
  
  // Theme toggle button
  if (elements.themeToggleBtn) {
    elements.themeToggleBtn.addEventListener('click', toggleTheme);
    // Initialize theme based on system preference or saved preference
    initTheme();
  }
  
  // Chat input enter key
  elements.chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  });
  
  // Prevent form submission on enter
  elements.chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
    }
  });
}

// Generate simple charts for analytics
function generateSimpleCharts() {
  // Get chart containers
  const completionChart = document.getElementById('completionChart');
  const priorityChart = document.getElementById('priorityChart');
  
  if (!completionChart || !priorityChart) return;
  
  // Get task data
  const allTasks = [...appData.tasks, ...appData.tomorrowTasks];
  const completedTasks = allTasks.filter(task => task.completed);
  const pendingTasks = allTasks.filter(task => !task.completed);
  
  // Simple text-based charts
  const completionCtx = completionChart.getContext('2d');
  const priorityCtx = priorityChart.getContext('2d');
  
  // Clear canvases
  completionCtx.clearRect(0, 0, completionChart.width, completionChart.height);
  priorityCtx.clearRect(0, 0, priorityChart.width, priorityChart.height);
  
  // Draw completion chart (simple bar chart)
  completionCtx.fillStyle = '#33808D';
  completionCtx.font = '14px Arial';
  completionCtx.fillText('Task Completion', 10, 20);
  
  const completionRate = allTasks.length > 0 ? (completedTasks.length / allTasks.length) * 100 : 0;
  
  // Draw bar
  completionCtx.fillStyle = '#33808D';
  completionCtx.fillRect(50, 40, completionRate * 3, 30);
  
  // Draw border
  completionCtx.strokeStyle = '#000';
  completionCtx.strokeRect(50, 40, 300, 30);
  
  // Draw labels
  completionCtx.fillStyle = '#000';
  completionCtx.fillText('0%', 50, 85);
  completionCtx.fillText('100%', 330, 85);
  completionCtx.fillText(`${Math.round(completionRate)}%`, 50 + (completionRate * 3) - 20, 35);
  
  // Draw priority chart
  priorityCtx.fillStyle = '#33808D';
  priorityCtx.font = '14px Arial';
  priorityCtx.fillText('Priority Distribution', 10, 20);
  
  // Count tasks by priority
  const priorityCounts = {
    'High': 0,
    'Medium': 0,
    'Low': 0
  };
  
  allTasks.forEach(task => {
    priorityCounts[task.priority]++;
  });
  
  // Draw simple bar chart for priorities
  const priorities = ['High', 'Medium', 'Low'];
  const barWidth = 60;
  const barSpacing = 20;
  const startX = 50;
  
  priorities.forEach((priority, index) => {
    const count = priorityCounts[priority];
    const x = startX + (index * (barWidth + barSpacing));
    const barHeight = count * 20; // Scale factor
    
    // Draw bar
    priorityCtx.fillStyle = priority === 'High' ? '#C0152F' : 
                          priority === 'Medium' ? '#A84B2F' : '#33808D';
    priorityCtx.fillRect(x, 100 - barHeight, barWidth, barHeight);
    
    // Draw label
    priorityCtx.fillStyle = '#000';
    priorityCtx.fillText(priority, x, 115);
    priorityCtx.fillText(count.toString(), x + barWidth/2 - 5, 95 - barHeight);
  });
}

// Theme toggle functions
function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-color-scheme') || 
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  
  // Add animation
  const themeIcon = elements.themeToggleBtn ? elements.themeToggleBtn.querySelector('i') : null;
  if (themeIcon) {
    // Add smooth animation
    themeIcon.style.transition = 'transform var(--duration-normal) var(--ease-standard), opacity var(--duration-fast) var(--ease-standard)';
    themeIcon.style.transform = 'rotate(45deg)';
    themeIcon.style.opacity = '0';
    
    setTimeout(() => {
      themeIcon.className = newTheme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
      themeIcon.style.transform = 'rotate(0deg)';
      themeIcon.style.opacity = '1';
    }, 150);
  }
  
  // Apply theme after a short delay to allow animation to start
  setTimeout(() => {
    document.documentElement.setAttribute('data-color-scheme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update button text
    if (elements.themeToggleText) {
      elements.themeToggleText.textContent = newTheme === 'dark' ? 'Dark Mode' : 'Light Mode';
    }
    
    addBotMessage(` switched to ${newTheme} mode.`);
  }, 100);
}

function initTheme() {
  // Check for saved theme
  const savedTheme = localStorage.getItem('theme');
  
  // Check for system preference if no saved theme
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  // Use saved theme, or system preference, or default to light
  const theme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
  
  document.documentElement.setAttribute('data-color-scheme', theme);
  
  // Update button text and icon
  if (elements.themeToggleText) {
    elements.themeToggleText.textContent = theme === 'dark' ? 'Dark Mode' : 'Light Mode';
  }
  
  const themeIcon = elements.themeToggleBtn ? elements.themeToggleBtn.querySelector('i') : null;
  if (themeIcon) {
    themeIcon.className = theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
  }
}

// Global function for task toggle (called from HTML)
window.toggleTask = toggleTask;

// Initialize notification system
function initNotifications() {
  // Check if browser supports notifications
  if (!("Notification" in window)) {
    console.log("This browser does not support desktop notification");
    // Hide notification settings panel if not supported
    const notificationSettings = document.querySelector('.notification-settings');
    if (notificationSettings) {
      notificationSettings.style.display = 'none';
    }
    return;
  }
  
  // Check current notification permission
  appData.notifications.permission = Notification.permission;
  appData.notifications.enabled = Notification.permission === 'granted';
  
  // If permission is not granted or denied, request permission
  if (Notification.permission === "default") {
    // Don't automatically request permission, let user enable it manually
  }
  
  // Start notification checks
  startNotificationChecks();
}

// Setup notification settings UI
function setupNotificationSettings() {
  // Update UI based on current settings
  if (elements.notificationsToggle) {
    elements.notificationsToggle.checked = appData.notifications.enabled;
  }
  
  if (elements.taskRemindersToggle) {
    elements.taskRemindersToggle.checked = appData.notifications.upcomingTaskReminder;
  }
  
  if (elements.weatherAlertsToggle) {
    elements.weatherAlertsToggle.checked = appData.notifications.weatherAlerts;
  }
  
  if (elements.locationAlertsToggle) {
    elements.locationAlertsToggle.checked = appData.notifications.locationBasedAlerts;
  }
  
  // Add event listeners
  if (elements.notificationsToggle) {
    elements.notificationsToggle.addEventListener('change', function() {
      if (this.checked && Notification.permission !== 'granted') {
        requestNotificationPermission();
      } else {
        appData.notifications.enabled = this.checked;
      }
    });
  }
  
  if (elements.taskRemindersToggle) {
    elements.taskRemindersToggle.addEventListener('change', function() {
      appData.notifications.upcomingTaskReminder = this.checked;
    });
  }
  
  if (elements.weatherAlertsToggle) {
    elements.weatherAlertsToggle.addEventListener('change', function() {
      appData.notifications.weatherAlerts = this.checked;
    });
  }
  
  if (elements.locationAlertsToggle) {
    elements.locationAlertsToggle.addEventListener('change', function() {
      appData.notifications.locationBasedAlerts = this.checked;
    });
  }
  
  if (elements.testNotificationBtn) {
    elements.testNotificationBtn.addEventListener('click', function() {
      if (appData.notifications.enabled) {
        showNotification(
          'Test Notification', 
          'This is a test notification from your Personal Task Planner Bot!',
          {
            icon: 'https://via.placeholder.com/48x48/33808D/FFFFFF?text=🔔'
          }
        );
        addBotMessage("I've sent you a test notification. Did you receive it?");
      } else {
        addBotMessage("Notifications are currently disabled. Please enable them first to receive test notifications.");
      }
    });
  }
}

// Request notification permission
function requestNotificationPermission() {
  if (!("Notification" in window)) {
    return;
  }
  
  Notification.requestPermission().then(function (permission) {
    appData.notifications.permission = permission;
    appData.notifications.enabled = permission === 'granted';
    
    // Update UI
    if (elements.notificationsToggle) {
      elements.notificationsToggle.checked = appData.notifications.enabled;
    }
    
    if (permission === 'granted') {
      showNotification('Notifications Enabled', 'You will now receive task reminders and alerts.');
      addBotMessage("Notifications have been enabled successfully! You'll now receive reminders and alerts.");
    } else {
      addBotMessage("Notification permission was denied. You can enable notifications later in your browser settings.");
    }
  });
}

// Show a notification
function showNotification(title, body, options = {}) {
  if (!appData.notifications.enabled) {
    return;
  }
  
  // Default options
  const defaultOptions = {
    icon: 'https://via.placeholder.com/48x48/33808D/FFFFFF?text=🔔',
    badge: 'https://via.placeholder.com/48x48/33808D/FFFFFF?text=🔔',
    ...options
  };
  
  // Create notification
  new Notification(title, {
    body: body,
    ...defaultOptions
  });
}

// Start notification checks
function startNotificationChecks() {
  // Clear any existing interval
  if (notificationInterval) {
    clearInterval(notificationInterval);
  }
  
  // Check for notifications every minute
  notificationInterval = setInterval(checkForNotifications, 60000);
  
  // Also check immediately
  setTimeout(checkForNotifications, 5000); // Check after 5 seconds
}

// Check for notifications to send
function checkForNotifications() {
  if (!appData.notifications.enabled) {
    return;
  }
  
  const now = new Date();
  const currentTime = now.getHours() * 60 + now.getMinutes(); // Minutes since midnight
  
  // Check for upcoming tasks (30 minutes before)
  checkUpcomingTasks(currentTime);
  
  // Check for weather alerts (every 30 minutes)
  if (currentTime % 30 === 0) {
    checkWeatherAlerts();
  }
}

// Check for upcoming tasks
function checkUpcomingTasks(currentTime) {
  if (!appData.notifications.upcomingTaskReminder) {
    return;
  }
  
  // Combine today's and tomorrow's tasks
  const allTasks = [...appData.tasks, ...appData.tomorrowTasks];
  
  allTasks.forEach(task => {
    // Skip completed tasks
    if (task.completed) {
      return;
    }
    
    // For demo purposes, we'll simulate task times
    // In a real app, tasks would have specific times
    const taskTime = 9 * 60; // 9:00 AM in minutes
    const reminderTime = taskTime - 30; // 30 minutes before
    
    // Check if it's time to send reminder
    if (currentTime === reminderTime) {
      showNotification(
        'Upcoming Task Reminder',
        `Don't forget: ${task.title} in 30 minutes!`,
        {
          icon: 'https://via.placeholder.com/48x48/33808D/FFFFFF?text=⏰'
        }
      );
    }
  });
}

// Check for weather alerts
function checkWeatherAlerts() {
  if (!appData.notifications.weatherAlerts) {
    return;
  }
  
  // Simulate weather alert check
  // In a real app, this would check actual weather conditions
  const weatherCondition = appData.weather.condition.toLowerCase();
  
  if (weatherCondition.includes('rain') || weatherCondition.includes('storm')) {
    showNotification(
      'Weather Alert',
      `Heads up! ${appData.weather.condition} expected. Consider rescheduling outdoor tasks.`,
      {
        icon: 'https://via.placeholder.com/48x48/33808D/FFFFFF?text=🌧️'
      }
    );
  }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', initApp);
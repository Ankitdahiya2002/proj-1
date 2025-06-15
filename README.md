
🕉️ ANTARYAMI - AI Voice Assistant
A comprehensive AI-powered voice assistant with authentication, chat history, and admin dashboard.

✨ Features
🔐 Authentication & Security
User registration and login system
Password hashing with SHA-256
Role-based access control (User/Admin)
Session management
Input sanitization and validation

💬 Chat System
Persistent chat history storage
Multi-language support (English/Hindi)
Content filtering for inappropriate content

📊 Admin Dashboard
User analytics and activity tracking
Chat statistics and visualizations
User management interface
System monitoring tools
Data export functionality

📧 Email Notifications
Welcome emails for new users
System notifications
Email configuration via environment variables

📥 Export Features
Export chat history (CSV/JSON)
Export user data
Export system analytics
🚀 Quick Start
1. Installation
bash
# Clone the repository
git clone <your-repo-url>
cd omniscient

# Install dependencies
pip install -r requirements.txt
2. Environment Setup
Create a .env file:

env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Optional Settings
RATE_LIMIT_PER_HOUR=100
MAX_CHAT_HISTORY=50
3. Database & Admin Setup
bash
# Initialize database and create admin user
python setup_admin.py
4. Run the Application
bash
# Start the Streamlit app
streamlit run app.py
📋 Project Structure
antaryami-assistant/
├── app.py                 # Main Streamlit application
├── src/
│   └── helper.py         # AI and utility functions
├── setup_admin.py        # Admin user creation script
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create this)
├── antaryami.db         # SQLite database (auto-created)
└── README.md            # This file
🔧 Configuration
Environment Variables
Variable	Description	Required	Default
GEMINI_API_KEY	Google Gemini AI API key	Yes	-
EMAIL_HOST	SMTP server host	No	smtp.gmail.com
EMAIL_PORT	SMTP server port	No	587
EMAIL_USER	Email username	No	-
EMAIL_PASSWORD	Email password/app password	No	-
RATE_LIMIT_PER_HOUR	API rate limit	No	100
MAX_CHAT_HISTORY	Max chat history to display	No	50
Getting API Keys
Gemini AI API Key:
Visit Google AI Studio
Create a new API key
Add it to your .env file
Email Configuration (Optional):
For Gmail: Enable 2FA and create an App Password
Use the App Password in EMAIL_PASSWORD
👥 User Roles
🧑‍💼 Admin Users
Access to admin dashboard
View all user analytics
Export system data
Manage users
System monitoring
👤 Regular Users
Chat with AI assistant
View personal chat history
Export personal data
Voice and text input
🎯 Usage
For Users
Register/Login: Create account or login
Choose Mode: Select AI personality (Professional/Casual/Naughty)
Interact: Use voice or text input
History: View and export your chat history
For Admins
Login: Use admin credentials
Dashboard: Navigate to Admin Dashboard
Analytics: View user activity and system stats
Export: Download user data and analytics
Manage: Monitor system health
📊 Analytics Features
User Analytics
Total users and new registrations
Active users tracking
User activity patterns
Top active users
Chat Analytics
Daily chat volume
Language distribution
AI mode usage
Response times
Visualizations
Interactive charts with Plotly
Time series analysis
Distribution plots
Activity heatmaps
🛡️ Security Features
Authentication
Secure password hashing
Session management
Role-based access control
Content Filtering
Inappropriate content detection
Automated content moderation
Safe response generation
Data Protection
Input sanitization
SQL injection prevention
Rate limiting ready
📱 Mobile Support
The app is fully responsive and works on:

Desktop browsers
Mobile browsers
Tablet devices
🔧 Troubleshooting
Common Issues
Audio not working:
Check microphone permissions
Install PyAudio: pip install pyaudio
Database errors:
Run python setup_admin.py to reinitialize
Check file permissions
Email not sending:
# OMNISICIENT-AI
# omnisicent-ai

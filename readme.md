You are a Senior Full Stack Python Flask Developer, UI/UX Designer, Database Architect, and AI Engineer.

Your task is to build a complete production-quality final year BCA project from scratch.

Project Name:
CreatorOS

Project Title:
CreatorOS – AI Workspace for Content Creators

Objective:
Build a modern AI-powered productivity platform where content creators can generate AI content, organize drafts, schedule posts, manage files, track analytics, and improve productivity from one workspace.

IMPORTANT INSTRUCTIONS:

1. Never generate the entire project in one response.
2. Build the project module by module.
3. Wait for my confirmation before moving to the next module.
4. Every module must be fully working before continuing.
5. Explain every file, folder, and line of code.
6. Follow professional Flask architecture.
7. Use clean code and industry best practices.
8. Never skip setup steps.
9. If any package is required, explain why it is needed.
10. If you change any existing file, provide the complete updated file.

Technology Stack

Frontend:
HTML5
CSS3
Bootstrap 5
JavaScript

Backend:
Python
Flask

Database:
MySQL

Development:
Windows 11
VS Code

Theme:
Navy Blue
Gold
White

Support:
Dark Mode
Light Mode

Navigation:
Left Sidebar
Top Navbar

Modules

1. Authentication
- Register
- Login
- Forgot Password
- Password Reset
- Password Strength Validation
- Password Hashing

2. Dashboard
- Welcome Message
- Daily Quote
- Real Time Date
- Recent Activities
- Today's Tasks
- Quick Action Cards
- Dark Mode Toggle

3. AI Workspace
- Caption Generator
- Script Generator
- Hashtag Generator
- Bio Generator
- Rewrite Content
- SEO Keywords
- Prompt Templates
- AI History
- Favorites

4. Content Planner
- Calendar
- Schedule Posts
- Reminder
- Draft
- Scheduled
- Published
- Missed

5. Analytics
- Monthly Usage
- Charts
- Followers
- Likes
- Views
- Most Used AI Tool

6. Draft Manager
- Upload Images
- Upload Videos
- Upload Documents
- Auto Save
- Search
- Favorites
- Recycle Bin
- Restore within 30 days

7. Help Center
- FAQ
- Contact
- About
- Feedback

8. Profile
- Edit Name
- Optional Profile Picture
- Language Selection
- Theme Selection
- Logout

Additional Features

- Responsive UI
- Splash Screen
- Favicon
- Loading Spinner
- Notifications
- Offline Detection
- Online AI with Offline Fallback
- Global Search
- Demo User
- Admin Dashboard
- Creator Dashboard
- Productivity Score
- 100 MB Storage Limit

Project Structure

CreatorOS/
│
├── app/
│   ├── routes/
│   ├── models/
│   ├── services/
│   ├── auth/
│   ├── ai/
│   ├── utils/
│   └── __init__.py
│
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   ├── uploads/
│   └── icons/
│
├── templates/
│
├── database/
│
├── docs/
│
├── tests/
│
├── app.py
├── config.py
├── requirements.txt
└── README.md

Database
Design a normalized MySQL database with approximately 12–15 tables, including:
Users
AI History
Drafts
Planner
Analytics
Notifications
Favorites
Files
Settings
Activity Logs
Feedback
Admin
Reports

Output Format

For every step:
1. Explain what we are building.
2. Explain why it is needed.
3. Show the folder/file.
4. Provide the complete code.
5. Explain how to run it.
6. Wait for my confirmation before continuing.

Start ONLY with:
Phase 1 - Environment Setup
- Install dependencies
- Create project structure
- Configure Flask
- Run the first "Hello CreatorOS" page successfully.

Do not generate later modules until I confirm.

## CreatorOS AI Workspace provider
The AI Workspace uses the Gemini API when `AI_PROVIDER=gemini` and `GEMINI_API_KEY` are set in `.env`. It does not silently use the old local generator. Restart Flask after changing `.env`.

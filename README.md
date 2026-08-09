# ai-interview-agent

# 🎯 AI Interview Agent

An intelligent technical interview agent that conducts personalized interviews based on a candidate's AI learning journey. Built for the AI Cohort Hackathon.

---

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Live Demo](#live-demo)
- [Setup Instructions](#setup-instructions)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [AI Usage](#ai-usage)
- [API Documentation](#api-documentation)
- [Team](#team)
- [License](#license)

---

## 🔍 Overview

The **AI Interview Agent** is a full-stack application that conducts realistic, multi-turn technical interviews. It adapts questions based on each candidate's unique learning journey through a 31-day AI engineering curriculum.

**Why this matters:** After completing an intensive AI program, learners often struggle to communicate their knowledge effectively in technical interviews. This agent bridges that gap by providing personalized, conversational practice interviews with actionable feedback.

---

## ✨ Features

### Core Features
- 🎯 **Personalized Interviews** - Questions adapt to each candidate's learning history
- 🧠 **AI-Powered Conversations** - Uses Google Gemini for natural, contextual dialogue
- 📊 **Progress Tracking** - Tracks questions asked and curriculum days covered
- 📝 **Structured Feedback** - Provides summary, strengths, gaps, and next steps
- 📥 **Report Export** - Download interview reports as text files

### Enhanced Features
- 👤 **20 Candidate Profiles** - Comprehensive dataset of AI learners
- 📚 **Day Tracker** - Visual tracking of curriculum days covered (minimum 4 required)
- 🎨 **Modern UI** - Clean, responsive, professional interface
- ⌨️ **Keyboard Shortcuts** - Ctrl+N (New), Ctrl+E (End), Esc (Close)
- 🎉 **Confetti Celebration** - Fun experience on interview completion
- 🔄 **Auto-Scroll** - Chat automatically scrolls to latest message

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI, Python |
| **AI Model** | Google Gemini API (gemini-1.5-flash) |
| **Frontend** | HTML, CSS, JavaScript |
| **Storage** | In-memory session management |
| **Deployment** | Vercel (Frontend), Render (Backend) |

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.9+
- Google Gemini API Key

### 1. Clone the Repository
```bash
git clone https://github.com/Tanishka-lab/ai-interview-agent.git
cd ai-interview-agent
2. Set Up Backend
bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
3. Add API Key
Create a .env file in the backend/ folder:

text
GOOGLE_API_KEY=your-api-key-here
4. Run the Backend
bash
python main.py
Server runs at: http://localhost:8000

5. Open Frontend
Open frontend/index.html in your browser.

6. Deploy to Vercel (Optional)
bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
⚙️ How It Works
Interview Flow
Select Candidate - Choose from 20 AI cohort participants

Start Interview - AI generates the first question

Answer Questions - AI adapts follow-up questions based on responses

Track Progress - Monitor questions and curriculum days covered

End Interview - Click "End Interview" or complete 8 questions

Get Feedback - Receive structured feedback with strengths and gaps

Download Report - Export interview results as text file

AI Logic
The AI uses Google Gemini to:

Generate personalized questions based on candidate's completed curriculum days

Adapt follow-up questions based on answer quality

Create structured feedback with summary, strengths, gaps, and next steps

Maintain conversation context across all exchanges

Curriculum Awareness
The agent tracks which curriculum days are covered during the interview:

Minimum requirement: 4 different days

Day tracker shows progress in real-time

AI explicitly references day numbers in questions

📁 Project Structure
text
ai-interview-agent/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables (API key)
│   ├── data/
│   │   ├── curriculum.json  # 31-day AI curriculum
│   │   └── candidates.json  # 20 candidate profiles
│   ├── models/
│   │   ├── schemas.py       # Pydantic models
│   │   └── interview_state.py # State management
│   ├── services/
│   │   ├── session_manager.py # Session storage
│   │   ├── data_loader.py   # JSON data loading
│   │   └── ai_integration.py # Google Gemini integration
│   └── routes/
│       └── interview.py     # /api/interview endpoint
├── frontend/
│   ├── index.html           # Main UI
│   ├── style.css            # Styling
│   └── app.js               # Frontend logic
├── AI_USAGE_LOG.md          # AI usage documentation
├── vercel.json              # Vercel deployment config
└── README.md                # This file
🤖 AI Usage
This project uses Google Gemini (gemini-1.5-flash) for:

Feature	Description
Question Generation	Creates personalized, curriculum-aware questions
Follow-up Logic	Adapts questions based on candidate responses
Feedback Generation	Produces structured, actionable feedback
Context Management	Maintains conversation history across turns
See AI_USAGE_LOG.md for detailed AI usage documentation.

📡 API Documentation
POST /api/interview
Request (Start Interview):

json
{
  "sessionId": "abc-123",
  "candidate": {
    "id": "CAND-001",
    "name": "Sarah Johnson",
    "jobRole": "Senior Data Engineer",
    "yearsExperience": 9,
    "education": "MS Computer Science",
    "status": "COMPLETED"
  }
}
Request (Send Message):

json
{
  "sessionId": "abc-123",
  "message": "Yes, I understand embeddings..."
}
Response:

json
{
  "reply": "Great answer! Let me ask you another question...",
  "done": false,
  "feedback": null
}
Final Response:

json
{
  "reply": "Interview completed.",
  "done": true,
  "feedback": {
    "summary": "Candidate demonstrated strong understanding...",
    "strengths": ["Good technical knowledge", "Clear communication"],
    "gaps": ["Could explore advanced topics more deeply"],
    "next": ["Review vector databases", "Practice system design"]
  }
}

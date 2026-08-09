# ai-interview-agent

# 🎯 AI Interview Agent

An intelligent technical interview agent that conducts personalized interviews based on a candidate's AI learning journey. Built for Vicodathon by team Codifiers. 

---
## 🚀 Live Demo

### 🌐 Deployed Application
**[https://ai-interview-agent-2-5g7w.onrender.com/](https://ai-interview-agent-2-5g7w.onrender.com/)**

The frontend is deployed as a Render Static Site and communicates with the deployed FastAPI backend.

### ⚙️ Backend API
**[https://ai-interview-agent-1-vhon.onrender.com](https://ai-interview-agent-1-vhon.onrender.com)**

---


## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
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

⚙️ How It Works

## Interview Flow
1. **Select Candidate** - Choose from 20 AI cohort participants
2. **Start Interview** - AI generates the first question
3. **Answer Questions** - AI adapts follow-up questions based on responses
4. **Track Progress** - Monitor questions and curriculum days covered
5. **End Interview** - Click "End Interview" or complete 8 questions
6. **Get Feedback** - Receive structured feedback with strengths and gaps
7. **Download Report** - Export interview results as a text file

## AI Logic
The AI uses Google Gemini to:
- Generate personalized questions based on candidate's completed curriculum days
- Adapt follow-up questions based on answer quality
- Create structured feedback with summary, strengths, gaps, and next steps
- Maintain conversation context across all exchanges

## Curriculum Awareness
The agent tracks which curriculum days are covered during the interview:
- **Minimum requirement:** 4 different days
- Day tracker shows progress in real-time
- AI explicitly references day numbers in questions

## 📁 Project Structure
\`\`\`
ai-interview-agent/
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables (API key)
│   ├── data/
│   │   ├── curriculum.json     # 31-day AI curriculum
│   │   └── candidates.json     # 20 candidate profiles
│   ├── models/
│   │   ├── schemas.py          # Pydantic models
│   │   └── interview_state.py  # State management
│   ├── services/
│   │   ├── session_manager.py  # Session storage
│   │   ├── data_loader.py      # JSON data loading
│   │   └── ai_integration.py   # Google Gemini integration
│   └── routes/
│       └── interview.py        # /api/interview endpoint
├── frontend/
│   ├── index.html              # Main UI
│   ├── style.css                # Styling
│   └── app.js                   # Frontend logic
├── AI_USAGE_LOG.md              # AI usage documentation
└── README.md                    # This file
\`\`\`

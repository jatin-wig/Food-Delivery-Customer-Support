# Food Delivery Support AI

AI-powered Food Delivery Support System combining deterministic workflows with LLM intelligence 
Built with FastAPI, Streamlit, SQLite, and GenAI to simulate real-world customer support operations including order lifecycle, ETA engine, cancellation, refunds, and conversational AI.

---
## Demo Video

[![Watch the video](https://img.youtube.com/vi/BA6S7_kaFD0/hqdefault.jpg)](https://www.youtube.com/watch?v=BA6S7_kaFD0)

## 🚀 Features

### Real-Time UI
- Place orders
- Real-time status updates
- ETA countdown
- Cancel orders
- Chat interface
- Auto-refresh system

### Conversational Support
Users can ask:
- "Where is my order?"
- "Cancel my order"
- "I received the wrong item"
- "Help"
  
The assistant responds with contextual awareness of the active order.

### Session Memory
- Maintains conversation history
- Auto-expires inactive sessions
- Prevents context overload

### 🗄️ Persistent Database
SQLite powered via SQLAlchemy:

- Orders table
- Tickets table
- Timestamped lifecycle tracking
  
---

## 🛠️ Tech Stack

**Backend**
- FastAPI
- SQLAlchemy
- SQLite

**Frontend**
- Streamlit

**AI**
- Gemini / LLM API
- Prompt-engineered support agent

---

# Setup Instructions

## 1) Clone the Repository
```bash

git clone https://github.com/jatin-wig/Food-Delivery-Customer-Support.git
```

## 2) Install Dependencies
```bash
pip install -r requirements.txt
```

## 3) Add Gemini API Key (Required)

Create a .env file in the project root directory:

GOOGLE_API_KEY=YOUR_GEMINI_API_KEY

## Important:

Do not upload .env to GitHub

Keep your Gemini API key private

## 4) Run the App
```bash
streamlit run app.py
 ```
or 
```bash
python -m streamlit run app.py 
```
and 
```bash
uvicorn main:app
```
or 
```bash
python -m uvicorn main:app
```

# Built by Jatin Wig
### GitHub: https://github.com/jatin-wig

  


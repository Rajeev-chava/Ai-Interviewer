# AI Interviewer Web App

A comprehensive virtual AI interviewer web application built with Flask and modern frontend technologies. This platform helps users practice and improve their interview skills through AI-generated questions, real-time transcription, detailed feedback, and personalized recommendations.

---
🌐 **Live Demo**: [Click Here](https://ai-interviewer-igiv.onrender.com)
---

## 🚀 Overview

The AI Interviewer simulates real interview experiences, allowing users to practice in a safe environment. It uses OpenAI's powerful language models to generate relevant interview questions, analyze responses, and provide constructive feedback.

---

## 🔑 Key Features

### 👤 User Management

* User registration and login
* Secure authentication with password hashing
* Personalized dashboard with interview history

### 🎯 Interview Customization

* Choose job role, experience level, and years of experience
* Select question types: technical, behavioral, situational, coding
* Specify coding languages (Python, JavaScript, etc.)
* Select difficulty level and number of questions

### 🤖 AI-Powered Functionality

* Question generation using OpenAI GPT-3.5/GPT-4
* Real-time audio recording and Whisper-based transcription
* Detailed feedback: relevance, structure, technical accuracy
* Scoring system (1–10) for interview performance

### 🧠 Practice & Learning Tools

* Interview prep mode with custom questions
* Python Tutor integration for code visualization
* Performance tracking across sessions

---

## 🧰 Technology Stack

### Backend

* Flask (Python)
* SQLite with SQLAlchemy ORM
* Flask-Login for sessions
* Werkzeug for password hashing

### Frontend

* HTML5, Tailwind CSS, JavaScript (ES6+)
* Font Awesome for icons

### AI Integration

* OpenAI API (GPT for Q\&A, Whisper for speech-to-text)
* Python Tutor for code visualization

### Dev Tools

* Git for version control
* dotenv for env management
* Virtual environment (venv)

---
## 🧑‍💻 Developed by

**Chava Rajeev**  
📧 22jr5a1207@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/chavarajeev)  
🔗 [GitHub](https://github.com/Rajeev-chava)
---

## ⚙️ Setup Instructions

### Prerequisites

* Python 3.8+
* Git
* OpenAI API key ([https://platform.openai.com](https://platform.openai.com))

### Installation

```bash
# Clone the repo
git clone https://github.com/Rajeev-chava/Ai-Interviewer.git
cd Ai-Interviewer

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# OR
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Add the following to .env:
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key

# Initialize the database
python
>>> from app import db
>>> db.create_all()
>>> exit()

# Run the app
python app.py
```

Visit: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## 🧭 Application Workflow

1. **User Registration & Login**
2. **Interview Setup**: Customize job title, experience level, question types, coding languages
3. **Practice Interview**: AI generates questions, records answers, and transcribes them
4. **Feedback & Results**: View scores, detailed feedback, and improvement tips
5. **Performance Tracking**: Monitor your progress over time

---

## 📁 Project Structure

```
Ai-Interviewer/
├── app.py                # Main Flask app
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (ignored in Git)
├── static/               # Static files (CSS, JS, images)
├── templates/            # HTML templates
├── instance/             # Contains SQLite DB
└── voice.py              # Audio processing
```

---

## 🔮 Future Enhancements

* Integration with job portals for personalized question sets
* Video analysis for presentation and body language
* Live code editor for mock coding interviews
* Peer feedback and collaboration tools
* Mobile app for on-the-go interview prep

---

## 🤝 Contributing

Contributions are welcome!

```bash
# Fork the repo and clone it
# Create a feature branch
# Commit and push your changes
# Open a Pull Request
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

* [OpenAI](https://openai.com/)
* [Flask](https://flask.palletsprojects.com/)
* [Tailwind CSS](https://tailwindcss.com/)
* [Font Awesome](https://fontawesome.com/)
* [Python Tutor](https://pythontutor.com/)

---

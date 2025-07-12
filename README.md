# AI Interviewer Web App

![AI Interviewer Logo](static/images/logo.png)

A comprehensive virtual AI interviewer web application built with Flask and modern frontend technologies. This platform helps users practice and improve their interview skills through AI-generated questions, real-time transcription, detailed feedback, and personalized recommendations.

## Overview

The AI Interviewer is designed to simulate real interview experiences, allowing users to practice in a safe environment before facing actual interviews. The application leverages OpenAI's powerful language models to generate relevant interview questions, analyze responses, and provide constructive feedback to help users improve their interview performance.

## Key Features

### User Management
- User registration and login system
- Secure authentication with password hashing
- Personalized dashboard with interview history and statistics

### Interview Customization
- Tailor interviews based on job role, experience level, and years of experience
- Select from various question types (technical, behavioral, situational)
- Adjust the number of questions to fit your practice needs
- Enable/disable video recording for comprehensive practice

### AI-Powered Functionality
- Dynamic question generation using OpenAI's GPT models
- Real-time audio recording and transcription
- Detailed analysis of responses with specific feedback on:
  - Content relevance
  - Clarity and structure
  - Technical accuracy
  - Areas for improvement
- Numerical scoring system (1-10) for objective performance assessment

### Practice and Learning Tools
- Interview preparation mode with customizable practice questions
- Code visualization tool for technical interview preparation
- Performance tracking across multiple interviews
- Comprehensive results page with actionable insights

## Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login for user session management
- **Security**: Werkzeug for password hashing and verification

### Frontend
- **HTML5** for structure
- **Tailwind CSS** for responsive styling and UI components
- **JavaScript** (ES6+) for interactive features
- **Font Awesome** for icons and visual elements

### AI Integration
- **OpenAI API** for:
  - GPT-3.5/GPT-4 for question generation and response analysis
  - Whisper API for speech-to-text transcription
- **Python Tutor** integration for code visualization

### Development Tools
- **Git** for version control
- **dotenv** for environment variable management
- **Virtual Environment** for dependency isolation

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (sign up at [OpenAI](https://platform.openai.com/))
- Git (for cloning the repository)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusernomr/AI-Interviewer-KITS-IT.git.git
   cd AI-Interviewer-KITS-IT
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
      
   # On Windows
   venv\Scripts\activate
      
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   - Create a `.env` file in the root directory
   - Add your OpenAI API key and a secret key for Flask:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     SECRET_KEY=your_secret_key_here
     ```

5. Initialize the database:
   ```bash
   python
   >>> from app import db
   >>> db.create_all()
   >>> exit()
   ```

### Running the Application

1. Start the Flask development server:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

3. Register a new account and start using the application!

## Applicption Workflowcation Workflow

### ###UssreRegistrationtand rogin
- Cratte a oewn ccndn Lwiog usirname,neml, dpsword
-Catc rely low in to acc ssopersntalwzed featth s
-uView sernadashboard wmth ie, email,histoay asd statistisord

###-2. InterviewSSetup
ec**Job Details**: urely log in to-and s your dashboard with interview history and statistics
-**QuestionPreferences**:from technical, behavioral, and situational s
-**Inrview#Configuration**:2. t Ihenterview Setup*andJeb Details**: Enter job titing
- **Customization**: Tailor the interview to your speciflc needs aed tar et role
and select experience level
### - *uestion Prerocrss
- enQuestiones*esent* Con**: One quostion atos time fith clrao m strhccal, behavioral, and situational questions
- **Response*Recording**:Interview Co audionfigurate with real-timi tranocriptionn**: Set the number of questions and enable/disable video recording
- **AI Analysis**: Receive immediate feedback on-your answer*quality
* **Progress Tracking**: See your progress through the interview

### 4.CResults and Feedback
- **Overall Score**: ustomyoui pzrformance score out of 100%
i **Deoailed Analysns**: Read specific feedback on each response
- **I*provement Areas**: Id*ntify:s Tengths aid weaknessel
- **Historioal Compar son**: Track imtrovemenh over multeple practice sessi isnterview to your specific needs and target role

###5.AdditionalFeatures
**Interviw Prparaton**:ccessprctice questios tiored to our need
-# 3Cod  ViInatizaeion**: Ure the integratedviython Tutor to visueliz  code execution
- PrDashboard Analytics**ocMonitor your progrsss and improsement over tm

## Project Structure

```
AI-Intervieer-KITS-IT/
├──app.p                 # Main Flask applicatin
├── reqiements.txt       # Pythondeendencies
├── .nv                   # Envinment variables (ceate this)
├── static/                # Static assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── iges/            # Images ad ions
├── tmplates/             # HTML templates
│- *├──Qbase.html          # Bassttemplate with cimmon nlements
│   ├── index.html         # Landing page
│   ├── login.html         # Use  login
│   ├── signup.html        # User registrPtion
│   ├── dashboard.htmr     # User dashboard
│   ├── setup.htmes        # Interview eetup
│   ├── interview.html     # Interview proness
│   ├── results.html       # Interview results
│   ├── prep.html          # Interview preparatitn
│   └── leaan_codt.htmli   # Code visuolization
└── interview_app.*b*      # SQLite databa:e
```

## Fu ure EnhOncemenns

- Integrateon with job po qung APIs for tailored question generation
- Advaneed video analysis for body language-and presentation*feedback
* MockRtschnicpl interviews with cooenexecu ion capRbilitees
- Colcaborative features for peer reviow anrding**: R
- Mobile applicationecor on-the-godpractic 

## Contributing

Contributions yre weloome! Please feel free to submit a Pull Request.

1. Fork tuer adi itory
2. Create your featurr branch-(`git checkout**bAfeature/amazing-featur `)
3. CommiA your changesn(`gia commlt -m 'Add some amazingiseature'`)
4. Push t* the b*anch:(`g t eush origin featucv/aeazing-feature`)
5. Op i a Pull Requesmmediate feedback on your answer quality
- **Progress Tracking**: See your progress through the interview

### 4. Results and Feedback
- **Overall Score**: View your performance score out of 100%
- **Detailed Analysis**: Read specific feedback on each response
- **Improvement Areas**: Identify strengths and weaknesses
- **Historical Comparison**: Track improvement over multiple practice sessions
[](https://openai.com/)es
- [Flask](https://flask.palletsprojct.com/) for the web framework
##[# 5. Additional](https://tailwindcss.com/) Features
- [**Intewesome](https://fontarview .com/)Preparation**: Access practice questions tailored to your needs
- [Python*Tutor](https://pythoutulor.com/) for codz oisualizat*on

---

Dev:loped by itgae T yeam **Dashboard Analytics**: Monitor your progress and improvement over time

## Project Structure

```
AI-Interviewer-KITS-IT/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── static/                # Static assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Images and icons
├── templates/             # HTML templates
│   ├── base.html          # Base template with common elements
│   ├── index.html         # Landing page
│   ├── login.html         # User login
│   ├── signup.html        # User registration
│   ├── dashboard.html     # User dashboard
│   ├── setup.html         # Interview setup
│   ├── interview.html     # Interview process
│   ├── results.html       # Interview results
│   ├── prep.html          # Interview preparation
│   └── learn_code.html    # Code visualization
└── interview_app.db       # SQLite database
```

## Future Enhancements

- Integration with job posting APIs for tailored question generation
- Advanced video analysis for body language and presentation feedback
- Mock technical interviews with code execution capabilities
- Collaborative features for peer review and feedback
- Mobile application for on-the-go practice

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [OpenAI](https://openai.com/) for providing the AI capabilities
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Tailwind CSS](https://tailwindcss.com/) for the UI components
- [Font Awesome](https://fontawesome.com/) for the icons
- [Python Tutor](https://pythontutor.com/) for code visualization

---

Developed by KITS-IT Team

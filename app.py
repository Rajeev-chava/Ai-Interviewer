import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dotenv import load_dotenv
import openai
import json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "default-secret-key")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///interview_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    interviews = db.relationship('Interview', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    experience_level = db.Column(db.String(50), nullable=False)
    experience_years = db.Column(db.Integer, nullable=True)
    overall_score = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responses = db.relationship('Response', backref='interview', lazy=True)

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interview.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)
    transcript = db.Column(db.Text, nullable=True)
    analysis = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()

# Interview questions by category
interview_questions = {
    "technical": [],
    "behavioral": [],
    "situational": []
}

@app.route('/')
def index():
    """Render the landing page"""
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate form data
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('signup.html')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('signup.html')

        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('signup.html')

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form

        # Validate form data
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')

        # Check if user exists
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash('Invalid username or password', 'error')
            return render_template('login.html')

        # Log in user
        login_user(user, remember=remember)

        # Redirect to the page the user was trying to access
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('dashboard')

        flash('Login successful!', 'success')
        return redirect(next_page)

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Render the user dashboard"""
    # Get user's interview history
    interviews = Interview.query.filter_by(user_id=current_user.id).order_by(Interview.created_at.desc()).all()

    return render_template('dashboard.html', interviews=interviews)

@app.route('/setup', methods=['GET', 'POST'])
@login_required
def setup():
    """Render the interview setup page and handle form submission"""
    if request.method == 'POST':
        # Get user preferences from form
        data = request.json
        job_title = data.get('job_title', '')
        experience_level = data.get('experience_level', '')
        experience_years = data.get('experience_years', 0)
        question_types = data.get('question_types', [])
        num_questions = int(data.get('num_questions', 5))

        # Generate questions based on preferences
        generated_questions = generate_interview_questions(
            job_title,
            experience_level,
            question_types,
            num_questions
        )

        # Create new interview record in database
        interview = Interview(
            user_id=current_user.id,
            job_title=job_title,
            experience_level=experience_level,
            experience_years=experience_years
        )

        db.session.add(interview)
        db.session.commit()

        # Store interview ID and questions in session for later use
        session['current_interview_id'] = interview.id
        session['interview_questions'] = generated_questions
        session['enable_video'] = data.get('enable_video', False)

        return jsonify({"questions": generated_questions, "interview_id": interview.id})

    return render_template('setup.html')

@app.route('/interview')
@login_required
def interview():
    """Render the interview page"""
    # Check if there's an active interview
    interview_id = session.get('current_interview_id')
    if not interview_id:
        flash('Please set up an interview first', 'error')
        return redirect(url_for('setup'))

    # Get interview details
    interview = Interview.query.get(interview_id)
    if not interview or interview.user_id != current_user.id:
        flash('Interview not found', 'error')
        return redirect(url_for('dashboard'))

    # Get questions for this interview from session
    questions = session.get('interview_questions', [])

    # If no questions in session, use some default questions for testing
    if not questions:
        questions = [
            {"type": "technical", "question": "What is your experience with Python programming?"},
            {"type": "behavioral", "question": "Tell me about a time when you had to work under pressure."},
            {"type": "situational", "question": "How would you handle a disagreement with a team member?"},
            {"type": "technical", "question": "Explain the concept of object-oriented programming."},
            {"type": "behavioral", "question": "Describe a project you're particularly proud of."}
        ]
        # Store these questions in the session
        session['interview_questions'] = questions
        print("Using default questions since none were found in session")

    # Print questions for debugging
    print("Questions being passed to template:", questions)

    return render_template('interview.html', interview=interview, questions=questions)

@app.route('/results')
@login_required
def results():
    """Render the results page"""
    # Check if there's an active interview
    interview_id = request.args.get('interview_id') or session.get('current_interview_id')
    if not interview_id:
        flash('No interview results to display', 'error')
        return redirect(url_for('dashboard'))

    # Get interview details
    interview = Interview.query.get(interview_id)
    if not interview or interview.user_id != current_user.id:
        flash('Interview not found', 'error')
        return redirect(url_for('dashboard'))

    # Get responses for this interview
    responses = Response.query.filter_by(interview_id=interview_id).all()

    # Format responses for the template
    formatted_responses = []
    for response in responses:
        try:
            analysis = json.loads(response.analysis) if response.analysis else {}
        except json.JSONDecodeError:
            analysis = {"text": response.analysis}

        formatted_responses.append({
            "question": {
                "question": response.question,
                "type": response.question_type
            },
            "transcript": response.transcript,
            "analysis": analysis
        })

    return render_template('results.html', interview=interview, responses=formatted_responses)

@app.route('/api/transcribe', methods=['POST'])
@login_required
def transcribe_audio():
    """Transcribe audio using OpenAI Whisper API"""
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    question_text = request.form.get('question_text')
    question_type = request.form.get('question_type')

    try:
        # Use OpenAI's Whisper API for transcription
        # Save the audio file to a temporary file
        temp_file_path = "temp_audio.webm"
        audio_file.save(temp_file_path)

        # Open the file and transcribe
        with open(temp_file_path, "rb") as audio_file_obj:
            transcript = openai.Audio.transcribe("whisper-1", audio_file_obj)

        # Remove the temporary file
        os.remove(temp_file_path)

        # Get the transcript text
        transcript_text = transcript.text

        # Save to database if we have an active interview
        interview_id = session.get('current_interview_id')
        if interview_id and question_text and question_type:
            # Check if response already exists
            existing_response = Response.query.filter_by(
                interview_id=interview_id,
                question=question_text,
                question_type=question_type
            ).first()

            if existing_response:
                # Update existing response
                existing_response.transcript = transcript_text
                db.session.commit()
            else:
                # Create new response
                response = Response(
                    interview_id=interview_id,
                    question=question_text,
                    question_type=question_type,
                    transcript=transcript_text
                )
                db.session.add(response)
                db.session.commit()

        return jsonify({"transcript": transcript_text})
    except Exception as e:
        print(f"Transcription error: {str(e)}")
        # Check if the file exists and remove it
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return jsonify({"error": f"Error transcribing audio: {str(e)}"}), 500

@app.route('/api/transcribe-text', methods=['POST'])
@login_required
def transcribe_text():
    """Save transcript text directly to database"""
    data = request.json
    transcript = data.get('transcript', '')
    question_text = data.get('question_text', '')
    question_type = data.get('question_type', '')

    if not transcript or not question_text or not question_type:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Save to database if we have an active interview
        interview_id = session.get('current_interview_id')
        if not interview_id:
            return jsonify({"error": "No active interview"}), 400

        # Check if response already exists
        existing_response = Response.query.filter_by(
            interview_id=interview_id,
            question=question_text,
            question_type=question_type
        ).first()

        if existing_response:
            # Update existing response
            existing_response.transcript = transcript
            db.session.commit()
        else:
            # Create new response
            response = Response(
                interview_id=interview_id,
                question=question_text,
                question_type=question_type,
                transcript=transcript
            )
            db.session.add(response)
            db.session.commit()

        return jsonify({"success": True})
    except Exception as e:
        print(f"Error saving transcript: {str(e)}")
        return jsonify({"error": f"Error saving transcript: {str(e)}"}), 500

@app.route('/api/analyze', methods=['POST'])
@login_required
def analyze_response():
    """Analyze interview response using OpenAI"""
    data = request.json
    question = data.get('question', '')
    response_text = data.get('response', '')
    question_type = data.get('question_type', 'general')

    try:
        # Use OpenAI to analyze the response
        analysis = analyze_interview_response(question, response_text)
        analysis_json = json.dumps(analysis)

        # Save to database if we have an active interview
        interview_id = session.get('current_interview_id')
        if interview_id and question:
            # Find the response in the database
            response_record = Response.query.filter_by(
                interview_id=interview_id,
                question=question,
                question_type=question_type
            ).first()

            if response_record:
                # Update with analysis
                response_record.analysis = analysis_json
                db.session.commit()

        return jsonify({"analysis": analysis})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get-responses', methods=['GET'])
@login_required
def get_responses():
    """Get all responses for an interview"""
    interview_id = request.args.get('interview_id')

    if not interview_id:
        return jsonify({"error": "Missing interview_id parameter"}), 400

    try:
        # Get all responses for this interview
        responses = Response.query.filter_by(interview_id=interview_id).all()

        # Convert to JSON
        responses_data = []
        for response in responses:
            try:
                analysis = json.loads(response.analysis) if response.analysis else {}
            except json.JSONDecodeError:
                analysis = {"text": response.analysis}

            response_data = {
                'id': response.id,
                'question': {
                    'text': response.question,
                    'type': response.question_type
                },
                'transcript': response.transcript,
                'analysis': analysis
            }
            responses_data.append(response_data)

        return jsonify({"responses": responses_data})
    except Exception as e:
        print(f"Error getting responses: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/save-interview', methods=['POST'])
@login_required
def save_interview():
    """Save completed interview data"""
    data = request.json
    responses = data.get('responses', [])

    interview_id = session.get('current_interview_id')
    if not interview_id:
        return jsonify({"error": "No active interview"}), 400

    try:
        # Save each response
        for resp in responses:
            question = resp.get('question', {})
            question_text = question.get('question', '')
            question_type = question.get('type', 'general')
            transcript = resp.get('transcript', '')
            analysis = resp.get('analysis', {})

            # Find or create response record
            response_record = Response.query.filter_by(
                interview_id=interview_id,
                question=question_text,
                question_type=question_type
            ).first()

            if response_record:
                # Update existing record
                response_record.transcript = transcript
                response_record.analysis = json.dumps(analysis)
            else:
                # Create new record
                response_record = Response(
                    interview_id=interview_id,
                    question=question_text,
                    question_type=question_type,
                    transcript=transcript,
                    analysis=json.dumps(analysis)
                )
                db.session.add(response_record)

        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/save-score', methods=['POST'])
@login_required
def save_score():
    """Save overall score for an interview"""
    data = request.json
    interview_id = data.get('interview_id')
    overall_score = data.get('overall_score')

    if not interview_id or overall_score is None:
        return jsonify({"error": "Missing interview_id or overall_score"}), 400

    try:
        # Get the interview
        interview = Interview.query.get(interview_id)

        # Check if the interview exists and belongs to the current user
        if not interview or interview.user_id != current_user.id:
            return jsonify({"error": "Interview not found"}), 404

        # Update the overall score (convert to integer if it's a string)
        interview.overall_score = int(overall_score) if isinstance(overall_score, (str, float)) else overall_score
        db.session.commit()

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_interview_questions(job_title, experience_level, question_types, num_questions):
    """Generate interview questions using OpenAI"""
    try:
        prompt = f"""Generate {num_questions} interview questions for a {experience_level} level {job_title} position.
        Include questions of these types: {', '.join(question_types)}.
        Format the response as a JSON array of objects with 'type' and 'question' fields."""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert interviewer for technical positions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )

        # Parse the response to extract questions
        content = response.choices[0].message.content
        try:
            # Try to parse as JSON directly
            questions = json.loads(content)
        except json.JSONDecodeError:
            # If not valid JSON, extract JSON part from the text
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            if start_idx != -1 and end_idx != -1:
                questions_json = content[start_idx:end_idx]
                questions = json.loads(questions_json)
            else:
                # Fallback: create structured questions from text
                lines = content.split('\n')
                questions = []
                for line in lines:
                    if line.strip() and ':' in line:
                        q_type = "general"
                        if "technical" in line.lower():
                            q_type = "technical"
                        elif "behavioral" in line.lower():
                            q_type = "behavioral"
                        elif "situational" in line.lower():
                            q_type = "situational"

                        question_text = line.split(':', 1)[1].strip()
                        questions.append({"type": q_type, "question": question_text})

        return questions
    except Exception as e:
        print(f"Error generating questions: {str(e)}")
        return []

def analyze_interview_response(question, response):
    """Analyze interview response using OpenAI"""
    try:
        prompt = f"""
        Question: {question}

        Response: {response}

        Please analyze this interview response and provide feedback on:
        1. Content relevance (how well the response addresses the question)
        2. Clarity and structure
        3. Technical accuracy (if applicable)
        4. Areas of improvement
        5. Score (rate the answer on a scale of 1-10)

        Format your response as a JSON object with these fields:
        {{"contentRelevance": "...", "clarityAndStructure": "...", "technicalAccuracy": "...", "areasOfImprovement": "...", "score": X}}

        Where X is a number between 1 and 10 representing your overall assessment of the answer quality. The score should be displayed as "X/10" in the final output.
        """

        analysis_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert at evaluating interview responses. Always format your response as valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )

        # Extract and parse the analysis
        content = analysis_response.choices[0].message.content
        print("Raw analysis response:", content)

        try:
            # Try to parse as JSON directly
            # First, clean up any potential formatting issues
            content = content.replace('\n', ' ').replace('\r', ' ')
            # Handle the case where score is formatted as X/10 which is not valid JSON
            content = content.replace('"score": 1/10', '"score": "1/10"')
            content = content.replace('"score": 2/10', '"score": "2/10"')
            content = content.replace('"score": 3/10', '"score": "3/10"')
            content = content.replace('"score": 4/10', '"score": "4/10"')
            content = content.replace('"score": 5/10', '"score": "5/10"')
            content = content.replace('"score": 6/10', '"score": "6/10"')
            content = content.replace('"score": 7/10', '"score": "7/10"')
            content = content.replace('"score": 8/10', '"score": "8/10"')
            content = content.replace('"score": 9/10', '"score": "9/10"')
            content = content.replace('"score": 10/10', '"score": "10/10"')

            analysis = json.loads(content)
            print("Successfully parsed JSON response")

            # Keep the score as a string in format X/10 for display purposes
            # We don't need to convert it to an integer anymore

            return analysis
        except json.JSONDecodeError as json_error:
            print(f"JSON parsing error: {str(json_error)}")

            # Try to extract JSON from the text
            try:
                # Look for JSON-like structure between curly braces
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1

                if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                    json_str = content[start_idx:end_idx]

                    # Handle the case where score is formatted as X/10 which is not valid JSON
                    json_str = json_str.replace('"score": 1/10', '"score": "1/10"')
                    json_str = json_str.replace('"score": 2/10', '"score": "2/10"')
                    json_str = json_str.replace('"score": 3/10', '"score": "3/10"')
                    json_str = json_str.replace('"score": 4/10', '"score": "4/10"')
                    json_str = json_str.replace('"score": 5/10', '"score": "5/10"')
                    json_str = json_str.replace('"score": 6/10', '"score": "6/10"')
                    json_str = json_str.replace('"score": 7/10', '"score": "7/10"')
                    json_str = json_str.replace('"score": 8/10', '"score": "8/10"')
                    json_str = json_str.replace('"score": 9/10', '"score": "9/10"')
                    json_str = json_str.replace('"score": 10/10', '"score": "10/10"')

                    analysis = json.loads(json_str)
                    print("Successfully extracted and parsed JSON from text")

                    # Keep the score as a string in format X/10 for display purposes
                    # We don't need to convert it to an integer anymore

                    return analysis
            except Exception as extract_error:
                print(f"JSON extraction error: {str(extract_error)}")

            # If all JSON parsing fails, return as formatted text
            formatted_text = content.replace('\n', '<br>')
            return {"text": formatted_text}
    except Exception as e:
        print(f"Error analyzing response: {str(e)}")
        return {"text": "There was an error analyzing your response. The system might be experiencing high load. Please try again later."}

@app.route('/prep')
@login_required
def prep():
    """Render the prep interview page"""
    return render_template('prep.html')

@app.route('/practice')
@login_required
def practice():
    """Render the practice interview page"""
    # Get practice questions from session
    questions = session.get('practice_questions', [])

    # If no questions in session, redirect to prep page
    if not questions:
        flash('No practice questions found. Please set up your practice first.', 'error')
        return redirect(url_for('prep'))

    return render_template('practice.html', questions=questions)

@app.route('/api/generate-prep-questions', methods=['POST'])
@login_required
def generate_prep_questions():
    """Generate practice interview questions"""
    data = request.json
    job_title = data.get('job_title', '')
    experience_level = data.get('experience_level', '')
    question_types = data.get('question_types', [])
    coding_languages = data.get('coding_languages', [])
    num_questions = int(data.get('num_questions', 5))
    difficulty = data.get('difficulty', 'medium')

    try:
        # Build prompt based on user preferences
        prompt = f"""Generate {num_questions} interview questions for a {experience_level} level {job_title} position.
        Include questions of these types: {', '.join(question_types)}.
        The difficulty level should be {difficulty}.
        """

        # Add specific instructions for coding questions
        if 'coding' in question_types and coding_languages:
            prompt += f"""For coding questions, include problems that can be solved in these languages: {', '.join(coding_languages)}.
            For each coding question, specify which language it's for.
            """

        prompt += """Format the response as a JSON array of objects with 'type', 'question', 'difficulty' fields.
        For coding questions, also include a 'language' field."""

        # Generate questions using OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert interviewer for technical positions. Generate diverse, challenging, and realistic interview questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )

        # Parse the response to extract questions
        content = response.choices[0].message.content
        try:
            # Try to parse as JSON directly
            questions = json.loads(content)
        except json.JSONDecodeError:
            # If not valid JSON, extract JSON part from the text
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            if start_idx != -1 and end_idx != -1:
                questions_json = content[start_idx:end_idx]
                questions = json.loads(questions_json)
            else:
                # Fallback: create structured questions from text
                lines = content.split('\n')
                questions = []
                current_question = {}

                for line in lines:
                    if line.strip() and ':' in line:
                        if line.lower().startswith('question'):
                            if current_question and 'question' in current_question:
                                questions.append(current_question)
                            current_question = {'type': 'general', 'question': line.split(':', 1)[1].strip()}
                        elif 'type' in line.lower():
                            q_type = line.split(':', 1)[1].strip().lower()
                            if 'technical' in q_type:
                                current_question['type'] = 'technical'
                            elif 'behavioral' in q_type:
                                current_question['type'] = 'behavioral'
                            elif 'situational' in q_type:
                                current_question['type'] = 'situational'
                            elif 'coding' in q_type:
                                current_question['type'] = 'coding'
                        elif 'language' in line.lower() and 'coding' in current_question.get('type', ''):
                            current_question['language'] = line.split(':', 1)[1].strip()
                        elif 'difficulty' in line.lower():
                            current_question['difficulty'] = line.split(':', 1)[1].strip().lower()

                if current_question and 'question' in current_question:
                    questions.append(current_question)

        # Store questions in session for reuse in practice page
        session['practice_questions'] = questions

        return jsonify({"questions": questions})
    except Exception as e:
        print(f"Error generating practice questions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/check-answer', methods=['POST'])
@login_required
def check_answer():
    """Check practice answer using OpenAI"""
    data = request.json
    question = data.get('question', {})
    answer = data.get('answer', '')

    try:
        # Build prompt based on question type
        prompt = f"""Question: {question.get('question')}
        Question Type: {question.get('type')}
        User's Answer: {answer}

        Please evaluate this interview answer and provide feedback on:
        1. Correctness (as a percentage from 0-100)
        2. Explanation of what was good and what could be improved
        3. Suggestions for improvement

        Format your response as a JSON object with these fields:
        {{"correctness": X, "explanation": "...", "suggestions": ["...", "...", "..."]}}

        Where X is a number between 0 and 100 representing the correctness of the answer.
        """

        # Generate feedback using OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert at evaluating interview responses. Provide constructive feedback to help the user improve."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )

        # Parse the response
        content = response.choices[0].message.content
        try:
            # Try to parse as JSON
            feedback = json.loads(content)
        except json.JSONDecodeError:
            # If not valid JSON, return as text
            feedback = {"explanation": content}

        # Calculate score (0-100)
        score = feedback.get('correctness', 0)

        return jsonify({"feedback": feedback, "score": score})
    except Exception as e:
        print(f"Error checking answer: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/learn-code')
@login_required
def learn_code():
    """Render the learn code page"""
    return render_template('learn_code.html')

@app.route('/api/run-code', methods=['POST'])
@login_required
def run_code():
    """Run code in a sandbox environment"""
    data = request.json
    code = data.get('code', '')
    language = data.get('language', 'python')

    try:
        # For security reasons, we'll just simulate code execution
        # In a real app, you would use a secure sandbox environment

        # Simulate output based on language and code
        if language == 'python':
            output = f"Python code execution simulated:\n\n```python\n{code}\n```\n\nIn a real environment, your code would run here."
        elif language == 'javascript':
            output = f"JavaScript code execution simulated:\n\n```javascript\n{code}\n```\n\nIn a real environment, your code would run here."
        else:
            output = f"{language.capitalize()} code execution simulated:\n\n```{language}\n{code}\n```\n\nIn a real environment, your code would run here."

        return jsonify({"output": output})
    except Exception as e:
        print(f"Error running code: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/explain-code', methods=['POST'])
@login_required
def explain_code():
    """Explain code using OpenAI"""
    data = request.json
    code = data.get('code', '')
    language = data.get('language', 'python')
    explain_type = data.get('explain_type', 'detailed')

    try:
        # Build prompt based on explanation type
        if explain_type == 'basic':
            prompt = f"""Explain this {language} code in a simple way:

```{language}
{code}
```

Provide a brief overview and explain what the code does."""
        elif explain_type == 'advanced':
            prompt = f"""Provide an advanced explanation of this {language} code:

```{language}
{code}
```

Include:
1. A detailed overview of what the code does
2. Line-by-line explanation with technical details
3. Analysis of time and space complexity
4. Potential edge cases and bugs
5. Suggestions for optimization
6. Variable tracking showing how each variable changes throughout execution

Format your response as a JSON object with these sections."""
        else:  # detailed (default)
            prompt = f"""Explain this {language} code in detail:

```{language}
{code}
```

Provide:
1. An overview of what the code does
2. Line-by-line explanation
3. Variable tracking showing how each variable changes throughout execution

Format your response as a JSON object with these fields:
{{"overview": "...", "line_by_line": [{{
    "code": "line of code",
    "explanation": "explanation of this line"
}}], "variable_tracking": [{{
    "line_number": X,
    "variables": {{
        "variable_name": {{
            "value": "current value",
            "type": "data type"
        }}
    }}
}}]}}"""

        # Generate explanation using OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert programming tutor. Explain code clearly and accurately, tracking variables and their values throughout execution."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )

        # Parse the response
        content = response.choices[0].message.content
        try:
            # Try to parse as JSON
            explanation = json.loads(content)
        except json.JSONDecodeError:
            # If not valid JSON, extract JSON part from the text
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                try:
                    explanation = json.loads(json_str)
                except json.JSONDecodeError:
                    # If still not valid JSON, return as text
                    explanation = {"overview": content}
            else:
                # If no JSON structure found, return as text
                explanation = {"overview": content}

        # Extract variable tracking if available
        variable_tracking = explanation.get('variable_tracking', None)

        return jsonify({"explanation": explanation, "variable_tracking": variable_tracking})
    except Exception as e:
        print(f"Error explaining code: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=True)


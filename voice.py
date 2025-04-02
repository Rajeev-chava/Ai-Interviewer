from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import speech_recognition as sr
import os
import traceback

app = Flask(__name__)
# Enable CORS for all routes with more specific settings
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST"], "allow_headers": "*"}})

# Path to store the audio file
AUDIO_FILE_PATH = "recorded_audio.wav"

# Initialize the recognizer
recognizer = sr.Recognizer()
# Adjust recognition settings
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.dynamic_energy_adjustment_damping = 0.15
recognizer.dynamic_energy_ratio = 1.5
recognizer.pause_threshold = 0.8
recognizer.phrase_threshold = 0.3
recognizer.non_speaking_duration = 0.5

@app.route('/')
def index():
    # Return a simple response for status check
    response = make_response(jsonify({
        "status": "ok",
        "message": "Voice recognition server is running"
    }))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/start_recording', methods=['POST', 'OPTIONS'])
def start_recording():
    # Add CORS headers
    response_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = make_response()
        for key, value in response_headers.items():
            response.headers.add(key, value)
        return response

    print("Start recording request received")
    response = jsonify(status="Recording started")
    for key, value in response_headers.items():
        response.headers.add(key, value)
    return response

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    # Add CORS headers
    response_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = make_response()
        for key, value in response_headers.items():
            response.headers.add(key, value)
        return response

    # Check if audio file is present
    if 'audio_data' not in request.files:
        print("Error: No audio file received in request")
        print("Request files:", list(request.files.keys()))
        return jsonify(status="Error", error="No audio file received."), 400

    audio_file = request.files['audio_data']
    print(f"Received audio file: {audio_file.filename}, size: {audio_file.content_length} bytes")

    # Check if file is empty
    audio_file.seek(0, os.SEEK_END)
    file_size = audio_file.tell()
    audio_file.seek(0)  # Reset file pointer

    if file_size == 0:
        print("Error: Empty audio file received")
        return jsonify(status="Error", error="Empty audio file received."), 400

    try:
        # Make sure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(AUDIO_FILE_PATH)), exist_ok=True)

        # Save the original file
        audio_file.save(AUDIO_FILE_PATH)
        print(f"Audio file saved to {AUDIO_FILE_PATH}")

        # Check if the file was saved correctly
        if not os.path.exists(AUDIO_FILE_PATH) or os.path.getsize(AUDIO_FILE_PATH) == 0:
            print(f"Error: Failed to save audio file or file is empty. Path: {AUDIO_FILE_PATH}")
            return jsonify(status="Error", error="Failed to save audio file."), 500

        # Use speech recognition with multiple attempts
        with sr.AudioFile(AUDIO_FILE_PATH) as source:
            print("Adjusting for ambient noise...")
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

            print("Recording from audio file...")
            # Record the entire audio file
            audio = recognizer.record(source)

            # Try recognition with different settings
            text = None
            exceptions = []

            print("Attempt 1: Using default settings for speech recognition...")
            # Attempt 1: Default settings
            try:
                text = recognizer.recognize_google(audio, language='en-US')
                print(f"Recognition successful: '{text}'")
            except sr.UnknownValueError as e:
                error_msg = "Google Speech Recognition could not understand audio"
                print(f"Recognition failed: {error_msg}")
                exceptions.append(error_msg)
            except sr.RequestError as e:
                error_msg = f"Could not request results from Google Speech Recognition service; {e}"
                print(f"Recognition failed: {error_msg}")
                exceptions.append(error_msg)
            except Exception as e:
                error_msg = str(e)
                print(f"Recognition failed with unexpected error: {error_msg}")
                exceptions.append(error_msg)
                traceback.print_exc()

            # Attempt 2: Different pause threshold
            if text is None:
                print("Attempt 2: Using increased pause threshold...")
                try:
                    recognizer.pause_threshold = 1
                    text = recognizer.recognize_google(audio, language='en-US')
                    print(f"Recognition successful: '{text}'")
                except Exception as e:
                    error_msg = str(e)
                    print(f"Recognition failed: {error_msg}")
                    exceptions.append(error_msg)

            # Attempt 3: Different energy threshold
            if text is None:
                print("Attempt 3: Using increased energy threshold...")
                try:
                    recognizer.energy_threshold = 400
                    text = recognizer.recognize_google(audio, language='en-US')
                    print(f"Recognition successful: '{text}'")
                except Exception as e:
                    error_msg = str(e)
                    print(f"Recognition failed: {error_msg}")
                    exceptions.append(error_msg)

            if text is None:
                error_msg = f"Speech recognition failed after multiple attempts. Errors: {'; '.join(exceptions)}"
                print(f"All recognition attempts failed: {error_msg}")
                raise sr.UnknownValueError(error_msg)

            response = jsonify(status="Recording stopped", text=text)
            for key, value in response_headers.items():
                response.headers.add(key, value)
            return response

    except sr.UnknownValueError as e:
        print(f"UnknownValueError: {str(e)}")
        response = jsonify(status="Error", error=f"Could not understand the audio. Please speak clearly and try again. Details: {str(e)}")
        for key, value in response_headers.items():
            response.headers.add(key, value)
        return response, 400
    except sr.RequestError as e:
        print(f"RequestError: {str(e)}")
        response = jsonify(status="Error", error=f"Could not request results from Google Speech Recognition service; {e}")
        for key, value in response_headers.items():
            response.headers.add(key, value)
        return response, 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        traceback.print_exc()
        response = jsonify(status="Error", error=f"Error processing audio: {str(e)}")
        for key, value in response_headers.items():
            response.headers.add(key, value)
        return response, 500
    finally:
        # Clean up the audio file
        if os.path.exists(AUDIO_FILE_PATH):
            try:
                print(f"Cleaning up temporary file: {AUDIO_FILE_PATH}")
                os.remove(AUDIO_FILE_PATH)
                print("File removed successfully")
            except Exception as e:
                print(f"Error removing temporary file: {str(e)}")

@app.route('/get_text', methods=['GET', 'OPTIONS'])
def get_text():
    # Add CORS headers
    response_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = make_response()
        for key, value in response_headers.items():
            response.headers.add(key, value)
        return response

    response = jsonify(status="Error", error="This endpoint is no longer supported.")
    for key, value in response_headers.items():
        response.headers.add(key, value)
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5500)
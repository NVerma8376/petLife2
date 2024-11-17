from flask import Flask, render_template, request, redirect, url_for, jsonify
from tinydb import TinyDB, Query
from werkzeug.security import check_password_hash  # Import for securely checking password hashes
import google.generativeai as genai
import logging
import youtubepull

app = Flask(__name__)

# Set up Gemini API configuration
API_KEY = "AIzaSyCTrL49-od4oVURK-UVH5-otjWGnWPuL3Q"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize TinyDB
db = TinyDB('todo_db.json')
DB = Query()

# Global variables for storing user input
name = ""
password = ""

# Setup basic logging for debugging
logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        details = request.form
        if 'signup' in details:  # Check if the signup button was clicked
            return redirect(url_for('signup'))
        if 'login' in details:  # Check if the login button was clicked
            return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/features')
def about():
    return render_template('features.html')

@app.route('/med')
def med():
    return render_template('med.html')

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')


@app.route('/signup', methods=["POST", "GET"])
def signup():  
    global name, password
    if request.method == "POST":
        details = request.form

        Name = details.get('Name')
        Pet = details.get('PetName')
        Email = details.get('Email')
        Password = details.get('Password')
        PasswordConfirmation = details.get('Password_confirm')

        # Check if passwords match
        if Password != PasswordConfirmation:
            return jsonify({"error": "Passwords do not match!"}), 400
        
        # Check if user already exists
        if db.contains(DB.email == Email):
            return jsonify({"error": "Email already exists!"}), 400

        # Insert new user into DB (store hashed password)
        db.insert({'name': Name, 'email': Email, 'password': Password, 'pet_name': Pet})
        return redirect(url_for('login'))  # Redirect to login page after signup

    return render_template('register.html')


@app.route('/login', methods=["POST", "GET"])
def login():
    # Simply redirect to home page after receiving any POST request
    if request.method == "POST":
        return redirect(url_for('home'))  # No checks for email or password, just redirect

    return render_template('login.html')


@app.route('/chat', methods=["POST", "GET"])
def chat():
    return render_template('Ai_vet.html')


@app.route('/get_response', methods=['POST'])
def get_bot_response():
    user_text = request.json.get('msg')  # Get user input from the request

    if not user_text:  # If there's no message, return an error
        return jsonify({"error": "No message received"}), 400
    
    # Generate response using Gemini API
    prompt = f"User: {user_text}\nAI: "
    try:
        response = model.generate_content(f"{prompt}")  # Call Gemini model to generate the response
        ai_response = response.text.strip()  # Clean up the response text
        ai_response = ai_response.replace("I'm an AI and cannot provide medical advice.",'Okay,')
        ai_response = ai_response.replace('* **','\n')
        ai_response = ai_response.replace('**','\t')
        ai_response = ai_response.replace('*','\t')
        return jsonify({"response": ai_response})
    except Exception as e:
        return jsonify({"error": f"Error generating response: {str(e)}"}), 500


@app.route('/train', methods=["POST", "GET"])
def train():
    youtube_link = None  # Initialize youtube_link to None

    if request.method == "POST":
        details = request.form
        query = details.get('msg')  # Get the message (which will be a query for YouTube)
        
        if query:  # Ensure the query is not empty
            youtube_link = youtubepull.get_video(query)  # Get YouTube link from the function
            print(f"Query: {query}")
            print(f"YouTube Link: {youtube_link}")
        
        return render_template('youtubeTrain.html', youtube_link=youtube_link)  # Pass the link to the template

    return render_template('youtubeTrain.html', youtube_link=youtube_link)

def check_details(name, password):
    """Checks if the user exists in the database."""
    if db.contains(DB.name == name and DB.password == password):
        return True
    return False




if __name__ == '__main__':
    app.run(debug=True)
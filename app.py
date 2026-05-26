app.py
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os
import sqlite3
import stripe

load_dotenv()

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# DATABASE SETUP
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT
)
''')

conn.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/save-email', methods=['POST'])
def save_email():
    data = request.json
    email = data.get('email')

    cursor.execute("INSERT INTO leads (email) VALUES (?)", (email,))
    conn.commit()

    return jsonify({'status': 'saved'})

@app.route('/improve-resume', methods=['POST'])
def improve_resume():
    data = request.json
    resume = data.get('resume')

    prompt = f"""
    Improve this resume.

    Make it:
    - ATS optimized
    - More professional
    - Stronger wording
    - Better formatting suggestions

    Resume:
    {resume}
    """

    response = client.chat.completions.create(
        model='gpt-4.1-mini',
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ]
    )

    result = response.choices[0].message.content

    return jsonify({'result': result})

@app.route('/generate-cover-letter', methods=['POST'])
def cover_letter():
    data = request.json

    job = data.get('job')
    resume = data.get('resume')

    prompt = f"""
    Create a professional cover letter.

    Job description:
    {job}

    Resume:
    {resume}
    """

    response = client.chat.completions.create(
        model='gpt-4.1-mini',
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ]
    )

    result = response.choices[0].message.content

    return jsonify({'result': result})

@app.route('/resume-score', methods=['POST'])
def score_resume():
    data = request.json
    resume = data.get('resume')

    prompt = f"""
    Score this resume from 1-100.

    Return:
    - Overall score
    - ATS score
    - Weaknesses
    - Improvements

    Resume:
    {resume}
    """

    response = client.chat.completions.create(
        model='gpt-4.1-mini',
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ]
    )

    result = response.choices[0].message.content

    return jsonify({'result': result})

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'AI Resume Booster Pro',
                },
                'unit_amount': 1900,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:5000/dashboard',
        cancel_url='http://localhost:5000/pricing',
    )

    return jsonify({'id': session.id})

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)

# Gmail credentials (replace with your own or use environment variables)
GMAIL_USERNAME = 'tkdhannouche@gmail.com'  # Substitua pelo seu email do Gmail
GMAIL_PASSWORD = 'qshu knag rchb gseu'  # Substitua pela sua senha de app do Gmail

@app.route('/contact', methods=['POST'])
def contact():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    location = data.get('location')
    message = data.get('message')
    want_response = data.get('want_response')

    # Create message
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USERNAME
    msg['To'] = GMAIL_USERNAME  # Send to yourself or specify recipient
    msg['Subject'] = 'Contact Form Submission'

    body = f"Name: {name}\nPhone: {phone}\nEmail: {email}\nLocation: {location}\nMessage: {message}\nWant Response: {want_response}"
    msg.attach(MIMEText(body, 'plain'))

    # Send email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 2525)
        server.starttls()
        server.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(GMAIL_USERNAME, GMAIL_USERNAME, text)
        server.quit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)

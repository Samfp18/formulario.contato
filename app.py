from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)

# Gmail credentials (replace with your own or use environment variables)
GMAIL_USERNAME = 'tkdhannouche@gmail.com'  # Substitua pelo seu email do Gmail
GMAIL_PASSWORD = 'qshu knag rchb gseu'  # Substitua pela sua senha de app do Gmail
@app.route('/')
def home():
    return "Contact server is running"
@app.route('/contact', methods=['POST'])
def contact():
    nome = request.form.get('nome')
    telefone = request.form.get('telefone')
    email = request.form.get('email')
    local_treino = request.form.get('local_treino')
    mensagem = request.form.get('mensagem')

    # Validação básica
    if not all([nome, telefone, email, mensagem]):
        return jsonify({'error': 'Os campos Nome, Telefone, Email e Mensagem são obrigatórios.'}), 400

    if '@' not in email or '.' not in email:
        return jsonify({'error': 'Email inválido.'}), 400

    # Configurações do email
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USERNAME
    msg['To'] = GMAIL_USERNAME  # Enviar para o seu Gmail
    msg['Subject'] = "Nova mensagem de contato - Equipe Hannouche"

    body = f"Nome: {nome}\nTelefone: {telefone}\nEmail: {email}\nLocal de Treino Desejado: {local_treino}\nMensagem: {mensagem}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(GMAIL_USERNAME, GMAIL_USERNAME, text)
        server.quit()
        return jsonify({'message': 'Mensagem enviada com sucesso!'}), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao enviar a mensagem: {str(e)}'}), 500



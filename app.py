from flask import Flask, request, jsonify, redirect, url_for, session
import os
import pickle
import google.auth.transport.requests
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecretkey")  # mude isso em produção

# Caminho do credentials.json baixado do Google Cloud
CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

@app.route("/")
def home():
    return "Servidor de contato com Gmail API está rodando!"

@app.route("/authorize")
def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for("oauth2callback", _external=True)
    )
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    session["state"] = state
    return redirect(authorization_url)

@app.route("/oauth2callback")
def oauth2callback():
    state = session["state"]
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for("oauth2callback", _external=True)
    )
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    with open("token.pkl", "wb") as token_file:
        pickle.dump(credentials, token_file)

    return "Autorização concluída! Agora você pode enviar e-mails."

def get_gmail_service():
    creds = None
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token_file:
            creds = pickle.load(token_file)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
            with open("token.pkl", "wb") as token_file:
                pickle.dump(creds, token_file)
        else:
            return None
    return build("gmail", "v1", credentials=creds)

@app.route("/contact", methods=["POST"])
def contact():
    nome = request.form.get("nome")
    telefone = request.form.get("telefone")
    email = request.form.get("email")
    local_treino = request.form.get("local_treino")
    mensagem = request.form.get("mensagem")

    if not all([nome, telefone, email, mensagem]):
        return jsonify({"error": "Campos obrigatórios faltando"}), 400

    body = (
        f"Nome: {nome}\n"
        f"Telefone: {telefone}\n"
        f"Email: {email}\n"
        f"Local de Treino: {local_treino}\n"
        f"Mensagem:\n{mensagem}"
    )

    try:
        service = get_gmail_service()
        if not service:
            return jsonify({"error": "Credenciais inválidas. Acesse /authorize para configurar."}), 401

        message = MIMEText(body)
        message["to"] = os.environ.get("DESTINATARIO", "seuemail@gmail.com")
        message["subject"] = "Nova mensagem de contato - Equipe Hannouche"

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        service.users().messages().send(userId="me", body={"raw": raw}).execute()

        return jsonify({"message": "Mensagem enviada com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao enviar mensagem: {str(e)}"}), 500


if __name__ == "__main__":
    app.run("0.0.0.0", port=int(os.environ.get("PORT", 5000)))
from flask import Flask, request, jsonify, redirect, url_for, session
import os
import pickle
import google.auth.transport.requests
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecretkey")  # mude isso em produção

# Caminho do credentials.json baixado do Google Cloud
CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

@app.route("/")
def home():
    return "Servidor de contato com Gmail API está rodando!"

@app.route("/authorize")
def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for("oauth2callback", _external=True)
    )
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    session["state"] = state
    return redirect(authorization_url)

@app.route("/oauth2callback")
def oauth2callback():
    state = session["state"]
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for("oauth2callback", _external=True)
    )
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    with open("token.pkl", "wb") as token_file:
        pickle.dump(credentials, token_file)

    return "Autorização concluída! Agora você pode enviar e-mails."

def get_gmail_service():
    creds = None
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token_file:
            creds = pickle.load(token_file)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
            with open("token.pkl", "wb") as token_file:
                pickle.dump(creds, token_file)
        else:
            return None
    return build("gmail", "v1", credentials=creds)

@app.route("/contact", methods=["POST"])
def contact():
    nome = request.form.get("nome")
    telefone = request.form.get("telefone")
    email = request.form.get("email")
    local_treino = request.form.get("local_treino")
    mensagem = request.form.get("mensagem")

    if not all([nome, telefone, email, mensagem]):
        return jsonify({"error": "Campos obrigatórios faltando"}), 400

    body = (
        f"Nome: {nome}\n"
        f"Telefone: {telefone}\n"
        f"Email: {email}\n"
        f"Local de Treino: {local_treino}\n"
        f"Mensagem:\n{mensagem}"
    )

    try:
        service = get_gmail_service()
        if not service:
            return jsonify({"error": "Credenciais inválidas. Acesse /authorize para configurar."}), 401

        message = MIMEText(body)
        message["to"] = os.environ.get("DESTINATARIO", "tkdhannouche@gmail.com")
        message["subject"] = "Nova mensagem de contato - Equipe Hannouche"

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        service.users().messages().send(userId="me", body={"raw": raw}).execute()

        return jsonify({"message": "Mensagem enviada com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao enviar mensagem: {str(e)}"}), 500


if __name__ == "__main__":
    app.run("0.0.0.0", port=int(os.environ.get("PORT", 5000)))

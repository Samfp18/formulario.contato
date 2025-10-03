from flask import Flask, request, redirect, url_for, jsonify
import os
import pickle
import base64
from email.mime.text import MIMEText

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

app = Flask(__name__)

# Arquivos de credenciais e token
CLIENT_SECRETS_FILE = "credentials.json"
TOKEN_FILE = "token.pkl"
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Função para carregar credenciais
def load_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, "wb") as token:
                pickle.dump(creds, token)
    return creds

# Rota para iniciar o processo de autorização
@app.route("/authorize")
def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=url_for("oauth2callback", _external=True)
    )
    auth_url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true")
    return redirect(auth_url)

# Callback do Google OAuth
@app.route("/oauth2callback")
def oauth2callback():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=url_for("oauth2callback", _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    with open(TOKEN_FILE, "wb") as token:
        pickle.dump(creds, token)
    return "Autorização concluída! Agora você pode enviar e-mails."

# Função para enviar e-mail via Gmail API
def enviar_email(conteudo, destinatario=None):
    creds = load_credentials()
    if not creds:
        return {"error": "Credenciais inválidas. Acesse /authorize para configurar."}

    service = build("gmail", "v1", credentials=creds)

    # destinatário definido no ambiente ou default
    to_email = destinatario or os.environ.get("DESTINATARIO", "tkdhannouche@gmail.com")

    message = MIMEText(conteudo)
    message["to"] = to_email
    message["subject"] = "Nova mensagem do formulário"

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    send_message = {"raw": raw_message}

    service.users().messages().send(userId="me", body=send_message).execute()
    return {"success": True}

# Rota para receber formulário ou JSON
@app.route("/contact", methods=["POST"])
def contact():
    data = {}
    if request.is_json:  # caso seja JSON (via API ou Postman)
        data = request.get_json()
    else:  # caso venha de um formulário HTML
        data = request.form.to_dict()

    nome = data.get("nome", "")
    telefone = data.get("telefone", "")
    email = data.get("email", "")
    local = data.get("local", "")
    mensagem = data.get("mensagem", "")

    conteudo = f"""
    Nome: {nome}
    Telefone: {telefone}
    Email: {email}
    Local de Treino: {local}
    Mensagem: {mensagem}
    """

    resultado = enviar_email(conteudo)
    return jsonify(resultado)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

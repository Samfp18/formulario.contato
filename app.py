from flask import Flask, request, redirect, url_for, jsonify
import os
import pickle
import base64
from email.mime.text import MIMEText

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

app = Flask(__name__)

# Arquivo de credenciais do Google (baixado no Cloud Console)
CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# 🔹 Carrega as credenciais a partir da variável de ambiente
def load_credentials():
    creds = None
    token_data = os.environ.get("GMAIL_TOKEN")
    if token_data:
        creds = pickle.loads(base64.b64decode(token_data))
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            os.environ["GMAIL_TOKEN"] = base64.b64encode(pickle.dumps(creds)).decode("utf-8")
    return creds

# 🔹 Rota para iniciar a autorização
@app.route("/authorize")
def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=url_for("oauth2callback", _external=True)
    )
    auth_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )
    return redirect(auth_url)

# 🔹 Callback do Google (gera o token)
@app.route("/oauth2callback")
def oauth2callback():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=url_for("oauth2callback", _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    token_value = base64.b64encode(pickle.dumps(creds)).decode("utf-8")

    # Salva em memória (vale até o container reiniciar)
    os.environ["GMAIL_TOKEN"] = token_value

    # Imprime no log para você copiar e salvar no Render → Environment Variables
    print("==== COPIE O TOKEN ABAIXO E SALVE NO RENDER COMO GMAIL_TOKEN ====")
    print(token_value)
    print("=================================================================")

    return "Autorização concluída! Agora copie o token do log e salve no Render."

# 🔹 Função que envia o e-mail via Gmail API
def enviar_email(conteudo, destinatario=None):
    creds = load_credentials()
    if not creds:
        return {"error": "Credenciais inválidas. Acesse /authorize para configurar."}

    service = build("gmail", "v1", credentials=creds)
    to_email = destinatario or os.environ.get("DESTINATARIO", "tkdhannouche@gmail.com")

    message = MIMEText(conteudo)
    message["to"] = to_email
    message["subject"] = "Nova mensagem do formulário"

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
    return {"success": True}

# 🔹 Endpoint para receber dados do formulário ou JSON
@app.route("/contact", methods=["POST"])
def contact():
    data = request.form.to_dict() if not request.is_json else request.get_json()
    conteudo = "\n".join([f"{k.capitalize()}: {v}" for k, v in data.items()])
    return jsonify(enviar_email(conteudo))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

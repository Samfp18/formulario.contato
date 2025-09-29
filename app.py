from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)  # nome padrão para o Flask

# === Configurações de e-mail ===
# Defina estas variáveis no painel do Render como variáveis de ambiente
GMAIL_USERNAME = os.environ.get("GMAIL_USERNAME", "tkdhannouche@gmail.com")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD", "sua_senha_de_app_aqui")

@app.route("/")
def home():
    return "Contact server is running"

@app.route("/contact", methods=["POST"])
def contact():
    nome = request.form.get("nome")
    telefone = request.form.get("telefone")
    email = request.form.get("email")
    local_treino = request.form.get("local_treino")
    mensagem = request.form.get("mensagem")

    # Validação básica
    if not all([nome, telefone, email, mensagem]):
        return jsonify({"error": "Os campos Nome, Telefone, Email e Mensagem são obrigatórios."}), 400

    if "@" not in email or "." not in email:
        return jsonify({"error": "Email inválido."}), 400

    # Monta a mensagem
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USERNAME
    msg["To"] = GMAIL_USERNAME
    msg["Subject"] = "Nova mensagem de contato - Equipe Hannouche"

    body = (
        f"Nome: {nome}\n"
        f"Telefone: {telefone}\n"
        f"Email: {email}\n"
        f"Local de Treino Desejado: {local_treino}\n"
        f"Mensagem: {mensagem}"
    )
    msg.attach(MIMEText(body, "plain"))

    try:
        # Timeout de 10 segundos para evitar travamento
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USERNAME, GMAIL_USERNAME, msg.as_string())
        server.quit()
        return jsonify({"message": "Mensagem enviada com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao enviar a mensagem: {str(e)}"}), 500


# Executado apenas em ambiente local (Render usa gunicorn)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # fallback seguro
    app.run(host="0.0.0.0", port=port)

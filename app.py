from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# === Configurações ===
SENDGRID_API_KEY = os.environ.get("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")
DESTINATARIO = os.environ.get("DESTINATARIO", "tkdhannouche@gmail.com")  
REMETENTE = os.environ.get("REMETENTE", "tkd.hannoucheoficial.com.br")

@app.route("/")
def home():
    return "Contact server with SendGrid is running"

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

    # Monta corpo do e-mail
    conteudo = (
        f"Nome: {nome}\n"
        f"Telefone: {telefone}\n"
        f"Email: {email}\n"
        f"Local de Treino Desejado: {local_treino}\n"
        f"Mensagem: {mensagem}"
    )

    data = {
        "personalizations": [
            {
                "to": [{"email": DESTINATARIO}],
                "subject": "Nova mensagem de contato - Equipe Hannouche"
            }
        ],
        "from": {"email": REMETENTE},
        "content": [{"type": "text/plain", "value": conteudo}],
    }

    try:
        r = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {SENDGRID_API_KEY}",
                "Content-Type": "application/json"
            },
            json=data
        )

        if r.status_code == 202:
            return jsonify({"message": "Mensagem enviada com sucesso!"}), 200
        else:
            return jsonify({"error": "Falha ao enviar e-mail", "detalhe": r.text}), 500

    except Exception as e:
        return jsonify({"error": f"Erro ao enviar a mensagem: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

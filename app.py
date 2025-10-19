import os
import json
from datetime import datetime
from flask import Flask, request, make_response, abort

app = Flask(__name__)

# Port et token de vérification (depuis variables d'environnement)
PORT = int(os.environ.get("PORT", 3000))
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

def now_ts():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

@app.route("/", methods=["GET"])
def verify_webhook():
    """
    Vérification du webhook (GET)
    """
    mode = request.args.get("hub.mode")
    challenge = request.args.get("hub.challenge")
    token = request.args.get("hub.verify_token")

    if mode == "subscribe" and token and VERIFY_TOKEN and token == VERIFY_TOKEN:
        app.logger.info("✅ WEBHOOK VÉRIFIÉ")
        resp = make_response(challenge or "", 200)
        resp.mimetype = "text/plain"
        return resp
    else:
        return abort(403)

@app.route("/", methods=["POST"])
def receive_webhook():
    """
    Réception des événements (POST)
    Affiche le JSON reçu + extrait numéro et message
    """
    ts = now_ts()
    app.logger.info(f"\n📩 Webhook reçu à {ts}")

    try:
        payload = request.get_json(force=True)
    except Exception as e:
        raw = request.get_data(as_text=True)
        app.logger.error(f"❌ Erreur parsing JSON : {e}")
        app.logger.info("📄 Corps brut reçu :\n" + raw)
        return "", 200

    # Log complet du JSON reçu
    body_pretty = json.dumps(payload, indent=2, ensure_ascii=False)
    app.logger.info("📦 Contenu JSON reçu :\n" + body_pretty)

    # Extraction du numéro et message (structure type WhatsApp Meta)
    try:
        entry = payload.get("entry", [])[0]
        change = entry.get("changes", [])[0]
        value = change.get("value", {})
        messages = value.get("messages", [])

        if messages:
            message_data = messages[0]
            sender = message_data.get("from", "inconnu")
            text = message_data.get("text", {}).get("body", "(aucun message)")
            app.logger.info(f"📨 Message de {sender} : {text}")
        else:
            app.logger.info("⚠️ Aucune donnée 'messages' dans la requête.")
    except Exception as e:
        app.logger.error(f"⚠️ Erreur lors de l'extraction des champs : {e}")

    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

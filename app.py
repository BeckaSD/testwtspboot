import os
import json
from datetime import datetime
from flask import Flask, request, make_response, abort

# Créer l'application Flask **avant d'utiliser @app.route**
app = Flask(__name__)

# Port et token de vérification
PORT = int(os.environ.get("PORT", 3000))
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

def now_ts():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

@app.route("/", methods=["GET"])
def verify_webhook():
    """
    Vérifie le webhook (GET)
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
    Reçoit un POST webhook, affiche le JSON + extrait numéro/message
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

    body_pretty = json.dumps(payload, indent=2, ensure_ascii=False)
    app.logger.info("📦 Contenu JSON reçu :\n" + body_pretty)

    # Extraction du numéro et message
    try:
        entry = payload.get("entry", [])[0]
        change = entry.get("changes", [])[0]
        value = change.get("value", {})
        messages = value.get("messages", [])

        if messages:
            msg = messages[0]
            sender = msg.get("from", "inconnu")
            text = msg.get("text", {}).get("body", "(aucun message)")
            app.logger.info(f"📨 Message de {sender} : {text}")
        else:
            app.logger.info("⚠️ Aucune donnée 'messages'")
    except Exception as e:
        app.logger.error(f"⚠️ Erreur extraction champs : {e}")

    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

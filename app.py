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
    Facebook-like: hub.mode, hub.challenge, hub.verify_token
    """
    mode = request.args.get("hub.mode")
    challenge = request.args.get("hub.challenge")
    token = request.args.get("hub.verify_token")

    if mode == "subscribe" and token and VERIFY_TOKEN and token == VERIFY_TOKEN:
        app.logger.info("WEBHOOK VERIFIED")
        # Retourner le challenge en texte brut avec code 200
        resp = make_response(challenge or "", 200)
        resp.mimetype = "text/plain"
        return resp
    else:
        # Forbidden
        return abort(403)

@app.route("/", methods=["POST"])
def receive_webhook():
    """
    Réception des événements (POST)
    Logge le JSON reçu avec timestamp et répond 200.
    """
    ts = now_ts()
    app.logger.info(f"\n\nWebhook received {ts}\n")
    try:
        payload = request.get_json(force=True)
    except Exception:
        # Si le body n'est pas du JSON valide, logguer la raw data
        raw = request.get_data(as_text=True)
        app.logger.info("Invalid JSON payload, raw body:")
        app.logger.info(raw)
        return ("", 200)

    # Pretty-print JSON dans les logs
    pretty = json.dumps(payload, indent=2, ensure_ascii=False)
    app.logger.info(pretty)

    return ("", 200)

if __name__ == "__main__":
    # Lancer le serveur Flask en développement ; pour production, utiliser gunicorn/uvicorn/etc.
    app.run(host="0.0.0.0", port=PORT)

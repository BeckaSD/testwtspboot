@app.route("/", methods=["POST"])
def receive_webhook():
    """
    Réception des événements (POST)
    Logge le JSON reçu avec timestamp, expéditeur, et message.
    """
    ts = now_ts()
    app.logger.info(f"\n\n📩 Webhook reçu à {ts}\n")

    try:
        payload = request.get_json(force=True)
    except Exception:
        raw = request.get_data(as_text=True)
        app.logger.info("❌ JSON invalide. Corps brut :")
        app.logger.info(raw)
        return ("", 200)

    # Log JSON brut (optionnel)
    app.logger.debug("🔍 Contenu brut JSON :\n" + json.dumps(payload, indent=2, ensure_ascii=False))

    # Extraction du message (structure typique Meta / WhatsApp)
    try:
        # Navigue dans la structure
        entry = payload.get("entry", [])[0]
        change = entry.get("changes", [])[0]
        value = change.get("value", {})
        messages = value.get("messages", [])

        if messages:
            message_data = messages[0]
            sender = message_data.get("from", "??")
            text = message_data.get("text", {}).get("body", "(aucun message)")

            # Log final
            app.logger.info(f"📨 Message reçu de {sender} : {text}")
        else:
            app.logger.info("⚠️ Aucune donnée 'messages' dans la requête.")
    except Exception as e:
        app.logger.error(f"⚠️ Erreur lors de l'extraction des données : {str(e)}")
        app.logger.debug("Payload reçu (brut):\n" + json.dumps(payload, indent=2, ensure_ascii=False))

    return ("", 200)

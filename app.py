from flask import Flask, request
import os
import requests

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "")


@app.route("/", methods=["GET"])
def home():
    return "ForexGPT WhatsApp Bot online", 200


@app.route("/webhook", methods=["GET"])
def verify_webhook():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def receive_message():

    data = request.get_json(silent=True)

    if not data:
        return "OK", 200

    try:

        entry = data.get("entry", [])

        for item in entry:

            changes = item.get("changes", [])

            for change in changes:

                value = change.get("value", {})

                messages = value.get(
                    "messages",
                    []
                )

                for message in messages:

                    sender = message.get(
                        "from"
                    )

                    message_type = message.get(
                        "type"
                    )

                    if message_type != "text":
                        continue

                    text = message.get(
                        "text",
                        {}
                    ).get(
                        "body",
                        ""
                    ).strip()

                    print(
                        "Messaggio ricevuto:",
                        text
                    )

                    reply = (
                        "🤖 FOREXGPT\n\n"
                        "Messaggio ricevuto correttamente! ✅\n\n"
                        "Hai scritto:\n"
                        + text
                        + "\n\n"
                        "Il collegamento WhatsApp "
                        "funziona."
                    )

                    send_whatsapp_message(
                        sender,
                        reply
                    )

    except Exception as error:

        print(
            "Errore webhook:",
            error
        )

    return "OK", 200


def send_whatsapp_message(
    recipient,
    message
):

    if not WHATSAPP_TOKEN:
        print(
            "ERRORE: WHATSAPP_TOKEN mancante"
        )
        return

    if not PHONE_NUMBER_ID:
        print(
            "ERRORE: PHONE_NUMBER_ID mancante"
        )
        return

    url = (
        "https://graph.facebook.com/v23.0/"
        + PHONE_NUMBER_ID
        + "/messages"
    )

    headers = {
        "Authorization":
            "Bearer " + WHATSAPP_TOKEN,

        "Content-Type":
            "application/json"
    }

    payload = {

        "messaging_product":
            "whatsapp",

        "recipient_type":
            "individual",

        "to":
            recipient,

        "type":
            "text",

        "text": {
            "preview_url":
                False,

            "body":
                message
        }
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=20
        )

        print(
            "WhatsApp:",
            response.status_code
        )

        print(
            response.text
        )

    except Exception as error:

        print(
            "Errore invio WhatsApp:",
            error
        )


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )

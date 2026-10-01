from flask import Flask, request
import hmac
import hashlib


app = Flask(__name__)

secret_key = ""


@app.post("/set_secret")
def set_secret():
    global secret_key
    data = request.json
    secret_key = data.get("key", "")
    return {"message": "secret key"}


@app.post("/webhook")
def webhook():
    body = request.get_data()
    signature_header = request.headers.get("X-Signature")

    expected = hmac.new(secret_key.encode(), body, hashlib.sha256).hexdigest()
    received = signature_header.replace("sha256=", "")

    if not hmac.compare_digest(expected, received):
        return {"message": "invalid signature"}, 401

    print(request.json)
    print("webhook received")

    return {"message": "ok"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, jsonify, request
from chatbot import get_chat_response, start_agent

app = Flask(__name__)

@app.route("/")
def home():
    return "Nifty Island x Coinbase Agent Example - Hello World", 200

@app.route("/niftyagent", methods=["POST"])
def niftyagent():
    data = request.get_json()
    text = data.get('text', '')

    processed_text = get_chat_response(text)

    return jsonify({"text": processed_text}), 200

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"status": 404, "message": "Not Found"}), 404

# starts the agent
start_agent()
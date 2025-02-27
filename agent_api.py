from flask import Flask, jsonify, request
from chatbot import get_chat_response, start_agent, handle_world_message

app = Flask(__name__)

@app.route("/")
def home():
    return "Nifty Island x Coinbase Agent Example - Hello World", 200

@app.route("/niftyagent", methods=["POST"])
def niftyagent():
    data = request.get_json()

    text = data.get('text', '')

    # if a world message, custom handling (and optional custom prompting)
    # the player will NOT see this response
    if (text is "WORLD_TICK" or text is "WORLD_EVENT"):
        handle_world_message(data)
        return jsonify({"text": "World message received"}), 200

    processed_text = get_chat_response(text)

    return jsonify({"text": processed_text}), 200

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"status": 404, "message": "Not Found"}), 404

# starts the agent
start_agent()

# Uncomment this line if running locally (starts up flask api)
# app.run()
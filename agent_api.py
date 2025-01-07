from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flasgger import Swagger
from chatbot import get_chat_response, start_agent

app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)

class NiftyCDPAgent(Resource):

    def post(self):
        """
        This method responds to the POST request for this endpoint and returns the data the agent provides.
        ---
        tags:
        - Text Processing
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  text:
                    type: string
                    description: The text is sent to the agent
                    example: "hello world"
        responses:
          200:
            description: A successful POST request
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    text:
                      type: string
                      description: The response from the agent
        """
        data = request.get_json()
        text = data.get('text', '')

        processed_text = get_chat_response(text)

        return jsonify({"text": processed_text})

api.add_resource(NiftyCDPAgent, "/niftyagent")

if __name__ == "__main__":
    start_agent()
    app.run(debug=True)
# Coinbase Agentkit x Nifty Island Integration

### Overview
Coinbase provides web3 developers with a [robust development platform](https://github.com/coinbase) to interact across multiple chains.

Included in this development platform is the [CDP Agentkit](https://github.com/coinbase/cdp-agentkit), a set of tools that simplifies creating and bringing AI Agents onchain.  [Documentation is extensive and exhaustive](https://docs.cdp.coinbase.com/agentkit/docs/welcome).

Under the hood of CDP Agentkit is [LangChain](https://python.langchain.com/docs/introduction/), a framework for developing applications powered by large language models.  Agents created with either CDP Agentkit, or Langchain, are supported in Nifty Island.

Nifty *highly encourages* exploring the documentation to learn how to build, extend, and maintain your own custom agent.  The below tutorial is a very simple implementation of a CDP Agent.

### Quick Start

This tutorial will modify the [example CDP Agentkit chat bot](https://github.com/coinbase/cdp-agentkit/blob/master/cdp-langchain/examples/chatbot/chatbot.py) and expose it behind an API for quick and easy access within the Nifty ecosystem.

The repository can be found [here], but this tutorial will walk through the setup from scratch.

#### Setup
First, ensure that you have Python 3.10+ installed.

In a new folder, create 2 files: `wallet_data.txt` and `.env`.

##### Wallet Data
`wallet_data.txt` holds the private key for the agent's wallet.  If you intend to deploy this agent, you will likely need to better secure the wallet private key.  Extensive details are available [here](https://docs.cdp.coinbase.com/mpc-wallet/docs/wallets).

The format for `wallet_data.txt` is as follows:
```
{"wallet_id": "a61c7fe9-fdab-4d10-928a-50db0f53e311", "seed": "67045d57c63baca12b8a475d87d4cd4f512eb2590dfe3a46c7a7c9b9e935b56071035047e1612220d9e63d1f044ca62c4f0b946a3819c0e59167970f00d3515a", "default_address_id": "0xEcd969FfEF1f9d31a66096445224Ba6579c13F3b"}
```

You can create a wallet using CDP with the following code:
```python
wallet = Wallet.create()
data = wallet.export_data()
```
Where `data` is the value to place in `wallet_data.txt`

##### .env
The `.env` file holds the relevant environment variables.  Most deployment platforms allow you to upload these variables in a safe and secure way.

Included in `.env` should be the following variables:
```
CDP_API_KEY_NAME=your_cdp_key_name
CDP_API_KEY_PRIVATE_KEY=your_cdp_private_key
OPENAI_API_KEY=your_openai_key # Or XAI_API_KEY if using the NodeJS template
NETWORK_ID="base-sepolia" # Optional, defaults to base-sepolia
```

Follow instructions [here](https://portal.cdp.coinbase.com/projects/api-keys) to generate a CDP key, and go [here](https://platform.openai.com/docs/overview) to generate an OpenAI api key (AgentKit is model-agnostic, but we'll use OpenAI for this guide).

Place these variables in the relevant sections of the `.env` file.

#### Requirements
This tutorial has a couple dependencies:
```
flask
flasgger
flask_restful
pyairtable
gunicorn
cdp-sdk
cdp-langchain
python-dotenv
```

Place these in a new file titles `requirements.txt`.  Then open a command line, navigate to the folder with the file, and type `pip install -r requirements.txt`.  This will install all necessary requirements to run the agent, and the API to reach the agent from Nifty.

#### Chatbot
Next, copy the contents of [this file](https://github.com/coinbase/cdp-agentkit/blob/master/cdp-langchain/examples/chatbot/chatbot.py) into a new file titled `chatbot.py`.  This is Coinbase's example chatbot agent that we will modify to run in Nifty Island.

Add the line `from dotenv import load_dotenv` near the top of the file.  This will handle loading in the environment variables from the `.env` file.  Below that, add these lines:
```
load_dotenv()

CDP_API_KEY_NAME = os.getenv('CDP_API_KEY_NAME')
CDP_API_KEY_PRIVATE_KEY = os.getenv('CDP_API_KEY_PRIVATE_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
NETWORK_ID = os.getenv('NETWORK_ID')
```
These lines set the values held in the `.env` file.

Next, delete the methods `run_autonomous_mode`, `run_chat_mode`, `choose_mode`.  These are helper functions that are not needed; we will default to chat mode and remove the option to run in autonomous mode.

:::note

Because Nifty uses REST APIs to drive agents in game, autonomous agentic modes will not be supported for v1 of Nifty Agents.  Your agent can still be "autonomous" externally (i.e. it can automatically take actions outside of Nifty), but v1 of agent support in Nifty necessitates initial user interaction.

:::

Next, remove the methods `main()`, as well as the `if __name__ == "__main__":` if-statement block at the bottom of the file.  These files handle startup of the agent, which we will handle elsewhere.

Replace those blocks with the following code:
```
def get_chat_response(message):
    global agent_executor, config

    print ("user: " + message)
    final_response = ""
    # Run agent with the user's input in chat mode
    for chunk in agent_executor.stream(
        {"messages": [HumanMessage(content=message)]}, config
    ):
        if "agent" in chunk:
            response = chunk["agent"]["messages"][0].content
        elif "tools" in chunk:
            response = chunk["tools"]["messages"][0].content
        
        print (response)
        if response != "":
            final_response += "\n" + response
    
    return response

agent_executor = None
config = None

def start_agent():
    """Start the chatbot agent."""
    global agent_executor, config
    agent_executor, config = initialize_agent()
```

This code modifies the startup to happen in a distinct method (`start_agent()`), and handles the chat response from the API that Nifty will hit (`get_chat_response()`).

#### API
Now that the agent is setup, we can expose it behind an API.  In a new file title `agent_api.py`, paste the following code:
```
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
```

This class uses [Flask](https://flask.palletsprojects.com/en/stable/), a package designed to quickly and easily create APIs.

When the API is hit with a POST request, this method will trigger.

The steps it takes are:
1. Parse the `text` object out of the request (`text = data.get('text', '')`)
2. Pass the text to the method we created for the agent (`processed_text = get_chat_response(text)`)
3. Return the text in the POST response (`return jsonify({"text": processed_text})`)

The code at the bottom of the file handles both the startup of the agent, and the API.

#### Testing
Included in the provided Nifty Island example agent repo is a test file `test_api.py`.

Start the agent and API with `py agent_api.py`, then run the test file with `py test_api.py`.  The test file will send a POST request to your api, and print out the response.  Try interacting with your agent with:
```
You: What is your wallet address?
You: Deploy an NFT collection called 'Cool Cats' with symbol 'COOL'
You: Register a basename for yourself that represents your identity
```

:::note

The default chain is `sepolia-base`.  You will need to fund your agent with test funds, or ask it to pull funds from a faucet itself.

:::

#### Deploy

Deploy your agent to any hosting platform, popular ones include [Vercel](https://vercel.com/) and [Heroku](https://www.heroku.com/)

### Considerations and Moving Forward

CDP is a powerful toolkit for interacting on-chain.  Agentkit opens up that functionality to be leveraged by AI Agents.

Agentkit comes with a set of actions the agent can take (ex. deploy nft, deploy token, get balance, mint nft, etc.), but can easily and quickly be extended by adding new actions to the [Agentkit action space](https://github.com/coinbase/cdp-agentkit/tree/master/cdp-agentkit-core/cdp_agentkit_core/actions).

Consider adding new actions to include the Nifty Island action space, or other on-chain actions you'd like your agent to carry out!
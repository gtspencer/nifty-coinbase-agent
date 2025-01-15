# Coinbase Agentkit x Nifty Island Integration

### Overview
Coinbase provides web3 developers with a [robust development platform](https://github.com/coinbase) to interact across multiple chains.

Included in this development platform is the [CDP Agentkit](https://github.com/coinbase/cdp-agentkit), a set of tools that simplifies creating and bringing AI Agents onchain.  [Documentation is extensive and exhaustive](https://docs.cdp.coinbase.com/agentkit/docs/welcome).

Under the hood of CDP Agentkit is [LangChain](https://python.langchain.com/docs/introduction/), a framework for developing applications powered by large language models.  Agents created with either CDP Agentkit, or Langchain, are supported in Nifty Island.

Nifty *highly encourages* exploring the documentation to learn how to build, extend, and maintain your own custom agent.  The below tutorial is a very simple implementation of a CDP Agent.

### Quick Start

This tutorial will modify the [example CDP Agentkit chat bot](https://github.com/coinbase/agentkit/tree/master/cdp-langchain/examples/chatbot-python) and expose it behind an API for quick and easy access within the Nifty ecosystem.

The repository can be found [here](https://github.com/gtspencer/nifty-coinbase-agent), but this tutorial will walk through the setup from scratch.

#### Setup
First, ensure that you have Python 3.10+ installed.

In a new folder, create 2 files: `wallet_data.txt` and `.env`.

##### Wallet Data
`wallet_data.txt` holds the private seed for the agent's wallet.  If you intend to deploy this agent, you will likely need to better secure the wallet private key.  Extensive details are available [here](https://docs.cdp.coinbase.com/mpc-wallet/docs/wallets).

:::note

This `seed` is not your private key; it is the seed with which the private key is derived.  While not the private key itself, it can be used to gain access to the private key.  Protect this like you would your personal private key.

:::

This tutorial also includes the option to store the `wallet_data` in the `.env` file.  This is marginally safer than storing the contents in a plain text file.  Skip to **[the .env section](#env)** for instructions on how to do so.

The format for `wallet_data.txt` is as follows:
```json
{
  "wallet_id": "a61c7fe9-fdab-4d10-928a-50db0f53e311",
  "seed": "67045d57c63baca12b8a475d87d4cd4f512eb2590dfe3a46c7a7c9b9e935b56071035047e1612220d9e63d1f044ca62c4f0b946a3819c0e59167970f00d3515a",
  "default_address_id": "0xEcd969FfEF1f9d31a66096445224Ba6579c13F3b"
}
```

You can create a wallet using CDP with the following code:
```py
wallet = Wallet.create()
data = wallet.export_data()
```
Where `data` is the value to place in `wallet_data.txt`

:::warning

DO NOT use this private key and address; it is leaked and unsecure.  Furthermore, take caution if/when deploying to GitHub that you DO NOT publish your private key.  Consider using [Multiparty Computation (MPC) wallets](https://docs.cdp.coinbase.com/mpc-wallet/docs/wallets#coinbase-managed-wallets) for added safety in production environments.

:::

##### .env
The `.env` file holds the relevant environment variables.  Most deployment platforms allow you to upload these variables in a safe and secure way.

Included in `.env` should be the following variables:
```
CDP_API_KEY_NAME=your_cdp_key_name
CDP_API_KEY_PRIVATE_KEY=your_cdp_private_key
OPENAI_API_KEY=your_openai_key # Or XAI_API_KEY if using the NodeJS template
NETWORK_ID="base-sepolia" # Optional, defaults to base-sepolia
```

Optionally, and in leu of the `wallet_data.txt` file, you may place your wallet variables in the `.env` file like so:
```
WALLET_INFO='{"wallet_id": "a61c7fe9-fdab-4d10-928a-50db0f53e311", "seed": "67045d57c63baca12b8a475d87d4cd4f512eb2590dfe3a46c7a7c9b9e935b56071035047e1612220d9e63d1f044ca62c4f0b946a3819c0e59167970f00d3515a", "default_address_id": "0xEcd969FfEF1f9d31a66096445224Ba6579c13F3b"}'
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
```py
load_dotenv()

CDP_API_KEY_NAME = os.getenv('CDP_API_KEY_NAME')
CDP_API_KEY_PRIVATE_KEY = os.getenv('CDP_API_KEY_PRIVATE_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
NETWORK_ID = os.getenv('NETWORK_ID')
```
These lines set the values held in the `.env` file.

If your wallet info is in your `.env` file, make sure to include this line to load in the variables:
```py
WALLET_INFO = os.getenv('WALLET_INFO')
```

Next, delete the methods `run_autonomous_mode`, `run_chat_mode`, `choose_mode`.  These are helper functions that are not needed; we will default to chat mode and remove the option to run in autonomous mode.

:::note

Because Nifty uses REST APIs to drive agents in game, autonomous agentic modes will not be supported for v1 of Nifty Agents.  Your agent can still be "autonomous" externally (i.e. it can automatically take actions outside of Nifty), but v1 of agent support in Nifty necessitates initial user interaction.

:::

If you are loading in your wallet through environment variables, remove the lines that load in the `.txt` file:
```py
wallet_data = None

if os.path.exists(wallet_data_file):
    with open(wallet_data_file) as f:
        wallet_data = f.read()
```
and set the `wallet_data` variable from the `WALLET_INFO` we load from the environment:
```py
wallet_data = WALLET_INFO
```

Included in the git repo is a file `create_wallet.py` that will help create the wallet to load into the agent.  Be sure to set the correct chain, as this is baked into the wallet seed and cannot interact across chains.

If you plan on deploying this, remove the following lines:
```py
wallet_data = agentkit.export_wallet()
with open(wallet_data_file, "w") as f:
    f.write(wallet_data)
```
These lines write your wallet info to a file.  Even if your deployment service allows server writes, writing wallet info to a file is generally considered bad practice.

Next, remove the methods `main()`, as well as the `if __name__ == "__main__":` if-statement block at the bottom of the file.  These files handle startup of the agent, which we will handle elsewhere.

Replace those blocks with the following code:
```py
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
```py
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
# Uncomment this line if running locally (starts up flask api)
# app.run()
```

This class uses [Flask](https://flask.palletsprojects.com/en/stable/), a package designed to quickly and easily create APIs.

When the API is hit with a POST request, the method `niftyagent` will trigger.

The steps it takes are:
1. Parse the `text` object out of the request (`text = data.get('text', '')`)
2. Pass the text to the method we created for the agent (`processed_text = get_chat_response(text)`)
3. Return the text in the POST response (`return jsonify({"text": processed_text})`)

The code at the bottom of the file handles the startup of the agent, and will run automatically when the Flask app starts.

#### Custom Tools

AgentKit enables easy tool creation with Coinbase's CDP.  Anything that can be done with CDP can be exposed to your agent.  In fact, you can use an LLM to create tools for you!  Coinbase provides a template prompt for LLMs to generate tools [here](https://gist.github.com/murrlincoln/2d413e102844f810cf686fd54f4a996a).

Provided in the Nifty x Coinbase repo are 2 example tools, one to [get $ISLAND balance](https://github.com/gtspencer/nifty-coinbase-agent/blob/main/tools/balance_island.py), and one to [transfer $ISLAND](https://github.com/gtspencer/nifty-coinbase-agent/blob/main/tools/transfer_island.py).

Tool creation is simple.  In a file called `transfer_island.py`, do the following:
1. Import dependencies
```py
from cdp import Wallet
from pydantic import BaseModel, Field
```
2. Determine the prompt
```py
# Define the $Island transfer action prompt
TRANSFER_ISLAND_PROMPT = """
This tool transfers $Island tokens from the agent's wallet to another wallet. 
It interacts with the $Island token contract to initiate a transfer.
"""
```
3. Specify the inputs
```py
# Define the input schema
class TransferIslandInput(BaseModel):
    """Input argument schema for transferring $Island tokens."""
    recipient_address: str = Field(
        ...,
        description="The address of the recipient. Must be a valid Ethereum address.",
        example="0x1234567890abcdef1234567890abcdef12345678"
    )
```
4. Define the action
```py
# Define the $Island transfer action
def transfer_island(wallet: Wallet, recipient_address: str) -> str:
    """
    Transfers the ERC20 token $ISLAND from the agent's wallet to a specified recipient.

    Args:
        wallet (Wallet): The agent's wallet that holds the tokens.
        recipient_address (str): The recipient's wallet address.

    Returns:
        str: Confirmation of the transaction hash.
    """
    # Define the $Island contract address
    contract_address = "0x157a6df6B74F4E5E45af4E4615FDe7B49225a662"

    balance = wallet.balance(contract_address)

    # Transfer the full balance of the $Island asset to the destination wallet.
    transfer = wallet.transfer(balance, contract_address, recipient_address)

    # Wait for the transfer to settle.
    transfer.wait()

    return f"Transfer successful. Transaction hash: {transfer.transaction_hash}"
```

5. Add the tool to your agent:
Go back to your `chatbot.py` file, and import the tool:
```py
from tools.transfer_island import TRANSFER_ISLAND_PROMPT, TransferIslandInput, transfer_island
```
Then, define the new tool, and add it to the CDP toolkit on initialization.
```py
# Define the $ISLAND transfer tool
transferIslandTool = CdpTool(
    name="transfer_island",
    description=TRANSFER_ISLAND_PROMPT,
    cdp_agentkit_wrapper=agentkit,  # Replace with your actual CdpAgentkitWrapper instance
    args_schema=TransferIslandInput,
    func=transfer_island,
)

# Initialize CDP Agentkit Toolkit and get tools.
cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
tools = cdp_toolkit.get_tools()
tools.append(transferIslandTool)
```

You're done!  Your agent is now capable of transferring $ISLAND.

::: note

This implementation can be expanded to any ERC20 token and does not need to be hard-coded to $ISLAND token.  Just redefine the tool inputs to take in an ERC20 contract address, and modify the action handler to take in this value.

:::


#### Testing
Included in the provided Nifty Island example agent repo is a test file `test_api.py`.

To configure the agent for local testing, append the following line to the end of `agent_api.py`
```py
app.run()
```

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

Deploy your agent to any hosting platform, popular ones include [Vercel](https://vercel.com/) and [Heroku](https://www.heroku.com/).

##### Vercel
Deployments to Vercel are made easy through the Vercel command line tool.

First, create an account on Vercel.

Then, create a new file in your root directory called `vercel.json`.  This will act as instructions for Vercel to start your app:
```json
{
    "builds":[{"src": "agent_api.py", "use":"@vercel/python"}],
    "routes":[{"src": "/(.*)", "dest":"agent_api.py"}]
}
```

`builds` tells Vercel the starting point of your application, and `routes` defines the default api routing.

Next, install the Vercel command line tool by opening up a command window, and typing `npm i -g vercel`.  Once done, login to Vercel by typing `vercel login`.  Choose the option you used to sign up to Vercel, and follow the printed instructions.

Once signed in, navigate to the root directory of your agent code, and type `vercel --prod`.  This automatically handles the deployment of your app.  Once done, this command will print the dev url of your app.  This url (rather unhelpfully) points to a developer endpoint; it is unreachable unless you are logged in to your Vercel account.

Its now deployed, but its missing the environment variables.  Log into the Vercel website, and navigate to your project.  In the top bar, hit `Settings`, then in the side bar, high `Environment Variables`.  In the `Create New` section, add your environment variables by copying and pasting each individual key and value pair into the window.  Then click save.

To get the production url, navigate back to your project page, and copy the url under `Domains` (outlined in red).
![vercel_demo](/img/docs_reference_images/agents/vercel_demo.png)

This is the live url!  To test if its working, append your route to the url, in our case `/niftyagent`, and input it into the `url` variable in the `test_api.py` file, and type `py test_api.py` into the terminal.  After a few seconds, your agent's response should be printed to the console!

Now open Nifty Island, place an agent, and configure it with this url, and you're all done!

### Personality

The Coinbase Agent comes "seeded" with some information to prompt the LLM; this string is provided as the `state_modifier` in the `initialize_agent()` method.  Feel free to modify this to add personality and flair to your agent.

### Considerations and Moving Forward

CDP is a powerful toolkit for interacting on-chain.  Agentkit opens up that functionality to be leveraged by AI Agents.

Agentkit comes with a set of actions the agent can take (ex. deploy nft, deploy token, get balance, mint nft, etc.), but can easily and quickly be extended by adding new actions to the [Agentkit action space](https://github.com/coinbase/cdp-agentkit/tree/master/cdp-agentkit-core/cdp_agentkit_core/actions).

Consider adding new actions to include the Nifty Island action space, or other on-chain actions you'd like your agent to carry out!
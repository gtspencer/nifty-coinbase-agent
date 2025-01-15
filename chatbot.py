import os

# Import Langchain dependencies
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Import CDP Agentkit Langchain Extension.
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
from cdp_langchain.tools import CdpTool

# Import Custom Tools
from tools.transfer_island import TRANSFER_ISLAND_PROMPT, TransferIslandInput, transfer_island
from tools.balance_island import ISLAND_BALANCE_PROMPT, IslandBalanceInput, island_balance

from dotenv import load_dotenv

load_dotenv()

CDP_API_KEY_NAME = os.getenv('CDP_API_KEY_NAME')
CDP_API_KEY_PRIVATE_KEY = os.getenv('CDP_API_KEY_PRIVATE_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
NETWORK_ID = os.getenv('NETWORK_ID')
WALLET_INFO = os.getenv('WALLET_INFO')


def initialize_agent():
    """Initialize the agent with CDP Agentkit."""
    # Initialize LLM.
    llm = ChatOpenAI(model="gpt-4o-mini")

    # load in wallet info from environment variables
    wallet_data = WALLET_INFO

    # Configure CDP Agentkit Langchain Extension.
    values = {}
    if wallet_data is not None:
        # If there is a persisted agentic wallet, load it and pass to the CDP Agentkit Wrapper.
        values = {"cdp_wallet_data": wallet_data}

    agentkit = CdpAgentkitWrapper(**values)

    # Define the ERC20 transfer tool
    transferIslandTool = CdpTool(
        name="transfer_island",
        description=TRANSFER_ISLAND_PROMPT,
        cdp_agentkit_wrapper=agentkit,  # Replace with your actual CdpAgentkitWrapper instance
        args_schema=TransferIslandInput,
        func=transfer_island,
    )

    # Define the ISLAND balance tool
    islandBalanceTool = CdpTool(
        name="island_balance",
        description=ISLAND_BALANCE_PROMPT,
        cdp_agentkit_wrapper=agentkit,  # Replace with your actual CdpAgentkitWrapper instance
        args_schema=IslandBalanceInput,
        func=island_balance,
    )

    # disable writing of wallet file
    # persist the agent's CDP MPC Wallet Data.
    # wallet_data = agentkit.export_wallet()
    # with open(wallet_data_file, "w") as f:
    #     f.write(wallet_data)

    # Initialize CDP Agentkit Toolkit and get tools.
    cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
    tools = cdp_toolkit.get_tools()
    tools.append(transferIslandTool)
    tools.append(islandBalanceTool)

    # Store buffered conversation history in memory.
    memory = MemorySaver()
    config = {"configurable": {"thread_id": "CDP Agentkit Chatbot Example!"}}

    # Create ReAct Agent using the LLM and CDP Agentkit tools.
    return create_react_agent(
        llm,
        tools=tools,
        checkpointer=memory,
        state_modifier=(
            "You are a helpful agent that can interact onchain using the Coinbase Developer Platform AgentKit. "
            "You are empowered to interact onchain using your tools. If you ever need funds, you can request "
            "them from the faucet if you are on network ID 'base-sepolia'. If not, you can provide your wallet "
            "details and request funds from the user. Before executing your first action, get the wallet details "
            "to see what network you're on. If there is a 5XX (internal) HTTP error code, ask the user to try "
            "again later. If someone asks you to do something you can't do with your currently available tools, "
            "you must say so, and encourage them to implement it themselves using the CDP SDK + Agentkit, "
            "recommend they go to docs.cdp.coinbase.com for more information. Be concise and helpful with your "
            "responses. Refrain from restating your tools' descriptions unless it is explicitly requested."
        ),

    ), config

def get_chat_response(message):
    global agent_executor, config

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
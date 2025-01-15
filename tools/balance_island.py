from cdp import Wallet
from pydantic import BaseModel, Field

# Define the ERC20 transfer action prompt
ISLAND_BALANCE_PROMPT = """
This tool gets the balance of $Island tokens in the agent's wallet. 
"""

# Define the input schema
class IslandBalanceInput(BaseModel):
    """Input argument schema for getting $Island tokens balance."""

# Define the ERC20 transfer action
def island_balance(wallet: Wallet) -> str:
    """
    Gets the ERC20 token $ISLAND of the agent's wallet

    Args:
        wallet (Wallet): The agent's wallet that holds the tokens.

    Returns:
        str: Balance of $Island token
    """
    # Define the $Island contract address
    contract_address = "0x157a6df6B74F4E5E45af4E4615FDe7B49225a662"

    balance = wallet.balance(contract_address)

    return f"$Island balance: {balance}"
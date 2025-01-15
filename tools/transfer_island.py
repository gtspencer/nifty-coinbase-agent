from cdp import Wallet
from pydantic import BaseModel, Field

# Define the $Island transfer action prompt
TRANSFER_ISLAND_PROMPT = """
This tool transfers $Island tokens from the agent's wallet to another wallet. 
It interacts with the $Island token contract to initiate a transfer.
"""

# Define the input schema
class TransferIslandInput(BaseModel):
    """Input argument schema for transferring $Island tokens."""
    recipient_address: str = Field(
        ...,
        description="The address of the recipient. Must be a valid Ethereum address.",
        example="0x1234567890abcdef1234567890abcdef12345678"
    )

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
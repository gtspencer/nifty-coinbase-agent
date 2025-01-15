import os
from cdp import *
from dotenv import load_dotenv

load_dotenv()

CDP_API_KEY_NAME = os.getenv('CDP_API_KEY_NAME')
CDP_API_KEY_PRIVATE_KEY = os.getenv('CDP_API_KEY_PRIVATE_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
NETWORK_ID = os.getenv('NETWORK_ID')

Cdp.configure(CDP_API_KEY_NAME, CDP_API_KEY_PRIVATE_KEY)

w = Wallet.create('base-sepolia') # or base-mainnet
print(w.export_data()) # convert this to json and place in either wallet_data or .env
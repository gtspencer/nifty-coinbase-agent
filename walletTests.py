import os
from cdp import *
from dotenv import load_dotenv

load_dotenv()

CDP_API_KEY_NAME = os.getenv('CDP_API_KEY_NAME')
CDP_API_KEY_PRIVATE_KEY = os.getenv('CDP_API_KEY_PRIVATE_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
NETWORK_ID = os.getenv('NETWORK_ID')

print (CDP_API_KEY_NAME)
print (CDP_API_KEY_PRIVATE_KEY)

Cdp.configure(CDP_API_KEY_NAME, CDP_API_KEY_PRIVATE_KEY)

newWallet = Wallet.create()

print(newWallet.export_data().to_dict())
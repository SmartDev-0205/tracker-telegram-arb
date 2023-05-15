from web3 import Web3
import json
import requests

# Update the following variables with your own Etherscan and BscScan API keys and Telegram bot token
TELEGRAM_BOT_TOKEN = '5800403587:AAHHpzfKWVyheYYIWcMHpUJsMlqIhQ7xoTM'
TELEGRAM_CHAT_ID = '-984543212'
BLOCKCHAIN_NAME = "ARBITRAM"

# Router address
ARBICAN_API_KEY = 'CIQC9D6IWVXQ1ZX8MJ53SJTE7JJZM875HE'
ARITRAM_ROUTER_ADDRESS = '0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45'
ARITRAM_USDT_ADDRESS = '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9'
ARITRAM_WETH_ADDRESS = '0x82af49447d8a07e3bd95bd0d56f35241523fbab1'
ARITRAM_RPC = 'https://arb1.arbitrum.io/rpc'
ETH_RPC = 'https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161'

original_eth_usdt = Web3.to_checksum_address('0xdac17f958d2ee523a2206206994597c13d831ec7')
original_eth_weth = Web3.to_checksum_address('0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2')
original_eth_router = Web3.to_checksum_address('0x7a250d5630b4cf539739df2c5dacb4c659f2488d')

# Connect to the Ethereum network
eth_w3 = Web3(Web3.HTTPProvider(ARITRAM_RPC))
eth_router = Web3.to_checksum_address(ARITRAM_ROUTER_ADDRESS)
eth_usdt = Web3.to_checksum_address(ARITRAM_USDT_ADDRESS)
eth_weth = Web3.to_checksum_address(ARITRAM_WETH_ADDRESS)

orginal_eth_w3 = Web3(Web3.HTTPProvider(ETH_RPC))

Round = lambda x, n: float(eval('"%.'+str(int(n))+'f" % '+repr(int(x)+round(float('.'+str(float(x)).split('.')[1]),n))))

eth_abi = ''
with open('abi/abi.json', 'r') as f:
    eth_abi = json.load(f)

router_abi = ''
with open('abi/router.json', 'r') as f:
    router_abi = json.load(f)


def get_eth_tokensymbol(token_address):
    # Create a contract instance for the token
    token_address = Web3.to_checksum_address(token_address)
    token_contract = eth_w3.eth.contract(address=token_address, abi=eth_abi)
    # Call the name() function on the token contract
    token_name = token_contract.functions.symbol().call()
    return token_name
print(get_eth_tokensymbol(ARITRAM_WETH_ADDRESS))
def get_eth_price():
    router_contract = orginal_eth_w3.eth.contract(address=original_eth_router, abi=router_abi)
    oneToken = eth_w3.to_wei(1, 'Ether')
    price = router_contract.functions.getAmountsOut(oneToken,
                                                    [original_eth_weth, original_eth_usdt]).call()
    return Round((price[1]) / 10 ** 6,2)


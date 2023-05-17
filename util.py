from web3 import Web3
import json

# Update the following variables with your own Etherscan and BscScan API keys and Telegram bot token
TELEGRAM_BOT_TOKEN = '5800403587:AAHHpzfKWVyheYYIWcMHpUJsMlqIhQ7xoTM'
TELEGRAM_CHAT_ID = '-984543212'
BLOCKCHAIN_NAME = "ARBITRAM"

# Arbitram network
ARBICAN_API_KEY = 'VCBJR8MN74YC5VSUR34E8HYUNJAJXCK9GB'
ARITRAM_ROUTER_ADDRESS = '0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45'
ARITRAM_USDT_ADDRESS = '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9'
ARITRAM_WETH_ADDRESS = '0x82af49447d8a07e3bd95bd0d56f35241523fbab1'
ARITRAM_RPC = 'https://arb1.arbitrum.io/rpc'
arb_eth_w3 = Web3(Web3.HTTPProvider(ARITRAM_RPC))
arb_eth_router = Web3.to_checksum_address(ARITRAM_ROUTER_ADDRESS)
arb_eth_usdt = Web3.to_checksum_address(ARITRAM_USDT_ADDRESS)
arb_eth_weth = Web3.to_checksum_address(ARITRAM_WETH_ADDRESS)


# ETHEREUM
ETH_API_KEY = 'IPMS9STM3WNJ4K55KR6FS1F1KB77VPI96K'
ETH_ROUTER_ADDRESS = '0x7a250d5630b4cf539739df2c5dacb4c659f2488d'
ETH_USDT_ADDRESS = '0xdac17f958d2ee523a2206206994597c13d831ec7'
ETH_WETH_ADDRESS = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
ETH_RPC = 'https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161'
eth_w3 = Web3(Web3.HTTPProvider(ETH_RPC))
eth_router = Web3.to_checksum_address(ETH_ROUTER_ADDRESS)
eth_usdt = Web3.to_checksum_address(ETH_USDT_ADDRESS)
eth_weth = Web3.to_checksum_address(ETH_WETH_ADDRESS)

# BINANCE
BSC_API_KEY = '97H84KY4GJ81VK591B3TKSFXG4ANTWYRV3'
BSC_ROUTER_ADDRESS = '0x10ED43C718714eb63d5aA57B78B54704E256024E'
BSC_USDT_ADDRESS = '0x55d398326f99059ff775485246999027b3197955'
BSC_WETH_ADDRESS = '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c'
BSC_RPC = 'https://bsc-dataseed1.binance.org:443'
bsc_w3 = Web3(Web3.HTTPProvider(BSC_RPC))
bsc_router = Web3.to_checksum_address(BSC_ROUTER_ADDRESS)
bsc_usdt = Web3.to_checksum_address(BSC_USDT_ADDRESS)
bsc_weth = Web3.to_checksum_address(BSC_WETH_ADDRESS)


Round = lambda x, n: float(eval('"%.'+str(int(n))+'f" % '+repr(int(x)+round(float('.'+str(float(x)).split('.')[1]),n))))

eth_abi = ''
with open('abi/abi.json', 'r') as f:
    eth_abi = json.load(f)

router_abi = ''
with open('abi/router.json', 'r') as f:
    router_abi = json.load(f)

def get_tokensymbol(token_address,blockchain):
    # Create a contract instance for the token
    token_address = Web3.to_checksum_address(token_address)
    if blockchain == 'eth':
        token_contract = eth_w3.eth.contract(address=token_address, abi=eth_abi)
    elif blockchain == 'bsc':
        token_contract = bsc_w3.eth.contract(address=token_address, abi=eth_abi)
    elif blockchain == 'arb':
        token_contract = arb_eth_w3.eth.contract(address=token_address, abi=eth_abi)
    # Call the name() function on the token contract
    token_name = token_contract.functions.symbol().call()
    return token_name

def get_eth_price():
    router_contract = eth_w3.eth.contract(address=eth_router, abi=router_abi)
    oneToken = eth_w3.to_wei(1, 'Ether')
    price = router_contract.functions.getAmountsOut(oneToken,
                                                    [eth_weth, eth_usdt]).call()
    return Round((price[1]) / 10 ** 6,2)

def get_bnb_price():
    router_contract = bsc_w3.eth.contract(address=bsc_router, abi=router_abi)
    oneToken = bsc_w3.to_wei(1, 'Ether')
    price = router_contract.functions.getAmountsOut(oneToken,
                                                    [bsc_weth, bsc_usdt]).call()
    normalizedPrice = bsc_w3.from_wei(price[1], 'Ether') / oneToken
    return Round((normalizedPrice) * 10 ** 18, 2)


import sys, os

try:
    raise NotImplementedError("No error")
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno,e)

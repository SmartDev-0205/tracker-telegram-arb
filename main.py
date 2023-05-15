import time
import os.path
import re
from util import *

last_block_arb_number = 0


# Define some helper functions
def get_wallet_transactions(wallet_address):
    url = f'https://api.arbiscan.io/api?module=account&action=txlist&address={wallet_address}&startblock={last_block_arb_number}&endblock=99999999&sort=desc&apikey={ARBICAN_API_KEY}'
    response = requests.get(url)
    data = json.loads(response.text)

    result = data.get('result', [])
    if not isinstance(result, list):
        print(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error fetching transactions for {wallet_address} on {BLOCKCHAIN_NAME} blockchain: {data}")
        return []

    return result


def send_telegram_notification(message, value, usd_value, tx_hash):
    etherscan_link = f'<a href="https://arbiscan.io/tx/{tx_hash}">ARBISCAN</a>'

    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': f'{TELEGRAM_CHAT_ID}',
               'text': f'{message}\n TX : {etherscan_link}\nValue: {value:.6f} {BLOCKCHAIN_NAME} (${usd_value:.2f})',
               'parse_mode': 'HTML'}

    response = requests.post(url, data=payload)
    print(
        f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Telegram notification sent with message: {message}, value: {value} {BLOCKCHAIN_NAME} (${usd_value:.2f})")
    return response


def get_current_block_number():
    # Get ETH block number
    url = f'https://api.arbiscan.io/api?module=proxy&action=eth_blockNumber&apikey={ARBICAN_API_KEY}'
    response = requests.get(url)
    data = json.loads(response.text)
    result = data.get('result', [])
    global last_block_arb_number
    last_block_arb_number = int(result, 0)


def monitor_wallets():
    get_current_block_number()
    file_path = "log/watched_wallets.txt"
    if not os.path.exists(file_path):
        open(file_path, 'w').close()

    latest_tx_hashes = {}
    latest_tx_hashes_path = "log/latest_tx_hashes.json"
    if os.path.exists(latest_tx_hashes_path):
        with open(latest_tx_hashes_path, "r") as f:
            latest_tx_hashes = json.load(f)

    last_run_time = 0
    last_run_time_path = "log/last_run_time.txt"
    if os.path.exists(last_run_time_path):
        with open(last_run_time_path, "r") as f:
            last_run_time = int(f.read())
    eth_usd_price = get_eth_price()
    while True:
        try:
            # Read from file
            with open(file_path, 'r') as f:
                watched_wallets = set(f.read().splitlines())

            for wallet in watched_wallets:
                blockchain, wallet_address = wallet.split(':')
                transactions = get_wallet_transactions(wallet_address)
                for tx in transactions:
                    tx_hash = tx['hash']
                    tx_time = int(tx['timeStamp'])

                    if tx_hash not in latest_tx_hashes and tx_time > last_run_time:

                        global last_block_arb_number
                        last_block_arb_number = int(tx['blockNumber'])

                        contract_address = tx['to']
                        method_id = tx['methodId']
                        input = tx['input']
                        behavious = 'BUY'
                        value = float(tx['value']) / 10 ** 18  # Convert from wei to ETH or BNB

                        if contract_address.lower() == ARITRAM_ROUTER_ADDRESS.lower() and method_id == '0x04e45aaf':
                            print("TX:{}".format(tx_hash))
                            try:
                                eth_usd_price = get_eth_price()
                            except:
                                print("Because of api server, we are using old price")

                            usd_value = value * eth_usd_price

                            # buy function
                            token1_addess = input[34:74]
                            token2_addess = input[98:138]
                            token1_name = get_eth_tokensymbol(token1_addess)
                            token2_name = get_eth_tokensymbol(token2_addess)

                            # buy function
                            if token1_name == "WETH":
                                token_name = token2_name
                                token_address = token1_addess
                            # sell function
                            elif token2_name == "WETH":
                                behavious = "SELL"
                                token_name = token1_name
                                token_address = token2_addess
                            else:
                                continue
                            message = f'🚨 Wallet:{wallet_address}\nBehaviour:{behavious}\nToken name:{token_name}\nChain:{BLOCKCHAIN_NAME}\nToken Address:{token_address}\n'
                            send_telegram_notification(message, value, usd_value, tx['hash'], BLOCKCHAIN_NAME)
                        latest_tx_hashes[tx_hash] = int(tx['blockNumber'])

            # Save latest_tx_hashes to file
            with open(latest_tx_hashes_path, "w") as f:
                json.dump(latest_tx_hashes, f)

            # Update last_run_time
            last_run_time = int(time.time())
            with open(last_run_time_path, "w") as f:
                f.write(str(last_run_time))

            # Sleep for 10 seconds
            time.sleep(10)
        except Exception as e:
            print(f'An error occurred: {e}')
            # Sleep for 10 seconds before trying again
            time.sleep(10)


def add_wallet(wallet_address, blockchain):
    if blockchain == 'arb':
        file_path = "log/watched_wallets.txt"
        with open(file_path, 'a') as f:
            f.write(f'{blockchain}:{wallet_address}\n')


def remove_wallet(wallet_address, blockchain):
    if blockchain == 'arb':
        file_path = "log/watched_wallets.txt"
        temp_file_path = "temp.txt"
        with open(file_path, 'r') as f, open(temp_file_path, 'w') as temp_f:
            for line in f:
                if line.strip() != f'{blockchain}:{wallet_address}':
                    temp_f.write(line)
        os.replace(temp_file_path, file_path)


# Define the command handlers for the Telegram bot
def start(update, context):
    pass


#     message = """
# 👋 Welcome to the Ethereum and Binance Wallet Monitoring Bot!
#
# Use /add <blockchain> <wallet_address> to add a new wallet to monitor.
#
# Example: /add ETH 0x123456789abcdef
#
# Use /remove <blockchain> <wallet_address> to stop monitoring a wallet.
#
# Example: /remove ETH 0x123456789abcdef
#
# Use /list <blockchain> to list all wallets being monitored for a specific blockchain.
#
# Example: /list ETH or just /list
#
# Don't forget to star my Github repo if you find this bot useful! https://github.com/cankatx/crypto-wallet-tracker ⭐️
#     """
#     context.bot.send_message(chat_id=update.message.chat_id, text=message)


def add(update, context):
    if len(context.args) < 2:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Please provide a blockchain and wallet address to add.")
        return

    blockchain = context.args[0].lower()
    wallet_address = context.args[1]

    # Check if the wallet address is in the correct format for the specified blockchain
    if blockchain == 'arb':
        if not re.match(r'^0x[a-fA-F0-9]{40}$', wallet_address):
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text=f"{wallet_address} is not a valid Ethereum wallet address.")
            return
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Invalid blockchain specified: {blockchain}")
        return

    add_wallet(wallet_address, blockchain)
    message = f'Added {wallet_address} to the list of watched {blockchain.upper()} wallets.'
    context.bot.send_message(chat_id=update.message.chat_id, text=message)


def remove(update, context):
    if len(context.args) < 2:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Please provide a blockchain and wallet address to remove.\nUsage: /remove ARB 0x123456789abcdef")
        return
    blockchain = context.args[0].lower()
    wallet_address = context.args[1]
    remove_wallet(wallet_address, blockchain)
    message = f'Removed {wallet_address} from the list of watched {blockchain.upper()} wallets.'
    context.bot.send_message(chat_id=update.message.chat_id, text=message)


def list_wallets(update, context):
    with open("log/watched_wallets.txt", "r") as f:
        wallets = [line.strip() for line in f.readlines()]
    if wallets:
        eth_wallets = []
        for wallet in wallets:
            blockchain, wallet_address = wallet.split(':')
            if blockchain == 'arb':
                eth_wallets.append(wallet_address)

        message = "The following wallets are currently being monitored\n"
        message += "\n"
        if eth_wallets:
            message += "ARBITRAM Wallets:\n"
            for i, wallet in enumerate(eth_wallets):
                message += f"{i + 1}. {wallet}\n"
            message += "\n"
        context.bot.send_message(chat_id=update.message.chat_id, text=message)
    else:
        message = "There are no wallets currently being monitored."
        context.bot.send_message(chat_id=update.message.chat_id, text=message)


# Set up the Telegram bot
from telegram.ext import Updater, CommandHandler

updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Define the command handlers
start_handler = CommandHandler('start', start)
add_handler = CommandHandler('add', add)
remove_handler = CommandHandler('remove', remove)
list_handler = CommandHandler('list', list_wallets)

# Add the command handlers to the dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(add_handler)
dispatcher.add_handler(remove_handler)
dispatcher.add_handler(list_handler)

updater.start_polling()
print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Telegram bot started.")

print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Monitoring wallets...")
monitor_wallets()
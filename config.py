import os

from dotenv import load_dotenv, find_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

ETHERSCAN_API_KEY = os.environ.get('ETHERSCAN_API_KEY')
CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')
START_BLOCK = int(os.environ.get('START_BLOCK'))

NUMBER_OF_LAST_BLOCKS = 10

BLOCKS_PROCESSED = 300
TRANSACTIONS_PROCESSED = 200
WALLETS_PROCESSED = 300

BLOCKS_QUEUE = 'BlocksToProcessQueue'
TRANSACTIONS_QUEUE = 'TransactionsToProcessQueue'
WALLETS_QUEUE = 'WalletBalanceToUpdateQueue'

TRANSACTIONS_TABLE_NAME = 'TokenTransactions'
WALLETS_TABLE_NAME = 'WalletAddresses'
TRANSACTIONS_RCU = 5
TRANSACTIONS_WCU = 10
WALLETS_RCU = 5
WALLETS_WCU = 10

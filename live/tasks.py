from datetime import datetime

from zappa.async import task

from config import NUMBER_OF_LAST_BLOCKS
from providers.etherscan import Etherscan
from storages.dynamodb import DynamoDB


def proccess_last_blocks_transactions():
    etherscan = Etherscan()
    dynamodb = DynamoDB('TokenTransactions')
    end_block = etherscan.current_block()
    start_block = end_block - NUMBER_OF_LAST_BLOCKS
    transactions = etherscan.get_transactions(start_block, end_block)
    if transactions:
        for transaction_data in transactions:
            item = etherscan.parse_transaction(transaction_data)
            dynamodb.put_item(item)
            update_wallet_balance(item.get('to'))
            update_wallet_balance(item.get('from'))


@task
def update_wallet_balance(wallet_address):
    etherscan = Etherscan()
    balance = etherscan.get_wallet_balance(wallet_address)
    if balance is not None:
        dynamodb_client = DynamoDB('WalletAddresses')
        dynamodb_client.put_item({'wallet_address': wallet_address,
                                  'balance': balance,
                                  'last_updated': str(datetime.now())})

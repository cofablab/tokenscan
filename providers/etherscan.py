import hashlib
from datetime import datetime

import requests

from config import CONTRACT_ADDRESS, ETHERSCAN_API_KEY
from utils import add_params_to_url


class Etherscan(object):
    def __init__(self):
        self.api_key = ETHERSCAN_API_KEY
        self.contract_address = CONTRACT_ADDRESS

    def current_block(self):
        url = 'https://api.etherscan.io/api'
        params = {'module': 'proxy', 'action': 'eth_blockNumber', 'apikey': self.api_key}
        url_path = add_params_to_url(url, params)
        response = requests.get(url_path)
        content = response.json()
        result = content['result']
        block_number = int(result, 0)
        return block_number

    def get_transactions(self, start_block, end_block):
        url = 'https://api.etherscan.io/api'
        params = {'module': 'account', 'action': 'tokentx', 'contractaddress': self.contract_address,
                  'startblock': start_block, 'endblock': end_block, 'sort': 'desc', 'apikey': self.api_key}
        url_path = add_params_to_url(url, params)
        response = requests.get(url_path)
        if response.status_code == 200:
            content = response.json()
            transactions = content['result']
            return transactions
        return None

    def get_wallet_balance(self, wallet_address):
        url = 'https://api.etherscan.io/api'
        params = {'module': 'account', 'action': 'tokenbalance', 'contractaddress': self.contract_address,
                  'address': wallet_address, 'tag': 'latest', 'apikey': self.api_key}
        url_path = add_params_to_url(url, params)
        response = requests.get(url_path)
        if response.status_code == 200:
            content = response.json()
            balance = content['result']
            return balance
        return None

    def parse_transaction(self, transaction_data):
        item = {}
        item['block_number'] = int(transaction_data.get('blockNumber'))
        item['timestamp'] = int(transaction_data.get('timeStamp'))
        item['from'] = transaction_data.get('from')
        item['hash'] = transaction_data.get('hash')
        item['to'] = transaction_data.get('to')
        item['token_symbol'] = transaction_data.get('tokenSymbol')
        item['value'] = int(transaction_data.get('value'))
        index = '{}:{}:{}'.format(transaction_data.get('hash'), transaction_data.get('from'),
                                  transaction_data.get('to'))
        item['index'] = hashlib.sha224(index.encode('utf-8')).hexdigest()
        item['date_updated'] = str(datetime.now())
        return item

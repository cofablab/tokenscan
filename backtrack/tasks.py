import json
from datetime import datetime

from zappa.async import task

from config import (BLOCKS_PROCESSED, BLOCKS_QUEUE, START_BLOCK, TRANSACTIONS_PROCESSED, TRANSACTIONS_QUEUE,
                    TRANSACTIONS_TABLE_NAME, WALLETS_PROCESSED, WALLETS_QUEUE, WALLETS_TABLE_NAME)
from providers.etherscan import Etherscan
from storages.dynamodb import DynamoDB
from storages.sqs import SQS


def run():
    etherscan = Etherscan()
    current_block = etherscan.current_block()
    start_block = START_BLOCK

    number_of_blocks = current_block - start_block
    number_of_block_offset = round(number_of_blocks / 10)

    for block_number in range(start_block, current_block, number_of_block_offset):
        process_blocks(block_number, block_number + number_of_block_offset)


def pull_blocks_from_sqs():
    if not has_messages(BLOCKS_QUEUE):
        return
    for _ in range(0, int(BLOCKS_PROCESSED / 10)):
        process_block_messages()


def pull_transactions_from_sqs():
    if not has_messages(TRANSACTIONS_QUEUE):
        return
    for _ in range(0, int(TRANSACTIONS_PROCESSED / 10)):
        process_transaction()


def pull_wallet_addresses_from_sqs():
    if not has_messages(WALLETS_QUEUE):
        return
    for _ in range(0, int(WALLETS_PROCESSED / 10)):
        process_wallet_address_messages()


@task
def process_blocks(start_block, current_block, offset=100):
    sqs_client = SQS(BLOCKS_QUEUE)
    for block_number in range(start_block, current_block, offset):
        body = '{}:{}'.format(block_number, block_number + offset)
        sqs_client.send_message(body)


def process_block_messages():
    for body_content, receipt_handle in get_messages_from_queue(BLOCKS_QUEUE):
        start_block, end_block = body_content.split(':')
        get_and_queue_transactions(start_block, end_block, receipt_handle)


def process_wallet_address_messages():
    for body_content, receipt_handle in get_messages_from_queue(WALLETS_QUEUE):
        update_wallet_balance(body_content, receipt_handle)


@task
def get_and_queue_transactions(start_block, end_block, receipt_handle):
    etherscan = Etherscan()
    transactions = etherscan.get_transactions(start_block, end_block)
    if transactions is not None:
        sqs_client_blocks = SQS(BLOCKS_QUEUE)
        sqs_client_transactions = SQS(TRANSACTIONS_QUEUE)
        sqs_client_blocks.delete_message(receipt_handle)
        for transaction_data in transactions:
            item = etherscan.parse_transaction(transaction_data)
            sqs_client_transactions.send_message(json.dumps(item))


def has_messages(queue_name):
    sqs_client = SQS(queue_name)
    messages = sqs_client.receive_messages()
    if messages and len(messages) > 0:
        return True
    return False


def get_messages_from_queue(queue_name):
    sqs_client = SQS(queue_name)
    messages = sqs_client.receive_messages()
    if messages:
        for message in messages:
            body_content = message.get('Body')
            receipt_handle = message.get('ReceiptHandle')
            yield body_content, receipt_handle


def process_transaction():
    dynamodb = DynamoDB(TRANSACTIONS_TABLE_NAME)
    sqs_client = SQS(TRANSACTIONS_QUEUE)
    for body_content, receipt_handle in get_messages_from_queue(TRANSACTIONS_QUEUE):
        item = json.loads(body_content)
        dynamodb.put_item(item)
        save_wallets(item)
        sqs_client.delete_message(receipt_handle)


def save_wallets(item):
    dynamodb = DynamoDB(WALLETS_TABLE_NAME)
    dynamodb.put_item({'wallet_address': item['from'], 'balance': 0})
    dynamodb.put_item({'wallet_address': item['to'], 'balance': 0})


@task
def update_wallet_balance(wallet_address, receipt_handle):
    etherscan = Etherscan()
    balance = etherscan.get_wallet_balance(wallet_address)
    if balance is not None:
        dynamodb_client = DynamoDB(WALLETS_TABLE_NAME)
        dynamodb_client.put_item({'wallet_address': wallet_address,
                                  'balance': balance,
                                  'last_updated': str(datetime.now())})
        sqs_client = SQS(WALLETS_QUEUE)
        sqs_client.delete_message(receipt_handle)


def refresh_wallets():
    dynamodb = DynamoDB(WALLETS_TABLE_NAME)
    pages = dynamodb.get_scan_paginator('wallet_address')
    for page in pages:
        items = page.get('Items', [])
        put_items_to_queue(items)


@task
def put_items_to_queue(items):
    sqs_client = SQS(WALLETS_QUEUE)
    for item in items:
        sqs_client.send_message(item['wallet_address']['S'])

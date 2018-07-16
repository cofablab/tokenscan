import string
import json
from random import choice
import click
import os.path

import boto3

from config import (BLOCKS_QUEUE, TRANSACTIONS_QUEUE, TRANSACTIONS_RCU, TRANSACTIONS_TABLE_NAME, TRANSACTIONS_WCU,
                    WALLETS_QUEUE, WALLETS_RCU, WALLETS_TABLE_NAME, WALLETS_WCU)


def random_string():
    allchar = string.ascii_letters + string.digits
    return "".join(choice(allchar) for _ in range(0, 10)).lower()


zappa_settings = {
    "live": {
        "app_function": "app.app",
        "aws_region": "eu-west-1",
        "profile_name": "default",
        "project_name": "tokenscan",
        "runtime": "python3.6",
        "s3_bucket": "zappa-njdxrwhz6",
        "memory_size": 128,
        "timeout_seconds": 300,
        "xray_tracing": True,
        "events": [
            {
                "function": "live.tasks.proccess_last_blocks_transactions",
                "expression": "rate(1 minute)"
            }
        ]
    },
    "backtrack": {
        "app_function": "app.app",
        "aws_region": "eu-west-1",
        "profile_name": "default",
        "project_name": "tokenscan",
        "runtime": "python3.6",
        "s3_bucket": "zappa-njdxrwhz6",
        "memory_size": 128,
        "timeout_seconds": 300,
        "apigateway_enabled": False,
        "xray_tracing": True,
        "events": [
            {
                "function": "backtrack.tasks.pull_blocks_from_sqs",
                "expression": "rate(1 minute)"
            },
            {
                "function": "backtrack.tasks.pull_transactions_from_sqs",
                "expression": "rate(1 minute)"
            },
            {
                "function": "backtrack.tasks.pull_wallet_addresses_from_sqs",
                "expression": "rate(1 minute)"
            }
        ]
    }
}


@click.command()
@click.option('--aws_region', default='eu-west-1', prompt='AWS Region',
              help='Select AWS Region')
@click.option('--s3_bucket', default='tokenscan-{}'.format(random_string()),
              prompt="""Your deployments will need to be uploaded to a private S3 bucket.
If you don't have a bucket yet, we'll create one for you too.
What do you want to call your bucket? default:""",
              help='Select S3 bucket')
def setup(aws_region, s3_bucket):
    live = zappa_settings['live']
    live['aws_region'] = aws_region
    live['s3_bucket'] = s3_bucket

    backtrack = zappa_settings['backtrack']
    backtrack['aws_region'] = aws_region
    backtrack['s3_bucket'] = s3_bucket

    if not os.path.isfile('zappa_settings.json'):
        with open('zappa_settings.json', 'w') as outfile:
            json.dump(zappa_settings, outfile)
            print('Generating zappa_settings.json')
    else:
        print('zappa_settings.json already exist')

    dynamodb = boto3.resource('dynamodb')
    dynamodb_client = boto3.client('dynamodb')
    try:
        dynamodb.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'block_number',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'index',
                    'AttributeType': 'S'
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'block_number',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'index',
                    'KeyType': 'RANGE'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': TRANSACTIONS_RCU,
                'WriteCapacityUnits': TRANSACTIONS_WCU
            },
            TableName=TRANSACTIONS_TABLE_NAME
        )
        print('{} table created'.format(TRANSACTIONS_TABLE_NAME))
    except dynamodb_client.exceptions.ResourceInUseException:
        print('{} table already exist'.format(TRANSACTIONS_TABLE_NAME))

    try:
        dynamodb.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'wallet_address',
                    'AttributeType': 'S'
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'wallet_address',
                    'KeyType': 'HASH'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': WALLETS_RCU,
                'WriteCapacityUnits': WALLETS_WCU
            },
            TableName=WALLETS_TABLE_NAME
        )
        print('{} table created'.format(WALLETS_TABLE_NAME))
    except dynamodb_client.exceptions.ResourceInUseException:
        print('{} table already exist'.format(WALLETS_TABLE_NAME))

    sqs = boto3.client('sqs')
    try:
        sqs.get_queue_url(
            QueueName=BLOCKS_QUEUE,
        )
        print('{} SQS queue already exist'.format(BLOCKS_QUEUE))
    except sqs.exceptions.QueueDoesNotExist:
        sqs.create_queue(
            QueueName=BLOCKS_QUEUE,
        )
        print('{} SQS queue created'.format(BLOCKS_QUEUE))

    try:
        sqs.get_queue_url(
            QueueName=WALLETS_QUEUE,
        )
        print('{} SQS queue already exist'.format(WALLETS_QUEUE))
    except sqs.exceptions.QueueDoesNotExist:
        sqs.create_queue(
            QueueName=WALLETS_QUEUE,
        )
        print('{} SQS queue created'.format(WALLETS_QUEUE))

    try:
        sqs.get_queue_url(
            QueueName=TRANSACTIONS_QUEUE,
        )
        print('{} SQS queue already exist'.format(TRANSACTIONS_QUEUE))
    except sqs.exceptions.QueueDoesNotExist:
        sqs.create_queue(
            QueueName=TRANSACTIONS_QUEUE,
        )
        print('{} SQS queue created'.format(TRANSACTIONS_QUEUE))


if __name__ == '__main__':
    setup()

# TokenScan

# About

Tokenscan is serverless tool to save Ethereum ERC20 token transactions and wallet balances to DynamoDB for further data analysis.

## AWS Services
This tool is using:
- SQS
- DynamoDB
- Lambda
- API Gateway

# Installation and Configuration

Before you begin, make sure you are running Python 3.6 and you have a valid AWS account and your [AWS credentials file](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html) is properly installed.

## AWS credentials file
- you need to have [AWS account](https://aws.amazon.com/console/)
- set up [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html) `brew install awscli`
- create [IAM user](https://console.aws.amazon.com/iam/) with `AdministratorAccess` premissions or check [zappa docs](https://github.com/Miserlou/Zappa) which permissions you need.
- `aws configure`

## Installation
- clone repo

```
cd tokenscan
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

*(If you use [pyenv](https://github.com/pyenv/pyenv) and love to manage virtualenvs with pyenv-virtualenv, you just have to call pyenv local [your_venv_name] and it's ready.)*

## Config

You also need to add values to `config.py` or rename `.env.example` to `.env` and add values there
- `ETHERSCAN_API_KEY` **required** (go [here](https://etherscan.io/myapikey) to generate api key)
- `CONTRACT_ADDRESS` **required** (token contract address)
- `START_BLOCK` **required** (ICO start block)

**[Optional]**

- `TRANSACTIONS_TABLE_NAME` (table name for transaction data) *default: TokenTransactions*
- `WALLETS_TABLE_NAME` (table name for wallets data) *default: WalletAddresses*
- `TRANSACTIONS_RCU` (dynamodb read capacity units for transaction table) *default: 5*
- `TRANSACTIONS_WCU` (dynamodb write capacity units for transaction table) *default: 10*
- `WALLETS_RCU` (dynamodb read capacity units for wallet table) *default: 5*
- `WALLETS_WCU` (dynamodb write capacity units for transaction table) *default: 10*
- `NUMBER_OF_LAST_BLOCKS` *live* (number of blocks to check for last 60s)
- `BLOCKS_PROCESSED` *backtrack* (blocks to processed each minute (more you process more you are hitting Etherscan)) *default: 300*
- `TRANSACTIONS_PROCESSED` *backtrack* (transactions processed each minute (more you process more WCU you need for transaction table)) *default: 200*
- `WALLETS_PROCESSED` *backtrack* (wallets for refreshing balances processed each minute (more you process more WCU you need for wallet table)) *default: 300*
- `BLOCKS_QUEUE` *backtrack* (queue name for blocks queue) *default: BlocksToProcessQueue*
- `TRANSACTIONS_QUEUE` *backtrack* (queue name for transaction queue) *default: TransactionsToProcessQueue*
- `WALLETS_QUEUE` *backtrack* (queue name for wallet queue) *default: WalletBalanceToUpdateQueue*



# Initial Deployments

There are 2 different tools. LIVE is to get real-time data of transactions and BACKTRACK is for loading history of transactions.

You should first deploy LIVE and then deploy BACKTRACK so you don't lose any transactions.

First you need to run a script to generate `zappa_settings.json` file and create DynamoDB tables `TokenTransactions` (WCU: 10, RCU:5) and `WalletAddresses` (WCU: 10, RCU:5) and SQS queues `BlocksToProcessQueue`, `BlocksToProcessQueue`, `WalletBalanceToUpdateQueue`.

    $ python setup.py

*Note: If this is your only DynamoDB tables this should be part of a free tier (WCU:25, RCU:25) on AWS and it won't cost you any money. You can also always change your RCU and WCU based on your needs.*

## LIVE
LIVE lambda is to get real-time transaction data to your DynamoDB table. It will set up a job which will check every minute for the last couple of blocks if there were any transaction on this contract address and save transactions and refresh wallet balance of affected wallets to DynamoDB.

To deploy it to AWS all you need to do is run:

    $ zappa deploy live

This will create lambda and all the events you need to have and you are ready to start saving transaction and wallets data to your DynamoDB.

## BACKTRACK
BACKTRACK lambda is used to get all transaction history from `START_BLOCK` till now. This is used if a token already exists and you want to get full transaction and wallet history.


To deploy it to AWS all you need to do is run:

    $ zappa deploy backtrack

When lambda is deployed you need to run:

    $ zappa invoke backtrack "backtrack.tasks.run"

This will start processing all transaction history and it can take a few hours. To know when it is done you can check SQS (Simple Queue Service) and when all queues have 0 that's mean that there are no more transactions to save in DynamoDB.

When all of this is done you can also refresh all balances for wallet addresses, so all wallets have up to date balance

    $ zappa invoke backtrack "backtrack.tasks.refresh_wallets"

You can again check SQS to see when this is done.

When everything is done you don't really need this lambda anymore, since LIVE will update DynamoDB tables every minute if there are any transactions so you can undeploy it.

    $ zappa undeploy backtrack


## Updates

If you changed any config data after you deploy you need to redeploy

    $ zappa update backtrack or zappa update live


## Rollback
You can also `rollback` the deployed code to a previous version by supplying the number of revisions to return to. For instance, to rollback to the version deployed 1 version ago:

    $ zappa rollback live -n 1

For more commands check [zappa docs](https://github.com/Miserlou/Zappa/blob/master/README.md)

# Contributing

All the contributions are welcome! Please open an issue or send us a pull request.

# Changelog

# 0.1
- Init version


find more tools like that on [CoFab](https://cofablab.com/)

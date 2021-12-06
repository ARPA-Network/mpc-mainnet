import boto3
import botocore
import os
from boto3.dynamodb.conditions import Key, Attr
from web3 import Web3, middleware
from web3.gas_strategies.time_based import fast_gas_price_strategy
from web3.auto.infura import w3


ABI = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,' \
      '"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},' \
      '{"name":"value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,' \
      '"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply",' \
      '"outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},' \
      '{"constant":false,"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"value",' \
      '"type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,' \
      '"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"minterAddress",' \
      '"type":"address"}],"name":"removeMinter","outputs":[],"payable":false,"stateMutability":"nonpayable",' \
      '"type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],' \
      '"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"spender",' \
      '"type":"address"},{"name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"name":"",' \
      '"type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{' \
      '"name":"","type":"address"}],"name":"minter","outputs":[{"name":"","type":"bool"}],"payable":false,' \
      '"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"unpause","outputs":[],' \
      '"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"to",' \
      '"type":"address"},{"name":"value","type":"uint256"}],"name":"mint","outputs":[{"name":"","type":"bool"}],' \
      '"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"value",' \
      '"type":"uint256"}],"name":"burn","outputs":[],"payable":false,"stateMutability":"nonpayable",' \
      '"type":"function"},{"constant":true,"inputs":[],"name":"paused","outputs":[{"name":"","type":"bool"}],' \
      '"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"owner",' \
      '"type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,' \
      '"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"renounceOwnership",' \
      '"outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{' \
      '"name":"from","type":"address"},{"name":"value","type":"uint256"}],"name":"burnFrom","outputs":[],' \
      '"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],' \
      '"name":"pause","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},' \
      '{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,' \
      '"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"isOwner","outputs":[{' \
      '"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,' \
      '"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view",' \
      '"type":"function"},{"constant":false,"inputs":[{"name":"minterAddress","type":"address"}],"name":"addMinter",' \
      '"outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{' \
      '"name":"spender","type":"address"},{"name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance",' \
      '"outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},' \
      '{"constant":false,"inputs":[{"name":"to","type":"address"},{"name":"value","type":"uint256"}],' \
      '"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable",' \
      '"type":"function"},{"constant":true,"inputs":[],"name":"initalSupply","outputs":[{"name":"",' \
      '"type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],' \
      '"name":"maxSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view",' \
      '"type":"function"},{"constant":true,"inputs":[{"name":"owner","type":"address"},{"name":"spender",' \
      '"type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,' \
      '"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"newOwner","type":"address"}],' \
      '"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},' \
      '{"inputs":[{"name":"manager","type":"address"}],"payable":false,"stateMutability":"nonpayable",' \
      '"type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"name":"previousOwner","type":"address"},' \
      '{"indexed":true,"name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},' \
      '{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to",' \
      '"type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"},' \
      '{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,' \
      '"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval",' \
      '"type":"event"}]'

eth_node_url = 'http://localhost:8545'
contract_address = Web3.toChecksumAddress('0xba50933c268f567bdc86e1ac131be072c6b0b71a')
contract = w3.eth.contract(contract_address, abi=ABI)
private_key = 'PRIVATE_KEY'
wallet_address = Web3.toChecksumAddress('WALLET_ADDRESS')

# w3 = Web3(Web3.HTTPProvider(eth_node_url))
print("geth node or infura is connected: {}".format(w3.isConnected()))
w3.eth.setGasPriceStrategy(fast_gas_price_strategy)
w3.middleware_onion.add(middleware.time_based_cache_middleware)
w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
w3.middleware_onion.add(middleware.simple_cache_middleware)
dynamodb_resource = boto3.resource('dynamodb', region_name='REGION_NAME')
dynamodb_client = boto3.client('dynamodb', region_name='REGION_NAME')


def lambda_handler(event, context):
    payload = event['Records'][0]['messageAttributes']
    username = payload['username']['stringValue']
    available_amount = int(payload['amount']['stringValue'])
    amount_18_decimal = available_amount*(10**18)
    to_address = getAddress(username)
    withdraw_id = payload['withdrawId']['stringValue']
    print("sending {} arpa tokens to {}, the withdrawId is {}, the username is {}".format(str(available_amount), to_address, withdraw_id, username))
    txn_hash = ''
    response = startWithdraw(withdraw_id, username)
    print(response)
    receipt = ''
    try:
        txn = contract.functions.transfer(
              to_address,
              amount_18_decimal,
        ).buildTransaction({
              'chainId': 1,
              'gas': 3000000,
              'gasPrice': w3.eth.generateGasPrice() * 2,
              'nonce': w3.eth.getTransactionCount(wallet_address, 'pending'),
        })
        print(txn)

        signed_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(Web3.toHex(txn_hash))
        response = updateWithdraw(withdraw_id, username, Web3.toHex(txn_hash))
        print(response)
        receipt = w3.eth.waitForTransactionReceipt(txn_hash, timeout=600)
        if int(receipt['status']) == 1:
            print('SUCCESS for withdraw id: {}, txn hash: {}, username: {}'.format(withdraw_id, Web3.toHex(txn_hash), username))
        else:
            response = failWithdraw(withdraw_id, username)
            print(response)
            print(receipt)
            return 1
    except Exception as e:
        print('withdraw with id: {} failed, username is {}'.format(withdraw_id, username))
        print(e)
        response = failWithdraw(withdraw_id, username)
        print(response)
        return 1
    response = completeWithdraw(withdraw_id, username)
    print(response)
    return 0

def getAddress(username):
    try:
        table = dynamodb_resource.Table('addresses')
        response = table.get_item(Key={'username': username})
    except Exception as e:
        print('getting address failed for username: {}'.format(username))
        print(e)
        raise
    return Web3.toChecksumAddress((response['Item']['address'].lower())) if 'Item' in response else {}
    
def completeWithdraw(withdraw_id, username):
    withdraws_table = dynamodb_resource.Table('withdraws')
    try:
        response = withdraws_table.update_item(
            Key={
                'withdrawId': withdraw_id,
                'username': username,
            },
            UpdateExpression="set completed = :completed",
            ExpressionAttributeValues={
                ':completed': True,
                },
            ReturnValues="UPDATED_NEW"
        )
    except Exception as e:
        print('withdraw with id: {} failed, username is {}'.format(withdraw_id, username))
        print(e)
    return response
    
def startWithdraw(withdraw_id, username):
    withdraws_table = dynamodb_resource.Table('withdraws')
    try:
        response = withdraws_table.update_item(
            Key={
                'withdrawId': withdraw_id,
                'username': username,
            },
            UpdateExpression="set started = :started",
            ExpressionAttributeValues={
                ':started': True,
                },
            ReturnValues="UPDATED_NEW"
        )
    except Exception as e:
        print('starting withdraw with id: {} failed, username is {}'.format(withdraw_id, username))
        print(e)
    return response
    
def failWithdraw(withdraw_id, username):
    withdraws_table = dynamodb_resource.Table('withdraws')
    try:
        response = withdraws_table.update_item(
            Key={
                'withdrawId': withdraw_id,
                'username': username,
            },
            UpdateExpression="set failed = :failed",
            ExpressionAttributeValues={
                ':failed': True,
                },
            ReturnValues="UPDATED_NEW"
        )
    except Exception as e:
        print('failing withdraw with id: {} failed, username is {}'.format(withdraw_id, username))
        print(e)
    return response
    
def updateWithdraw(withdraw_id, username, txn_hash):
    withdraws_table = dynamodb_resource.Table('withdraws')
    try:
        response = withdraws_table.update_item(
            Key={
                'withdrawId': withdraw_id,
                'username': username,
            },
            UpdateExpression="set transactionHash = :txn_hash",
            ExpressionAttributeValues={
                ':txn_hash': txn_hash,
                },
            ReturnValues="UPDATED_NEW"
        )
    except Exception as e:
        print('update with id: {} failed, txn hash is {}, username is {}'.format(withdraw_id, txn_hash, username))
        print(e)
    return response
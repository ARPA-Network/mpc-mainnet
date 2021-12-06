import boto3
import botocore
import time
from datetime import date
import uuid

MIN_STAKING_AMOUNT = 50000
POOL_STAKING_CAP = 3000000

def lambda_handler(event, context):
    print(event)
    if 'username' not in event or 'nodeId' not in event or 'amount' not in event:
        return 'username, nodeId, amount are all required!'
    if int(event['amount']) < MIN_STAKING_AMOUNT:
        return 'staking amount does not meet the minimum requirement!'
    if not event['nodeId'].startswith('MiningPool') and not event['nodeId'].startswith('StarTrek'):
        return 'invalid nodeId!'
        
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    internal_transactions_table = dynamodb.Table('internalTransactions')
    accounts_table = dynamodb.Table('accounts')
    nodes_table = dynamodb.Table('nodes')
    node = {}
    
    try:
        existing_node = nodes_table.get_item(Key={'username': event['nodeId']})
    except Exception as e:
        print(e)
        return 1
    current_node_staking = 0  
    if 'Item' in existing_node:
        node = existing_node['Item']
        current_node_staking = int(node['staking'])
        # if not node['isOn']:
        #     return 'the mining pool is not on!'
        if current_node_staking + int(event['amount']) > POOL_STAKING_CAP:
            return 'your staking will exceed the cap of this mining pool!'
    else:
        return 'the mining pool is not found!'
        
    try:
        existing_account = accounts_table.get_item(Key={'username': event['username']})
    except Exception as e:
        print(e)
        return 1
    current_account_balance = 0
    current_account_total_staking_amount = 0
    if 'Item' in existing_account:
        account = existing_account['Item']
        current_account_balance = int(account['balance'])
        current_account_total_staking_amount = int(account['totalStakingAmount'])
        if current_account_balance < int(event['amount']):
            return 'insufficient fund!'
    else:
        return 'the user has not yet deposited any fund!'
    
    new_id = str(uuid.uuid1())
    transaction = {
        'id': new_id,
        'username': event['username'],
        'nodeId': event['nodeId'],
        'nodeName': node['nodeName'],
        'amount': int(event['amount']),
        'timestamp': str(time.time()),
        'datestamp': str(date.today()),
        'unstakeDateStamp': 'N/A',
        'type': 'STAKE',
        'isWithdrawn': False,
        'isPendingWithdrawl': False
    }
    
    try:
        response = internal_transactions_table.put_item(
            Item=transaction
        )
    except Exception as e:
        print(e)
        return 1
    try:
        response = accounts_table.update_item(
            Key={'username': event['username']},
            UpdateExpression="set balance = :balance, totalStakingAmount = :totalStakingAmount, updatedAt = :updatedAt",
            ExpressionAttributeValues={
                ':balance': current_account_balance - int(event['amount']),
                ':totalStakingAmount': current_account_total_staking_amount + int(event['amount']),
                ':updatedAt': str(time.time()),
            },
            ReturnValues="UPDATED_NEW",
            )
    except Exception as e:
        print(e)
        # rollback:
        response = internal_transactions_table.delete_item(
            Key={'id': event['id']}
            )
        return 1
    try:
        response = nodes_table.update_item(
            Key={'username': event['nodeId']},
            UpdateExpression="set staking = :staking",
            ExpressionAttributeValues={
                ':staking': str(current_node_staking + int(event['amount'])),
            },
            ReturnValues="UPDATED_NEW",
            )
    except Exception as e:
        print(e)
        # rollback:
        response = internal_transactions_table.delete_item(
            Key={'id': event['id']}
            )
        response = accounts_table.update_item(
            Key={'username': event['username']},
            UpdateExpression="set balance = :balance, totalStakingAmount = :totalStakingAmount, updatedAt = :updatedAt",
            ExpressionAttributeValues={
                ':balance': current_account_balance,
                ':totalStakingAmount': current_account_total_staking_amount,
                ':updatedAt': str(time.time()),
            },
            ReturnValues="UPDATED_NEW",
            )
        return 1
    return 0
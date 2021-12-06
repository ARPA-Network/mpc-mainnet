import boto3
import botocore
import time

def lambda_handler(event, context):
    event = event['responsePayload']
    if 'id' not in event or 'actualAmount' not in event:
        return 'id, actualAmount are all required!'
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    external_transactions_table = dynamodb.Table('externalTransactions')
    accounts_table = dynamodb.Table('accounts')
    response = external_transactions_table.get_item(Key={'id': event['id']})
    if 'Item' not in response:
        return 'transaction not found!'
    elif not response['Item']['isPending']:
        return 'the transaction has already been processed!'
    elif response['Item']['isApproved']:
        return 'cannot reject an approved transaction!'
    elif response['Item']['isRejected']:
        return 'the transaction is already rejected!'
    username = response['Item']['username']
    direction = response['Item']['direction']
    try:
        response = external_transactions_table.update_item(
            Key={'id': event['id']},
            UpdateExpression="set actualAmount = :actualAmount, isPending = :isPending, isApproved = :isApproved, transactionHash = :transactionHash",
            ExpressionAttributeValues={
                ':actualAmount': int(event['actualAmount']),
                ':isPending': False,
                ':isApproved': True,
                ':transactionHash': event['transactionHash'] if 'transactionHash' in event else 'N/A'
            },
            ReturnValues="UPDATED_NEW",
        )
    except Exception as e:
        print(e)
        return 1
    try:
        existing_account = accounts_table.get_item(Key={'username': username})
        if 'Item' in existing_account:
            account = existing_account['Item']
            response = accounts_table.update_item(
                Key={'username': username},
                UpdateExpression="set balance = :balance, updatedAt = :updatedAt",
                ExpressionAttributeValues={
                    ':balance': account['balance'] + int(event['actualAmount']) * direction,
                    ':updatedAt': str(time.time()),
                },
                ReturnValues="UPDATED_NEW",
                )
        elif direction == 1:
            response = accounts_table.put_item(
                Item={
                    'username': username,
                    'balance': int(event['actualAmount']),
                    'updatedAt':str(time.time()),
                    'totalStakingAmount': 0,
                    'totalRewardAmount': 0
                }
                )
    except Exception as e:
        print(e)
        # rollback:
        response = external_transactions_table.update_item(
            Key={'id': event['id']},
            UpdateExpression="set actualAmount = :actualAmount, isPending = :isPending, isApproved = :isApproved, transactionHash = :transactionHash",
            ExpressionAttributeValues={
                ':actualAmount': 0,
                ':isPending': True,
                ':isApproved': False,
                ':transactionHash': 'N/A'
            },
            ReturnValues="UPDATED_NEW",
        )
        return 1
    event['username'] = username
    print(event)
    return event
    
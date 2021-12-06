import functools
import boto3
import botocore
import uuid
import time
import random
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

dynamodb_client = boto3.client('dynamodb', region_name='REGION_NAME')
dynamodb_resource = boto3.resource('dynamodb', region_name='REGION_NAME')
sqs = boto3.resource('sqs', region_name='REGION_NAME')
queue = sqs.get_queue_by_name(QueueName='withdraws.fifo')
print(queue.url)

FEE = 200

def lambda_handler(event, context):
    event = event['responsePayload']
    print(event)
    if event['direction'] > 0:
        return "not a withdrawl!"
    withdraw_id = str(event['id'])
    amount = int(event['actualAmount'])
    if amount < 1:
        return {
            "username": event['username'], 
            "amount": 0,
        }
    else:
        withdraw = {
            "withdrawId": withdraw_id,
            "username": event['username'], 
            "amount": amount,
            "fee": FEE,
            "completed": False,
            "started": False,
            "failed": False,
            "transactionHash": 'N/A',
            "timestamp": str(time.time()),
        }
        response = createWithdraw(withdraw)
        print(response)
        response = sendMessage(withdraw_id, event['username'], amount)
        print(response)
        # Testing withdraw message queue
        # response = sendMessage('test_withdrawl', 'test_account', amount + random.randint(1,10000))
        return withdraw
    
def sendMessage(withdraw_id, username, amount):
    try:
        response = queue.send_message(
            MessageBody='boto3', 
            MessageAttributes={
                'withdrawId': {
                    'StringValue': withdraw_id,
                    'DataType': 'String',
                },
                'username': {
                    'StringValue': username,
                    'DataType': 'String',
                },
                'amount': {
                    'StringValue': str(amount),
                    'DataType': 'Number',
                },
            },
            MessageGroupId="withdraw",
            MessageDeduplicationId=withdraw_id,
        )
    except:
        raise
    return response
    
def createWithdraw(withdraw):
    withdraws_table = dynamodb_resource.Table('withdraws')
    try:
        response = withdraws_table.put_item(Item=withdraw)
    except:
        raise
    return response
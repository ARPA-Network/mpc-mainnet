import functools
import boto3
import botocore
import uuid
import time
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

dynamodb_client = boto3.client('dynamodb', region_name='REGION_NAME')
dynamodb_resource = boto3.resource('dynamodb', region_name='REGION_NAME')
sqs = boto3.resource('sqs', region_name='REGION_NAME')
queue = sqs.get_queue_by_name(QueueName='withdraws.fifo')
print(queue.url)
fee = 200
withdraw_limit = 50

def lambda_handler(event, context):
    withdraw_id = str(uuid.uuid1())
    available_rewards = getAllAvailableRewards(event['username'])
    if len(available_rewards) < 1:
        return {
            "username": event['username'], 
            "amount": 0,
        }
    else:
        total_available_reward_amount = calculateTotalAmount(available_rewards)
        withdraw = {
            "withdrawId": withdraw_id,
            "username": event['username'], 
            "amount": total_available_reward_amount,
            "fee": fee,
            "completed": False,
            "started": False,
            "failed": False,
            "transactionHash": 'N/A',
            "timestamp": str(time.time()),
        }
        if total_available_reward_amount >= withdraw_limit:
            response = markWithdrawn(withdraw_id, available_rewards)
            print(response)
            response = createWithdraw(withdraw)
            print(response)
            response = sendMessage(withdraw_id, event['username'], total_available_reward_amount)
            print(response)
        return withdraw
    
def getAllAvailableRewards(username):
    available_rewards = []
    filter_expression = Attr('isWithdrawn').eq(False)
    try:
        rewards_table = dynamodb_resource.Table('rewards')
        response = rewards_table.query(
            IndexName='username-index',
            KeyConditionExpression=Key('username').eq(username),
            FilterExpression=filter_expression
            )
        available_rewards = response['Items']
        
        while response.get('LastEvaluatedKey'):
            response = rewards_table.query(
                IndexName='username-index',
                ExclusiveStartKey=response['LastEvaluatedKey'],
                KeyConditionExpression=Key('username').eq(username),
                FilterExpression=filter_expression
                )
            available_rewards.extend(response['Items'])
    except:
        raise
    return available_rewards
    
def calculateTotalAmount(rewards):
    if len(rewards) < 1:
        return 0
    elif len(rewards) == 1:
        return rewards[0]['amount']
    else:    
        return functools.reduce(lambda a,b : a + b, [reward['amount'] for reward in rewards])

def markWithdrawn(withdraw_id, available_rewards):
    rewards_table = dynamodb_resource.Table('rewards')
    try:
        for reward in available_rewards:
            response = rewards_table.update_item(
                Key={
                    'taskId': reward['taskId'], 
                    'username': reward['username']
                },
                UpdateExpression="set isWithdrawn = :is_withdrawn, withdrawId = :withdraw_id",
                ExpressionAttributeValues={
                    ':is_withdrawn': True,
                    ':withdraw_id': withdraw_id,
                    },
                ReturnValues="UPDATED_NEW"
            )
    except ClientError as e:
        raise
    return response

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
                    'StringValue': str(amount - fee),
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
import boto3
import botocore
from boto3.dynamodb.conditions import Key, Attr
import time

reward_amount = 15

def lambda_handler(event, context):
    try:
        dynamodb = boto3.client('dynamodb', region_name='REGION_NAME')
        paginator = dynamodb.get_paginator('scan')
        all_tasks = []
        for page in paginator.paginate(TableName='tasks'):
            tasks = page['Items']
            all_tasks.extend(tasks)
        for task in all_tasks:
            taskId = task['taskId']['S']
            statuses = task['statuses']['L']
            numPlayers = task['numPlayers']['N']
            if int(numPlayers) == len(statuses):
                for status in statuses:
                    if not status['M']['isSuccessful']['BOOL']:
                        print("incomplete task found")
                        break
                    else:
                        username = status['M']['username']['S']
                        if rewardExists(taskId, username) is False:
                            db_source = boto3.resource('dynamodb', region_name='REGION_NAME')
                            rewards_table = db_source.Table('rewards')
                            new_reward = {
                                        'taskId': taskId,
                                        'username': username,
                                        'amount': reward_amount,
                                        'timestamp': str(time.time()),
                                        'isWithdrawn': False
                                    }
                            try:
                                response = rewards_table.put_item(
                                    Item=new_reward
                                    )
                                print(new_reward)
                            except botocore.exceptions.ClientError as e:
                                raise
                        
    except:
        raise
    return 0

def rewardExists(taskId, username):
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    table = dynamodb.Table('rewards')
    try:
        response = table.get_item(Key={'taskId': taskId, 'username': username})
        if 'Item' in response:
            item = response['Item']
            return True
    except:
        raise
    return False
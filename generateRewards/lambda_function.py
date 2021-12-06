import boto3
import botocore
import time

reward_amount = 15

def lambda_handler(event, context):
    payload = event['responsePayload']
    taskId = payload['taskId']
    username = payload['username']
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    tasks_table = dynamodb.Table('tasks')
    response = tasks_table.get_item(Key={'taskId': taskId})
    rewards = []
    if 'Item' in response:
        task = response['Item']
        print(task)
        statuses = task['statuses']
        if task['numPlayers'] != len(statuses):
            print("some players failed to report their statuses")
            return 1
        else:
            for status in statuses:
                if not status['isSuccessful']:
                    print("some players failed their mpc task")
                    return 1
            rewards_table = dynamodb.Table('rewards')
            for status in statuses:
                try:
                    reward = {
                            'taskId': taskId,
                            'username': status['username'],
                            'amount': reward_amount,
                            'timestamp': str(time.time()),
                            'isWithdrawn': False
                        }
                    response = rewards_table.put_item(
                        Item=reward
                        )
                    rewards.append(reward)
                except botocore.exceptions.ClientError as e:
                    return 1
    return rewards
import boto3
import botocore
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    table = dynamodb.Table('tasks')
    try:
        response = table.update_item(
            Key={
                'taskId': event['taskId']
            },
            UpdateExpression="set statuses = list_append(statuses, :status)",
            ExpressionAttributeValues={
                ':status': [{
                        'username': event['username'],
                        'playerId': event['playerId'],
                        'isSuccessful': event['isSuccessful']
                    }]
                },
            ReturnValues="UPDATED_NEW"
        )
        print(response)
    except Exception as e:
        print(e)
    finally:    
        return {'taskId': event['taskId'], 'username': event['username']}
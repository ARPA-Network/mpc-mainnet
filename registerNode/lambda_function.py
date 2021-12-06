import boto3
import botocore

def lambda_handler(event, context):
    client = boto3.client('dynamodb', region_name='REGION_NAME')
    put_new_node = {
        'Put': {
            'TableName': 'nodes',
            'ConditionExpression': 'attribute_not_exists(username)',
            'Item': {
                'username': {'S': event['username']},
                'nodeName': {'S': event['nodeName']},
                'staking': {'S': str(event['staking'])},
                'txHash': {'S': event['txHash']},
                'isOn': {'BOOL': False},
                'isBusy': {'BOOL': False}
            }
        }
    }
    try:
        response = client.transact_write_items(
                TransactItems=[put_new_node]
            )
    except botocore.exceptions.ClientError as e:
        print(e)
        if 'ConditionalCheckFailed' in e.response['Error']['Message']:
            return 1
        else:
            raise
    return 0
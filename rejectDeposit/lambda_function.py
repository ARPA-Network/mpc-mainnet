import boto3
import botocore
import time

def lambda_handler(event, context):
    if 'id' not in event:
        return 'id is required!'
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    external_transactions_table = dynamodb.Table('externalTransactions')
    response = external_transactions_table.get_item(Key={'id': event['id']})
    if 'Item' not in response:
        return 'deposit not found!'
    elif not response['Item']['isPending']:
        return 'the deposit has already been processed'
    elif response['Item']['isApproved']:
        return 'cannot reject an approved deposit'
    elif response['Item']['isRejected']:
        return 'the deposit is already rejected'
    else:
        try:
            response = external_transactions_table.update_item(
                Key={'id': event['id']},
                UpdateExpression="set isPending = :isPending, isRejected = :isRejected",
                ExpressionAttributeValues={
                    ':isPending': False,
                    ':isRejected': True,
                },
                ReturnValues="UPDATED_NEW",
            )
        except Exception as e:
            print(e)
            return 1
    return 0
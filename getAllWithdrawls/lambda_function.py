import boto3
import botocore
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    external_transactions_table = dynamodb.Table('externalTransactions')
    response = external_transactions_table.scan()
    all_transactions = response['Items']
    while response.get('LastEvaluatedKey'):
        response = external_transactions_table.scan(
            ExclusiveStartKey=response['LastEvaluatedKey'],
            )
        all_transactions.extend(response['Items'])
    return list(filter(lambda transaction: (transaction['direction'] == -1 and transaction['isApproved'] == False and transaction['isPending'] == True and transaction['isRejected'] == False), all_transactions))
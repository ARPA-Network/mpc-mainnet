import boto3
import botocore
from boto3.dynamodb.conditions import Key

TYPE_POOL = 'POOL'
TYPE_MPC = 'MPC'
TYPE_NONE = 'NONE'

def lambda_handler(event, context):
    result = {}
    result['applications'] = []
    print(event)
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    applications_table = dynamodb.Table('applications')
    pool_applications_table = dynamodb.Table('poolApplications')
    response = applications_table.get_item(Key={'username': event['username']})
    if 'Item' in response:
        # result['type'] = TYPE_MPC
        # result['applications'].append(response['Item'])
        # return result
        return response['Item']
    else:
        filter_exp = Key('username').eq(event['username'])
        response = pool_applications_table.query(KeyConditionExpression=filter_exp)
        print(response)
        if len(response['Items']) > 0:
            result['type'] = TYPE_POOL
            result['applications'] += response['Items']
            return result
        else:
            result['type'] = TYPE_NONE
            return result
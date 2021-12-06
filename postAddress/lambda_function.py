import boto3
import botocore

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    addresses_table = dynamodb.Table('addresses')
    if 'address' not in event:
        return 1
    try:
        response = addresses_table.put_item(Item=event)
        print(response)
    except:
        return 1
    print('insert new address completed')
    return 0
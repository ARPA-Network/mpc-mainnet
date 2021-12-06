import boto3
import botocore
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    nodes_table = dynamodb.Table('nodes')
    nodes_response = nodes_table.scan()
    all_nodes = nodes_response['Items']
    while nodes_response.get('LastEvaluatedKey'):
        nodes_response = nodes_table.scan(
            ExclusiveStartKey=nodes_response['LastEvaluatedKey'],
            )
        all_nodes.extend(nodes_response['Items'])
    return list(filter(lambda node: node['username'].startswith('MiningPool_'), all_nodes)) + list(filter(lambda node: node['username'].startswith('StarTrek'), all_nodes)) 
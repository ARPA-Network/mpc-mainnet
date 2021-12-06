import boto3
import botocore
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    
    nodes_table = dynamodb.Table('nodes')
    response = nodes_table.scan(
        FilterExpression=Attr('isOn').eq(True)
        )
    nodes = response['Items']
    while response.get('LastEvaluatedKey'):
        response = nodes_table.scan(
            ExclusiveStartKey=response['LastEvaluatedKey']
            )
        nodes.extend(response['Items'])
        
    node_staking_map = {node['username']: 0 for node in nodes}
    
    internal_transactions_table = dynamodb.Table('internalTransactions')
    response = internal_transactions_table.scan(
        FilterExpression=Attr('type').eq('STAKE') &  Attr('isWithdrawn').eq(False)
        )
    stakings = response['Items']
    while response.get('LastEvaluatedKey'):
        response = internal_transactions_table.scan(
            ExclusiveStartKey=response['LastEvaluatedKey']
            )
        stakings.extend(response['Items'])
    
    for staking in stakings:
        node_staking_map[staking['nodeId']] += staking['amount']
    for node_id in node_staking_map:
        try:
            response = nodes_table.update_item(
                Key={
                    'username': node_id
                },
                UpdateExpression="set staking = :string",
                ExpressionAttributeValues={
                    ':string': str(node_staking_map[node_id]),
                    },
                ReturnValues="UPDATED_NEW"
            )
        except Exception as e:
            print(e)
            raise
    return stakings, nodes, node_staking_map
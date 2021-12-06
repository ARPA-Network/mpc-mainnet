import boto3
import botocore
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    nodes_table = dynamodb.Table('nodes')
    rewards_table = dynamodb.Table('rewards')

    nodes_response = nodes_table.scan()
    all_nodes = nodes_response['Items']
    while nodes_response.get('LastEvaluatedKey'):
        nodes_response = nodes_table.scan(
            ExclusiveStartKey=nodes_response['LastEvaluatedKey'],
            )
        all_nodes.extend(nodes_response['Items'])
    print(len(all_nodes), ' number of nodes in total')
    
    for node in all_nodes:
        if node['username'].startswith('MiningPool_'):
            all_rewards = []
            rewards_response = rewards_table.query(
                IndexName='username-index',
                KeyConditionExpression=Key('username').eq(node['username'])
            )
            rewards = rewards_response['Items']
            while rewards_response.get('LastEvaluatedKey'):
                rewards_response = rewards_table.query(
                    IndexName='username-index',
                    ExclusiveStartKey=rewards_response.get('LastEvaluatedKey'),
                    KeyConditionExpression=Key('username').eq(node['username'])
                    )
                rewards.extend(rewards_response['Items'])
            all_rewards.extend(rewards)
            # may = [ i for i in all_rewards if float(i['timestamp']) >= 1588291200.0]
            print(node['username'], ',', node['staking'], ',', len(all_rewards)*15)
    # scanned_rewards_response = rewards_table.scan()
    # scanned_rewards = scanned_rewards_response['Items']
    # while scanned_rewards_response.get('LastEvaluatedKey'):
    #     scanned_rewards_response = rewards_table.scan(
    #         ExclusiveStartKey=scanned_rewards_response.get('LastEvaluatedKey')
    #         )
    #     scanned_rewards.extend(scanned_rewards_response['Items'])
    # print(len(scanned_rewards))
    # unmatched_count = 0
    # all_rewards_dict = {}
    # for reward in all_rewards:
    #     key = reward['username'] + reward['taskId']
    #     all_rewards_dict[key] = 'dummy'
    # for scanned_reward in scanned_rewards:
    #     key = scanned_reward['username'] + scanned_reward['taskId']
    #     if key not in all_rewards_dict:
    #         unmatched_count += 1
    # return unmatched_count + len(all_rewards) == len(scanned_rewards)
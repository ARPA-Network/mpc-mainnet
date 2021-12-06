import boto3
from boto3.dynamodb.conditions import Key, Attr
import random
from numpy.random import choice

def lambda_handler(event, context):
    print(event)
    try:
        dynamodb = boto3.client('dynamodb', region_name='REGION_NAME')
        paginator = dynamodb.get_paginator('scan')
        all_nodes = []
        for page in paginator.paginate(TableName='nodes'):
            nodes = page['Items']
            all_nodes.extend(nodes)
        selected_nodes = select_n_nodes(all_nodes, event['numNodes'])
    except:
        raise

    nodes = assign_player([{'username': node['username']["S"]} for node in selected_nodes])
    return {
            'numNodes': event['numNodes'],
            'programId': event['programId'],
            'nodes': nodes
        }
        
def select_n_nodes_random(all_nodes, n):
    free_on_nodes = list(filter(lambda node: node['isOn']['BOOL'] and not node['isBusy']['BOOL'], all_nodes))
    return random.sample(free_on_nodes, n)
    
def select_n_nodes(all_nodes, n):
    alpha = 1.359141
    free_on_nodes = list(filter(lambda node: node['isOn']['BOOL'] and not node['isBusy']['BOOL'], all_nodes))
    print(free_on_nodes)
    stakings = [float(node['staking']['S']) for node in free_on_nodes]
    tickets = [staking**alpha for staking in stakings]
    sum_tickets = sum(tickets)
    probability_distribution = [ticket/sum_tickets for ticket in tickets]
    selected_nodes = choice(free_on_nodes, n, p=probability_distribution, replace=False)
    return selected_nodes
    
def assign_player(nodes):
    for index, node in enumerate(nodes):
        node['playerId'] = 'Player{}'.format(str(index+1))
    return nodes
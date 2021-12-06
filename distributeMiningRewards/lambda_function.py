import boto3
import botocore
from boto3.dynamodb.conditions import Key, Attr
import math, time
from decimal import Decimal

def lambda_handler(event, context):
    payload = event['responsePayload']
    if isinstance(payload, int) or not isinstance(payload, list):
        return 1
    for r in payload:
        if r['username'].startswith('MiningPool_') or r['username'].startswith('StarTrek'):
            dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
            internal_stakes_table = dynamodb.Table('internalTransactions')
            rewards_table = dynamodb.Table('miningRewards')
            accounts_table = dynamodb.Table('accounts')
            stakes_response = internal_stakes_table.query(
                IndexName='type-nodeId-index',
                KeyConditionExpression=Key('type').eq('STAKE') & Key('nodeId').eq(r['username'])
            )
            stakes = stakes_response['Items']
            while stakes_response.get('LastEvaluatedKey'):
                stakes_response = internal_stakes_table.query(
                    IndexName='type-nodeId-index',
                    ExclusiveStartKey=stakes_response.get('LastEvaluatedKey'),
                    KeyConditionExpression=Key('type').eq('STAKE') & Key('nodeId').eq(r['username']),
                    ConditionExpression='NOT isWithdrawn' # AND NOT isPendingWithdrawl
                    )
                stakes.extend(stakes_response['Items'])
            user_stake_map = {}
            total_staking_amount = 0
            for stake in stakes:
                if not stake['isWithdrawn']: # and not stake['isPendingWithdrawl']:
                    if stake['username'] in user_stake_map:
                        user_stake_map[stake['username']] += stake['amount']
                    else:
                        user_stake_map[stake['username']] = stake['amount']
                    total_staking_amount += stake['amount']
            print(total_staking_amount)
            for user in user_stake_map:
                amount = round_down(r['amount'] * user_stake_map[user] / total_staking_amount, 5)
                now = time.time()
                reward = {
                    'taskId': r['taskId']+'_'+r['username'],
                    'username': user,
                    'amount': amount,
                    'timestamp': str(now)
                }
                try:
                    print(reward)
                    response = rewards_table.put_item(
                        Item=reward,
                        ConditionExpression='attribute_not_exists(username) AND attribute_not_exists(taskId)'
                        )
                except Exception as e:
                    print(e)
                    continue
                response = accounts_table.update_item(
                    Key={'username': user},
                    UpdateExpression="set totalRewardAmount = if_not_exists(totalRewardAmount, :start) + :increment, balance = if_not_exists(balance, :start) + :increment, updatedAt = :updatedAt",
                    ExpressionAttributeValues={
                        ':start': 0,
                        ':increment': amount,
                        ':updatedAt': str(time.time()),
                    },
                    ReturnValues="UPDATED_NEW",
                )
    return 0

def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return Decimal(str(math.floor(n * multiplier) / multiplier))
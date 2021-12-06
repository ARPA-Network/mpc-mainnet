import boto3
import botocore

def lambda_handler(event, context):
    client = boto3.client('dynamodb', region_name='REGION_NAME')
    put_new_player = {
        'Put': {
            'TableName': 'players',
            'ConditionExpression': 'attribute_not_exists(playerId)',
            'Item': {
                'playerId': {'S': event['playerId']},
                'ip': {'S': event['ip']},
                'commonName': {'S': event['commonName']},
                'agentPort': {'N': str(event['agentPort'])},
                'mpcPort': {'N': str(event['mpcPort'])},
                'wssPort': {'N': str(event['wssPort'])},
                'isBusy': {'BOOL': False},
                'staking': {'N': '0'}
            }
        }
    }
    # put_new_status = {
    #     'Put': {
    #         'TableName': 'player_statuses',
    #         'ConditionExpression': 'attribute_not_exists(playerId)',
    #         'Item': {
    #             'playerId': {'S': event['playerId']},
    #             'isBusy': {'BOOL': False}
    #         }
    #     }
    # }
    # put_new_staking = {
    #     'Put': {
    #         'TableName': 'player_stakings',
    #         'ConditionExpression': 'attribute_not_exists(playerId)',
    #         'Item': {
    #             'playerId': {'S': event['playerId']},
    #             'staking': {'N': '0'}
    #         }
    #     }
    # }
    try:
        response = client.transact_write_items(
                TransactItems=[
                    put_new_player
                    # put_new_status,
                    # put_new_staking
                    ]
            )
    except botocore.exceptions.ClientError as e:
        if 'ConditionalCheckFailed' in e.response['Error']['Message']:
            return 1
        else:
            raise
    return 0
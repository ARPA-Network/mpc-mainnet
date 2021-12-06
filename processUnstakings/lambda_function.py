import boto3
import botocore
from boto3.dynamodb.conditions import Key, Attr
import datetime
import time

date_format = '%Y-%m-%d'
date_now = datetime.datetime.now().date()

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    internal_transactions_table = dynamodb.Table('internalTransactions')
    response = internal_transactions_table.scan(
        FilterExpression=Attr('type').eq('STAKE') & Attr('isPendingWithdrawl').eq(True) & Attr('isWithdrawn').eq(False)
        )
    unprocessed_unstakings = response['Items']
    while response.get('LastEvaluatedKey'):
        response = internal_transactions_table.scan(
            ExclusiveStartKey=response['LastEvaluatedKey']
            )
        unprocessed_unstakings.extend(response['Items'])
    # unstakings_to_process = []
    # for unstaking in unprocessed_unstakings:
    #     unstake_date = datetime.datetime.strptime(unstaking['unstakeDateStamp'], date_format).date()
    #     delta = date_now - unstake_date
    #     if delta.days >= 1:
    #         unstakings_to_process.append(unstaking)
    print(unprocessed_unstakings)
    for unstaking in unprocessed_unstakings:
        try:
            print('updating...')
            response = internal_transactions_table.update_item(
                Key={'id': str(unstaking['id'])},
                UpdateExpression="set isPendingWithdrawl = :isPendingWithdrawl, isWithdrawn = :isWithdrawn",
                ExpressionAttributeValues={
                    ':isPendingWithdrawl': False,
                    ':isWithdrawn': True
                },
                ReturnValues="UPDATED_NEW",
                )
        except Exception as e:
            print(e)
            return 1
        try:
            accounts_table = dynamodb.Table('accounts')
            existing_account = accounts_table.get_item(Key={'username': unstaking['username']})
            if 'Item' in existing_account:
                account = existing_account['Item']
                print('username: ', unstaking['username'])
                print('staked at: ', unstaking['nodeId'])
                print('unstaked amount: ', unstaking['amount'])
                print('before balance: ', account['balance'])
                print('after balance: ', account['balance'] + unstaking['amount'])
                print('before total staking amount: ', account['totalStakingAmount'])
                print('after total staking amount: ', account['totalStakingAmount'] - unstaking['amount'])
                response = accounts_table.update_item(
                    Key={'username': unstaking['username']},
                    UpdateExpression="set balance = :balance, totalStakingAmount = :totalStakingAmount, updatedAt = :updatedAt",
                    ExpressionAttributeValues={
                        ':balance': account['balance'] + unstaking['amount'],
                        ':totalStakingAmount': account['totalStakingAmount'] - unstaking['amount'],
                        ':updatedAt': str(time.time()),
                    },
                    ReturnValues="UPDATED_NEW",
                    )
                print(response)
        except Exception as e:
            print(e)
    return 0
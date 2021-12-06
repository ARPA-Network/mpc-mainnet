import boto3
import paramiko
import re
import uuid


def lambda_handler(event, context):
    ec2_username='ubuntu'
    local_private_key = 'PATH_TO_PRIVATE_KEY'
    s3_client = boto3.client('s3')
    s3_client.download_file('mpc-ssh-keys', 'PRIVATE_KEY.pem', local_private_key)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    table = dynamodb.Table('players')
    
    payload = event['responsePayload']
    nodes = payload['nodes']
    payload['taskId'] = str(uuid.uuid1())
    for node in nodes:
        print(node)
        cmd = (
            "cd"
            " && source ~/mainnet-mpc_agent/venv/bin/activate"
            " && cd ~/scale"
            )
        response = table.get_item(Key={'playerId': node['playerId']})
        player = response['Item']
        hostname = player['ip']
        player_number = re.match('.*?([0-9]+)$', player['playerId']).group(1)
        player_index = int(player_number) - 1
        print('connecting to {}: {}'.format(player['playerId'], hostname))
        cmd = cmd + " && python3 ./executor.py " + node['username'] + ' ' + str(player_index) + ' ' + payload['taskId']
        cmd = cmd + " 2>&1 | tee ~/{}.log > /dev/null 2>&1 &".format(player['playerId'])
        print(cmd)
        ssh_client.connect(hostname=hostname, username=ec2_username, key_filename=local_private_key)
        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        print(stdout)
    return payload
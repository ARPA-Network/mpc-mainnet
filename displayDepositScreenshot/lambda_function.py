import json
import base64
import boto3

BUCKET_NAME = 'deposit-screenshots'

def lambda_handler(event, context):
    if 'id' not in event:
        return 'id is required!'
    s3 = boto3.client('s3')
    presigned_url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': event['id']
        }
    )
    return presigned_url
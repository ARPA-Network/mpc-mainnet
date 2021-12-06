def lambda_handler(event, context):
    username_mapping = {

    }
    if event['username'] in username_mapping:
        return username_mapping[event['username']]
    else:
        return ''
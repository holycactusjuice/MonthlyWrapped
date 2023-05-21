from update import update_db
import json


def lambda_handler(event, context):

    update_db()

    return {
        'statusCode': 200,
        'body': json.dumps("Hello from Lambda")
    }

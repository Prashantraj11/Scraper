import json
import boto3

def lambda_handler(event, context):
    # TODO implement
    client = boto3.client('stepfunctions') 
    state_machine_arn = 'arn:aws:states:ap-south-1:137068270532:stateMachine:MyStateMachine-t75g9b6k2'

    url = event['queryStringParameters']['page']

    response = client.start_execution( 
        stateMachineArn=state_machine_arn, 
        input=json.dumps({'page': url})
    )

    execution_arn = response['executionArn']

    return { 
        'statusCode': 200, 
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        'body': json.dumps({ 
            'executionArn': execution_arn, 
            'status': 'The pipeline is executing. Typically, it should take around 2 minutes. Check back for the response afterwards.', 
            'url': f'https://o2crc9xy03.execute-api.ap-south-1.amazonaws.com/dev/api/reviews?executionArn={execution_arn}' 
        }) 
    }

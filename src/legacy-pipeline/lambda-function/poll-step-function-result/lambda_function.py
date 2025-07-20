import json
import boto3

def lambda_handler(event, context):
    client = boto3.client('stepfunctions')
    execution_arn = event['queryStringParameters']['executionArn']
    
    response = client.describe_execution(
        executionArn=execution_arn
    )
    
    status = response['status']
    if status == 'SUCCEEDED':
        output = json.loads(response['output'])
        return {
            'statusCode': 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            'body': json.dumps({
                'statusCode': output['statusCode'],
                'reviews_count': output['reviews_count'],
                'reviews': output['reviews']
            })
        }
    elif status == 'FAILED':
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Step Function execution failed'})
        }
    else:
        return {
            'statusCode': 202,
            'body': json.dumps({'status': status})
        }

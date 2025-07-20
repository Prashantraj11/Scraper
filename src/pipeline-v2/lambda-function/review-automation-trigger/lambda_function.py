import json
import boto3
import uuid
import time

def lambda_handler(event, context):
    # Extract URL from the event
    url = event['queryStringParameters']['page']

    # return {
    #     'statusCode': 200,
    #     'headers': {'Content-Type': 'application/json'},
    #     'body': json.dumps(url)
    # }
    
    # Initialize SSM client
    ssm = boto3.client('ssm', region_name='ap-south-1')
    unique_id = str(uuid.uuid4())

    # Send command to EC2 instance
    response = ssm.send_command(
        InstanceIds=['i-07b0999d978efd1fb'],
        DocumentName='AWS-RunPowerShellScript',
        Parameters={
            'commands': [f'C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python311\\python.exe C:\\final-automation.py "{url}" "{unique_id}"']
        }
    )

    command_id = response['Command']['CommandId']
    
    # Wait for the command to complete
    while True:
        try:
            invocation_response = ssm.get_command_invocation(
                CommandId=command_id,
                InstanceId='i-07b0999d978efd1fb'
            )
            
            status = invocation_response['Status']
            
            if status in ['Success', 'Failed', 'Cancelled', 'TimedOut']:
                print(f"Command finished with status: {status}")
                break
            
            print(f"Current status: {status}. Waiting for completion...")
            time.sleep(8)
        
        except ssm.exceptions.InvocationDoesNotExist:
            print("Invocation does not exist yet. Retrying...")
            time.sleep(2)

    # Initialize S3 client
    s3_client = boto3.client('s3')
    
    # Fetch data from S3 bucket
    bucket_name = 'extracted-reviews'
    file_name = f'{unique_id}.json'
    
    try:
        s3_response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
        file_data = s3_response['Body'].read().decode('utf-8')
        json_data = json.loads(file_data)  # Assuming the content is JSON

        return {
            'statusCode': 200,
            "headers": {
                'Content-Type': 'application/json',
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            'body': json.dumps(json_data)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            "headers": {
                'Content-Type': 'application/json',
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            'body': json.dumps({'error': str(e)})
        }

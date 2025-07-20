import boto3
import time
import uuid

def lambda_handler(event, context):
    ssm = boto3.client('ssm', region_name='ap-south-1')
    
    url = event.get('url')
    review_paginate_next = event.get('reviewPaginateNext')
    review_author = event.get('reviewAuthor')
    review_title = event.get('reviewTitle')
    review_text = event.get('reviewText')
    review_rating = event.get('reviewRating')
    
    unique_id = str(uuid.uuid4())
    
    response = ssm.send_command(
        InstanceIds=['i-07b0999d978efd1fb'],
        DocumentName='AWS-RunPowerShellScript',
        Parameters={
            'commands': [f'C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python311\\python.exe C:\\automation.py "{url}" "{unique_id}"']
            # 'commands': [f'C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python311\\python.exe C:\\install.py']
        }
    )
    
    command_id = response['Command']['CommandId']
    
    time.sleep(12)
    
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
            time.sleep(10)
        except ssm.exceptions.InvocationDoesNotExist:
            print("Invocation does not exist yet. Retrying...")
            time.sleep(2)  

    return {
        'CommandId': command_id,
        'Status': status,
        'Output': invocation_response['StandardOutputContent'],
        'Error': invocation_response['StandardErrorContent'],
        'uuid': unique_id,
        'reviewPaginateNext': review_paginate_next,
        'reviewAuthor': review_author,
        'reviewTitle': review_title,
        'reviewBody': review_text,
        "rating": review_rating
    }

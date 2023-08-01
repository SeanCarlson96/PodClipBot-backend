import boto3
import json

client = boto3.client('stepfunctions')

def start_step_function(state_machine_arn: str, input_data: dict) -> str:
    response = client.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps(input_data)
    )
    
    return response['executionArn']

def check_step_function_state(state_machine_arn, execution_arn):
    try:
        response = client.describe_execution(
            stateMachineArn=state_machine_arn,
            executionArn=execution_arn
        )
        state = response['status']
        return state
    except Exception as e:
        print(f"Error checking state: {str(e)}")
        return None

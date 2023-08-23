import boto3
import json

def lambda_handler(event, context):
    # Get the Fargate task definition and cluster ARNs
    task_definition = "arn:aws:ecs:us-east-2:328963664440:task-definition/pcb-clipper-task:1"
    cluster = "pod-clip-bot"
    
    network_configuration = {
        'awsvpcConfiguration': {
            'subnets': ['subnet-069406d49d20ada2d', 'subnet-0a3e1c8b4a8211295', 'subnet-06bc6bcad7ab96630'],
            'securityGroups': ['sg-068860ee559772acd'],
            'assignPublicIp': 'ENABLED'
        }
    }

    # Create an ECS client
    ecs_client = boto3.client('ecs')
    
    response = "error"
    for record in event["Records"]:
        # Define the container overrides
        container_overrides = [
            {
                'name': 'pcb-clipper',
                'environment': [
                    {
                        'name': 'INPUT_PAYLOAD',
                        'value': json.dumps(record["body"])
                    }
                ]
            }
        ]
        
        # Start the Fargate task
        response = ecs_client.run_task(
            cluster=cluster,
            taskDefinition=task_definition,
            overrides={'containerOverrides': container_overrides},
            launchType='FARGATE',
            networkConfiguration=network_configuration
        )
        print(response)
    
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

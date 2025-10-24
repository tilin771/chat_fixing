from data.connections import bedrock_agent_client, AGENT_ALIAS_ARN_ROBOT, AGENT_ARN_ROBOT

def run_robot(prompt, session_id):
    response_stream = bedrock_agent_client.invoke_agent(
        agentId=AGENT_ARN_ROBOT.split("/")[-1],
        agentAliasId=AGENT_ALIAS_ARN_ROBOT.split("/")[-1],
        sessionId=session_id,
        inputText=prompt,
        streamingConfigurations={
            'streamFinalResponse': True,
            'applyGuardrailInterval': 123
        }
    )

    for event in response_stream['completion']:
        if 'chunk' in event:
            yield event['chunk']['bytes'].decode('utf-8')
        elif 'internalServerException' in event:
            raise Exception("Internal error: " + event['internalServerException']['message'])
        elif 'throttlingException' in event:
            raise Exception("Throttled: " + event['throttlingException']['message'])
        elif 'validationException' in event:
            raise Exception("Validation error: " + event['validationException']['message'])

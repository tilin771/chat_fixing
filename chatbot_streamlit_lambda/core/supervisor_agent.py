from data.connections import bedrock_agent_client, AGENT_ALIAS_ARN, AGENT_ARN


def run_supervisor(prompt, session_id):
    response_stream = bedrock_agent_client.invoke_agent(
        agentId=AGENT_ARN.split("/")[-1],
        agentAliasId=AGENT_ALIAS_ARN.split("/")[-1],
        sessionId=session_id,
        inputText=prompt
    )
    
    # Procesar el EventStream
    final_response = ""
    for event in response_stream['completion']:
        if 'chunk' in event:
            data = event['chunk']['bytes']
            text_piece = data.decode('utf-8')
            final_response += text_piece
    print(final_response)
    return final_response


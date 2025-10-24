import os
import boto3


KB_ID = "XXZNYWBVII"
MODEL_ARN = "us.amazon.nova-pro-v1:0"
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

# Crear sesión usando variables de entorno AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY
session = boto3.Session(region_name=REGION)

bedrock_agent_client = session.client("bedrock-agent-runtime")

AGENT_ARN = "arn:aws:bedrock:us-east-1:699541216231:agent/UT8RWCB5UB"
AGENT_ALIAS_ARN = "arn:aws:bedrock:us-east-1:699541216231:agent-alias/TVC2F3RTGE"

AGENT_ARN_TICKET = "arn:aws:bedrock:us-east-1:699541216231:agent/IV0UXLYYQZ"
AGENT_ALIAS_ARN_TICKET = "arn:aws:bedrock:us-east-1:699541216231:agent-alias/L1DFRWB9AN"

AGENT_ARN_ROBOT = "arn:aws:bedrock:us-east-1:699541216231:agent/3XOGAAC9MU"
AGENT_ALIAS_ARN_ROBOT = "arn:aws:bedrock:us-east-1:699541216231:agent-alias/S1O2VUKYEM"


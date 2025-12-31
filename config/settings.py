import os
from dotenv import load_dotenv
load_dotenv()

# Graph API Configuration
CLIENT_ID = os.getenv("GRAPH_CLIENT_ID")
CLIENT_SECRET = os.getenv("GRAPH_CLIENT_SECRET")
TENANT_ID = os.getenv("GRAPH_TENANT_ID")
GRAPH_API_ENDPOINT = os.getenv("GRAPH_API_ENDPOINT", "https://graph.microsoft.com/v1.0")

# Main Database Configuration
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Tenant Database Configuration
TENANT_DB_HOST = os.getenv("TENANT_DB_HOST")
TENANT_DB_PORT = os.getenv("TENANT_DB_PORT", "5432")
TENANT_DB_NAME = os.getenv("TENANT_DB_NAME", "tenant_db")
TENANT_DB_USER = os.getenv("TENANT_DB_USER")
TENANT_DB_PASSWORD = os.getenv("TENANT_DB_PASSWORD")

# AWS Configuration (LocalStack)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL")
AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID")
VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() in ('true', '1', 'yes')

# S3 Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "invoice-attachments")

# SQS Configuration
SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME")

# Construct SQS Queue URL from components
if SQS_QUEUE_NAME:
    if AWS_ENDPOINT_URL:
        # LocalStack: use endpoint URL with dummy account ID
        SQS_QUEUE_URL = f"{AWS_ENDPOINT_URL}/000000000000/{SQS_QUEUE_NAME}"
    else:
        # Real AWS: construct full URL
        SQS_QUEUE_URL = f"https://sqs.{AWS_REGION}.amazonaws.com/{AWS_ACCOUNT_ID}/{SQS_QUEUE_NAME}"
else:
    SQS_QUEUE_URL = None

# Scheduler Configuration
SCHEDULER_INTERVAL_MINUTES = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", "60"))

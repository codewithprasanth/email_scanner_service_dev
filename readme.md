# 📧 Email Scanner Service (Simplified)

A production-ready **Email Scanner Service** that:
1. Fetches new emails from Microsoft Outlook (Graph API)
2. Skips duplicates at the very start
3. Stores emails and **all attachments** in PostgreSQL + S3
4. Pushes **only `work_id`** to SQS for downstream processing
5. Runs on a configurable scheduler


---

## 🧠 High-Level Flow

Outlook Inbox  
→ Duplicate Check (DB)  
→ Store Email (Postgres)  
→ Upload Attachments (S3)  
→ Push `work_id` → SQS  

---

## 📦 Tech Stack

- Python 3.9+
- Microsoft Graph API
- PostgreSQL
- AWS S3 (LocalStack supported)
- AWS SQS (LocalStack supported)
- schedule

---

## 📁 Project Structure

```
.
email_scanner/
│
├── main.py                      # Entry point
│
├── config/
│   └── settings.py              # env vars, constants
│
├── db/
│   ├── connection.py            # DB connections
│   ├── check_email.py           # check email exist or not 
│   ├── fetch_last_timestamp.py  # fetches  last time of scan in db
│   ├── insert_email.py          # insert email in db
│   ├── update_scanner.py        # update last scan details in db
│   └── insert_document.py       # insert document to db
│
├── aws/
│   ├── s3_client.py             # create client
│   ├── sqs_client.py            # create queue
│   ├── check_sqs.py             # ensure bucket exist
│   ├── push_s3.py               # push to bucket
│   ├── push_sqs.py              # push to queue
│   └── check_s3.py              # ensure queue exist
│
├── graph/
│   ├── auth.py                  # MSAL auth
│   ├── client.py                # Graph API calls to get session
│   ├── attachment.py            # process attachments
│   └── folder_id.py             # get folder id 
│
├── services/
│   └── fetch_email.py           # fetch new email from last timestamp
│
├── utils/
│   ├── logger.py                 # Setup logger
│   ├── document_type.py          # Help to get document type from file name
│   └── generate_work_id.py       # Generates work id
│
├── bootstrap/
│   ├── configuration_store.py    # Storing Tentant config
│   ├── tentant_config.py         # Fetching tenant config
│   └── startup.py                # Check everything fine or not
│
│── .gitignore
│
│── .env
│
│── docker-compose.yaml
└── requirements.txt


```

---

## 🔧 Prerequisites

- Python 3.9+
- PostgreSQL (Main DB + Tenant DB)
- Azure App Registration with Mail.Read permissions
- LocalStack (optional for local S3/SQS)

---

## 📜 Environment Variables

Create a `.env` file:

### Microsoft Graph
```
GRAPH_CLIENT_ID=xxxx
GRAPH_CLIENT_SECRET=xxxx
GRAPH_TENANT_ID=xxxx
GRAPH_API_ENDPOINT=https://graph.microsoft.com/v1.0
USER_EMAIL=invoice@company.com
```

### Main Database
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=email_db
DB_USER=postgres
DB_PASSWORD=postgres
```

### Tenant Database
```
TENANT_DB_HOST=localhost
TENANT_DB_PORT=5432
TENANT_DB_NAME=tenant_db
TENANT_DB_USER=postgres
TENANT_DB_PASSWORD=postgres
```

### AWS / LocalStack
```
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_REGION=us-east-1
AWS_ENDPOINT_URL=http://localhost:4566
S3_BUCKET_NAME=invoice-attachments
SQS_QUEUE_NAME=invoice-processing-queue
```


---

## 📦 Install Dependencies

```
pip install -r requirements.txt
```

Minimum required packages:
```
msal
requests
psycopg2-binary
boto3
schedule
python-dotenv
```

---

## ▶️ Run the Service

```
python email_scanner.py
```

On startup:
- Ensures S3 bucket & SQS queue
- Loads tenant config
- Runs initial scan
- Starts scheduler

---


## 🛑 Stop Service

Press `Ctrl + C` to stop gracefully.

---

## ✅ Design Highlights

- Duplicate emails skipped at source
- Attachments always stored
- Minimal SQS payload (`work_id` only)
- Idempotent & safe re-runs
- Local & cloud friendly

---

## 🚀 Ready for Production

Built for scalable, queue-driven invoice ingestion pipelines.
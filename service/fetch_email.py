import time
from aws.push_sqs import push_to_sqs_queue
from config.settings import *
from db.fetch_last_timestamp import get_last_processed_timestamp_from_db
from db.update_scanner import update_scanner_state_in_db
from db.check_email import check_email
from db.insert_email import insert_email_to_database
from graph.auth import get_graph_access_token
from graph.client import get_session 
from graph.folder_id import get_folder_id
from graph.attachments import process_attachments
from utils.logger import get_logger
import uuid
from typing import Dict, List, Any
from datetime import datetime, timedelta
from utils.scan_name import build_scan_name
import re

logger = get_logger(__name__)


def fetch_new_emails_from_graph(
    folder_name: str = "Inbox", 
    user_email: str = None,
    client_id: str = "",
    client_secret: str = "",
    tenant_id: str = "",
    sqs_queue_url: str = None
) -> List[Dict[str, Any]]:
    """
    Fetch emails from Microsoft Graph, store them, process attachments,
    and push work_id to SQS.
    
    Args:
        folder_name: Mail folder to scan
        user_email: Email account to scan
        client_id: Azure AD client ID
        client_secret: Azure AD client secret
        tenant_id: Azure AD tenant ID
        sqs_queue_url: SQS Queue URL for pushing work_ids
    """
    
    if not user_email:
        logger.error("user_email required")
        return []
    
    if not sqs_queue_url:
        logger.error("sqs_queue_url required")
        return []
    
    scanner_id = str(uuid.uuid4())
    entity_id = str(uuid.uuid4())
    scan_name = build_scan_name(user_email, folder_name)

    logger.info(
        f"Starting email scan | user={user_email}, folder={folder_name}, "
        f"scanner_id={scanner_id}, scan_name={scan_name}"
    )
    
    results: List[Dict[str, Any]] = []
    scan_start_time = time.perf_counter()
    
    # Counters
    page_count = 0
    new_emails = 0
    duplicates_skipped = 0
    attachments_uploaded = 0
    sqs_sent = 0
    failed_emails = 0
    last_timestamp = None
    last_email_id = None

    try:
        # Authenticate
        access_token = get_graph_access_token(client_id, client_secret, tenant_id)
        session = get_session(access_token)
        folder_id = get_folder_id(session, user_email, folder_name)
        
        # Get last timestamp
        last_fetch = get_last_processed_timestamp_from_db(user_email)
        if not last_fetch:
            last_fetch = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        dt = datetime.fromisoformat(last_fetch.replace('Z', '+00:00')) - timedelta(minutes=30)
        filter_param = f"receivedDateTime ge {dt.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        
        base_url = f"{GRAPH_API_ENDPOINT}/users/{user_email}/mailFolders/{folder_id}/messages"
        params = {"$filter": filter_param, "$orderby": "receivedDateTime desc"}
        
        url = base_url
        
        while url:
            page_count += 1
            response = session.get(url, params=params if url == base_url else None)
            response.raise_for_status()
            data = response.json()
            
            for message in data.get("value", []):
                try:
                    subject = message.get("subject", "")
                    
                    # Skip RE: and FW: emails
                    if re.search(r'^(RE:|FW:)', subject, re.IGNORECASE):
                        continue
                    
                    email_id = message.get("id")
                    received_time = message.get("receivedDateTime", "")
                    
                    # Track latest timestamp
                    if not last_timestamp or received_time > last_timestamp:
                        last_timestamp = received_time
                        last_email_id = email_id
                    
                    # ✅ SINGLE DUPLICATE CHECK - At the beginning
                    if check_email(email_id):
                        duplicates_skipped += 1
                        logger.debug(f"⏭ Duplicate email skipped: {email_id[:30]}...")
                        continue
                    
                    # NEW EMAIL - Process everything
                    email_start_time = time.perf_counter()
                    
                    to_recipients = message.get("toRecipients", [])
                    recipient_emails = [
                        r.get("emailAddress", {}).get("address", "") 
                        for r in to_recipients 
                        if r.get("emailAddress", {}).get("address")
                    ]
                    
                    # ✅ FIX: Use hasAttachments flag from Graph API
                    has_attachments = message.get("hasAttachments", False)
                    
                    email_data = {
                        "graph_message": message,
                        "id": email_id,
                        "conversation_id": message.get("conversationId", ""),
                        "subject": subject,
                        "sender": message.get("sender", {}).get("emailAddress", {}).get("name", ""),
                        "sender_email": message.get("sender", {}).get("emailAddress", {}).get("address", ""),
                        "body": message.get("body", {}).get("content", ""),
                        "received_time": received_time,
                        "has_attachments": has_attachments,
                        "attachment_count": 0,  # Will be updated after processing
                        "recipient_mailbox": recipient_emails
                    }
                    
                    try:
                        # STEP 1: Insert email
                        work_id = insert_email_to_database(email_data, entity_id)
                        if not work_id:
                            logger.error(f"Failed to insert email: {email_id}")
                            failed_emails += 1
                            continue

                        logger.info(
                            f"Processing email | work_id={work_id}, email_id={email_id}, "
                            f"has_attachments={has_attachments}, subject='{subject[:50]}...'"
                        )
                        new_emails += 1
                        
                        # STEP 2: Process ALL attachments if email has any
                        email_attachments = 0
                        if has_attachments:
                            logger.info(
                                f"Email flagged with attachments | work_id={work_id}, "
                                f"fetching attachment details from Graph API..."
                            )
                            
                            # ✅ FIX: Don't pass message.get("attachments") - let the function fetch them
                            # The initial message list doesn't include attachment details
                            email_attachments = process_attachments(
                                session,
                                user_email,
                                folder_id,
                                email_id,
                                work_id,
                                None  # ✅ Pass None - function will fetch from API
                            )
                            
                            attachments_uploaded += email_attachments
                            
                            if email_attachments > 0:
                                logger.info(
                                    f"✓ Attachments stored | work_id={work_id}, "
                                    f"count={email_attachments}"
                                )
                            else:
                                logger.warning(
                                    f"⚠ No attachments found | work_id={work_id} "
                                    f"(hasAttachments=True but none retrieved)"
                                )
                        else:
                            logger.debug(f"No attachments to process | work_id={work_id}")
                        
                        # STEP 3: Push work_id to SQS
                        if push_to_sqs_queue(work_id, sqs_queue_url):
                            sqs_sent += 1
                            logger.debug(f"✓ Pushed to SQS | work_id={work_id}")
                        else:
                            logger.warning(f"✗ Failed to push to SQS | work_id={work_id}")
                        
                        # Calculate email processing time
                        email_latency_sec = time.perf_counter() - email_start_time
                        
                        logger.info(
                            f"✓ Email processed successfully | work_id={work_id}, "
                            f"attachments={email_attachments}, latency={email_latency_sec:.2f}s"
                        )
                        
                        results.append(email_data)
                    
                    except Exception as e:
                        email_latency = time.perf_counter() - email_start_time
                        failed_emails += 1
                        logger.error(
                            f"✗ Email processing failed | email_id={email_id}, "
                            f"latency={email_latency:.2f}s | Error: {str(e)}",
                            exc_info=True
                        )
                        continue
                
                except Exception as e:
                    logger.error(
                        f"Message parsing failed | Error: {str(e)}",
                        exc_info=True
                    )
                    continue
            
            url = data.get("@odata.nextLink")
        
        # Update scanner state
        if last_timestamp and last_email_id:
            update_scanner_state_in_db(
                scanner_id, entity_id, user_email,
                last_timestamp, last_email_id, new_emails, 'success'
            )
        
        # Calculate total scan time
        scan_latency = time.perf_counter() - scan_start_time
        
        logger.info(
            f"✓ Scan completed | scan_name={scan_name} | "
            f"new={new_emails}, duplicates={duplicates_skipped}, "
            f"attachments={attachments_uploaded}, sqs_sent={sqs_sent}, "
            f"failed={failed_emails}, pages={page_count}, "
            f"latency={scan_latency:.2f}s"
        )
        
        return results
    
    except Exception as e:
        scan_latency = time.perf_counter() - scan_start_time
        logger.error(
            f"✗ Scan failed | scan_name={scan_name}, "
            f"latency={scan_latency:.2f}s | Error: {str(e)}",
            exc_info=True
        )
        
        # Update scanner state with error
        if last_timestamp and last_email_id:
            update_scanner_state_in_db(
                scanner_id, entity_id, user_email,
                last_timestamp, last_email_id, new_emails, 'error'
            )
        
        return []
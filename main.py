
"""
Email Scanner Service - FastAPI Web Service
Fetches emails based on database config and pushes to SQS
"""

import sys
import threading
import time
from fastapi import FastAPI
import uvicorn
from bootstrap.startup import check_config
from bootstrap.configuration_store import CONFIG
from service.fetch_email import fetch_new_emails_from_graph
from aws.check_sqs import ensure_sqs_queue_exists
from config.settings import CLIENT_ID, CLIENT_SECRET, TENANT_ID, SCHEDULER_INTERVAL_MINUTES
from utils.logger import get_logger

logger = get_logger(__name__)

# FastAPI app
app = FastAPI(title="Email Scanner Service", version="1.0.0")

# Scheduler state
scheduler_running = False
scheduler_thread = None
sqs_queue_url = None


def scan_emails():
    """Core email scanning logic - kept from original implementation."""
    try:
        logger.info("Starting email scan...")
        fetch_new_emails_from_graph(
            folder_name="Inbox",
            user_email="sprintaptest1@mindsprint.com",
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            tenant_id=TENANT_ID,
            sqs_queue_url=sqs_queue_url
        )
        logger.info("Email scan completed successfully")
        return {"status": "success", "message": "Email scan completed"}
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        return {"status": "error", "message": str(e)}


def scheduler_job():
    """Background scheduler that runs email scans periodically."""
    global scheduler_running
    logger.info(f"Scheduler started - running every {SCHEDULER_INTERVAL_MINUTES} minutes")
    
    while scheduler_running:
        scan_emails()
        if scheduler_running:  # Check again before sleeping
            time.sleep(SCHEDULER_INTERVAL_MINUTES * 60)
    
    logger.info("Scheduler stopped")


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup."""
    global sqs_queue_url
    
    logger.info("Starting Email Scanner Service on port 8080")
    
    if not check_config():
        logger.error("Configuration check failed")
        sys.exit(1)
    
    sqs_queue_url = ensure_sqs_queue_exists()
    logger.info("Service initialized and ready")


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "service": "Email Scanner Service",
        "status": "running",
        "scheduler_status": "running" if scheduler_running else "stopped",
        "scheduler_interval_minutes": SCHEDULER_INTERVAL_MINUTES
    }


@app.post("/scan")
async def trigger_immediate_scan():
    """Trigger an immediate one-time email scan (fire-and-forget)."""
    logger.info("Immediate scan triggered via API")
    
    # Run scan in background thread (fire-and-forget)
    scan_thread = threading.Thread(target=scan_emails, daemon=True)
    scan_thread.start()
    
    return {
        "status": "success",
        "message": "Email scan started in background"
    }


@app.post("/scheduler/start")
async def start_scheduler():
    """Start the email scanning scheduler."""
    global scheduler_running, scheduler_thread
    
    if scheduler_running:
        return {"status": "already_running", "message": "Scheduler is already running"}
    
    scheduler_running = True
    scheduler_thread = threading.Thread(target=scheduler_job, daemon=True)
    scheduler_thread.start()
    
    logger.info(f"Scheduler started - interval: {SCHEDULER_INTERVAL_MINUTES} minutes")
    return {
        "status": "success",
        "message": f"Scheduler started with {SCHEDULER_INTERVAL_MINUTES} minute interval"
    }


@app.post("/scheduler/stop")
async def stop_scheduler():
    """Stop the email scanning scheduler."""
    global scheduler_running
    
    if not scheduler_running:
        return {"status": "not_running", "message": "Scheduler is not running"}
    
    scheduler_running = False
    logger.info("Scheduler stop requested")
    
    return {"status": "success", "message": "Scheduler stopped"}


@app.get("/scheduler/status")
async def get_scheduler_status():
    """Get the current scheduler status."""
    return {
        "running": scheduler_running,
        "interval_minutes": SCHEDULER_INTERVAL_MINUTES,
        "status": "running" if scheduler_running else "stopped"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
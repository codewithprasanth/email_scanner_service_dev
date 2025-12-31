from typing import Optional, Dict, Any
from utils.logger import get_logger
from aws.check_s3 import ensure_s3_bucket_exists
from aws.check_sqs import ensure_sqs_queue_exists
from config.settings import S3_BUCKET_NAME
from bootstrap.tentant_config import fetch_tenant_config
from bootstrap.configuration_store import CONFIG

logger = get_logger(__name__)

def check_config() -> bool:
    """
    Perform startup checks and load runtime configuration.
    Verifies S3, SQS, and tenant config availability.
    """
    global CONFIG
    logger.info("SERVICE STARTUP CHECK — INITIALIZING DEPENDENCIES")

    # ---- S3 (blocking) ----
    logger.info("Checking S3 bucket availability...")
    if not ensure_s3_bucket_exists():
        logger.error("Startup check failed — S3 bucket not available")
        return False
    logger.info("S3 bucket check passed")

    # ---- SQS (blocking) ----
    logger.info("Checking SQS queue availability...")
    if not ensure_sqs_queue_exists():
        logger.error("Startup check failed — SQS queue not available")
        return False
    logger.info("SQS queue check passed")

    # ---- Tenant config (blocking) ----
    logger.info("Loading tenant configuration...")
    CONFIG = fetch_tenant_config()

    if not CONFIG:
        logger.error("Startup check failed — tenant configuration missing or invalid")
        return False

    # ---- Summary ----
    logger.info("Startup configuration loaded successfully")
    logger.info(f"Scan interval (mins)  : {CONFIG['scan_interval_mins']}")
    logger.info(f"S3 bucket             : {S3_BUCKET_NAME}")

    logger.info("SERVICE READY — ALL REQUIRED DEPENDENCIES AVAILABLE")

    return True

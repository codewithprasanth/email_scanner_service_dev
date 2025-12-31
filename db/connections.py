import psycopg2
from psycopg2 import OperationalError, InterfaceError
from utils.logger import get_logger
from config.settings import *

logger = get_logger(__name__)

def get_guident_db():
    """Connect to the main Guident database."""
    try:
        logger.info(f"Connecting to Guident DB at {DB_HOST}:{DB_PORT}/{DB_NAME}")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logger.info("Guident DB connection established successfully")
        return conn
    except OperationalError as e:
        logger.error(f"OperationalError while connecting to Guident DB: {str(e)}", exc_info=True)
    except InterfaceError as e:
        logger.error(f"InterfaceError while connecting to Guident DB: {str(e)}", exc_info=True)
    except Exception as e:
        logger.error(f"Unexpected error connecting to Guident DB: {str(e)}", exc_info=True)
    return None


def get_tenant_db():
    """Connect to the tenant-specific database."""
    try:
        logger.info(f"Connecting to Tenant DB at {TENANT_DB_HOST}:{TENANT_DB_PORT}/{TENANT_DB_NAME}")
        conn = psycopg2.connect(
            host=TENANT_DB_HOST,
            port=TENANT_DB_PORT,
            database=TENANT_DB_NAME,
            user=TENANT_DB_USER,
            password=TENANT_DB_PASSWORD
        )
        logger.info("Tenant DB connection established successfully")
        return conn
    except OperationalError as e:
        logger.error(f"OperationalError while connecting to Tenant DB: {str(e)}", exc_info=True)
    except InterfaceError as e:
        logger.error(f"InterfaceError while connecting to Tenant DB: {str(e)}", exc_info=True)
    except Exception as e:
        logger.error(f"Unexpected error connecting to Tenant DB: {str(e)}", exc_info=True)
    return None

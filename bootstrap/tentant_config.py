from db.connections import get_tenant_db
from typing import Optional ,Dict,Any
from utils.logger import get_logger
logger=get_logger(__name__)
def fetch_tenant_config() -> Optional[Dict[str, Any]]:
    # """Fetch tenant configuration."""
    # conn = None
    # try:
    #     conn = get_tenant_db()
    #     cursor = conn.cursor()
        
    #     query = """
    #         SELECT invoice_email_addresses, email_scan_interval_mins
    #         FROM public.tenant_config
    #         WHERE is_active = true
    #         LIMIT 1
    #     """
        
    #     cursor.execute(query)
    #     row = cursor.fetchone()
    #     cursor.close()
        
    #     if row:
    #         user_email = row[0]  
    #         if not user_email:
    #             logger.error("USER_EMAIL missing in tenant_config table!")
    #             return None
            
    #         config = {
    #             "email_addresses": row[0] if row[0] else [],
    #             "scan_interval_mins": row[1],
    #             "user_email": user_email
    #         }
            
    #         logger.info(f"Config: {config['user_email']}, Interval: {config['scan_interval_mins']} mins")
    #         return config
    #     else:
    #         logger.warning("No active tenant config")
    #         return None
        
    # except Exception as e:
    #     logger.error(f"Config error: {str(e)}")
    #     return None
    # finally:
    #     if conn:
    #         conn.close()

    return  {
                "email_addresses": [],
                "scan_interval_mins": 10,
                "user_email": "SprintAPtest1@mindsprint.com"
            }


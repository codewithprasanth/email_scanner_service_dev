# graph/auth.py
import msal
import os
from utils.logger import get_logger

logger = get_logger(__name__)


def get_graph_access_token(   client_id: str,
    client_secret: str,
    tenant_id: str) -> str:
    """
    Acquire Microsoft Graph API access token using client credentials.
    """
    logger.info("Starting Microsoft Graph authentication")

    try:
        logger.debug(
            "Initializing MSAL ConfidentialClientApplication "
            f"(tenant_id={tenant_id})"
        )
        
        # Check if SSL verification should be disabled
        verify_ssl = os.getenv("VERIFY_SSL", "true").lower() in ('true', '1', 'yes')
        
        # Create HTTP client configuration
        http_client_config = {}
        if not verify_ssl:
            logger.warning("SSL verification disabled for Microsoft Graph API")
            http_client_config = {"verify": False}

        app = msal.ConfidentialClientApplication(
            client_id,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
            client_credential=client_secret,
            verify=verify_ssl
        )

        logger.debug("Requesting Graph API access token")
        result = app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )

        if "access_token" not in result:
            error = result.get("error")
            error_desc = result.get("error_description")

            logger.error(
                "Failed to acquire Graph access token | "
                f"error={error}, description={error_desc}"
            )
            raise RuntimeError("Graph authentication failed")

        logger.info("Graph access token acquired successfully")
        return result["access_token"]

    except Exception as e:
        logger.error("Graph authentication exception occurred", exc_info=True)
        raise

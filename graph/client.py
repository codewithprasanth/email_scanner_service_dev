import requests
import os
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


def get_session(access_token: str) -> requests.Session:
    """
    Create a requests session with Graph API authorization headers.
    """
    logger.debug("Creating Graph API session")

    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {access_token}"
    })
    
    # Check if SSL verification should be disabled
    verify_ssl = os.getenv("VERIFY_SSL", "true").lower() in ('true', '1', 'yes')
    if not verify_ssl:
        logger.warning("SSL verification disabled for Graph API requests")
        session.verify = False
        # Suppress SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    logger.info("Graph API session initialized successfully")
    return session


def get_data(
    session: requests.Session,
    url: str,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Perform a GET request to Microsoft Graph API and return JSON response.
    """
    logger.debug(
        "Graph API GET request | "
        f"url={url} | params={params}"
    )

    try:
        response = session.get(url, params=params, timeout=30)
        response.raise_for_status()

        logger.debug(
            "Graph API response received | "
            f"status_code={response.status_code}"
        )

        data = response.json()
        logger.debug(
            "Graph API response parsed successfully | "
            f"keys={list(data.keys())}"
        )

        return data

    except requests.exceptions.HTTPError as e:
        logger.error(
            "Graph API HTTP error | "
            f"url={url} | status_code={getattr(e.response, 'status_code', None)} | "
            f"response={getattr(e.response, 'text', '')[:300]}",
            exc_info=True
        )
        raise

    except requests.exceptions.RequestException as e:
        logger.error(
            f"Graph API request failed | url={url}",
            exc_info=True
        )
        raise

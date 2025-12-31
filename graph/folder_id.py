from graph.client import get_data
from config.settings import GRAPH_API_ENDPOINT
from utils.logger import get_logger

logger = get_logger(__name__)


def get_folder_id(session, user_email: str, folder_name: str) -> str:
    """
    Resolve Microsoft Graph mail folder ID by folder name.
    """

    logger.info(
        "Resolving mail folder ID | "
        f"user={user_email}, folder='{folder_name}'"
    )

    try:
        #  Check top-level mail folders
        url = f"{GRAPH_API_ENDPOINT}/users/{user_email}/mailFolders"
        logger.debug(f"Fetching top-level mail folders | url={url}")

        data = get_data(session, url)
        folders = data.get("value", [])

        logger.debug(f"Top-level folders fetched | count={len(folders)}")

        for folder in folders:
            if folder.get("displayName") == folder_name:
                folder_id = folder.get("id")
                logger.info(
                    f"Folder found at top level | "
                    f"folder='{folder_name}', folder_id={folder_id}"
                )
                return folder_id

        # Fallback: check inbox child folders
        url = f"{GRAPH_API_ENDPOINT}/users/{user_email}/mailFolders/inbox/childFolders"
        logger.debug(f"Fetching inbox child folders | url={url}")

        data = get_data(session, url)
        child_folders = data.get("value", [])

        logger.debug(f"Inbox child folders fetched | count={len(child_folders)}")

        for folder in child_folders:
            if folder.get("displayName") == folder_name:
                folder_id = folder.get("id")
                logger.info(
                    f"Folder found in inbox child folders | "
                    f"folder='{folder_name}', folder_id={folder_id}"
                )
                return folder_id

        
        logger.error(
            f"Mail folder not found | user={user_email}, folder='{folder_name}'"
        )
        raise RuntimeError(f"Folder '{folder_name}' not found")

    except Exception as e:
        logger.error(
            f"Failed to resolve mail folder | user={user_email}, folder='{folder_name}'",
            exc_info=True
        )
        raise

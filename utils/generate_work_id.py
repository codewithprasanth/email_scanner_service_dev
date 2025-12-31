import uuid
from utils.logger import get_logger

logger = get_logger(__name__)

def generate_work_id() -> str:
    """
    Generate a unique work_id.
    """
    logger.debug("Generating new work_id")

    work_id=str(uuid.uuid4())

    logger.info(f"Generated work_id={work_id}")
    return work_id

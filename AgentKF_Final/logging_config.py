
# ============================================================
# AgentKF - LOGGING
# ============================================================

import logging
from pathlib import Path


PROJECT_DIR = Path(
    "/content/AgentKF"
)

LOG_DIR = (
    PROJECT_DIR / "outputs"
)

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)


LOG_FILE = (
    LOG_DIR / "agentkf.log"
)


logging.basicConfig(

    level=logging.INFO,

    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    ),

    handlers=[

        logging.FileHandler(
            LOG_FILE
        ),

        logging.StreamHandler()

    ]

)


logger = logging.getLogger(
    "AgentKF"
)

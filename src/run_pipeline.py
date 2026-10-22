
import logging
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

STAGES = [
    ("Extract", "src/extract.py"),
    ("Transform", "src/transform.py"),
    ("SQL analysis", "src/analyze.py"),
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    for stage_name, script_path in STAGES:
        logger.info("Starting stage: %s", stage_name)

        subprocess.run(
            [sys.executable, str(PROJECT_ROOT / script_path)],
            cwd=PROJECT_ROOT,
            check=True,
        )

        logger.info("Stage completed: %s", stage_name)

    logger.info("Pipeline completed successfully")


if __name__ == "__main__":
    main()

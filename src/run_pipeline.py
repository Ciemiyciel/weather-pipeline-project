
"""Run the complete weather data pipeline."""

import logging
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

STEPS = [
    ("Extract", "src/extract.py"),
    ("Transform", "src/transform.py"),
    ("Analyze", "src/analyze.py"),
    ("Load to PostgreSQL", "src/load_postgres.py"),
    ("Data quality checks", "src/check_postgres.py"),
]


def run_pipeline():
    """Execute each pipeline stage in order."""
    for step_name, script_path in STEPS:
        logger.info("Starting step: %s", step_name)

        subprocess.run(
            [sys.executable, str(PROJECT_ROOT / script_path)],
            cwd=PROJECT_ROOT,
            check=True,
        )

        logger.info("Completed step: %s", step_name)

    logger.info("Pipeline completed successfully.")


if __name__ == "__main__":
    try:
        run_pipeline()
    except subprocess.CalledProcessError as error:
        logger.error(
            "Pipeline failed at a subprocess (exit code %s).",
            error.returncode,
        )
        sys.exit(error.returncode)

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]

# Load .env
load_dotenv(ROOT_DIR / ".env")

# Read environment name
ENVIRONMENT = os.getenv("ENV", "qa")

# Environment configuration
ENV_FILE = (
    ROOT_DIR
    / "config"
    / "environments"
    / f"{ENVIRONMENT}.yaml"
)

# Test data
TEST_DATA_FILE = ROOT_DIR / "data" / "test_data.yaml"
CART_TEST_DATA_FILE = ROOT_DIR / "data" / "cart_test_data.yaml"


def load_yaml(file_path):
    """Load a YAML configuration or test-data file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


environment_config = load_yaml(ENV_FILE)
test_data = load_yaml(TEST_DATA_FILE)
cart_test_data = load_yaml(CART_TEST_DATA_FILE)

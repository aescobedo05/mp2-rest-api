# data_loaders.py
from pathlib import Path

import logging
import pandas as pd
import json
import yaml

logger = logging.getLogger(__name__)


def load_csv(filepath):
    """Load a CSV file into a DataFrame.
    filepath is a Path object.
    """
    df = pd.read_csv(filepath)
    logger.info("Loaded CSV file: %s (%s rows)", filepath, len(df))

    return df


def load_json(filepath):
    """Load a JSON file into a Python object (dict or list).
    filepath is a Path object.
    """
    with open(filepath, "r") as f:
        data = json.load(f)
    logger.info("Loaded JSON file: %s", filepath)

    return data



def load_yaml(filepath):
    """Load a YAML file into a Python object.
    filepath is a Path object.
    """
    with open(filepath, "r") as f:
        config = yaml.safe_load(f)
    logger.info("Loaded YAML file: %s", filepath)

    return config



def load_data(filepath):
    """Load a file based on its extension.
    filepath is a string, such as 'fixtures/sample.csv'
    """
    data_dir = Path(filepath)
    if data_dir.suffix == '.csv':
        return load_csv(data_dir)
    elif data_dir.suffix == '.json':
        return load_json(data_dir)
    elif data_dir.suffix == '.yaml':
        return load_yaml(data_dir)
    else:
        logger.error("Unsupported file format: %s", data_dir.suffix)
        raise ValueError(f"Unsupported file format: {data_dir.suffix}")

# src/data_validator.py
import logging
import pandas as pd


logger = logging.getLogger(__name__)


def validate_dataframe(df, required_columns, numeric_columns):
    """Validate the DataFrame and return valid data.

    required_columns: a list of column names that must exist.
    numeric_columns: a list of column names whose values should be numeric.
    """
    original_df = df
    for column in required_columns:
        if column not in df.columns:
            logger.error("")
            raise ValueError

    for col in numeric_columns:
        invalid_rows = []
        for i, value in df[col].items():
            if pd.notna(value):
                try:
                    float(value)
                except ValueError:
                    logger.warning("Invalid value in %s: %s", col, value)
                    invalid_rows.append(i)

        if invalid_rows:
            df = df.drop(index=invalid_rows)

        df[col] = pd.to_numeric(df[col])

    logger.debug("Validation: %s → %s rows", len(original_df), len(df))

    return df

# data_processor.py
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def remove_duplicates(df):
    """Remove duplicate rows."""
    df_dropped = df.drop_duplicates()

    after = len(df_dropped)

    logger.debug("remove_duplicates: %s → %s", len(df), after)

    return df_dropped


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    if axis == "rows":
        df_cleaned = df.dropna()
        after = len(df_cleaned)
        logger.debug("handle_missing: %s → %s rows", len(df), after)
    elif axis == "columns":
        df_cleaned = df.dropna(axis=1)
        after = len(df_cleaned)
        logger.debug("handle_missing: %s → %s rows", len(df), after)
    else:
        logger.debug("Unsupported axis type")
        raise ValueError

    return df_cleaned


def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""    
    if method not in {"iqr", "zscore"}:
        logger.error("%s is unsupported method type", method)
        raise ValueError(f"{method} is unsupported method type")

    df_score_cleaned = df.copy()

    for column in columns:
        if column not in df.columns:
            logger.warning("%s does not exist", column)
            continue

        if not pd.api.types.is_numeric_dtype(df[column]):
            logger.warning("%s is not a numeric column", column)
            continue

        if method == "iqr":
            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)
            iqr = q3 - q1

            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr

            df_score_cleaned = df_score_cleaned[(df_score_cleaned[column] >= lower) 
                                                & (df_score_cleaned[column] <= upper)]

        elif method == "zscore":
            mean = df[column].mean()
            std = df[column].std()

            z_scores = (df[column] - mean) / std

            df_score_cleaned = df_score_cleaned[z_scores.abs() <= threshold]


    rows_removed = len(df) - len(df_score_cleaned)
    logger.debug("method: %s, threshold: %s, %s rows removed", method, threshold, rows_removed)

    return df_score_cleaned


def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""
    processing = config["processing"]

    if processing["remove_duplicates"]:
        df = remove_duplicates(df)

    if processing["missing"]["enabled"]:
        axis = processing["missing"]["axis"]
        df = handle_missing(df, axis)

    if processing["outliers"]["enabled"]:
        columns = processing["outliers"]["columns"]
        method = processing["outliers"]["method"]
        threshold = processing["outliers"]["threshold"]

        df = remove_outliers(df, columns, method, threshold)

    return df


def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""
    return {
        "row_before": len(df_before),
        "rows_after": len(df_after),
        "rows_removed": len(df_before) - len(df_after),
        "columns_before": len(df_before.columns),
        "columns_after": len(df_after.columns),
        "columns_removed": len(df_before.columns) - len(df_after.columns),
    }

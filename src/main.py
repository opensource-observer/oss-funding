import json
import logging
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd
from pandas import DataFrame

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DATA_DIR = Path("data")
OUT_NAME = "funding_data"
REQ_COLS = [
    "to_project_name",
    "amount",
    "funding_date",
    "from_funder_name",
    "grant_pool_name",
    "metadata",
]


def load_funding_csv(csv_file_path: Union[str, Path]) -> DataFrame:
    """
    Load a CSV file and extract the required columns.

    Args:
        csv_file_path: Path to the CSV file

    Returns:
        DataFrame containing the required columns or empty DataFrame if an error occurs
    """
    try:
        df = pd.read_csv(csv_file_path)
        df = df[REQ_COLS]
        df["file_path"] = str(csv_file_path)
        logger.info(f"Loaded CSV at: {csv_file_path}")
        return df
    except Exception as e:
        logger.error(f"Error reading {csv_file_path}: {e}")
        return pd.DataFrame()


def walk_funding_csvs(
    data_dir: Union[str, Path], ignore_list: Optional[List[Union[str, Path]]] = None
) -> DataFrame:
    """
    Walk through a directory tree to find and process CSV files.

    Args:
        data_dir: The root directory to walk through
        ignore_list: List of file paths to ignore

    Returns:
        Combined DataFrame of all CSVs or empty DataFrame if none found
    """
    ignore_list = set(str(Path(p)) for p in (ignore_list or []))
    dataframes = []

    for path in Path(data_dir).glob("**/*.csv"):
        file_path = str(path)
        if file_path not in ignore_list:
            df = load_funding_csv(file_path)
            if not df.empty:
                dataframes.append(df)

    if dataframes:
        return pd.concat(dataframes, ignore_index=True)

    logger.warning("No CSV files found.")
    return pd.DataFrame()


def json_export(dataframe: DataFrame, json_outpath: Union[str, Path]) -> None:
    """
    Export DataFrame to JSON file with appropriate data transformations.

    Args:
        dataframe: The DataFrame to export
        json_outpath: Path to save the JSON file
    """
    df_export = dataframe.copy()

    df_export["amount"] = df_export["amount"].fillna(0)
    df_export["funding_date"] = df_export["funding_date"].fillna("")

    data = df_export.to_dict(orient="records")

    for grant in data:
        if not isinstance(grant["to_project_name"], str):
            grant["to_project_name"] = None

        try:
            grant["metadata"] = json.loads(grant["metadata"])
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in metadata: {grant['metadata']}")
            grant["metadata"] = {}

    with open(json_outpath, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=2)

    logger.info(f"Exported to {json_outpath}")


def main() -> None:
    """Main function to process funding CSVs and export to JSON and CSV."""
    csv_outpath = DATA_DIR / f"{OUT_NAME}.csv"
    json_outpath = DATA_DIR / f"{OUT_NAME}.json"

    df = walk_funding_csvs(DATA_DIR, ignore_list=[csv_outpath])

    if df.empty:
        logger.warning("No data to export")
        return

    json_export(df, json_outpath)

    df_csv = df.copy()
    df_csv["amount"] = df_csv["amount"].fillna(0)
    df_csv.set_index(REQ_COLS[0], drop=True, inplace=True)
    df_csv.to_csv(csv_outpath)
    logger.info(f"Exported to {csv_outpath}")


if __name__ == "__main__":
    main()

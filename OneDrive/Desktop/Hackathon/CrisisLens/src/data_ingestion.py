"""
data_ingestion.py
=================

Loads and cleans the synthetic disaster report dataset for CrisisLens.

WHAT THIS MODULE DOES
---------------------
1. Reads `data/raw/disaster_reports.csv` with pandas.
2. Checks that every required column is present.
3. Tidies up obvious problems (extra whitespace, empty strings, text numbers).
4. Returns a clean pandas DataFrame.

WHAT THIS MODULE DOES NOT DO
----------------------------
No machine learning, no K-Means, no GIS, no risk scoring. It only produces
a clean table. The NLP module (nlp_classifier.py) consumes what this returns.

Run this file directly to see a quick summary of the dataset:
    python src/data_ingestion.py
"""

from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# We build paths from the location of THIS file instead of relying on the
# folder you happen to be in when you run the script. This means the code
# works whether you run it from the CrisisLens root, from inside src/, or
# from VS Code's Run button.
#
#   __file__              -> .../CrisisLens/src/data_ingestion.py
#   .resolve().parents[0] -> .../CrisisLens/src
#   .resolve().parents[1] -> .../CrisisLens            <-- project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "disaster_reports.csv"

# ---------------------------------------------------------------------------
# Column definitions
# ---------------------------------------------------------------------------
# Exactly the columns the rest of the pipeline expects. If the CSV is edited
# by hand and a column is renamed or deleted, load_reports() will complain
# instead of failing later in a confusing way.
REQUIRED_COLUMNS = [
    "report_id",
    "timestamp",
    "report_text",
    "latitude",
    "longitude",
    "source",
    "disaster_type",
    "severity",
    "trapped_persons",
    "resource_need",
]

# Columns that hold text. We strip whitespace from these.
TEXT_COLUMNS = [
    "report_id",
    "report_text",
    "source",
    "disaster_type",
    "severity",
    "resource_need",
]

# Columns that must hold numbers.
NUMERIC_COLUMNS = [
    "latitude",
    "longitude",
    "trapped_persons",
]

# Columns that get a sensible placeholder if they are empty.
# (report_text is NOT here on purpose: a report with no text is useless to us,
#  so those rows are dropped instead of filled in.)
FILL_VALUES = {
    "report_id": "UNKNOWN_ID",
    "source": "Unknown",
    "disaster_type": "Unknown",
    "severity": "Unknown",
    "resource_need": "Unknown",
}


def load_reports(path=DATA_PATH):
    """
    Load the synthetic disaster reports CSV and return a clean DataFrame.

    Parameters
    ----------
    path : str or pathlib.Path, optional
        Where the CSV lives. Defaults to data/raw/disaster_reports.csv.

    Returns
    -------
    pandas.DataFrame
        Cleaned reports, one row per report.

    Raises
    ------
    FileNotFoundError
        If the CSV file does not exist.
    ValueError
        If required columns are missing from the CSV.
    """
    path = Path(path)

    # --- 1. Make sure the file is actually there ---------------------------
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find the dataset at:\n    {path}\n"
            "Expected file: data/raw/disaster_reports.csv "
            "(run commands from the CrisisLens project root)."
        )

    # --- 2. Read it --------------------------------------------------------
    # keep_default_na=False is important here. By default pandas treats the
    # literal text "None" as a MISSING value - but "None" is a legitimate
    # value in our resource_need column ("nothing needed"). Without this flag
    # those rows would silently become NaN and get relabelled "Unknown",
    # inventing a class that does not exist in the real data.
    #
    # na_values=[""] then restores the behaviour we DO want: an empty cell
    # counts as missing.
    df = pd.read_csv(path, keep_default_na=False, na_values=[""])

    # Column names are stripped so " latitude" or "latitude " still work.
    df.columns = [str(col).strip() for col in df.columns]

    # --- 3. Validate the columns ------------------------------------------
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(
            "The dataset is missing these required columns:\n"
            f"    {missing_columns}\n"
            f"Columns found in the file: {list(df.columns)}"
        )

    # Keep only the columns we care about, in a predictable order.
    # The .copy() stops pandas from warning us when we modify things below.
    df = df[REQUIRED_COLUMNS].copy()

    # --- 4. Clean the text columns ----------------------------------------
    for column in TEXT_COLUMNS:
        # "string" dtype handles missing values more predictably than object.
        df[column] = df[column].astype("string").str.strip()

        # Treat empty strings and the text "nan" as genuinely missing.
        # NOTE: we do NOT convert the word "None" to missing, because
        # "None" is a valid value in the resource_need column.
        df[column] = df[column].replace({"": pd.NA, "nan": pd.NA, "NaN": pd.NA})

    # --- 5. Clean the numeric columns -------------------------------------
    for column in NUMERIC_COLUMNS:
        # errors="coerce" turns anything unparseable into NaN instead of
        # crashing the whole script.
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # --- 6. Timestamps ----------------------------------------------------
    # Bad timestamps become NaT (the datetime equivalent of NaN).
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # --- 7. Drop rows we cannot use ---------------------------------------
    # No report text  -> nothing for the NLP model to read.
    # No coordinates  -> nothing for the GIS teammate to map.
    # We count them first so the drop is visible, not silent.
    rows_before = len(df)
    df = df.dropna(subset=["report_text", "latitude", "longitude"])
    dropped = rows_before - len(df)
    if dropped > 0:
        print(
            f"[data_ingestion] Dropped {dropped} row(s) that had no report "
            "text or no coordinates."
        )

    # --- 8. Fill the remaining gaps ---------------------------------------
    for column, value in FILL_VALUES.items():
        df[column] = df[column].fillna(value)

    # Nobody trapped is recorded as 0, not as a blank.
    df["trapped_persons"] = df["trapped_persons"].fillna(0).astype(int)

    # --- 9. Tidy the index and hand it back -------------------------------
    df = df.reset_index(drop=True)

    return df


# ---------------------------------------------------------------------------
# Quick manual check:  python src/data_ingestion.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    reports = load_reports()

    print("=" * 60)
    print("CrisisLens - data ingestion self-check")
    print("=" * 60)
    print(f"Dataset file      : {DATA_PATH}")
    print(f"Rows loaded       : {len(reports)}")
    print(f"Columns           : {list(reports.columns)}")
    print()

    print("Rows per disaster_type:")
    print(reports["disaster_type"].value_counts().to_string())
    print()

    print("Rows per severity:")
    print(reports["severity"].value_counts().to_string())
    print()

    print("Rows per resource_need:")
    print(reports["resource_need"].value_counts().to_string())
    print()

    print("Any remaining missing values per column:")
    print(reports.isna().sum().to_string())
    print()

    print("First 3 rows:")
    print(reports.head(3).to_string())

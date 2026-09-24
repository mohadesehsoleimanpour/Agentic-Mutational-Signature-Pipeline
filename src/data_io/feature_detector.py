import re
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------
# Recognize mutation-context column names
# Examples:
# AAA_ACA
# AAA>ACA
# AAA→ACA
# ---------------------------------------------------------

MUTATION_PATTERN = re.compile(
    r"^[ACGT]{2,3}(?:_|>|→)[ACGT]{2,3}$",
    re.IGNORECASE,
)


def is_mutation_feature(column_name: str) -> bool:
    """
    Return True when a column name looks like a mutation-context feature.
    """

    column_name = str(column_name).strip()

    return bool(
        MUTATION_PATTERN.fullmatch(column_name)
    )


def inspect_column_roles(
    file_path: str,
    sample_rows: int = 1000,
):

    path = Path(file_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(
            f"File does not exist: {path}"
        )

    # Only read a small sample.
    df = pd.read_csv(
        path,
        nrows=sample_rows,
        low_memory=False,
    )

    mutation_columns = [
        column
        for column in df.columns
        if is_mutation_feature(column)
    ]

    metadata_columns = [
        column
        for column in df.columns
        if column not in mutation_columns
    ]

    numeric_metadata = [
        column
        for column in metadata_columns
        if pd.api.types.is_numeric_dtype(df[column])
    ]

    non_numeric_metadata = [
        column
        for column in metadata_columns
        if not pd.api.types.is_numeric_dtype(df[column])
    ]

    print("\nCOLUMN ROLE INSPECTION")
    print("----------------------")

    print(f"Total columns:             {len(df.columns)}")
    print(f"Mutation feature columns:  {len(mutation_columns)}")
    print(f"Metadata columns:          {len(metadata_columns)}")

    print(f"Numeric metadata columns:  {len(numeric_metadata)}")
    print(f"Text metadata columns:     {len(non_numeric_metadata)}")

    print("\nExample mutation features:")
    print(mutation_columns[:10])

    print("\nExample metadata columns:")
    print(metadata_columns[:20])

    return {
        "mutation_columns": mutation_columns,
        "metadata_columns": metadata_columns,
        "numeric_metadata": numeric_metadata,
        "non_numeric_metadata": non_numeric_metadata,
    }


if __name__ == "__main__":

    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    data_path = (
        PROJECT_ROOT
        / "data"
        / "master_normalized_3nt_context_with_metadata.csv"
    )

    inspect_column_roles(
        str(data_path)
    )

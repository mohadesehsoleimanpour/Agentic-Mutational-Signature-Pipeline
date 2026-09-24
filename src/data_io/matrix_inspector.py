from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------
# Store the inspection results
# ---------------------------------------------------------

@dataclass
class MatrixInspection:
    path: str
    file_size_gb: float
    number_of_columns: int
    sampled_rows: int

    numeric_columns: int
    non_numeric_columns: int

    missing_fraction: float
    negative_fraction: float
    zero_fraction: float

    integer_like_fraction: float
    nonzero_integer_like_fraction: float
    fractional_nonzero_fraction: float

    inferred_matrix_type: str
    recommended_next_stage: str


# ---------------------------------------------------------
# Inspect a large CSV without loading the full file
# ---------------------------------------------------------

def inspect_csv_matrix(
    file_path: str,
    sample_rows: int = 5000,
) -> MatrixInspection:

    path = Path(file_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(
            f"File does not exist: {path}"
        )

    # -----------------------------------------------------
    # 1. Get file size
    # -----------------------------------------------------

    file_size_gb = path.stat().st_size / (1024 ** 3)

    # -----------------------------------------------------
    # 2. Read only a sample
    # -----------------------------------------------------

    df = pd.read_csv(
        path,
        nrows=sample_rows,
        low_memory=False,
    )

    # -----------------------------------------------------
    # 3. Separate numeric and non-numeric columns
    # -----------------------------------------------------

    numeric_df = df.select_dtypes(include=[np.number])

    non_numeric_columns = [
        column
        for column in df.columns
        if column not in numeric_df.columns
    ]

    # -----------------------------------------------------
    # Default values
    # -----------------------------------------------------

    missing_fraction = np.nan
    negative_fraction = np.nan
    zero_fraction = np.nan

    integer_like_fraction = np.nan
    nonzero_integer_like_fraction = np.nan
    fractional_nonzero_fraction = np.nan

    inferred_type = "unknown"
    next_stage = "manual_review"

    # -----------------------------------------------------
    # 4. Basic statistics
    # -----------------------------------------------------

    if numeric_df.empty:

        inferred_type = "non_numeric_table"
        next_stage = "manual_review"

    else:

        values = numeric_df.to_numpy(dtype=float)

        finite_mask = np.isfinite(values)

        total_cells = values.size
        finite_count = finite_mask.sum()

        missing_fraction = (
            1.0 - finite_count / total_cells
        )

        finite_values = values[finite_mask]

        if finite_values.size > 0:

            negative_fraction = float(
                np.mean(finite_values < 0)
            )

            zero_fraction = float(
                np.mean(finite_values == 0)
            )

            integer_like_fraction = float(
                np.mean(
                    np.isclose(
                        finite_values,
                        np.round(finite_values),
                    )
                )
            )

            # -------------------------------------------------
            # IMPORTANT:
            # Check integer behavior only among NON-ZERO values.
            # This prevents a highly sparse matrix from being
            # incorrectly classified as a count matrix simply
            # because most cells are zero.
            # -------------------------------------------------

            nonzero_values = finite_values[
                finite_values != 0
            ]

            if nonzero_values.size > 0:

                nonzero_integer_like_fraction = float(
                    np.mean(
                        np.isclose(
                            nonzero_values,
                            np.round(nonzero_values),
                        )
                    )
                )

                fractional_nonzero_fraction = float(
                    np.mean(
                        ~np.isclose(
                            nonzero_values,
                            np.round(nonzero_values),
                        )
                    )
                )

        # -------------------------------------------------
        # 5. First-pass matrix classification
        # -------------------------------------------------

        if (
            negative_fraction == 0
            and nonzero_integer_like_fraction >= 0.99
        ):

            inferred_type = "likely_count_matrix"
            next_stage = "matrix_qc"

        elif (
            negative_fraction == 0
            and fractional_nonzero_fraction > 0.01
        ):

            inferred_type = "likely_normalized_matrix"
            next_stage = "matrix_qc"

        elif negative_fraction == 0:

            inferred_type = "nonnegative_numeric_matrix"
            next_stage = "matrix_qc"

        else:

            inferred_type = "continuous_numeric_matrix"
            next_stage = "matrix_qc"

    return MatrixInspection(
        path=str(path),
        file_size_gb=file_size_gb,
        number_of_columns=len(df.columns),
        sampled_rows=len(df),

        numeric_columns=len(numeric_df.columns),
        non_numeric_columns=len(non_numeric_columns),

        missing_fraction=float(missing_fraction),
        negative_fraction=float(negative_fraction),
        zero_fraction=float(zero_fraction),

        integer_like_fraction=float(integer_like_fraction),
        nonzero_integer_like_fraction=float(
            nonzero_integer_like_fraction
        ),
        fractional_nonzero_fraction=float(
            fractional_nonzero_fraction
        ),

        inferred_matrix_type=inferred_type,
        recommended_next_stage=next_stage,
    )


# ---------------------------------------------------------
# Print the result
# ---------------------------------------------------------

def print_matrix_inspection(
    inspection: MatrixInspection,
) -> None:

    print("\nMATRIX INSPECTION")
    print("-----------------")

    print(f"Path:                    {inspection.path}")
    print(f"File size:               {inspection.file_size_gb:.3f} GB")
    print(f"Columns:                 {inspection.number_of_columns}")
    print(f"Rows sampled:            {inspection.sampled_rows}")

    print(f"Numeric columns:         {inspection.numeric_columns}")
    print(f"Non-numeric columns:     {inspection.non_numeric_columns}")

    print(f"Missing fraction:        {inspection.missing_fraction:.4f}")
    print(f"Negative fraction:       {inspection.negative_fraction:.4f}")
    print(f"Zero fraction:           {inspection.zero_fraction:.4f}")

    print(f"Integer-like fraction:   {inspection.integer_like_fraction:.4f}")
    print(
        f"Non-zero integer-like:   "
        f"{inspection.nonzero_integer_like_fraction:.4f}"
    )
    print(
        f"Fractional non-zero:     "
        f"{inspection.fractional_nonzero_fraction:.4f}"
    )

    print(f"Inferred matrix type:    {inspection.inferred_matrix_type}")
    print(f"Next stage:              {inspection.recommended_next_stage}")


# ---------------------------------------------------------
# Temporary test
# ---------------------------------------------------------
if __name__ == "__main__":

    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    data_path = (
        PROJECT_ROOT
        / "data"
        / "master_normalized_3nt_context_with_metadata.csv"
    )

    inspection = inspect_csv_matrix(
        str(data_path)
    )

    print_matrix_inspection(inspection)
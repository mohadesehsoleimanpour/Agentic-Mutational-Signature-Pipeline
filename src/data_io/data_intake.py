from dataclasses import dataclass
from pathlib import Path


# ---------------------------------------------------------
# A small object that stores what we learned about the input
# ---------------------------------------------------------

@dataclass
class DataSummary:
    location: str
    path: str
    data_format: str
    number_of_files: int
    total_size_bytes: int
    entry_stage: str


# ---------------------------------------------------------
# Detect the file format
# ---------------------------------------------------------

def detect_file_format(path: Path) -> str:
    """
    Detect the general format of the input data.

    Important:
    CSV or Excel does NOT automatically mean count matrix.
    We only identify the file format here.
    """

    name = path.name.lower()

    if name.endswith((".fastq", ".fq", ".fastq.gz", ".fq.gz")):
        return "fastq"

    if name.endswith(".csv"):
        return "csv"

    if name.endswith((".tsv", ".txt")):
        return "tsv"

    if name.endswith((".xlsx", ".xls")):
        return "excel"

    return "unknown"


# ---------------------------------------------------------
# Decide where this input should enter the pipeline
# ---------------------------------------------------------

def determine_entry_stage(data_format: str) -> str:
    """
    Decide the next major pipeline stage.

    FASTQ needs sequence-level preprocessing first.
    Tabular files need matrix inspection before we decide
    whether they are valid mutation-count matrices.
    """

    if data_format == "fastq":
        return "fastq_qc"

    if data_format in {"csv", "tsv", "excel"}:
        return "matrix_inspection"

    return "manual_review"


# ---------------------------------------------------------
# Inspect local input
# ---------------------------------------------------------

def summarize_local_data(data_path: str) -> DataSummary:
    """
    Inspect a local file or directory without modifying it.
    """

    path = Path(data_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(
            f"Input path does not exist: {path}"
        )

    # ----------------------------
    # Case 1: user gives one file
    # ----------------------------

    if path.is_file():
        data_format = detect_file_format(path)

        return DataSummary(
            location="local",
            path=str(path),
            data_format=data_format,
            number_of_files=1,
            total_size_bytes=path.stat().st_size,
            entry_stage=determine_entry_stage(data_format),
        )

    # ----------------------------
    # Case 2: user gives directory
    # ----------------------------

    files = [
        file
        for file in path.rglob("*")
        if file.is_file()
    ]

    if not files:
        raise ValueError(
            f"No files were found inside: {path}"
        )

    formats = {
        detect_file_format(file)
        for file in files
    }

    # Remove unknown files when other recognized formats exist
    known_formats = formats - {"unknown"}

    if len(known_formats) == 1:
        data_format = next(iter(known_formats))

    elif len(known_formats) > 1:
        data_format = "mixed"

    else:
        data_format = "unknown"

    total_size = sum(
        file.stat().st_size
        for file in files
    )

    return DataSummary(
        location="local",
        path=str(path),
        data_format=data_format,
        number_of_files=len(files),
        total_size_bytes=total_size,
        entry_stage=determine_entry_stage(data_format),
    )


# ---------------------------------------------------------
# Human-readable display
# ---------------------------------------------------------

def print_data_summary(summary: DataSummary) -> None:
    size_gb = summary.total_size_bytes / (1024 ** 3)

    print("\nDATA INTAKE SUMMARY")
    print("-------------------")
    print(f"Location:        {summary.location}")
    print(f"Path:            {summary.path}")
    print(f"Format:          {summary.data_format}")
    print(f"Number of files: {summary.number_of_files}")
    print(f"Total size:      {size_gb:.3f} GB")
    print(f"Next stage:      {summary.entry_stage}")




if __name__ == "__main__":
    summary = summarize_local_data("data/examples")
    print_data_summary(summary)
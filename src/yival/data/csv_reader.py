import csv
import logging
from typing import Iterator, List

from ..schemas.common_structures import InputData
from ..schemas.reader_configs import CSVReaderConfig
from .base_reader import BaseReader


class CSVReader(BaseReader):
    """
    Reader for CSV files.

    This reader expects the first row of the CSV to be a header row, defining
    the keys for the yielded dictionaries. It yields chunks of rows for efficient
    processing.

    If the CSV does not have a header row, an exception is raised.

    Attributes:
    - path (str): The path to the CSV file to be read.
    - chunk_size (int): The number of rows per chunk. Defaults to 100.

    Yields:
    - List[Dict[str, Any]]: A chunk of rows from the CSV file, each row represented as
      a dictionary.
    """

    def __init__(self, config: CSVReaderConfig):
        super().__init__(config)

    def read(self, path: str) -> Iterator[List[InputData]]:
        chunk = []
        issues = []
        chunk_size = self.config.chunk_size
        with open(path, mode="r", encoding="utf-8") as file:
            # Check for header
            header = file.readline().strip().split(",")
            if not header or header[0] == "":
                raise ValueError(
                    f"CSV file at {path} is missing a header row."
                )

            # Reset file pointer after header check
            file.seek(0)
            reader = csv.DictReader(file)

            for row in reader:
                # Check for missing data in row
                if any(not value for value in row.values()):
                    issues.append(f"Missing data on line {reader.line_num}")
                    continue  # Skip problematic row
                example_id = self.generate_example_id(row, path)
                input_data_instance = InputData(
                    example_id=example_id, content=row
                )
                chunk.append(input_data_instance)

                if len(chunk) >= chunk_size:
                    yield chunk
                    chunk = []

            if chunk:
                yield chunk

        # Log all issues at the end
        for issue in issues:
            logging.warning(issue)

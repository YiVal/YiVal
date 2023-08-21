"""
Read data from CSV
"""
import csv
import logging
import os
from pathlib import Path
from typing import Iterator, List

from ..schemas.common_structures import InputData
from ..schemas.reader_configs import CSVReaderConfig
from .base_reader import BaseReader


def get_valid_path(user_specified_path):
    """
    Get valid csv input path.
    """
    current_file_path = Path(__file__)
    yival_root_path = current_file_path.parent.parent
    if not str(user_specified_path).startswith('/'):
        combined_path = os.path.join(yival_root_path, user_specified_path)
        if os.path.exists(combined_path):
            return combined_path

    if os.path.exists(user_specified_path):
        return user_specified_path

    raise FileNotFoundError(f"File not found at '{user_specified_path}'")


class CSVReader(BaseReader):
    """
        CSVReader is a class derived from BaseReader to read datasets from CSV
        files.

        Attributes:
            config (CSVReaderConfig): Configuration object specifying reader
                                        parameters.
            default_config (CSVReaderConfig): Default configuration for the
                                                reader.

        Methods:
            __init__(self, config: CSVReaderConfig): Initializes the CSVReader
                                                    with a given configuration.
            read(self, path: str) -> Iterator[List[InputData]]: Reads the CSV
                                    file and yields chunks of InputData.

        Note:
            The read method checks for headers in the CSV file and raises an
            error if missing.
            It also checks for missing data in rows, skipping those with
            missing values but logs them.
            If a specified column contains expected results, it extracts those
            results from the row.
            Rows are read in chunks, and each chunk is yielded once its size
            reaches `chunk_size`.
            The class supports registering with the BaseReader using the
            `register_reader` method.

        Usage:
            reader = CSVReader(config)
            for chunk in reader.read(path_to_csv_file):
                process(chunk)
        """

    config: CSVReaderConfig
    default_config = CSVReaderConfig(
        chunk_size=10000000,
        use_first_column_as_id=False,
    )

    def __init__(self, config: CSVReaderConfig):
        super().__init__(config)
        self.config = config

    def read(self, path: str) -> Iterator[List[InputData]]:
        chunk = []
        issues = []
        chunk_size = self.config.chunk_size
        file_path = get_valid_path(path)
        with open(file_path, mode="r", encoding="utf-8") as file:
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

                expected_result = None
                if self.config.expected_result_column:
                    expected_result = row.get(
                        self.config.expected_result_column
                    )
                    if expected_result:
                        del row[self.config.expected_result_column]
                    else:
                        issues.append(
                            f"Missing expected result on line {reader.line_num}"
                        )

                example_id = self.generate_example_id(row, path)
                input_data_instance = InputData(
                    example_id=example_id,
                    content=row,
                    expected_result=expected_result
                )
                chunk.append(input_data_instance)

                if len(chunk) >= chunk_size:
                    yield chunk
                    chunk = []

            if chunk:
                yield chunk

        for issue in issues:
            logging.warning(issue)


BaseReader.register_reader("csv_reader", CSVReader, CSVReaderConfig)

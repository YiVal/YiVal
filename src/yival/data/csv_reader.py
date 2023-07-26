import csv
import logging
from typing import Iterator, List

from ..schemas.common_structures import InputData
from ..schemas.reader_configs import CSVReaderConfig
from .base_reader import BaseReader


class CSVReader(BaseReader):
    config: CSVReaderConfig
    default_config = CSVReaderConfig(
        chunk_size=100,
        use_first_column_as_id=False,
    )

    def __init__(self, config: CSVReaderConfig):
        super().__init__(config)
        self.config = config

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

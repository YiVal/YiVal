import re
from typing import Iterator, List

import requests

from yival.data.base_reader import BaseReader
from yival.schemas.experiment_config import InputData
from yival.schemas.reader_configs import HuggingFaceDatasetReaderConfig


class HuggingFaceDatasetReader(BaseReader):
    config: HuggingFaceDatasetReaderConfig
    default_config = HuggingFaceDatasetReaderConfig(
        chunk_size=10000, example_limit=2, output_mapping={}
    )

    def __init__(self, config: HuggingFaceDatasetReaderConfig):
        super().__init__(config)
        self.config = config

    def read(self, path: str) -> Iterator[List[InputData]]:
        offset = 0
        limit = 100
        examples = []

        # Keep fetching until we reach the example_limit
        while offset < self.config.example_limit:
            path = f"{path}&offset={offset}&limit={limit}"
            response = requests.get(path)
            data = response.json()
            for item in data['rows']:
                transformed_item = {
                    self.config.output_mapping[key]: item['row'][key]
                    for key in self.config.output_mapping.keys()
                    if key in item['row']
                }
                if self.config.include:
                    if not any(
                        re.search(pattern, str(transformed_item.values()))
                        for pattern in self.config.include
                    ):
                        continue

                if self.config.exclude:
                    if any(
                        re.search(pattern, str(transformed_item.values()))
                        for pattern in self.config.exclude
                    ):
                        continue

                examples.append(InputData(content=transformed_item))

                # Break if we've reached the example_limit
                if len(examples) >= self.config.example_limit:
                    break

            offset += limit

            # If we've reached the example_limit, break out of the loop
            if len(examples) >= self.config.example_limit:
                break

        yield examples[:self.config.example_limit]


# Register the HuggingFaceDatasetReader with BaseReader again
BaseReader.register_reader(
    "huggingface_dataset_reader", HuggingFaceDatasetReader,
    HuggingFaceDatasetReaderConfig
)


def main():
    reader = HuggingFaceDatasetReader(
        HuggingFaceDatasetReaderConfig(
            chunk_size=1000,
            example_limit=100,
            output_mapping={'question': 'leetcode_problem'},
            include=['^(?!.*# Hard).*$']
        )
    )
    res = reader.read(
        "https://datasets-server.huggingface.co/rows?dataset=BoyuanJackchen%2Fleetcode_free_questions_text&config=default&split=train"
    )
    for i in res:
        print(i)


if __name__ == "__main__":
    main()

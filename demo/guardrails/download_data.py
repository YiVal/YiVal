import csv

import requests


def main():
    offset = 0
    limit = 100
    total_data = 100
    questions = []

    while offset < total_data:
        url = f"https://datasets-server.huggingface.co/rows?dataset=BoyuanJackchen%2Fleetcode_free_questions_text&config=default&split=train&offset={offset}&limit={limit}"
        response = requests.get(url)
        data = response.json()
        for item in data['rows']:
            question_content = item['row']['question']
            if "# Medium" in question_content or "# Easy" in question_content:
                # Strip headers and difficulty labels
                content = question_content.split('"""\n\t\t'
                                                 )[1].rsplit('\n\t\t', 1)[0]
                questions.append(content)
        offset += limit + 1
    csv_file_path = "leetcode_problems.csv"
    print(len(questions))
    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["leetcode_problem"])
        for question in questions:
            csv_writer.writerow([question])


if __name__ == "__main__":
    main()

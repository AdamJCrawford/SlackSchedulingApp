import csv

from datetime import datetime

DATE = datetime.today().strftime("%Y-%m-%d")

PEOPLE = []

with open("names.txt", 'r') as names:
    for name in names:
        PEOPLE.append(name.strip())

NUM_PEOPLE = len(PEOPLE)

current_row = [None] * (1 + 4 * NUM_PEOPLE)
with open("shifts.csv") as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        if row and row[0] == DATE:
            if len(row) != len(current_row):
                current_row = [DATE]
                for name in PEOPLE:
                    if name in row:
                        current_row.extend(row[row.index(name): row.index(name) + 4])
                    else:
                        current_row.extend([name] + [None] * 3)
            else:
                current_row = row


BLOCKS = [
    {
        "type": "actions",
        "elements": [
            {
                "type": "datepicker",
                "initial_date": DATE if DATE else "2002-01-01",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a date",
                },
                "action_id": "date"
            }
        ]
    }
]

row_index = 1

for person in range(NUM_PEOPLE):
    BLOCKS.extend(
        [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": current_row[row_index] if current_row[row_index] else PEOPLE[person],
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "timepicker",
                    "initial_time": current_row[row_index + 1] if current_row[row_index + 1] else "00:00",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select time",
                    },
                    "action_id": f"person{person}_start"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Start Time",
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "timepicker",
                    "initial_time": current_row[row_index + 2] if current_row[row_index + 2] else "00:00",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select time",
                    },
                    "action_id": f"person{person}_end"
                },
                "label": {
                    "type": "plain_text",
                    "text": "End Time",
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": f"person{person}_comment",
                    "initial_value": current_row[row_index + 3] if current_row[row_index + 3] else ""
                },
                "label": {
                    "type": "plain_text",
                    "text": "Comments",
                }
            },
            {
                "type": "divider"
            }
        ]
    )
    row_index += 4

BLOCKS.append(
    {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Save",
                },
                "action_id": "save_button"
            }
        ]
    }
)


VIEW = {
    "type": "home",
    "callback_id": "home_view",
    "external_id": "home",
    # body of the view
    "blocks": BLOCKS
}

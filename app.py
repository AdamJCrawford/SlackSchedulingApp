from pathlib import Path
from dotenv import load_dotenv

import blocks
import csv
import os

# Use the package we installed
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

from flask import Flask, request

CLIENT = None

env_path = Path('.') / ".env"
load_dotenv(dotenv_path=env_path)

# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ["Token"],
    signing_secret=os.environ["Signing_Secret"]
)

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


def update_values(body, row):
    values = blocks.VIEW["blocks"]
    counter = 0
    for value in values:
        if value["type"] == "actions" and value["elements"][0]["type"] == "datepicker":
            value["elements"][0]["initial_date"] = row[counter] if row[counter] else blocks.DATE
        elif value["type"] == "input" and value["element"]["type"] == "timepicker":
            value["element"]["initial_time"] = row[counter] if row[counter] else "00:00"
        elif value["type"] == "input" and value["element"]["type"] == "plain_text_input":
            value["element"]["initial_value"] = row[counter] if row[counter] else ""
        else:
            continue
        counter += 1
        if counter == 1 or counter == 5 or counter == 9:
            counter += 1

    CLIENT.views_update(view=blocks.VIEW, external_id="home")


@app.action("date")
def handle_date(ack, body, logger):
    ack()
    logger.info(body)
    values = body["view"]["state"]["values"]
    for code in values.values():
        for key, value in code.items():
            if value["type"] == "datepicker":
                blocks.DATE = value["selected_date"]

    current_row = [None] * (1 + 4 * blocks.NUM_PEOPLE)
    with open("shifts.csv") as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            if row and row[0] == blocks.DATE:
                current_row = row
    update_values(body, current_row)


@app.action("save_button")
def handle_save_button(ack, body, logger):
    ack()
    logger.info(body)

    data = {
        "date": None,
    }

    for i, person in enumerate(blocks.PEOPLE):
        data[f"name{i}"] = person

    values = body["view"]["state"]["values"]
    for code in values.values():
        for key, value in code.items():
            if value["type"] == "datepicker":
                data[key] = value["selected_date"]
            elif value["type"] == "timepicker":
                data[key] = value["selected_time"]
            elif value["type"] == "plain_text_input":
                data[key] = value["value"]
    rows = []
    with open("shifts.csv", "r") as csv_file:
        for row in csv.reader(csv_file):
            if row and row[0] != blocks.DATE:
                rows.append(row)
    newest_data = [
        data["date"],
    ]
    for i, names, in enumerate(blocks.PEOPLE):
        newest_data.extend(
            [
                data[f"name{i}"],
                data[f"person{i}_start"],
                data[f"person{i}_end"],
                data[f"person{i}_comment"]
            ]
        )

    with open("shifts.csv", "w") as csv_file:
        writer = csv.writer(csv_file)
        for row in rows:
            writer.writerow(row)
        writer.writerow(newest_data)


@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    global CLIENT
    try:
        CLIENT = client
        # views.publish is the method that your app uses to push a view to the Home tab
        client.views_publish(
            # the user that opened your app's app home
            user_id=event["user"],
            # the view object that appears in the app home
            view=blocks.VIEW
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


# Start your app and listen for events
if __name__ == "__main__":
    flask_app.run(debug=True, port=3000)
#     app.start(port=int(os.environ.get("PORT", 3000)))

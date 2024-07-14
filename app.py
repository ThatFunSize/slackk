from flask import Flask, request, make_response, Response
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from slack_sdk import WebClient

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

SLACK_VERIFICATION_TOKEN = os.environ["SIGNING_SECRET"]

slack_client = WebClient(token=os.environ['SLACK_TOKEN'])

app = Flask(__name__)

ENTRIES = {}

@app.route('/en', methods=['POST'])
def en():
    data = request.form
    user_id = data.get('user_id')
    

    order_dm = slack_client.chat_postMessage(
    channel='#bot_test',
    text="It's time to make an Engineering Notebook entry!",
    attachments=[{
        "text": "",
        "callback_id": user_id + "new_entry_form",
        "color": "#3AA3E3",
        "attachment_type": "default",
        "actions": [{
        "name": "new_entry",
        "text": ":clipboard: New Entry",
        "type": "button",
        "value": "new_entry"
        }]
    }]
    )

    ENTRIES[user_id] = {
        "order_channel": order_dm["channel"],
        "message_ts": "",
        "order": {}
    }
    return Response(), 200

@app.route("/slack/message_actions", methods=["POST"])
def message_actions():
    # Parse the request payload
    message_action = json.loads(request.form["payload"])
    user_id = message_action["user"]["id"]

    if message_action["type"] == "interactive_message":
        # Add the message_ts to the user's order info
        ENTRIES[user_id]["message_ts"] = message_action["message_ts"]

        # Show the ordering dialog to the user
        open_dialog = slack_client.dialog_open(
            trigger_id=message_action["trigger_id"],
            dialog={
                "title": "New Entry",
                "submit_label": "Submit",
                "callback_id": user_id + "new_entry_form",
                "elements": [
                    {
                        "label": "Subject",
                        "type": "select",
                        "name": "subject",
                        "placeholder": "Select a Subject",
                        "options": [
                            {
                                "label": "Drivetrain",
                                "value": "drivetrain"
                            },
                            {
                                "label": "Shooter",
                                "value": "shooter"
                            },
                            {
                                "label": "Intake",
                                "value": "intake"
                            },
                            {
                                "label": "Turret",
                                "value": "turret"
                            }
                        ]
                    },
                    {
                        "label": "Subject",
                        "type": "select",
                        "name": "test",
                        "data_source": "users"
                    }
                ]
            }
        )

        print(open_dialog)

        # Update the message to show that we're in the process of taking their order
        slack_client.chat_update(
            channel=ENTRIES[user_id]["order_channel"],
            ts=message_action["message_ts"],
            text=":pencil: Taking your order...",
            attachments=[]
        )

    elif message_action["type"] == "dialog_submission":
        new_entry = ENTRIES[user_id]
        # Update the message to show that we're in the process of taking their order
        slack_client.chat_update(
            channel=ENTRIES[user_id]["order_channel"],
            ts=new_entry["message_ts"],
            text=":white_check_mark: Order received!",
            attachments=[]
        )
        print(message_action['submission'],message_action['user']['name'])
    return make_response("", 200)

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)))
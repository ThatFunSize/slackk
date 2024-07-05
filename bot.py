import slack_sdk as slack
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, make_response, Response
from slackeventsapi import SlackEventAdapter

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']

@app.route('/en', methods=['POST'])
def en():
    data = request.form
    user_id = data.get('user_id')
    return Response(), 200

COFFEE_ORDERS = {}
#user_id = "U0CAV5XME"
order_dm = client.chat_postMessage(
  #"chat.postMessage",
  as_user=True,
  channel='#bot_test',
  text="I am Coffeebot ::robot_face::, and I\'m here to help bring you fresh coffee :coffee:",
  attachments=[{
    "text": "",
    "callback_id": user_id + "coffee_order_form",
    "color": "#3AA3E3",
    "attachment_type": "default",
    "actions": [{
      "name": "coffee_order",
      "text": ":coffee: Order Coffee",
      "type": "button",
      "value": "coffee_order"
    }]
  }]
)

# Create a new order for this user in the COFFEE_ORDERS dictionary
COFFEE_ORDERS[user_id] = {
    "order_channel": order_dm["channel"],
    "message_ts": "",
    "order": {}
}


@app.route("/slack/message_actions", methods=["POST"])
def message_actions():
    # Parse the request payload
    message_action = json.loads(request.form["payload"])
    user_id = message_action["user"]["id"]

    if message_action["type"] == "interactive_message":
        # Add the message_ts to the user's order info
        COFFEE_ORDERS[user_id]["message_ts"] = message_action["message_ts"]

        # Show the ordering dialog to the user
        open_dialog = client.api_call(
            "dialog.open",
            trigger_id=message_action["trigger_id"],
            dialog={
                "title": "Request a coffee",
                "submit_label": "Submit",
                "callback_id": user_id + "coffee_order_form",
                "elements": [
                    {
                        "label": "Coffee Type",
                        "type": "select",
                        "name": "meal_preferences",
                        "placeholder": "Select a drink",
                        "options": [
                            {
                                "label": "Cappuccino",
                                "value": "cappuccino"
                            },
                            {
                                "label": "Latte",
                                "value": "latte"
                            },
                            {
                                "label": "Pour Over",
                                "value": "pour_over"
                            },
                            {
                                "label": "Cold Brew",
                                "value": "cold_brew"
                            }
                        ]
                    }
                ]
            }
        )

        print(open_dialog)

        # Update the message to show that we're in the process of taking their order
        client.api_call(
            "chat.update",
            channel=COFFEE_ORDERS[user_id]["order_channel"],
            ts=message_action["message_ts"],
            text=":pencil: Taking your order...",
            attachments=[]
        )

    elif message_action["type"] == "dialog_submission":
        coffee_order = COFFEE_ORDERS[user_id]

        # Update the message to show that we're in the process of taking their order
        client.api_call(
            "chat.update",
            channel=COFFEE_ORDERS[user_id]["order_channel"],
            ts=coffee_order["message_ts"],
            text=":white_check_mark: Order received!",
            attachments=[]
        )

    return make_response("", 200)












#@slack_event_adapter.on('message')
#def message(payload):
#    event = payload.get('event', {})
#    channel_id = event.get('channel')
#    user_id = event.get('user')
#    text = event.get('text')
#
#    if BOT_ID != user_id:
#        client.chat_postMessage(channel=channel_id, text=text)


if __name__ == "__main__":
    app.run(debug=True)
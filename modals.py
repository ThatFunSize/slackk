
from pathlib import Path
from dotenv import load_dotenv
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

SLACK_BOT_TOKEN="slackbottokenstring"
SLACK_SIGNING_SECRET="slacksigningsecretstring"

import os
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request

flask_app = Flask(__name__)
app = App(
    token = os.environ['SLACK_TOKEN'],
    signing_secret = os.environ["SIGNING_SECRET"]
)
handler = SlackRequestHandler(app)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

@app.shortcut("en_new")
def handle_shortcuts(ack, body, logger,client):
    ack()
    logger.info(body)
    #print(body)

    res = client.views_open(
        trigger_id=body["trigger_id"],
    view={
	"type": "modal",
    "callback_id": "modal-identifier",
	"submit": {
		"type": "plain_text",
		"text": "Submit"
	},
	"close": {
		"type": "plain_text",
		"text": "Cancel"
	},
	"title": {
		"type": "plain_text",
		"text": "Create New Entry"
	},
	"blocks": [
		{
			"type": "input",
			"element": {
				"type": "multi_users_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select People"
				},
				"action_id": "multi_users_select-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Who Was There?"
			}
		},
		{
			"type": "input",
			"element": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select an item"
				},
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "Drivetrain"
						},
						"value": "drivetrain"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Turret"
						},
						"value": "turret"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Programming"
						},
						"value": "programming"
					}
				],
				"action_id": "static_select-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Category"
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "plain_text_input-action"
			},
			"label": {
				"type": "plain_text",
				"text": "What You Did:"
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "plain_text_input-action"
			},
			"label": {
				"type": "plain_text",
				"text": "What You Learned:"
			}
		},
		{
			"type": "input",
			"element": {
				"type": "radio_buttons",
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "Yes"
						},
						"value": "yes"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "No"
						},
						"value": "no"
					}
				],
				"action_id": "radio_buttons-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Milestone?"
			}
		},
		{
			"type": "input",
			"block_id": "input_block_id",
			"label": {
				"type": "plain_text",
				"text": "Upload Images"
			},
			"element": {
				"type": "file_input",
				"action_id": "file_input_action_id_1",
				"filetypes": [
					"jpg",
					"png",
					"jpeg",
					"heic"
				],
				"max_files": 10
			}
		}
	]
}
    )

@app.view("modal-identifier")
def handle_view_submission(ack, body, logger):
    ack()
    logger.info(body)
    # Process the view submission here
    user = body['user']['id']
    submitted_data = body['view']['state']['values']
    logger.info(f"User {user} submitted data: {submitted_data}")
    print(f"User {user} submitted data: {submitted_data}")


# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
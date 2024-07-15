
from pathlib import Path
from dotenv import load_dotenv
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

import json
import os
import hickle as hkl
import datetime
import requests
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

def open_modal(trigger_id, client):
	res = client.views_open(
		trigger_id=trigger_id,
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
	return res

@app.command("/en")
def handle_command(ack, body, logger, client):
	ack()
	logger.info(body)
	#print(body)
	trigger_id = body["trigger_id"]
	open_modal(trigger_id, client)

@app.view("modal-identifier")
def handle_view_submission(ack, body, logger, client):
	ack()
	logger.info(body)
	#print(body)
	user_id = body['user']['id']
	submitted_data = body['view']['state']['values']
	
	# Keeping track of how many entries
	entry_number = hkl.load('entrys')
	entry_number += 1
	hkl.dump(entry_number, 'entrys')

	# Time when entry was submitted
	entry_time = datetime.datetime.now()
	entry_time = entry_time.strftime('%c')

	user_response = client.users_info(user=user_id)
	if user_response['ok']:
		submitting_user = user_response['user']['real_name']

	user_ids = []
	for block_id, block_data in submitted_data.items():
		for action_id, action_data in block_data.items():
			if action_data['type'] == 'multi_users_select':
				user_ids = action_data['selected_users']

	user_info = []
	for user_id in user_ids:
		response = client.users_info(user=user_id)
		if response['ok']:
			user_info.append({
				response['user']['real_name']
			})       
	
	category = submitted_data['WYrS1']['static_select-action']['selected_option']['text']['text']
	what_you_did = submitted_data['NrWG9']['plain_text_input-action']['value']
	what_you_learned = submitted_data['F8XWy']['plain_text_input-action']['value']
	milestone = submitted_data['dH9JE']['radio_buttons-action']['selected_option']['text']['text']
	files = submitted_data['input_block_id']['file_input_action_id_1']['files']

	submission_data = {
		"entry_num": entry_number,
		"entry_time": entry_time,
		"submitting_user": submitting_user,
		"selected_users": user_info,
		"category": category,
		"what_you_did": what_you_did,
		"what_you_learned": what_you_learned,
		"milestone": milestone,
		"files":[]
	}
	
	for file in files:
		file_info = {
			"file_name": file['name'],
			"file_type": file['filetype'],
			"file_url": file['url_private']
		}
		submission_data["files"].append(file_info)
		
	def convert_sets_to_lists(obj):
		if isinstance(obj, set):
			return list(obj)
		elif isinstance(obj, dict):
			return {k: convert_sets_to_lists(v) for k, v in obj.items()}
		elif isinstance(obj, list):
			return [convert_sets_to_lists(elem) for elem in obj]
		else:
			return obj
	
	submission_data = convert_sets_to_lists(submission_data)
	existing_data = []

	if os.path.exists("submission_data.json"):
		with open('submission_data.json', 'r') as json_file:
			existing_data.clear()
			existing_data.append(json.load(json_file))
	else: 
		existing_data = []
	
	existing_data.append(submission_data)

	#write data to json file
	with open('submission_data.json', 'w') as json_file:
		json.dump(existing_data, json_file, indent = 4)
	




	#Print data for debug
	#submitted_data = body['view']['state']['values']
	#logger.info(f"User {user} submitted data: {submitted_data}")
	print(f"Submitted by: {submitting_user}")
	print(f"Selected Users: {user_info}")
	print(f"Category: {category}")
	print(f"What You Did: {what_you_did}")
	print(f"What You Learned: {what_you_learned}")
	print(f"Milestone: {milestone}")
	


# Start your app
if __name__ == "__main__":
	app.start(port=int(os.environ.get("PORT", 5000)))
optionss = [{
					"value": "mech",
					"text": {
						"type": "plain_text",
						"text": "Mechanical"
					}
				},
				{
					"value": "prog",
					"text": {
						"type": "plain_text",
						"text": "Programming"
					}
				},
				{
					"value": "outreach",
					"text": {
						"type": "plain_text",
						"text": "Outreach"
					}
				}]
print(optionss)
inn = "testing"
n = inn.lower()
r = inn.capitalize()
appending = {
					"value": n,
					"text": {
						"type": "plain_text",
						"text": r
					}
				}
optionss.append(appending)
print(optionss)
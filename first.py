import hickle as hkl

#entry_number = hkl.load('entrys')
mech_options = [{
					"value": "drivetrain",
					"text": {
						"type": "plain_text",
						"text": "Drivetrain"
					}
				}]
hkl.dump(mech_options, 'mech_cat')
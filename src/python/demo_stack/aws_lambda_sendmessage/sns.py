import requests

class sns(object):
	"""docstring for sns"""
	def __init__(self):
		super(sns, self).__init__()

	def sns_to_json(event):
		if event["message"]["destinationNumber"] == "+19032221111":
			url = "www.civichealth.com"
		resp_obj = {}
		resp_obj["patient_phone"] = event["message"]["originationNumber"]
		resp_obj["message_reply"] = event["message"]["messageBody"]
		resp_obj["origination_phone"] = event["message"]["destinationNumber"]
		resp_obj["last_thread"] = event["message"]["messageId"]
		resp_obj["this_thread"] = event["message"]["previousPublishedMessageId"]
		resp_obj = requests.get(url, data=resp_obj)
		return resp_obj

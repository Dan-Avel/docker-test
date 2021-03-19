import requests, boto3, botocore

pinpoint = boto3.client("pinpoint")
try:
	apps = pinpoint.get_apps()['ApplicationsResponse']['Item']
	print([(i['Id'], f"{i['Name']}") for i in apps])
	print('\n\n')
	acts = pinpoint.get_campaign_activities(ApplicationId='fd93c6bb0bc74e5eb2f6165327b29100', CampaignId='a1f548b9d610477e89504db3c7614f85', PageSize='12')['ActivitiesResponse']['Item']
	print([{"Id":i['Id']} for i in acts])
except botocore.client.ClientError as e:
	print(dir(e))
	print(e.response['Error']['Code'])
	raise e

# read upload file
import_file_locs = {
	"civichealth":{
		"api":"X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\civicImport.csv",
		"pinpoint":"X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\importCivic.csv"
	},
	"cai":{
		"api":"X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\caiImport.csv",
		"pinpoint":"X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\importCAI.csv"
	},
	"both":{
		"api":"X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\bothImport.csv",
		"pinpoint":"X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\importBoth.csv"
	},
}
export_file_locs = []

import_map = [
	"CivicHealthID",
	"AlternateID",
	"IsRepFor",
	"RelationshipToPatient",
	"NameLast",
	"NameFirst",
	"NameMiddle",
	"NamePrefix",
	"NameSuffix",
	"DateOfBirth",
	"ContactPhysicalAddress1",
	"ContactPhysicalAddress2",
	"ContactPhysicalCity",
	"ContactPhysicalState",
	"ContactPhysicalZip",
	"PhoneHome",
	"PhoneCell",
	"PhoneWork",
	"EmailPrimary",
	"EmailAlt",
	"DateOfEntry",
	"RiskCategory",
	"IsPatientReferredBackToClient",
	"PreferredContactMethod",
	"WillUseWebChat",
	"Program",
	"CustomerID"
]

pinpoint_import_headers = [
	"User.UserId",
	"ChannelType",
	"Address",
	"Location.Country"
]

export_map = [
	"ConsumerID",
	"InboundDatetime"
	"InboundMessage",
	"Note",
	"NoteDateTime",
	"OutboundDateTime",
	"OutboundMessage",
	"PatientID"
]


import_object = {}
import_str = ""
export_object = {}
export_str = "User.UserId,ChannelType,Address,Location.Country\n"

# import civic health to pinpoint import format
for consumer in import_file_locs:
	try:
		file = open(import_file_locs[consumer]["api"], "x")
		file.close()
	except FileExistsError as e:
		pass

	with open(import_file_locs[consumer]["api"], "r") as file:
		file.readline().replace("\n", "")
		row = file.readline().replace("\n", "").split(',')
		while row != "":
			if len(row) == 27:
				for i in range(0,len(import_map)):
					import_object[import_map[i]] = row[i]
				export_str += f"{import_object['CivicHealthID']},SMS,+1-{import_object['PhoneCell']},US\n"
				import_object = {}
				row = file.readline().replace("\n", "").split(',')
			else:
				row = ""

	with open(import_file_locs[consumer]["pinpoint"], "w+") as file:
		file.write("")
		file.write(export_str)
	import_object = {}
	import_str = ""
	export_object = {}
	export_str = "User.UserId,ChannelType,Address,Location.Country\n"


# pinpoint response format to civic health export fomat.
response_pinpoint = {
	"Type" : "Notification",
	"MessageId" : "6ec64d38-13f5-5b5a-b4c8-1590ada4b187",
	"TopicArn" : "arn:aws:sns:us-east-1:358627972992:demo-sms-responses",
	"Message" : {
		"originationNumber":"+14199800664",
		"destinationNumber":"+19037410023",
		"messageKeyword":"keyword_358627972992",
		"messageBody":"YES",
		"inboundMessageId":"d6ae7c21-ad2e-465a-8398-c069d6375ec0",
		"previousPublishedMessageId":"bcce2dccea2842cf9ff76ce7021f74fe5e3252d48c4be5fdd2a48df4e4547560"
	},
	"Timestamp" : "2021-02-18T19:12:17.468Z",
	"SignatureVersion" : "1",
	"Signature" : "fe6arb0Y+JAyMKAFLeeS8kv+Jqf8dHUAZo6Lo9cufszm+ErOtSil13+B/H/2oHU11x25/mn7XVj9iMLdiLstIhwDB3u4JYRM/be2TTDc5q+Eob4jNjH6uQeOQ7DAd3QfieYmD4St2LKVpiEE3zu4wHkxShwAnnsjreyNpDbytRYEYVyjj3dOFUUV2LdY6+r8Cp9rEFc2vQfeXAO0vQcHnY1V3pO4Z+r2c5dUPUNL76LNnv+KSCz9neNE0QyrSMQU3B9qsDdbdnTYV0I1rnOo71lC5IMHKfVYfo0oHcpCbtHeMpBbSqtTM1g/dWByDpkSDRewCfnGdIG/ZWkySlf/yg==",
	"SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-010a507c1833636cd94bdb98bd93083a.pem",
	"UnsubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:358627972992:demo-sms-responses:3f325f04-808b-4eba-8b7b-a5e88929188b"
}

if response_pinpoint["TopicArn"] == "arn:aws:sns:us-east-1:358627972992:demo-sms-responses":
	request = {
		"ConsumerID":"",	# How am I getting this? Phone -> (patientID x consumerID) in dynamoDB or Athena
		"PatientID":"",
		"Note":None,	# temporarily null
		"NoteDateTime":None,
		"OutboundMessage":"",	#get message from response_pinpoint["previousPublishedMessageId"]
		"OutboundDateTime":"",
		"InboundMessage":response_pinpoint["Message"]["messageBody"],
		"InboundDatetime":response_pinpoint["Timestamp"]
	}

	# get previous message

	# set OutboundMessage
	# set OutboundDateTime
	# set ConsumerID
	# set PatientID

	# write json to file
	
	# requests.get("https://community.civichealth.com/CAI_API/Api/Contacts", data=request)
import os, sys, time, botocore, boto3, json
from demo_stack.aws_lambda_sendmessage.send_message import *
import demo_stack.aws_lambda_sendmessage.s3

# create dependencies
demo_pinpoint = pinpoint()
demo_s3 = s3.s3()
demo_iam = iam.iam()
dynamoDB = boto3.client('dynamodb')

number_of_projects = 10
segment_import_file = "C:\\Users\\javelares\\Documents\\ChromeDownloads\\Hassan Text_4306\\Hassan Text_4306.csv"
# segment_import_file = "X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import.csv" # Testing import file
data = []

with open(segment_import_file, 'r') as file:
	entry = file.readline().replace("\n", "").split(',')
	###
	# Hassan import
	###
	data.append({
		"ConsumerId":entry[28],
		"Pc":entry[19],
		"t":1,
		"Po":None,
		"PhoneHash":None,
		"PhoneKey":None
	})


	###
	#	Strategic Healthcare import
	###
	# data.append({
	# 	"ConsumerId":file[0],
	# 	"Pc":file[16],
	# 	"t":"1",
	# 	"Po":None,
	# 	"PhoneHash":None,
	# 	"PhoneKey":None
	# })


def fetch_row(TableName, PhoneHash=None, PhoneKey=None, ConsumerId=None, Pc=None, Po=None, t=None):
	if TableName == hash_table_name:
		if PhoneHash != None and PhoneKey != None:
			return dynamoDB.get_item(
				TableName=TableName,
				Key={
					'PhoneHash':{
						'N':f'{PhoneHash}'
					},
					'PhoneKey':{
						'N':f'{PhoneKey}'
					}
				}
			)
		else:
			return dynamoDB.scan({})
	elif TableName == id_table_name:
		if ConsumerId != None:
			return dynamoDB.get_item(
				TableName=TableName,
				Key={
					'ConsumerId':{
						'N':f'{ConsumerId}'
					}
				}
			)
		else:
			return dynamoDB.get_item(
				TableName=TableName,
				Key={
					'Pc':{
						'N':f'{Pc}'
					},
					'Po':{
						'N':f'{Po}'
					}
				}
			)

def fetch_hash_and_key(Pc,Po,t):
	pass

def fetch_Pco_and_time(mhash, key):
	pass

###
#	(Pc, Po, t) This ties the CID to (hash, key) combo.
#	(Hash,key) allows for faster indexing of phone history.
#	this function.generates (PhoneHash, PhoneKey)
###
def get_hash_and_key(Pc, Po, t):
	for i in list(filter(lambda x: x["Pc"] == Pc and x["Po"] == Po and x["t"] == t, data)):
		if (i["Pc"] == Pc) and (i["Po"] == Po) and (i["t"] == t):
			return {"PhoneHash":i["PhoneHash"], "PhoneKey":i["PhoneKey"]}

def get_Pco_and_time(mhash, key):
	for i in list(filter(lambda x: x["PhoneHash"] == mhash, data)):
		if (i["PhoneKey"] == key):
			return i

def set_hash_and_key(Pc, Po, t):	# if Pc, Po combo isn't already a latest/current entry
	resp_val = {
		"Pc":Pc,
		"t":t,
		"Po":Po,
		"PhoneHash": int(f"{Pc}{Po}") % int(t),
		"PhoneKey": len(list(filter(lambda x: x['PhoneHash']==int(f"{Pc}{Po}") % int(t), data)))
	}
	return resp_val

#create a dynamoDB table with a name as param.
def create_table(TableName="my_table", TableType="", KeySchema=None):
	KeySchema = {}
	if TableType =="hash":
		KeySchema=[
			{
				'AttributeName': 'PhoneHash',
				'KeyType': 'HASH'
			},
			{
				'AttributeName': 'PhoneKey',
				'KeyType': 'RANGE'
			}
		]
	elif TableType == "id":
		KeySchema=[
			{
				'AttributeName': 'Pc',
				'KeyType': 'HASH'
			},
			{
				'AttributeName': 'Po',
				'KeyType': 'RANGE'
			}
		]
	else:
		raise Exception("KeySchema not found.")
	AttributeDefinitions = []
	for i in range(len(KeySchema)):
		AttributeDefinitions.append({
			"AttributeName":KeySchema[i]['AttributeName'],
			"AttributeType":"N"
		})
	new_table = dynamoDB.create_table(
		AttributeDefinitions=AttributeDefinitions,
		TableName=TableName,
		KeySchema=KeySchema,
		BillingMode='PAY_PER_REQUEST',
		StreamSpecification={
			'StreamEnabled': False
		}
	)
	print(new_table)
	return new_table

for i in range(0, 1):
	try:
		# Create Project
		demo_project = demo_pinpoint.create_project()
		print("project:", demo_project.name)

		# create segment.
		if i%2 == 0:
			#prepFile
			# User.UserId,ChannelType,Address,Location.Country
			with open(segment_import_file, 'r+') as file:
				entry = file.readline().replace("\n", "").split(',')
				row = "User.UserId,ChannelType,Address,Location.Country\n"
				print(len(entry))
				count = 0
				while  len(entry) > 19:
					row += f"hasan-{entry[0]}{entry[1]}".replace("\"", "")
					if len(entry[18]) >= 7:
						row += f",SMS,+1-{entry[18][1:4]}".replace("\"", "")
						row += f"-{entry[18][4:7]}-"
						row += f"{entry[18][7:]},US\n".replace("\"", "")
					row.replace("\"", "")
					if count % 10 == 0:
						with open("X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import.csv", "a") as file1:
							file1.write(f"{row}")
						demo_segment = demo_pinpoint.create_segment_import_local(fileLocation="X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import.csv", s3client=demo_s3.client, s3resource=demo_s3.resource, iam=demo_iam)
					elif count % 10 == 1:
						with open("X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import1.csv", "a") as file1:
							file1.write(f"{row}")
						demo_segment = demo_pinpoint.create_segment_import_local(fileLocation="X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import1.csv", s3client=demo_s3.client, s3resource=demo_s3.resource, iam=demo_iam)
					elif count % 10 == 2:
						with open("X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import2.csv", "a") as file1:
							file1.write(f"{row}")
						demo_segment = demo_pinpoint.create_segment_import_local(fileLocation="X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import2.csv", s3client=demo_s3.client, s3resource=demo_s3.resource, iam=demo_iam)
					elif count % 10 == 3:
						with open("X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import3.csv", "a") as file1:
							file1.write(f"{row}")
						demo_segment = demo_pinpoint.create_segment_import_local(fileLocation="X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import3.csv", s3client=demo_s3.client, s3resource=demo_s3.resource, iam=demo_iam)
					elif count % 10 == 4:
						with open("X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import4.csv", "a") as file1:
							file1.write(f"{row}")
						demo_segment = demo_pinpoint.create_segment_import_local(fileLocation="X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import4.csv", s3client=demo_s3.client, s3resource=demo_s3.resource, iam=demo_iam)
					elif count % 10 == 5:
						with open("X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import5.csv", "a") as file1:
							file1.write(f"{row}")
						demo_segment = demo_pinpoint.create_segment_import_local(fileLocation="X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import5.csv", s3client=demo_s3.client, s3resource=demo_s3.resource, iam=demo_iam)
					elif count % 10 == 6:
						with open("X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import6.csv", "a") as file1:
							file1.write(f"{row}")
						demo_segment = demo_pinpoint.create_segment_import_local(fileLocation="X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import6.csv", s3client=demo_s3.client, s3resource=demo_s3.resource, iam=demo_iam)
					elif count % 10 == 7:
						with open("X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import7.csv", "a") as file1:
							file1.write(f"{row}")
						demo_segment = demo_pinpoint.create_segment_import_local(fileLocation="X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import7.csv", s3client=demo_s3.client, s3resource=demo_s3.resource, iam=demo_iam)
					elif count % 10 == 8:
						with open("X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import8.csv", "a") as file1:
							file1.write(f"{row}")
						demo_segment = demo_pinpoint.create_segment_import_local(fileLocation="X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import8.csv", s3client=demo_s3.client, s3resource=demo_s3.resource, iam=demo_iam)
					elif count % 10 == 9:
						with open("X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import9.csv", "a") as file1:
							file1.write(f"{row}")
						demo_segment = demo_pinpoint.create_segment_import_local(fileLocation="X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import9.csv", s3client=demo_s3.client, s3resource=demo_s3.resource, iam=demo_iam)
					if count % 1000 == 1:
						print(row)
					count+=1
					entry = file.readline().replace("\n", "").split(',')
					row = ""
		else:
			demo_segment = demo_pinpoint.create_segment_import_local(fileLocation=segemnt_import_folder, s3client=demo_s3.client, s3resource=demo_s3.resource, iam=demo_iam)
		print("segment", demo_segment['ImportJobResponse']['Definition']['SegmentId'])

		# create & schedule campaign
		time.sleep(1200)
		demo_campaign = demo_pinpoint.create_campaign(name=demo_project.name, SegmentId=demo_segment['ImportJobResponse']['Definition']['SegmentId'])
		print("campaign",demo_campaign)

		# steps to update lambda for each campaign. it should be 1 to 1 for numbers to campaigns.
		# 1. deploy json transform lambda triggers next lambda. (built needs deployment.)
		# 2. bind SNS subscription.
		# 3. deploy url endpoint request lambda from this script.
		# 4. check endpoint.

	except botocore.client.ClientError as e:
		print(e.response)
		print(f"rollback {demo_project.name} : Error, {e.response['Error']['Code']} : {e.response['Error']['Message']}")
		# del_resp = demo_pinpoint.delete_project(app_id=demo_project.id)
		raise e
	except Exception as e:
		raise e
	finally:
		time.sleep(10)
		for i in demo_pinpoint.projects:
			try:
				# resp = demo_pinpoint.delete_project(app_id=i.id)
				print(f"deleted {i.name}")
			except botocore.client.ClientError as e:
				print(f"could not delete {i.name}")
				pass
			finally:
				pass


# 1 list lambda projects from local folder
# if os.getcwd() != "X:\\Documents\\Python":
# 	os.chdir("X:\\Documents\\Python")

# all aws-lambda-* folders
# lambdas_found = 0
# for entry in os.scandir():
# 	if entry.is_dir() & entry.name.startswith("aws-lambda-*"):
# 		if lambdas_found < 1:
# 			print("select one: \n")
# 		print("{lambdas_found}) entry.name")

# if lambdas_found < 1:
# 	print(f"No lambdas found in dir, '{os.getcwd()}'.")

# deploy lambda
# run x times



###
#	-------------------------------
#	Summary of Data transformations
#	-------------------------------

# CivicHealth ID,Alternate ID,IsRepFor,Relationship To Patient,LastName,FirstName,MiddleName,Prefix,Suffix,DOB,ContactPhysicalAddress1,ContactPhysicalAddress2,ContactPhysicalCity,PhysicalState,ContactPhysicalZip,Home Phone,Cell Phone,Work Phone,Email,ALT Email,Date Of Entry,Risk Category,Patient Referred back to Client(Flag),Preferred Contact Method,Will Use Web Chat?,Program/Client,CustomerID
# 10200000,M2456930000,No,Self,Avelares,Daniel,J,,- None Selected -,07/22/1973,920 Harbor Street,Appt 2B,Defiance,OH,45202,000-000-0000,419-388-8164,000-000-0000,jose.avelares@email.com,javelares@email.com,02/23/5/2020,,TRUE,SMS,Yes,CAI Case Management,CAI_Demo

# after Import by my script

# User.UserId,ChannelType,Address,Location.Country
# demo-1,SMS,+1-419-388-8164,US
# demo-adam,SMS,+1-419-980-0664,US
# demo-jeff-1,SMS,+1-419-789-2100,US
# demo-jeff-2,SMS,+1-260-572-9385,US

# after message sent/received by aws

# {
# 	"Type" : "Notification",
# 	"MessageId" : "88456dd2-7b36-5dcb-a5af-356a1f7f5a4d",
# 	"TopicArn" : "arn:aws:sns:us-east-1:358627972992:demo-sms-responses",
# 	"Message" : {
# 		'originationNumber':'+14197892100',
# 		'destinationNumber':'+19037410023',
# 		'messageKeyword':'keyword_358627972992',
# 		'messageBody':'No',
# 		'inboundMessageId':'6387f2a3-4624-4b76-a042-c5dcad8e7eab',
# 		'previousPublishedMessageId':'b97dbad454ad4abba4e04c03e89e72ba96b76a46703c61e674356695c043f036'
# 	},
# 	"Timestamp" : "2021-03-02T16:04:25.076Z",
# 	"SignatureVersion" : "1",
# 	"Signature" : "AUcmr0b5XkJe207qpG2wIHpTOyM8UqBrXKEiqpzBPGNJEBwUAXq0N707arKp9f4lh+aN8VP//gjsbFkNC/ty5EYJGWWkixYhEdR0D43CJJ68VUdxYhd7Iru5ktyyfqm4jdE4q2K/ZKPMz/E1MdpU4GgTmfRTKlvMOw+QQOQqUPkBb+5UGm1YCWVN8Trr7xxcWn0RLTzvNv22W76nJK3PrSfBntr9RVMjGtcHOGqFC+8KxxH9MUcAd1QSjTee6eZENoO5OYpreR8m07LhbXSGTtnJrwVvOBrEcDLbElP7pLh9JfWDe45eaEG5Cn2lwRDzh8dB9kOOKZr9/JmM38lWPA==",
# 	"SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-010a507c1833636cd94bdb98bd93083a.pem",
# 	"UnsubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:358627972992:demo-sms-responses:3f325f04-808b-4eba-8b7b-a5e88929188b"
# }

# After Lambda listening to SNS topic for "arn:aws:sns:us-east-1:358627972992:*-sms-*"

# {
# 	"customerID": "ABC123!@$",
# 	"patientID": "12345",
# 	"contactNote": "Called Patient",
# 	"contactNoteDateTime": "01/28/2021 03:15 PM"
# }
###
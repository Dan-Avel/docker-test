import boto3, random, string, os, botocore, json, time, sys, traceback
from datetime import datetime
from datetime import timedelta
from . import s3
from . import iam

pipo = boto3.client('pinpoint')

def format_exception(e):
	exception_list = traceback.format_stack()
	exception_list = exception_list[:-2]
	exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
	exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

	exception_str = "Traceback (most recent call last):\n"
	exception_str += "".join(exception_list)
	# Removing the last \n
	exception_str = exception_str[:-1]

	return exception_str

def get_random(cnt:int=1) -> str:
	return "".join(random.choice(string.ascii_letters) for _ in range(cnt))

def msg_response_to_strjson(msg):
	return ""

def strjson_to_url(strjson):
	endpoint_response = {}
	return endpoint_response

class pinpoint_project(object):
	"""AWS Pinpoint project"""
	def __init__(self, client_project=None):
		super(pinpoint_project, self).__init__()
		if client_project == None:
			self._client_project = pipo.create_app(CreateApplicationRequest={'Name':"demo-"+"".join(random.choice(string.ascii_letters) for _ in range(12)), 'tags':{'stage':'demo'}})["ApplicationResponse"]
		else:
			self._client_project = client_project
		self.name = self._client_project["Name"]
		self.tags = self._client_project["tags"]
		self.arn = self._client_project["Arn"]
		self.id = self._client_project["Id"]
		self.campaigns = []

	def __str__(self):
		return f"{self.id}, {self.arn}, {self.name}, {self.tags}"

class pinpoint_campaign(object):
	"""AWS Pinpoint campaign"""
	def __init__(self, arg):
		super(pinpoint_campaign, self).__init__()
		self.arg = arg

class pinpoint_segment(object):
	"""AWS Pinpoint segment"""
	def __init__(self, arg):
		super(pinpoint_segment, self).__init__()
		self.arg = arg

class pinpoint_message(object):
	"""AWS Pinpoint message"""
	def __init__(self, arg):
		super(pinpoint_message, self).__init__()
		self.arg = arg

class pinpoint(object):
	"""Python Pinpoint client wrapper"""
	def __init__(self, client:boto3.client=pipo):
		super(pinpoint, self).__init__()
		self.client = client
		self.projects = []

	def create_campaign():
		# get project
		# create campaign in aws
		pipo.create_campaign()
		# assign new local campaign
		# return aws create campaign response
		pass

	def create_project(self, project:dict=None) -> pinpoint_project:
		project = pinpoint_project(client_project=project)
		self.projects.append(project)
		return project

	def delete_project(self, name=None, app_id=None, arn=None):
		if not name is None:
			app_filter = filter(lambda x: (x.name == name), self.projects)
			if len(list(app_filter)) == 1:
				for item in app_filter:
					app_id = item.id
			else:
				raise Exception("project does not exist in memory, cannot reference by name.")
		elif not app_id is None:
			pass
		elif not arn is None:
			app_id = 0
		else:
			raise Exception("No identifier provided.")
		try:
			resp_obj = self.client.delete_app(ApplicationId=str(app_id))
			self.projects = list(filter(lambda x:x.id == app_id, self.projects))
		except botocore.client.ClientError as e:
			raise
		return resp_obj


	def send_message(self, number="4193888164", message="Run. Now."):
		pass

	def create_segment_import_s3(self, s3Bucket=None, Key:string=None):
		# if key is not none check for key's existance
			# then wrap single item in list.
		# else every file in the bucket is added to the list for import.
		ImportJobRequest={
			'DefineSegment': True,
			'Format': 'CSV',
			'RegisterEndpoints': True,
			'RoleArn': '', # create a role for this
			'S3Url': f"s3://{s3Bucket}/{Key}",
			'SegmentId': name,
			'SegmentName': name
		}
		return self.client.create_import_job(ApplicationId=ApplicationId, ImportJobRequest=ImportJobRequest)

	def create_segment_import_local(self, s3resource=None, s3client=None, iam:iam.iam=None, fileLocation:string="X:\\Documents\\Python\\aws-concurrent\\demo_stack\\aws_lambda_sendmessage\\import.csv", name=None, ApplicationId=None):
		try:
			files = []
			resp_obj = None
			if s3resource == None or s3client == None:
				raise ValueError("s3resource must be defined.")
			if ApplicationId is None:
				ApplicationId = self.projects[-1].id
			if name is None:
				name=list(filter(lambda x: x.id == ApplicationId, self.projects))[0].name
			if fileLocation is None:
				fileLocation = "C:"
			if os.path.isdir(fileLocation):
				for file in os.listdir(fileLocation):
					file = os.path.join(fileLocation,file)
					if os.path.isfile(file):
						files.append(file)
			else:
				files.append(fileLocation)

			# create s3 bucket
			bucket_name = str("".join(random.choice(string.ascii_letters) for _ in range(16)).lower())
			temp_bucket = s3resource.create_bucket(Bucket=bucket_name)
			
			key = "import.csv"
			temp_object = temp_bucket.Object(f"{key}")
			temp_object.upload_file(fileLocation)

			for file in files:
				role_name = "dZzYjh"
				trust_policy = {
					"Version": "2012-10-17",
					"Statement": [
						{
							"Sid": "AllowUserToImportEndpointDefinitions",
							"Effect": "Allow",
							"Principal":{
								"Service":["pinpoint.amazonaws.com"]
							},
							"Action": "sts:AssumeRole"
						}
					]
				}
				role_obj = iam.client.get_role(RoleName=role_name)
				print(role_obj)
				# AmazonS3ReadOnlyAccess < --- Attach this policy
				iam.client.attach_role_policy(RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess")
				# print("role:::", role_obj)
				ImportJobRequest={
					'S3Url': f"s3://{temp_bucket.name}/{key}",
					'RoleArn': role_obj["Role"]["Arn"], # reference role created here
					'Format': 'CSV',
					'RegisterEndpoints': True,
					'DefineSegment': True
				}
				time.sleep(3)
				print(role_obj["Role"]["Arn"])
				print("****************")
				print("projid",ApplicationId)
				# is job id in the response?
				resp_obj = self.client.create_import_job(ApplicationId=ApplicationId, ImportJobRequest=ImportJobRequest)
				print("****************")
		except botocore.client.ClientError as e:
			print("error..")
			print("Printing only the traceback above the current stack frame")
			print("".join(traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])))
			print("Printing the full traceback as if we had not caught it here...")
			# print(type(resp_import_job), resp_import_job)
			print(format_exception(e))
			raise
		finally:
			the_buck = s3resource.Bucket(temp_bucket.name)
			# temp_object.delete()
			# the_buck.delete()
			print("respobj",resp_obj)
			print("bucket ",temp_bucket.name)
			return resp_obj

	def create_segment(self, WriteSegmentRequest=None, ApplicationId=None):
		if ApplicationId is None:
			ApplicationId = self.projects[-1].id

		if WriteSegmentRequest is None:
			WriteSegmentRequest = {
				"Name": list(filter(lambda x: x.id == ApplicationId, self.projects))[0].name,
				"tags":{},
				"SegmentGroups": {
					"Groups": [
						{
							"SourceSegments":[],
							"SourceType": "ALL",
							"Type": "ANY"
						}
					],
					"Include":"ALL"
				}
			}

		return self.client.create_segment(WriteSegmentRequest=WriteSegmentRequest,
		ApplicationId=ApplicationId)

	def create_campaign(self, name=None, app_id=None, SegmentId=None):
		print(name)
		if not name is None:
			app = next((item for item in self.projects if item.name == name), None)
			if app is not None:
				app_id = app.id
			else:
				raise Exception("project does not exist in memory, cannot reference by name.")
		else:
			raise Exception("No identifier provided.")
		print(app_id, len(self.projects))
		target_project = next((item for item in self.projects if item.id == app_id), None)
		print((datetime.now() + timedelta(minutes = 305)).strftime("%Y-%m-%dT%H:%M:59.999Z"))
		time.sleep(60)
		print(SegmentId)
		return self.client.create_campaign(ApplicationId=target_project.id, WriteCampaignRequest={
			'SegmentId': SegmentId,
			'Name': f'demo-{get_random(6)}',
			'Schedule': {
				'StartTime':(datetime.now() + timedelta(minutes = 340)).strftime("%Y-%m-%dT%H:%M:59.999Z"),
				'EndTime':(datetime.now() + timedelta(days = 1)).strftime("%Y-12-31T%H:%M:59.999Z"),
				'Frequency': 'ONCE',
				'Timezone': 'UTC-05'
			},
			'MessageConfiguration': {
				'SMSMessage': {
					'Body': 'Sen. Hassan voted to give convicted felons - like Cop-Killer Michael Addison - $1400 of YOUR tax dollars! Help defeat Hassan and Flip the Senate: DefeatHassan.org',
					'MessageType': 'TRANSACTIONAL'
					# 'MessageType': 'PROMOTIONAL'
					# 'OriginationNumber':'+19037410023'
				}
			}
		})


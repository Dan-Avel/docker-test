import boto3, botocore, json

def get_random(cnt:int=1):
	return "".join(random.choice(string.ascii_letters) for _ in range(cnt))

class iam(object):
	"""docstring for iam"""
	def __init__(self):
		super(iam, self).__init__()
		self.client = boto3.client("iam")
		self.roles = []

	def create_role(self, RoleName:str="NewRole", PolicyDoc:dict={}):
		if RoleName == None:
			RoleName = get_random()
		try:
			resp_obj = self.client.create_role(RoleName=RoleName, AssumeRolePolicyDocument=json.dumps(PolicyDoc))
			print("creating: Role ",resp_obj)#ExportImportRole)
			self.roles.append(resp_obj['Role'])
			return resp_obj
		except botocore.client.ClientError as e:
			print("iam.create_role Error:", e)
			raise e

	def assign_role():
		pass

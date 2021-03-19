import boto3, botocore

class s3(object):
	def __init__(self):
		super(s3, self).__init__()
		self.resource = boto3.resource("s3")
		self.client = boto3.client('s3')
		self.buckets = self.client.list_buckets()

	def create_bucket(bucket_name):
		resp_obj = s3resource.create_bucket(Bucket=bucket_name)
		self.buckets.append(resp_obj)
		return resp_obj

	def delete_bucket(bucket_name):
		# delete objects in bucket
		# delete bucket in S3
		# remove bucket from list of buckets
		return self.client.delete_bucket(bucket_name)

	def fetch_buckets(bucket_name):
		pass
		# refresh bucket and object data for self.buckets.
		# no return value


class s3Bucket(object):
	def __init__(self, name:str, s3client:botocore.client):
		super(s3Bucket, self).__init__()
		self.name = name
		self.arn = ""
		self.objects = self.client.list_objects()
		self.client = s3client

	def create_object(self, key):
		resp_obj = bucket.Object(key)
		self.objects.append(resp_obj)
		return resp_obj

	def get_bucket(self):
		pass
		# return botocore.bucket


class s3object(object):
	def __init__(self, bucket:s3Bucket, name:str, s3client:botocore.client):
		super(s3object, self).__init__()
		self.bucket = bucket
		self.name = name
		self.client = s3client

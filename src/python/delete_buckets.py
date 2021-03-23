import os, sys, time, botocore, boto3
from demo_stack.aws_lambda_sendmessage.send_message import *
import demo_stack.aws_lambda_sendmessage.s3

demo_pinpoint = pinpoint()
demo_s3 = s3.s3()
demo_iam = iam.iam()
app_exceptions = []
bucket_exceptions = []

for bucket in demo_s3.client.list_buckets()["Buckets"]:
	if len(bucket['Name']) == 16:
		if bucket['Name'] not in bucket_exceptions:
			print(bucket["Name"])
			demo_s3.client.delete_object(Bucket=f"{bucket['Name']}", Key="import.csv")
			demo_s3.client.delete_bucket(Bucket=f"{bucket['Name']}")
			time.sleep(1)
count = 1
while count > 0:
	count = 0
	for app in demo_pinpoint.client.get_apps()["ApplicationsResponse"]["Item"]:
		if "demo-" in app["Name"]:
			print(app["Name"])
			if app["Name"] not in app_exceptions:
				demo_pinpoint.client.delete_app(ApplicationId=app["Id"])
import boto3, json, time

dynamoDB = boto3.client('dynamodb')

data = [
	{
		"ConsumerId":"12145",
		"Pc":"1245",
		"t":"7",
		"Po":"1419",
		"PhoneHash":"",
		"PhoneKey":""
	},
	{
		"ConsumerId":"12145",
		"Pc":"1245",
		"t":"1",
		"Po":"1212",
		"PhoneHash":"",
		"PhoneKey":""
	},
	{
		"ConsumerId":"12145",
		"Pc":"1245",
		"t":"2",
		"Po":"1305",
		"PhoneHash":"",
		"PhoneKey":""
	},
	{
		"ConsumerId":"12145",
		"Pc":"1245",
		"t":"3",
		"Po":"1782",
		"PhoneHash":"",
		"PhoneKey":""
	},
	{
		"ConsumerId":"12145",
		"Pc":"1245",
		"t":"4",
		"Po":"1419",
		"PhoneHash":"",
		"PhoneKey":""
	},
	{
		"ConsumerId":"12145",
		"Pc":"1245",
		"t":"5",
		"Po":"1422",
		"PhoneHash":"",
		"PhoneKey":""
	},
	{
		"ConsumerId":"12145",
		"Pc":"1245",
		"t":"6",
		"Po":"1855",
		"PhoneHash":"",
		"PhoneKey":""
	},
	{
		"ConsumerId":"12144",
		"Pc":"1246",
		"t":"7",
		"Po":"1419",
		"PhoneHash":"",
		"PhoneKey":""
	},
	{
		"ConsumerId":"12144",
		"Pc":"1246",
		"t":"1",
		"Po":"1212",
		"PhoneHash":"",
		"PhoneKey":""
	},
	{
		"ConsumerId":"12144",
		"Pc":"1246",
		"t":"2",
		"Po":"1503",
		"PhoneHash":"",
		"PhoneKey":""
	},
	{
		"ConsumerId":"12144",
		"Pc":"1246",
		"t":"3",
		"Po":"1906",
		"PhoneHash":"",
		"PhoneKey":""
	},
	{
		"ConsumerId":"12144",
		"Pc":"1246",
		"t":"4",
		"Po":"1418",
		"PhoneHash":"",
		"PhoneKey":""
	},
	{
		"ConsumerId":"12144",
		"Pc":"1246",
		"t":"5",
		"Po":"1422",
		"PhoneHash":"",
		"PhoneKey":""
	},
	{
		"ConsumerId":"12144",
		"Pc":"1246",
		"t":"6",
		"Po":"1855",
		"PhoneHash":"",
		"PhoneKey":""
	}
]

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

###
#	(Pc, Po, t) This ties the CID to (hash, key) combo.
#	(Hash,key) allows for faster indexing of phone history.
#	this function.generates (PhoneHash, PhoneKey)
###
def get_hash_and_key(Pc, Po, t):
	for i in list(filter(lambda x: x["Pc"] == Pc and x["Po"] == Po and x["t"] == t, data)):
		if (i["Pc"] == Pc) and (i["Po"] == Po) and (i["t"] == t):
			return {"PhoneHash":i["PhoneHash"], "PhoneKey":i["PhoneKey"]}

def fetch_Pco_and_time(mhash, key):
	pass

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

hash_table_name = "civic_health_hash"
id_table_name="civic_health_id"

# create data structures
create_table(TableName=hash_table_name, TableType='hash')
create_table(TableName=id_table_name, TableType='id')

# wait for data structures to provision
for x in range(120):
	print('{0}'.format(x), end="\r")
	time.sleep(1)

index = 0
# Loop through each local data entry
for row in data:
	# generate index identifiers
	cid = row['ConsumerId']
	print(cid)
	row = set_hash_and_key(Pc=row["Pc"], Po=row["Po"], t=row["t"])
	row['ConsumerId'] = cid
	# update indexes in cache
	data[index]["PhoneHash"] = row["PhoneHash"]
	data[index]["PhoneKey"] = row["PhoneKey"]
	# get index from cache
	H_K = get_hash_and_key(Pc=row["Pc"], Po=row["Po"], t=row["t"])
	# populate remote data structures
	hash_table_item = {}
	id_table_item = {}
	for it in row:
		tt = ""
		if isinstance(row[it],str):
			tt = "N"
		elif isinstance(row[it], int):
			tt = "N"

		if it == "ConsumerId":
			id_table_item[it] = json.loads("{"+f'"{tt}":"{row[it]}"'+"}")
		elif it == "PhoneHash" or it == "PhoneKey":
			hash_table_item[it] = json.loads("{"+f'"{tt}":"{row[it]}"'+"}")
		else:
			hash_table_item[it] = json.loads("{"+f'"{tt}":"{row[it]}"'+"}")
			id_table_item[it] = json.loads("{"+f'"{tt}":"{row[it]}"'+"}")

	print("Puts")
	print(hash_table_item)
	dynamoDB.put_item(TableName=hash_table_name, Item=hash_table_item)
	print(id_table_item)
	dynamoDB.put_item(TableName=id_table_name, Item=id_table_item)

	print("Gets")
	# fetch remote data with index from cache.
	fetch_hash_table_result = fetch_row(TableName=hash_table_name, PhoneHash=H_K['PhoneHash'], PhoneKey=H_K['PhoneKey'])
	# assert results
	print(fetch_hash_table_result['Item'])
	# fetch romote data with generated index.
	fetch_hash_table_result = fetch_row(TableName=hash_table_name, PhoneHash=row['PhoneHash'], PhoneKey=row['PhoneKey'])
	# assert results
	print(fetch_hash_table_result['Item'])
	# # fetch romote data with consumer id.
	# fetch_id_table_result = fetch_row(TableName=id_table_name, ConsumerId=row['ConsumerId'])
	# # assert results
	# print(fetch_id_table_result['Item'])

	# fetch_id_table_result = fetch_row(TableName=hash_table_name, Pc=row['Pc'], Po=row['Po'], t=row['t'])
	# print(fetch_id_table_result['Item'])

	fetch_hash_table_result = fetch_row(TableName=id_table_name, Pc=row['Pc'], Po=row['Po'], t=row['t'])
	print(fetch_hash_table_result['Item'])
	index += 1	# next local data entry.
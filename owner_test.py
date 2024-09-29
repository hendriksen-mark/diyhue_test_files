import uuid
username = str(uuid.uuid1())
print(username)
username = username.replace('-', '')
print(username)

result = {}
result["owner"] = {"rid": username, "rtype": "device"}

#print(type(result["owner"]))
#print(type(username))

#         2aedac84        -    6d0d              -    11ef               -    8e97              -    acde48001122
apiuser = username[:8] + '-' + username[8:12] + '-' + username[12:16] + '-' + username[16:20]+ '-' + username[20:]

print(apiuser)
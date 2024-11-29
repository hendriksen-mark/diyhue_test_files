postDict = {"protocol": "", "config": ""}


if "ip" in postDict and "protocol" in postDict and "config" in postDict:
    print(postDict)

if all(i in postDict for i in ["ip", "protocol", "config"]):
    print(postDict)
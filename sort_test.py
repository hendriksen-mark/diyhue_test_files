from datetime import datetime
 
# Initialising list of dictionary"time": {"hour": 7, "minute": 0, "second": 0},
ini_list = [{"name":"akshat", "time": {"hour": 10, "minute": 10, "second": 0},},#4
            {"name":"vashu", "time": {"hour": 7, "minute": 30, "second": 0},},#2
            {"name":"manjeet", "time": {"hour": 7, "minute": 40, "second": 0},},#1
            {"name":"nikhil", "time": {"hour": 9, "minute": 20, "second": 0},}]#3

slots = [{"start_time": {"kind": "time", "time": {"hour": 7, "minute": 0, "second": 0}}, "target": {"rid": "43b3b7c2-eb23-4e72-9628-20d73507d7bc", "rtype": "scene"}}, {"start_time": {"kind": "time", "time": {"hour": 10, "minute": 0, "second": 0}}, "target": {"rid": "f2ab39ae-2f6c-4d78-a67e-08e08b2bad16", "rtype": "scene"}}, {"start_time": {"kind": "sunset"}, "target": {"rid": "66d4471f-6b1a-4151-a38c-f421d07e2b13", "rtype": "scene"}}, {"start_time": {"kind": "time", "time": {"hour": 20, "minute": 0, "second": 0}}, "target": {"rid": "b1fb3678-aa27-4da0-8baf-10b42f46d820", "rtype": "scene"}}, {"start_time": {"kind": "time", "time": {"hour": 22, "minute": 0, "second": 0}}, "target": {"rid": "0e098d29-2ccd-4043-8de4-30412637cd25", "rtype": "scene"}}, {"start_time": {"kind": "time", "time": {"hour": 0, "minute": 0, "second": 0}}, "target": {"rid": "d564f1fd-cb53-4de6-90ad-96502a044377", "rtype": "scene"}}]
                 
# printing initial list
#print ("initial list : ", str(ini_list))
 
# code to sort list on date
#slots.sort(key = lambda x: datetime.strptime(str(x["start_time"]["time"]), "{'hour': %H, 'minute': %M, 'second': %S}"))
 
# printing final list
#print ("result", str(slots[0]["start_time"]["time"]))
print(datetime.strptime(str(slots[0]["start_time"]["time"]), "{'hour': %H, 'minute': %M, 'second': %S}"))
from datetime import datetime
 
# Initialising list of dictionary
ini_list = [{'name':'akshat', 'd.o.b':'1997-09-01'},
            {'name':'vashu', 'd.o.b':'1997-08-19'},
            {'name':'manjeet', 'd.o.b':'1997-01-04'},
            {'name':'nikhil', 'd.o.b':'1997-09-13'}]
                 
# printing initial list
print ("initial list : ", str(ini_list))
 
# code to sort list on date
ini_list.sort(key = lambda x: datetime.strptime(x['d.o.b'], '%Y-%m-%d'))
 
# printing final list
print ("result", str(ini_list))
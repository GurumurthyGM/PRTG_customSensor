import json
import sys

import requests
from paepy.ChannelDefinition import CustomSensorResult


try:
    data = json.loads(sys.argv[1])
except:
    data = {"host":"172.25.23.34","params":"SFP-1-1-1:-Distance,-Wavelength;SFP-1-2-1:-SI,-Distance"}

ip = data['host']

username = data.get('linuxloginusername', 'DIAGUSER')
password = data.get('linuxloginpassword', 'j72e#05t')




if len(req_obj) == 0:
    result = CustomSensorResult()
    
    result.add_error("Parameters_required = Objects seperated by ';' and attributes seperated by ',' : object_name1:Attribute1,Attribute2;object_name2:Attribute3,Attribute4 (@ Additional Parameters while adding sensor)")    
    print(result.get_json_result())
    sys.exit(-1)


req_obj={}
if len(data["params"]):
    a1=data['params'].split(';')    
    for i in a1:
        a=i.split(':')
        req_obj[a[0]]=a[1].split(',')
        

def NeSession():
    try:
        session = requests.Session()
        session.auth = (username, password)
        session.headers.update({"Cookie":"LOGIN_LEVEL=2; path=/;"})
        return session
    except Exception as e:
        print (e)
    

def NeGetObjects(ip,ObjectList):
    try:
        s = NeSession()
        try:
            url = "http://"+ip+":20080/NMSRequest/GetObjects?NoHTML=true&Objects="+ObjectList
            re = s.get(url)
        except:
            url = "https://"+ip+"/NMSRequest/GetObjects?NoHTML=true&Objects="+ObjectList
            re = s.get(url, verify=False)
        object_data = re.text.strip().splitlines()
        List_of_objects = []
        for obj in object_data:
            info = {}
            infoArr = obj.split("\t")
            info.update({'ObjectName' : infoArr[0]})
            for i in range(2, len(infoArr[2:]), 2):
                info.update({infoArr[i] : infoArr[i+1]})
            List_of_objects.append(info)
        return List_of_objects       
    except Exception as e:
        print(e)
        return False

# create sensor result
result = CustomSensorResult("Monitoring attributes @: "+ip)

for each_obj in req_obj:
    objects = NeGetObjects(ip,each_obj)
    #print(objects)
    if objects:
            for attrb in req_obj[each_obj]:
                if attrb in objects[0]:
                    #print(attrb)
                    result.add_channel(channel_name=each_obj+"_"+attrb, unit="",  value=objects[0][attrb], is_float=True, decimal_mode='Auto')

print(result.get_json_result())


############################
__author__="Guru"
#
#Parameters_required = Eth ports object name
#Based on previous 15min bin
#############################

import requests
import sys, json


from paepy.ChannelDefinition import CustomSensorResult

#data = {"host":"172.25.28.48","params":"Port_Eth"}
data = json.loads(sys.argv[1])



ipaddr = data['host']
objs = data['params'].split()


if len(objs) == 0:
    result = CustomSensorResult()
    result.add_error("Please provide Eth port's objects as parametes --> Port_Eth")
    print(result.get_json_result())
    sys.exit(-1)


objlist = '%0A'.join(objs)




def NeSession():
    try:
        session = requests.Session()
        session.auth = ('DIAGUSER', 'j72e#05t')
        session.headers.update({"Cookie":"LOGIN_LEVEL=2; path=/;"})
        return session
    except Exception as e:
        print (e)


def NeGetObjects(ip,Objects):
    try:
        s=NeSession()
        url = "http://"+ip+":20080/NMSRequest/IntervalStats?NoHTML=true&Start=1&Last=1&Type=0&Objects="+Objects
        re = s.get(url)
        data = re.text.strip()
        #print(data)
        if 'no objects' in data:
            return False
        dataArr = data.splitlines()
        ObjectArr = zip(*(iter(dataArr),) * 3)
        return ObjectArr
    except Exception as e:
        print(e)

PM = NeGetObjects(ipaddr,objlist)
d_pm={}
for (x,y,z) in PM:
    d_pm[x.split()[0]] = dict(zip(y.split(),z.split()))
    
    
# create sensor result
result = CustomSensorResult("BW monitor: {}".format(ipaddr))
for k,v in d_pm.items():
    result.add_channel(channel_name="{}_{}".format(k,"TX"), unit="Mbps", value=int(d_pm[k]["-OctetsTx"])*8 / 900 / 1048576 )
    result.add_channel(channel_name="{}_{}".format(k,"RX"), unit="Mbps", value=int(d_pm[k]["-OctetsRx"])*8 / 900 / 1048576 )

    
print(result.get_json_result())




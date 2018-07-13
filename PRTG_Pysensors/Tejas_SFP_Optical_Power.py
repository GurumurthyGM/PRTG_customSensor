##########################
#__Author__=Guru
#
#Parameters_required = SFP_Objects seperated space max 25 eg: SFP-1-11-1 SFP-1-10-5
#
##########################


import requests
import sys, json
from pprint import pprint
from paepy.ChannelDefinition import CustomSensorResult


#data = {"host":"172.25.23.23","params":"SFP"}
data = json.loads(sys.argv[1])

ip = data['host']
objs = data['params'].split()

if len(objs) == 0:
    result = CustomSensorResult()
    result.add_error("Parameters_required = SFP_Objects seperated space max 25 eg: SFP or SFP-1-11-1 SFP-1-10-5")
    print(result.get_json_result())
    sys.exit(-1)

sfplist = "%0A".join(objs)


def NeSession():
    try:
        session = requests.Session()
        session.auth = ('DIAGUSER', 'j72e#05t')
        session.headers.update({"Cookie":"LOGIN_LEVEL=2; path=/;"})
        return session
    except Exception as e:
        print (e)
    

def NeGetObjects(ip,ObjectList):
    try:
        s = NeSession()
        url = "http://"+ip+":20080/NMSRequest/GetObjects?NoHTML=true&Objects="+ObjectList
        re = s.get(url)
        sfpdata = re.text.strip().splitlines()
        sfps = []
        for sfp in sfpdata:
            info = {}
            infoArr = sfp.split("\t")
            info.update({'ObjectName' : infoArr[0]})
            for i in range(2, len(infoArr[2:]), 2):
                info.update({infoArr[i] : infoArr[i+1]})
            sfps.append(info)
        return sfps
    except Exception as e:
        print(e)
        return False

# create sensor result
result = CustomSensorResult("Optical Power monitor on SFPs @: "+ip)

sfps = NeGetObjects(ip,sfplist)
if sfps:
    for sfp in sfps:
        result.add_channel(channel_name=sfp['ObjectName']+'_Rx', unit="dBm", value=sfp['-RxPower'], is_float=True)
        result.add_channel(channel_name=sfp['ObjectName']+'_Tx', unit="dBm", value=sfp['-TxPower'], is_float=True)

pprint(result.get_json_result())
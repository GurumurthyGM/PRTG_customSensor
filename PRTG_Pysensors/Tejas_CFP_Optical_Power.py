##########################
__author__="Guru"
#
#Parameters_required = CFP_Objects seperated space, max 25 eg: MSACFP or MSACFP-1-11-511 MSACFP-1-10-505
#
##########################

import requests
import sys, json
from math import log10
from paepy.ChannelDefinition import CustomSensorResult

data = {"host":"172.25.25.31","params":"MSACFP"}
data = json.loads(sys.argv[1])

ip = data['host']
objs = data['params'].split()

if len(objs) == 0:
    result = CustomSensorResult()
    result.add_error("Parameters_required = CFP_Objects seperated space, max 25 eg: MSACFP or MSACFP-1-11-511 MSACFP-1-10-505 (@ Additional Parameters while adding sensor)")
    print(result.get_json_result())
    sys.exit(-1)

cfplist = '%0A'.join(objs)


def NeSession():
    try:
        session = requests.Session()
        session.auth = ('DIAGUSER', 'j72e#05t')
        session.headers.update({"Cookie":"LOGIN_LEVEL=2; path=/;"})
        return session
    except Exception as e:
        print (e)
    

def NeGetObjects(ip,Objectlist):
    try:
        s = NeSession()
        try:
            url = "http://"+ip+":20080/NMSRequest/GetObjects?NoHTML=true&Objects="+Objectlist
            re = s.get(url)
        except:
            url = "https://"+ip+"/NMSRequest/GetObjects?NoHTML=true&Objects="+Objectlist
            re = s.get(url, verify=False)
        cfpdata = re.text.strip().splitlines()
        cfps = []
        for cfp in cfpdata:
            info = {}
            infoArr = cfp.split("\t")
            info.update({'ObjectName' : infoArr[0]})
            for i in range(2, len(infoArr[2:]), 2):
                info.update({infoArr[i] : infoArr[i+1]})
            cfps.append(info)
        return cfps
    except Exception as e:
        print(e)

# create sensor result
result = CustomSensorResult("Optical Power monitor on CFPs @: {}".format(ip))

cfps = NeGetObjects(ip,cfplist)

if cfps:
    for cfp in cfps:
        RX_mW=0
        cfpRX=cfp['-RxPower'].split(";")
        for i in filter(None,cfpRX):
            RX_mW = RX_mW + float(i.split("=")[1])
        RX_dbm = 10.*log10(RX_mW) if RX_mW > 0 else 0
        result.add_channel(channel_name=cfp['ObjectName']+'_Rx', unit="dBm", value=RX_dbm,  is_float=True, decimal_mode='Auto')

        TX_mW=0
        cfpTX=cfp['-TxPower'].split(";")
        for i in filter(None,cfpTX):
            TX_mW = TX_mW + float(i.split("=")[1])
        TX_dbm = 10.*log10(TX_mW) if TX_mW > 0 else 0
        result.add_channel(channel_name=cfp['ObjectName']+'_Tx', unit="dBm", value=TX_dbm, is_float=True, decimal_mode='Auto')


print(result.get_json_result())

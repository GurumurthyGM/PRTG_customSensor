##########################
__author__="Guru"
#
#Parameters_required = NONE
#
##########################


import telnetlib
import sys,os
import json
import requests
from paepy.ChannelDefinition import CustomSensorResult
from html_table_parser import HTMLTableParser

try:
    data = json.loads(sys.argv[1])
except:
    data = {"host":"172.25.200.161", "linuxloginusername":"tejas", "linuxloginpassword":"j72e#05t"}

ip=data['host']
username = data.get('linuxloginusername', 'tejas')
passwd = data.get('linuxloginpassword', 'j72e#05t')


def NeSession():
    try:
        session = requests.Session()
        session.auth = ('DIAGUSER', 'j72e#05t')
        session.headers.update({"Cookie":"LOGIN_LEVEL=2; path=/;"})
        return session
    except Exception as e:
        print (e)
    
def NeGetObject(ip,ObjectName):
    try:
        s = NeSession()
        try:
            url = "http://"+ip+":20080/NMSRequest/GetObjects?NoHTML=true&Objects="+str(ObjectName)
            re = s.get(url)
        except:
            url = "https://"+ip+"/NMSRequest/GetObjects?NoHTML=true&Objects="+str(ObjectName)
            re = s.get(url, verify=False)
        info = {}
        infoArr = re.text.strip().split("\t")
        info.update({'ObjectName' : infoArr[0]})
        for i in range(2, len(infoArr[2:]), 2):
            info.update({infoArr[i][1:] : infoArr[i+1]})
            
        return info
    except Exception as e:
        print(e)
        return False

#Define telnet parameters    
username = b'guest'
password = b'iltwat'
port = 2023
connection_timeout = 30
reading_timeout = 30
    
    #Logging into device
connection = telnetlib.Telnet(ip, port, connection_timeout)
        
router_output = connection.read_until(b"login:", reading_timeout)
connection.write(username + b'\n')
    #print(router_output)
        
router_output = connection.read_until(b"Password:", reading_timeout)
connection.write(password + b'\n')
        #print(router_output)

router_output = connection.read_until(b'>', reading_timeout)
        #print router_output
        
        
connection.write(b"top -bn1 \n")
topdata=connection.read_until(b">", reading_timeout).splitlines()

connection.write(b"cat /proc/meminfo \n")
meminfo=connection.read_until(b">", reading_timeout).splitlines()

connection.write(b"cat /proc/msd_test \n")
msd_test=connection.read_until(b">", reading_timeout).splitlines()

connection.write(b"cat /proc/tejas/storage/smart/smartInfo \n")
smart=connection.read_until(b">", reading_timeout).splitlines()

connection.write(b"ifconfig mate | grep 'inet ' | cut -d: -f2 | awk '{print $1}' \n")
sip=connection.read_until(b">", reading_timeout).splitlines()


scip=0
sc_msd_test=0
for i in sip:
    if b'127.' in i:
        scip = list(map(int,i.strip().split(b'.')))
        for d in range(len(scip)):
            if scip[d] == 254:
                scip[d] -= 1
        scip = '.'.join(list(map(str,scip))).encode()

#print(scip)

if scip != 0:
    connection.write(b'( sleep 2; echo "iltwat"; echo "cat /proc/msd_test"; sleep 2; ) | telnet '+scip+b' 2023 -l guest \n')
    sc_msd_test = connection.read_until(b">",reading_timeout)
    sc_msd_test = connection.read_until(b">",reading_timeout).splitlines()
    
connection.close()

nm = pm = cc = fm = ospf = gpon = gmpls = chAgent = net = SvcSwitchMgr = l2SvcMgr = bcmHal = ifmgr = ifagent = ssmtm = {}

memplace = 6
cpuplace = -3
system = NeGetObject(ip,"System-1")

if system.get('ProductCode', 'NA') == "TJMC140018":
    cpuplace = -4
uptime = system.get('UpTime', 0)

    
for d in topdata:
    if 'nm.d' in d:
        nm ={'cpu':d.split()[cpuplace], 'mem':d.split()[memplace]}
        

    if 'pm.d' in d:
        pm ={'cpu':d.split()[cpuplace], 'mem':d.split()[memplace]}


    if 'cc.d' in d:
        cc ={'cpu':d.split()[cpuplace], 'mem':d.split()[memplace]}


    if 'fm.d' in d:
        fm ={'cpu':d.split()[cpuplace], 'mem':d.split()[memplace]}

    if 'ospf.d' in d:
        ospf={'cpu':d.split()[cpuplace], 'mem':d.split()[memplace]}

    if 'gpon.d' in d:
        gpon={'cpu':d.split()[cpuplace], 'mem':d.split()[memplace]}
    
    if 'gmpls.d' in d:
        gmpls={'cpu':d.split()[cpuplace], 'mem':d.split()[memplace]}
    
    if 'chAgent.d' in d:
        chAgent={'cpu':d.split()[cpuplace], 'mem':d.split()[memplace]}
    
    if 'net.d' in d:
        net={'cpu':d.split()[cpuplace], 'mem':d.split()[memplace]}
    
    if 'SvcSwitchMgr.d' in d:
        SvcSwitchMgr={'cpu':d.split()[cpuplace], 'mem':d.split()[memplace]}
    
    if 'l2SvcMgr.d' in d:
        l2SvcMgr={'cpu':d.split()[cpuplace], 'mem':d.split()[memplace]}
    
    if 'bcmHal.d' in d:
        bcmHal={'cpu':d.split()[cpuplace], 'mem':d.split()[memplace]}
 
    if 'ifmgr.d' in d:
        ifmgr={'cpu':d.split()[cpuplace], 'mem':d.split()[memplace]}
    
    if 'ifagent.d' in d:
        ifagent={'cpu':d.split()[cpuplace], 'mem':d.split()[memplace]}
    
    if 'ssmtm.d' in d:
        ssmtm={'cpu':d.split()[cpuplace], 'mem':d.split()[memplace]}
    


    if b'Load' in d:
        Load ={'cpu':d.split()[2]}
    
Tmem = 0
Fmem = 0
for m in meminfo:
    if b'MemTotal' in m:
        Tmem = m.split()[1]
    if b'MemFree' in m:
        Fmem = m.split()[1]


#print(nm)
# create sensor result
result = CustomSensorResult("NE health monitoring on: {0} RAM: {1:.2f} MB; Uptime:{2}Hrs {3}Min".format(ip,int(Tmem)/1024, int(uptime)//3600, (int(uptime)%3600)//60))

# add primary channel
result.add_channel(channel_name="CPU load", unit=" ", value=Load['cpu'], is_float=True, primary_channel=True,
                       is_limit_mode=True, limit_min_error=0, limit_max_error=10,
                       limit_error_msg="Percentage too high", decimal_mode='Auto')

result.add_channel(channel_name="UsedMemory", unit="MB", value=(int(Tmem)-int(Fmem))/1024, is_float=False, decimal_mode='Auto')
# add additional channel
result.add_channel(channel_name="CPU_NM.d", unit="%", value=nm.get('cpu',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="CPU_PM.d", unit="%", value=pm.get('cpu',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="CPU_FM.d", unit="%", value=fm.get('cpu',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="CPU_CC.d", unit="%", value=cc.get('cpu',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="CPU_ospf.d", unit="%", value=ospf.get('cpu',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="CPU_gpon.d", unit="%", value=gpon.get('cpu',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="CPU_gmpls.d", unit="%", value=gmpls.get('cpu',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="CPU_net.d", unit="%", value=net.get('cpu',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="CPU_SvcSwitchMgr.d", unit="%", value=SvcSwitchMgr.get('cpu',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="CPU_l2SvcMgr.d", unit="%", value=l2SvcMgr.get('cpu',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="CPU_bcmHal.d", unit="%", value=bcmHal.get('cpu',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="CPU_ifmgr.d", unit="%", value=ifmgr.get('cpu',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="CPU_ifagent.d", unit="%", value=ifagent.get('cpu',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="CPU_ssmtm.d", unit="%", value=ssmtm.get('cpu',0), is_float=True, decimal_mode='Auto')


result.add_channel(channel_name="MEM_NM.d", unit="%", value=nm.get('mem',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="MEM_PM.d", unit="%", value=pm.get('mem',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="MEM_FM.d", unit="%", value=fm.get('mem',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="MEM_CC.d", unit="%", value=cc.get('mem',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="MEM_ospf.d", unit="%", value=ospf.get('mem',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="MEM_gpon.d", unit="%", value=gpon.get('mem',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="MEM_gmpls.d", unit="%", value=gmpls.get('mem',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="MEM_net.d", unit="%", value=net.get('mem',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="MEM_SvcSwitchMgr.d", unit="%", value=SvcSwitchMgr.get('mem',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="MEM_l2SvcMgr.d", unit="%", value=l2SvcMgr.get('mem',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="MEM_bcmHal.d", unit="%", value=bcmHal.get('mem',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="MEM_ifmgr.d", unit="%", value=ifmgr.get('mem',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="MEM_ifagent.d", unit="%", value=ifagent.get('mem',0), is_float=True, decimal_mode='Auto')
result.add_channel(channel_name="MEM_ssmtm.d", unit="%", value=ssmtm.get('mem',0), is_float=True, decimal_mode='Auto')





def main(ip):
    s=NeSession()
    try:
            url = "http://"+ip+":20080/EMSRequest/VoltageStatistics"
            re = s.get(url)
    except:
            url = "https://"+ip+"/EMSRequest/VoltageStatistics"
            re = s.get(url, verify=False)
    xhtml = re.text.strip()

    p = HTMLTableParser()
    p.feed(xhtml)
    return p.tables


a = main(ip)
psus = []
for i in range(1,len(a[0])):
    psus.append(dict(zip(a[0][0],a[0][i])))

    

for psu in psus:
    result.add_channel(channel_name=psu.get("Card Name"), unit="V", value=psu.get("Current Voltage Value (Volts)"), is_float=True, decimal_mode='Auto')


def NeGetObject(ip,ObjectName):
    try:
        s = NeSession()
        try:
            url = "http://"+ip+":20080/NMSRequest/GetObjects?NoHTML=true&Objects="+str(ObjectName)
            re = s.get(url)
        except:
            url = "https://"+ip+"/NMSRequest/GetObjects?NoHTML=true&Objects="+str(ObjectName)
            re = s.get(url, verify=False)
        info = {}
        infoArr = re.text.strip().split("\t")
        info.update({'ObjectName' : infoArr[0]})
        for i in range(2, len(infoArr[2:]), 2):
            info.update({infoArr[i][1:] : infoArr[i+1]})
            
        return info
    except Exception as e:
        print(e)
        return False

def NeGetObjects(ip,Objects):
    try:
        s=NeSession()
        try:
            url = "http://"+ip+":20080/NMSRequest/GetObjects?NoHTML=true&Objects="+Objects
            re = s.get(url)
        except:
            url = "https://"+ip+"/NMSRequest/GetObjects?NoHTML=true&Objects="+Objects
            re = s.get(url, verify=False)
        data = re.text.strip()
        if data.find('no objects') != -1:
            return False
        ObjectArr = data.split('\n')
        ObjectList = []
        for i in ObjectArr:
            ObjectList.append(i.strip().split('\t')[0])

        return ObjectList
    except Exception as e:
        print(e)
        return False

objs = NeGetObjects(ip,'Card')

for obj in objs:
    temp = NeGetObject(ip,obj)
    if temp:
        if int(temp['Temp']) > 0:
            result.add_channel(channel_name=temp['ObjectName'], unit="Temperature", value=temp['Temp'], is_float=True, decimal_mode='Auto')

PCycle=0
Life=0

for i in smart:
    if b"Remaining Life" in i:
        Life = i.split(b"=")[1].strip()
    if b"Power Cycle" in i:
        PCycle = i.split(b"=")[1].strip()


tdict={}
for i in msd_test:
    if b"R-succ" in i:
        tmp = i.split()
        tdict = {tmp[i]:tmp[i+1] for i in range(0, len(tmp), 2)}


stdict={}
if sc_msd_test:
    for i in sc_msd_test:
        if b"R-succ" in i:
            stmp = i.split()
            stdict = {stmp[i]:stmp[i+1] for i in range(0, len(stmp), 2)}

    
Wsucc = int(tdict.get(b"W-succ:",0))
Rsucc = int(tdict.get(b"R-succ:",0))
    
sWsucc = int(stdict.get(b"W-succ:",0))
sRsucc = int(stdict.get(b"R-succ:",0))

pWsucc=0
pRsucc=0
psWsucc=0
psRsucc=0
folder="c:\\Users\\Public\\"+ip
try:
    if not os.path.exists(folder):
        os.mkdir(folder)
        
    sys.path.append(folder)
    import temp
    pWsucc=temp.pWsucc
    pRsucc=temp.pRsucc
    psWsucc=temp.psWsucc
    psRsucc=temp.psRsucc

    with open(folder+"\\temp.py", 'w') as f:
        f.write("pWsucc="+str(Wsucc))
        f.write("\npRsucc="+str(Rsucc))
        f.write("\npsWsucc="+str(sWsucc))
        f.write("\npsRsucc="+str(sRsucc))

except Exception:
    with open(folder+"\\temp.py", 'w') as f:
        f.write("pWsucc="+str(Wsucc))
        f.write("\npRsucc="+str(Rsucc))
        f.write("\npsWsucc="+str(sWsucc))
        f.write("\npsRsucc="+str(sRsucc))
    Wsucc=0
    Rsucc=0
    sWsucc=0
    sRsucc=0
    pWsucc=0
    pRsucc=0
    psWsucc=0
    psRsucc=0

if Life:
    result.add_channel(channel_name="Remaining Life", unit="Percent", value=Life)
    result.add_channel(channel_name="Power Cycle", value=PCycle)

    
result.add_channel(channel_name="Master W-succ", unit="KB", value=(Wsucc-pWsucc)/2 if Wsucc-pWsucc > 0 else 0)
result.add_channel(channel_name="Master R-succ", unit="KB", value=(Rsucc-pRsucc)/2 if Rsucc-pRsucc > 0 else 0)

if stdict:
    result.add_channel(channel_name="Slave W-succ", unit="KB", value=(sWsucc-psWsucc)/2 if sWsucc-psWsucc > 0 else 0)
    result.add_channel(channel_name="Slave R-succ", unit="KB", value=(sRsucc-psRsucc)/2 if sRsucc-psRsucc > 0 else 0)

    
# print sensor result to stdout
print(result.get_json_result())





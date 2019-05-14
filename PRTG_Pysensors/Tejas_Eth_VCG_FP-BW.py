from pysnmp.hlapi import *
import sys, json
from paepy.ChannelDefinition import CustomSensorResult
from time import sleep
import time

###########constants########
OIDdict = {"Port_Eth":{"TX":"1.3.6.1.4.1.8255.1.2.1.2.37.1.1.482.{0}.{1}.{2}.{3}","RX":"1.3.6.1.4.1.8255.1.2.1.2.37.1.1.480.{0}.{1}.{2}.{3}"},
    "VCG":{"TX":".1.3.6.1.4.1.8255.1.2.1.2.58.1.1.340.{0}.{1}.{2}","RX":".1.3.6.1.4.1.8255.1.2.1.2.58.1.1.342.{0}.{1}.{2}"},
    "FlowPoint":{"TX":".1.3.6.1.4.1.8255.1.2.1.2.144.1.1.31.{0}.{1}.{2}.{3}.{4}","RX":".1.3.6.1.4.1.8255.1.2.1.2.144.1.1.32.{0}.{1}.{2}.{3}.{4}"}
    }
Unit = 'Mbps' #Mbps / MBps
delay = 20
############################

try:
    data = json.loads(sys.argv[1])
except:
    data = {"host":"192.168.22.200", "snmpcommv2":"public", "params":"FlowPoint-0-0-5-1-1"}

ip=data.get('host')
Community = data.get('snmpcommv2','public')
object_name = data.get('params').strip()


def printError(msg):
    result = CustomSensorResult()
    result.add_error(msg)
    print(result.get_json_result())
    sys.exit(-1)

def snmpget(IP,Community,Obj):
    objdata = Obj.split("-")
    if objdata[0] in list(OIDdict.keys()):
        Obj_Tx=OIDdict.get(objdata[0])['TX']
        Obj_Rx=OIDdict.get(objdata[0])['RX']
        Obj_TX=Obj_Tx.format(*objdata[1:])
        Obj_RX=Obj_Rx.format(*objdata[1:])
        
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
            CommunityData(Community),
            UdpTransportTarget((IP, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(Obj_TX)),
            ObjectType(ObjectIdentity(Obj_RX)))
    )
    if errorIndication:
        printError(errorIndication)
    elif errorStatus:
        printError('%s at %s' % (errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    return varBinds

def getSpeed():
    varBinds1 = snmpget(ip,Community,object_name)
    t1 = time.time()
    sleep(delay)
    varBinds2 = snmpget(ip,Community,object_name)
    t2 = time.time()

    varBindTX1 = varBinds1[0][1]
    varBindRX1 = varBinds1[1][1]

    varBindTX2 = varBinds2[0][1]
    varBindRX2 = varBinds2[1][1]

    TX = int(varBindTX2) - int(varBindTX1)
    RX = int(varBindRX2) - int(varBindRX1)
    T = t2-t1

    if TX < 0 or RX < 0:
        sleep(5)
        getSpeed()
    
    if Unit == "MBps":
        TX = (TX/1000000)/T
        RX = (RX/1000000)/T
    else:
        RX = (RX*8/1000000)/T
        TX = (TX*8/1000000)/T
        
    return TX,RX

try:

    tx,rx = getSpeed()
    

    # create sensor result
    result = CustomSensorResult("BandWith Monitor @ {0}   {1}".format(ip,object_name))   
    result.add_channel(channel_name='Total', unit=Unit, value=format(float(tx+rx), '.2f'),  is_float=True, decimal_mode='Auto')
    result.add_channel(channel_name='TX', unit=Unit, value=format(float(tx), '.2f'),  is_float=True, decimal_mode='Auto')
    result.add_channel(channel_name='RX', unit=Unit, value=format(float(rx), '.2f'),  is_float=True, decimal_mode='Auto')
    
    print(result.get_json_result())
except Exception as e:
    printError(e)


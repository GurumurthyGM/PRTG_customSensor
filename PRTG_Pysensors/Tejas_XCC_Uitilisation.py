############################
__author__="Guru"
#
#Parameters_required = XCC capacity
#
#############################

import requests
import sys, json


from paepy.ChannelDefinition import CustomSensorResult


data = {'host':"172.25.28.102", "params":"640"}
#data = json.loads(sys.argv[1])

ip = data['host']
param = data['params'].strip()


if len(param) == 0:
    result = CustomSensorResult()
    result.add_error("Please provide NE capacity as a parameter in Gig eg: 320")
    print(result.get_json_result())
    sys.exit(-1)


capacity = int(param)

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
        url = "http://"+ip+":20080/NMSRequest/GetObjects?NoHTML=true&Objects="+Objects
        re = s.get(url)
        dataArr = re.text.strip().splitlines()
        objects = []
        if 'no objects' not in dataArr[0]:
            for data in dataArr:
                info = {}
                infoArr = data.split("\t")
                info.update({'ObjectName' : infoArr[0]})
                for i in range(2, len(infoArr[2:]), 2):
                    info.update({infoArr[i] : infoArr[i+1]})
                objects.append(info)
       
        return objects
    except Exception as e:
        print(e)
        

def NeXcs(ip, objects):
    CCs = NeGetObjects(ip, objects)
    Xcapacity_LO = 0
    Xcapacity_HO = 0
    Xcapacity=0
    XCcount = len(CCs)
    XCup=0
    XCvc12=0
    XCvc3=0
    XCvc4=0
    XCvc4c=0
    XCvc16c=0
    XCvc64c=0
        
    XCvc12_up=0
    XCvc3_up=0
    XCvc4_up=0
    XCvc4c_up=0
    XCvc16c_up=0
    XCvc64c_up=0
    if CCs:
        
        for cc in CCs:
            
            if cc["-Capacity"] == "vc12":
                XCvc12 += 1
                Xcapacity_LO += 2 
                if cc["-DP_Enable"] == '1':
                    Xcapacity_LO += 1
                if cc["-SP_Enable"] == '1':
                    Xcapacity_LO += 1
                if cc["-DstOperStatus"] == 'dst_oper_up' and cc["-SrcOperStatus"] == 'src_oper_up':
                    XCvc12_up += 1
                    
            elif cc["-Capacity"] == "vc3":
                XCvc3 += 1
                Xcapacity_LO += 2 * 21 
                if cc["-DP_Enable"] == '1':
                    Xcapacity_LO += 21
                if cc["-SP_Enable"] == '1':
                    Xcapacity_LO += 21
                if cc["-DstOperStatus"] == 'dst_oper_up' and cc["-SrcOperStatus"] == 'src_oper_up':
                    XCvc3_up += 1
                    
            elif cc["-Capacity"] == "vc4":
                XCvc4 += 1
                Xcapacity_HO += 2
                if cc["-DP_Enable"] == '1':
                    Xcapacity_HO += 1
                if cc["-SP_Enable"] == '1':
                    Xcapacity_HO += 1
                if cc["-DstOperStatus"] == 'dst_oper_up' and cc["-SrcOperStatus"] == 'src_oper_up':
                    XCvc4_up += 1
                    
            elif cc["-Capacity"] == "vc4_4c":
                XCvc4c += 1
                Xcapacity_HO += 2 * 4 
                if cc["-DP_Enable"] == '1':
                    Xcapacity_HO +=  4
                if cc["-SP_Enable"] == '1':
                    Xcapacity_HO +=  4
                if cc["-DstOperStatus"] == 'dst_oper_up' and cc["-SrcOperStatus"] == 'src_oper_up':
                    XCvc4c_up += 1
                    
            elif cc["-Capacity"] == "vc4_16c":
                XCvc16c += 1
                Xcapacity_HO += 2 * 16
                if cc["-DP_Enable"] == '1':
                    Xcapacity_HO +=  16
                if cc["-SP_Enable"] == '1':
                    Xcapacity_HO +=  16
                if cc["-DstOperStatus"] == 'dst_oper_up' and cc["-SrcOperStatus"] == 'src_oper_up':
                    XCvc16c_up += 1
                    
            elif cc["-Capacity"] == "vc4_64c":
                XCvc64c += 1
                Xcapacity += 2 * 64
                if cc["-DP_Enable"] == '1':
                    Xcapacity_HO +=  64
                if cc["-SP_Enable"] == '1':
                    Xcapacity_HO +=  64
                if cc["-DstOperStatus"] == 'dst_oper_up' and cc["-SrcOperStatus"] == 'src_oper_up':
                    XCvc64c_up += 1

        XCup = XCvc12_up + XCvc3_up + XCvc4_up + XCvc4c_up + XCvc16c_up + XCvc64c_up
        Xcapacity = Xcapacity_LO + Xcapacity_HO * 63
    
    return ( XCcount, XCup, Xcapacity, Xcapacity_LO, Xcapacity_HO, XCvc12, XCvc3, XCvc4, XCvc4c, XCvc16c, XCvc64c, XCvc12, XCvc3, XCvc4, XCvc4c, XCvc16c, XCvc64c)

def NEvcgXcs(ip, objects):
    vcgs = NeGetObjects(ip, objects)
    VXCcount = len(vcgs)
    Vcapacity=0
    Vcapacity_LO = 0
    Vcapacity_HO = 0
    VXCup=0
    VXtu12=0
    VXtu3=0
    VXau4=0
    
    VXtu12_up=0
    VXtu3_up=0
    VXau4_up=0
    if vcgs:
        for vcg in vcgs:
            if "TU12-" in vcg["-LCTName"]:
                VXtu12 += 1
                Vcapacity_LO += 2
                if vcg["-P_Enable"] == '1':
                    Vcapacity_LO += 1
                if vcg["-OperStatus"] == "opersts_up":
                    VXtu12_up += 1
                
                    
            if "TU3-" in vcg["-LCTName"]:
                VXtu3 += 1
                Vcapacity_LO += 2 * 21
                if vcg["-P_Enable"] == '1':
                    Vcapacity_LO += 21
                if vcg["-OperStatus"] == "opersts_up":
                    VXtu3_up += 1
                
                    
            if "AU4-" in vcg["-LCTName"]:
                VXau4 += 1
                Vcapacity_HO += 2
                if vcg["-P_Enable"] == '1':
                    Vcapacity_HO += 1
                if vcg["-OperStatus"] == "opersts_up":
                    VXau4_up += 1
                

        VXCup = VXtu12_up + VXtu3_up + VXau4_up
        Vcapacity = Vcapacity_LO + Vcapacity_HO * 63

    return (VXCcount, VXCup, Vcapacity, Vcapacity_LO, Vcapacity_HO, VXtu12, VXtu3, VXau4, VXtu12_up, VXtu3_up, VXau4_up)

def NEoduXcs(ip, objects):
    odus = NeGetObjects(ip, objects)
    OXCcount = len(odus)
    OXCup=0
    odu0=0
    if odus:
        for odu in odus:
            if odu["-SrcOperStatus"] == "src_oper_up" and odu["-DstOperStatus"] == "dst_oper_up" :
                OXCup += 1
            if odu["-Capacity"] == "ODU0":
                odu0 += 1
            if odu["-Capacity"] == "ODU1" :
                odu0 += 2
            if odu["-Capacity"] == "ODU2" :
                odu0 += 8
            if odu["-Capacity"] == "ODU2e":
                odu0 += 8
            if odu["-Capacity"] == "ODU4" :
                odu0 += 80

    return (OXCcount,OXCup,odu0)


# create sensor result
result = CustomSensorResult("Traffic monitor on CCs @: {} -> {} Gig.".format(ip,capacity))

CC_status = NeXcs(ip, "CrossConnect")
VCG_status = NEvcgXcs(ip, "VCGAssociation")
odu_status = NEoduXcs(ip, "ODUConnection")

ho_used = ((CC_status[4] + VCG_status[4] ) * 156.87 + odu_status[2] * 1244.16)/1024
lo_used = ((CC_status[3] + VCG_status[3] ) * 2.49)/1024

capacity_used = (ho_used + lo_used) 

result.add_channel(channel_name="Loaded_Capacity%", unit="Percent", value=capacity_used*100/capacity, is_float=True, decimal_mode=3)

result.add_channel(channel_name="Capacity_Utilized", unit="Gig", value=capacity_used, is_float=True, decimal_mode=3)

result.add_channel(channel_name="HO_Used", unit="Gig", value=ho_used, is_float=True, decimal_mode=3)

result.add_channel(channel_name="LO_Used", unit="Gig", value=lo_used, is_float=True, decimal_mode=3)


result.add_channel(channel_name="XCs Total", value=CC_status[0], is_float=True, decimal_mode=3)
result.add_channel(channel_name="XCs UP", value=CC_status[1], is_float=True, decimal_mode=3)
 
    
result.add_channel(channel_name="VCG-XCs Total", value=VCG_status[0], is_float=True, decimal_mode=3)
result.add_channel(channel_name="VCG-XCs UP", value=VCG_status[1], is_float=True, decimal_mode=3)


result.add_channel(channel_name="ODU-XCs Total", value=odu_status[0], is_float=True, decimal_mode=3)
result.add_channel(channel_name="ODU-XCs UP", value=odu_status[1], is_float=True, decimal_mode=3)
    
print(result.get_json_result())
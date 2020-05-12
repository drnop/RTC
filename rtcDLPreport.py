#!/usr/bin/python3                                                                                                                         
import json
import sys
import rtcdb
import cats
import os
import rtclogger
from ldap3 import Server, Connection, ALL

def main(argv):
    debug_level = 0
    mylogger = rtclogger.LOGGER("GetDynOptions",debug_level,"")

    try:
        if 'REQUEST_METHOD' in os.environ :
            ### this is called as CGI script and we should avoid printouts                                                              
            debug = False
            post = str(sys.stdin.read())
            temp = json.loads(post)
            email = temp["email"]
            sam = temp["username"]
            days = temp["days"]
            hours = temp["hours"]
            minutes = temp["minutes"]

        else :
            ### this is called via CLI for troubleshooting                                                                                item = "all"
            debug = True
            email = "atorralb@cisco.com"
            sam = "hacke"
            days = 90
            hours = 0
            minutes = 0 

            
        dbconn = rtcdb.RTCDB()
        dbresult = dbconn.getXconfig("smaconfig")
        creds = json.loads(dbresult["configstring"])
        SMA_SERVER= creds["sma_server"]
        SMA_USERNAME=creds["sma_username"]
        SMA_PASSWORD=creds["sma_password"]

        dbresult = dbconn.getXconfig("duoconfig")
        creds = json.loads(dbresult["configstring"])
        api_ikey = creds["api_ikey"]    
        api_skey = creds["api_skey"]    
        duo_host = creds["duo_host"]

        sma = cats.SMA(server=SMA_SERVER,username=SMA_USERNAME,password=SMA_PASSWORD,debug=debug)
        sma_rsp = sma.getDLPdetails(days=days,hours=hours,minutes=minutes,sender=email,critical=True,high=True,medium=True,low=True)

        if debug:
            print(json.dumps(sma_rsp,indent=4,sort_keys=True))
        rsp = {"rtcResult":"OK",
               "smadata":sma_rsp["data"]}

        duo=cats.DUO_ADMIN(api_ikey=api_ikey,api_skey =api_skey, duo_host=duo_host, debug=debug, logfile="")
        duo_rsp = duo.getAuthLogs(username=sam,days=days,hours=hours,minutes=minutes)
        rsp.update({"duo":duo_rsp})

        print("Content-type:application/json\n\n")

        ret = json.dumps(rsp)
        print (ret)

    except Exception as err:
        print("Content-type:application/json\n\n")
        result = { "rtcResult":"Error","info":"some error {}".format(mylogger.exception_info(err)) }
        print(json.dumps(result))


if __name__ == "__main__":
    main(sys.argv[1:])

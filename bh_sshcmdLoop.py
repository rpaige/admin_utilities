import subprocess
import paramiko
import threading
import sys

#hostsList = []
#hostsList = ["127.0.0.1","rpaige-X550LA"]
#hostsList.append("127.0.0.1");
#hostsList.append("rpaige-X550LA");

def ssh_command(ip,user,passwd,command,pkey):
    client = paramiko.SSHClient()
    #client.load_host_keys('/home/rpaige/.ssh/known_hosts')
    
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    #------------------------------------------------------------------
    # set policy to automatically add unknown hosts to known_hosts file
    #------------------------------------------------------------------
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())   
    
    #------------------------------------------------------------------
    #connect(hostname, port=22, username=None, password=None, pkey=None, 
    #       key_filename=None, timeout=None, allow_agent=True, look_for_keys=True, 
    #       compress=False, sock=None, gss_auth=False, gss_kex=False, gss_deleg_creds=True, 
    #       gss_host=None, banner_timeout=None)
    #------------------------------------------------------------------
    client.connect(ip,username=user,password=passwd)
    
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(command)
        print ssh_session.recv(1024)
    return


#---------------------------------------
def main():
#---------------------------------------    
    if len(sys.argv[1:]) != 2:
        print "Usage: ./bh_sshcmdLoop.py HostListFile commandsFileName"
        sys.exit(0)
    hostsFileName = sys.argv[1]
    commandsFileName = sys.argv[2]
    
    #print hostsFileName
    with open(hostsFileName) as hosts:
        hostsList = [hosts.read().strip("\n")]
        
    with open(commandsFileName) as commands:
        commandsList = [commands.read().strip("\n")]
    i = 0

    #print "#host entries = %d" % len(hostsList)
    
    while(True):
        print "Host = " + hostsList[i]
        ssh_command(hostsList[i],"rpaige","!957Ldap","cat ./ssh/id_rsa.pub >>.ssh/authorized_keys",pkey=None)
        i = i + 1
        if (len(hostsList) <= i):
            break

main()
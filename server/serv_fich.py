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
PRIMARY = True
SERVER = 1
MESSAGE_ID = 0
WHO_PRIMARY = SERVER1_PORT
SERVERS = [SERVER2_PORT, SERVER3_PORT]
SERVERS_HEARTBEAT = [SERVER2HEARTBEAT_PORT, SERVER3HEARTBEAT_PORT]
class State:
    Identification, Authentication, Main, Downloading, Uploading = range(5)

def sendOK( s, params="" ):
    s.sendall( ("OK{}\r\n".format( params )).encode( "ascii" ) )

def sendER( s, code=1 ):
    s.sendall( ("ER{}\r\n".format( code )).encode( "ascii" ) )

def session(s):
    state = State.Identification
    global MESSAGE_ID

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
            s_server1 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            s_server1.connect( ('', SERVER1_PORT) )
            s_server1.sendall(str(MESSAGE_ID).encode() + 'ç'.encode() + message.encode())
            new_message = s_server1.recv(1024).decode()
            s_server1.close()
            print ("Child: message received: " + new_message + "")

            if new_message == "OK":
                MESSAGE_ID += 1
                print ("Child: OK! Sending back to client...")
                sendOK( s )
            else:
                print ("Child: An error occurred with the replies...")
                sendER( s, 12 )

            state = State.Uploading

        elif message.startswith( szasar.Command.Upload2 ):
            if state != State.Uploading:
                sendER( s )
                continue

            state = State.Main
            filedata = szasar.recvall(s, filesize)

            print ("Entered message delivery...")
            s_server1 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            s_server1.connect( ('', SERVER1_PORT) )
            s_server1.sendall(str(MESSAGE_ID).encode() + 'ç'.encode() + message.encode() + '|'.encode() + filedata)
            new_message = s_server1.recv(1024).decode()
            s_server1.close()
            print ("Child: message received: " + new_message + "")

            if new_message == "OK":
                MESSAGE_ID += 1
                print ("Child: OK! Sending back to client...")
                sendOK( s )
            else:
                print ("Child: An error occurred with the replies...")
                sendER( s, 12 )

        elif message.startswith( szasar.Command.Delete ):
            if state != State.Main:
                sendER( s )
                continue
            if user == 0:
                sendER( s, 7 )
                continue

            print ("Entered message delivery...")
            s_server1 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            s_server1.connect( ('', SERVER1_PORT) )

            s_server1.sendall(str(MESSAGE_ID).encode() + 'ç'.encode() + message.encode())
            new_message = s_server1.recv(1024).decode()
            s_server1.close()
            print ("Child: message received: " + new_message + "")

            if new_message == "OK":
                MESSAGE_ID += 1
                print ("Child: OK! Sending back to client...")
                sendOK( s )
            else:
                print ("Child: An error occurred with the replies...")
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
            s_server1 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            s_server1.connect( ('', SERVER1_PORT) )

            s_server1.sendall(str(MESSAGE_ID).encode() + 'ç'.encode() + message.encode())
            new_message = s_server1.recv(1024).decode()
            s_server1.close()
            print ("Child: message received: " + new_message + "")

            if new_message == "OK":
                MESSAGE_ID += 1
                print ("Child: OK! Sending back to client...")
                sendOK( s )
            else:
                print ("Child: An error occurred with the replies...")
                sendER( s, 12 )

        elif message.startswith( szasar.Command.Delete_Dir ):
            if state != State.Main:
                sendER( s )
                continue
            if user == 0:
                sendER( s, 7 )
                continue

            print ("Entered message delivery...")
            s_server1 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            s_server1.connect( ('', SERVER1_PORT) )

            s_server1.sendall(str(MESSAGE_ID).encode() + 'ç'.encode() + message.encode())
            new_message = s_server1.recv(1024).decode()
            s_server1.close()
            print ("Child: message received: " + new_message + "")

            if new_message == "OK":
                MESSAGE_ID += 1
                print ("Child: OK! Sending back to client...")
                sendOK( s )
            else:
                print ("Child: An error occurred with the replies...")
                sendER( s, 12 )
        
        elif message.startswith( szasar.Command.Rename_File ):
            if state != State.Main:
                sendER( s )
                continue
            if user == 0:
                sendER( s, 7 )
                continue

            print ("Entered message delivery...")
            s_server1 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            s_server1.connect( ('', SERVER1_PORT) )

            s_server1.sendall(str(MESSAGE_ID).encode() + 'ç'.encode() + message.encode())
            new_message = s_server1.recv(1024).decode()
            s_server1.close()
            print ("Child: message received: " + new_message + "")

            if new_message == "OK":
                MESSAGE_ID += 1
                print ("Child: OK! Sending back to client...")
                sendOK( s )
            else:
                print ("Child: An error occurred with the replies...")
                sendER( s, 12 )

        elif message.startswith( szasar.Command.Attr_Modified ):
            if state != State.Main:
                sendER( s )
                continue
            if user == 0:
                sendER( s, 7 )
                continue

            print ("Entered message delivery...")
            s_server1 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            s_server1.connect( ('', SERVER1_PORT) )
            s_server1.sendall(str(MESSAGE_ID).encode() + 'ç'.encode() + message.encode())
            new_message = s_server1.recv(1024).decode()
            s_server1.close()
            print ("Child: message received: " + new_message + "")

            if new_message == "OK":
                MESSAGE_ID += 1
                print ("Child: OK! Sending back to client...")
                sendOK( s )
            else:
                print ("Child: An error occurred with the replies...")
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

    s_server1 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s_server1.bind(("", SERVER1_PORT))
    s_server1.listen(5)

    s_server1hb = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s_server1hb.bind(("", SERVER1HEARTBEAT_PORT))
    s_server1hb.listen(5)

    s_server2 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s_server3 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

    def signal_handler(sig, frame):
        print ("Closing server...")
        s.close()
        s_server1.close()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    
    messages = []
    heartbeat = 5
    CONNECTED = False

    while True:
        if PRIMARY:
            if CONNECTED:
                heartbeat -= 1
                if heartbeat < 1:
                    heartbeat = 5
                    print ("Sending heartbeat...")
                    message = 'HEARTBEAT'
                    for server in SERVERS_HEARTBEAT:
                        s_serverhb = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                        s_serverhb.connect( ('', server) )
                        s_serverhb.sendall(message.encode())
                        s_serverhb.close()

            try:
                readable, writable, exceptional = select.select([s, s_server1, s_server1hb], [], [], 0.5)
            except select.error:
                continue

            for sock in readable:
                if sock == s:
                    (dialog, address) = s.accept()
                    CONNECTED = True
                    print( "Cliente: Conexión aceptada del socket {0[0]}:{0[1]}.".format( address ) )
                    if( os.fork() ):
                        dialog.close()
                    else:
                        s.close()
                        session(dialog)
                        dialog.close()
                        exit( 0 )

                elif sock == s_server1:
                    (dialog, address) = s_server1.accept()
                    message_complete = dialog.recv(4096).decode()

                    message_split = message_complete.split('ç')
                    message_id = message_split[0]
                    message = message_split[1]

                    print ("Message received in socket server1: " + message + " with id: " + message_id + ". Current messages: " + str(messages))

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

        else:
            sockets = [s_server1]
            while True:
                readable, writable, exceptional = select.select(sockets, [], [], 0.5)

                for sock in readable:
                    (dialog, address) = sock.accept()
                    message_complete = dialog.recv(4096).decode()

                    message_split = message_complete.split('ç')
                    message_id = message_split[0]
                    message = message_split[1]

                    print ("Message received in socket server1: " + message + " with id: " + message_id + ". Current messages: " + str(messages))

                    if message_id in messages:
                        print ("Message already received. Sending OK...")
                        dialog.sendall('OK'.encode())
                        dialog.close()

                    else:
                        if message.startswith( 'HEARTBEAT' ):
                            timeout = 15
                            dialog.sendall('OK'.encode())
                            dialog.close()
                            continue

                        elif message.startswith( szasar.Command.Create_Dir ):
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
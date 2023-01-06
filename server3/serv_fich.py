#!/usr/bin/env python3

import shutil
import socket, sys, os, signal
import szasar as szasar
import select, queue, time, threading

PORT = 6012
SERVER1_PORT = 6013
SERVER2_PORT = 6014
SERVER3_PORT = 6015
FILES_PATH = "files"
MAX_FILE_SIZE = 10 * 1 << 20 # 10 MiB
SPACE_MARGIN = 50 * 1 << 20  # 50 MiB
USERS = ("anonimous", "sar", "sza")
PASSWORDS = ("", "sar", "sza")
PRIMARY = False
SERVER = 3
MESSAGE_ID = 0

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

        elif message.startswith( szasar.Command.List ):
            if state != State.Main:
                sendER( s )
                continue
            try:
                message = "OK\r\n"
                for filename in os.listdir( FILES_PATH ):
                    filesize = os.path.getsize( os.path.join( FILES_PATH, filename ) )
                    message += "{}?{}\r\n".format( filename, filesize )
                message += "\r\n"
            except:
                sendER( s, 4 )
            else:
                s.sendall( message.encode( "ascii" ) )

        elif message.startswith( szasar.Command.Download ):
            if state != State.Main:
                sendER( s )
                continue
            filename = os.path.join( FILES_PATH, message[4:] )
            try:
                filesize = os.path.getsize( filename )
            except:
                sendER( s, 5 )
                continue
            else:
                sendOK( s, filesize )
                state = State.Downloading

        elif message.startswith( szasar.Command.Download2 ):
            if state != State.Downloading:
                sendER( s )
                continue
            state = State.Main
            try:
                with open( filename, "rb" ) as f:
                    filedata = f.read()
            except:
                sendER( s, 6 )
            else:
                sendOK( s )
                s.sendall( filedata )

        elif message.startswith( szasar.Command.Upload ):
            if state != State.Main:
                sendER( s )
                continue
            if user == 0:
                sendER( s, 7 )
                continue
            filename, filesize = message[4:].split('?')
            filesize = int(filesize)
            if filesize > MAX_FILE_SIZE:
                sendER( s, 8 )
                continue
            svfs = os.statvfs( FILES_PATH )
            if filesize + SPACE_MARGIN > svfs.f_bsize * svfs.f_bavail:
                sendER( s, 9 )
                continue
            sendOK( s )
            state = State.Uploading

        elif message.startswith( szasar.Command.Upload2 ):
            if state != State.Uploading:
                sendER( s )
                continue
            state = State.Main
            try:
                with open( os.path.join( FILES_PATH, filename), "wb" ) as f:
                    filedata = szasar.recvall( s, filesize )
                    f.write( filedata )
            except:
                sendER( s, 10 )
            else:
                sendOK( s )

        elif message.startswith( szasar.Command.Delete ):
            if state != State.Main:
                sendER( s )
                continue
            if user == 0:
                sendER( s, 7 )
                continue
            try:
                os.remove( os.path.join( FILES_PATH, message[4:] ) )
            except:
                sendER( s, 11 )
            else:
                sendOK( s )

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

            s_server1.sendall(str(MESSAGE_ID).encode() + '-'.encode() + message.encode())
            new_message = s_server1.recv(1024).decode()
            s_server1.close()
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
            try:
                shutil.rmtree( os.path.join( FILES_PATH, message[4:] ) )
            except:
                sendER( s, 13 )
            else:
                sendOK( s )
        
        elif message.startswith( szasar.Command.Rename_File ):
            if state != State.Main:
                sendER( s )
                continue
            if user == 0:
                sendER( s, 7 )
                continue
            try:
                oldname, newname = message[4:].split(' ')
                os.rename( os.path.join( FILES_PATH, oldname ), os.path.join( FILES_PATH, newname ) )
            except:
                sendER( s, 14 )
            else:
                sendOK( s )

        elif message.startswith( szasar.Command.Attr_Modified ):
            if state != State.Main:
                sendER( s )
                continue
            if user == 0:
                sendER( s, 7 )
                continue
            try:
                filename, permissions, timestamp, atime = message[4:].split(' ')
                perm_mask = oct(int(permissions) & 0o777)
                os.utime( os.path.join( FILES_PATH, filename ), ( float(atime), float(timestamp) ) )
                os.chmod( os.path.join( FILES_PATH, filename ), int(perm_mask, base=8))
            except:
                sendER( s, 2 )
            else:
                sendOK( s )
        else:
            sendER( s )


if __name__ == "__main__":

    if PRIMARY:
        s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        s.bind(('', PORT))
        s.listen(5)

    s_server3 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s_server3.bind(("", SERVER3_PORT))
    s_server3.listen(5)

    def signal_handler(sig, frame):
        s.close()
        s_server3.close()
        sys.exit(0)
    signal.signal(signal.SIGCHLD, signal_handler)

    messages = []

    while True:
        if PRIMARY:
            try:
                readable, writable, exceptional = select.select([s, s_server3], [], [], 0.5)
            except select.error:
                continue

            for sock in readable:
                if sock == s:
                    (dialog, address) = s.accept()
                    print( "Cliente: Conexión aceptada del socket {0[0]}:{0[1]}.".format( address ) )
                    if( os.fork() ):
                        dialog.close()
                    else:
                        s.close()
                        session(dialog)
                        dialog.close()
                        exit( 0 )

                elif sock == s_server3:
                    (dialog, address) = s_server3.accept()
                    message_complete = dialog.recv(1024).decode()

                    message_split = message_complete.split('-')
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
                            print ("Appended to messages: " + message_id)
                            replies = []

                            s_server2 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                            s_server1 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

                            s_server2.connect( ('', SERVER2_PORT) )
                            s_server2.sendall(message_complete.encode())
                            s2_message = s_server2.recv(1024).decode()
                            replies.append(s2_message)
                            s_server2.close()
            
                            s_server1.connect( ('', SERVER1_PORT) )
                            s_server1.sendall(message_complete.encode())
                            s1_message = s_server1.recv(1024).decode()
                            replies.append(s1_message)
                            s_server3.close()

                            print ("Replies: " + str(replies))

                            if all(reply == 'OK' for reply in replies):
                                dialog.sendall('OK'.encode())
                                dialog.close()
                            else:
                                dialog.sendall('ER'.encode())
                                dialog.close()


        else:
            sockets = [s_server3]
            while True:
                readable, writable, exceptional = select.select(sockets, [], [], 0.5)

                for sock in readable:
                    (dialog, address) = sock.accept()
                    message_complete = dialog.recv(1024).decode()

                    message_split = message_complete.split('-')
                    message_id = message_split[0]
                    message = message_split[1]

                    print ("Message received in socket server3: " + message + " with id: " + message_id + ". Current messages: " + str(messages))

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
                            else:
                                messages.append(message_id)
                                dialog.sendall('OK'.encode())
                                dialog.close()

                            s_server2 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                            s_server1 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                            
                            print ("Sending message to server1...")
                            s_server1.connect( ('', SERVER1_PORT) )
                            s_server1.sendall(message_complete.encode())
                            s1_message = s_server1.recv(1024).decode()
                            print ("Message received from server1: " + s1_message)
                            s_server1.close()

                            print ("Sending message to server2...")
                            s_server2.connect( ('', SERVER2_PORT) )
                            s_server2.sendall(message_complete.encode())
                            s_server2.close()
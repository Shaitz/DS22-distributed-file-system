#!/usr/bin/env python3

import shutil
import socket, sys, os, signal
import szasar as szasar

PORT = 6012
SERVER_PORT = 6013
FILES_PATH = "files"
MAX_FILE_SIZE = 10 * 1 << 20 # 10 MiB
SPACE_MARGIN = 50 * 1 << 20  # 50 MiB
USERS = ("anonimous", "sar", "sza")
PASSWORDS = ("", "sar", "sza")
PRIMARY = True

class State:
	Identification, Authentication, Main, Downloading, Uploading = range(5)

def sendOK( s, params="" ):
	s.sendall( ("OK{}\r\n".format( params )).encode( "ascii" ) )

def sendER( s, code=1 ):
	s.sendall( ("ER{}\r\n".format( code )).encode( "ascii" ) )

def session( s ):
	state = State.Identification

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
			try:
				os.mkdir( os.path.join( FILES_PATH, message[4:] ) )
			except:
				sendER( s, 12 )
			else:
				sendOK( s )

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

		s_server = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		s_server.bind(("", SERVER_PORT))
		s_server.listen(5)

	else:
		s_server2 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		s_server2.connect( ('localhost', SERVER_PORT) )

	def signal_handler(sig, frame):
		s.close()
		s_server.close()
		sys.exit(0)
	signal.signal(signal.SIGCHLD, signal_handler)

	while True:
		if PRIMARY:
			dialog, address = s.accept()
			if dialog:
				print( "Cliente: Conexión aceptada del socket {0[0]}:{0[1]}.".format( address ) )
				if( os.fork() ):
					dialog.close()
				else:
					s.close()
					session( dialog )
					dialog.close()
					exit( 0 )

			dialog_server, address_server = s_server.accept()

			if dialog_server:
				print( "Servidor: Conexión aceptada del socket {0[0]}:{0[1]}.".format( address ) )
				if( os.fork() ):
					dialog_server.close()
				else:
					s_server.close()
					session( dialog_server )
					dialog_server.close()
					exit( 0 )
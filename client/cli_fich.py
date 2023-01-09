#!/usr/bin/env python3

import socket, sys, os, time
import szasar as szasar

SERVER = 'localhost'
PORT = 6012
ER_MSG = (
	"Correcto.",
	"Comando desconocido o inesperado.",
	"Usuario desconocido.",
	"Clave de paso o password incorrecto.",
	"Error al crear la lista de ficheros.",
	"El fichero no existe.",
	"Error al bajar el fichero.",
	"Un usuario anonimo no tiene permisos para esta operacion.",
	"El fichero es demasiado grande.",
	"Error al preparar el fichero para subirlo.",
	"Error al subir el fichero.",
	"Error al borrar el fichero.",
	"Error al cambiar de nombre" )

class Menu:
	List, Download, Upload, Delete, Exit = range( 1, 6 )
	Options = ( "Lista de ficheros", "Bajar fichero", "Subir fichero", "Borrar fichero", "Salir" )

	def menu():
		print( "+{}+".format( '-' * 30 ) )
		for i,option in enumerate( Menu.Options, 1 ):
			print( "| {}.- {:<25}|".format( i, option ) )
		print( "+{}+".format( '-' * 30 ) )

		while True:
			try:
				selected = int( input( "Selecciona una opción: " ) )
			except:
				print( "Opción no válida." )
				continue
			if 0 < selected <= len( Menu.Options ):
				return selected
			else:
				print( "Opción no válida." )

def iserror( message ):
	if( message.startswith( "ER" ) ):
		code = int( message[2:] )
		print( ER_MSG[code] )
		return True
	else:
		return False

def int2bytes( n ):
	if n < 1 << 10:
		return str(n) + " B  "
	elif n < 1 << 20:
		return str(round( n / (1 << 10) ) ) + " KiB"
	elif n < 1 << 30:
		return str(round( n / (1 << 20) ) ) + " MiB"
	else:
		return str(round( n / (1 << 30) ) ) + " GiB"



if __name__ == "__main__":
	
	if len( sys.argv ) > 3:
		print( "Uso: {} [<servidor> [<puerto>]]".format( sys.argv[0] ) )
		exit( 2 )

	if len( sys.argv ) >= 2:
		SERVER = sys.argv[1]
	if len( sys.argv ) == 3:
		PORT = int( sys.argv[2])

	s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	s.connect( (SERVER, PORT) )

	user = "sar"
	message = "{}{}\r\n".format( szasar.Command.User, user )
	s.sendall( message.encode( "ascii" ) )
	message = szasar.recvline( s ).decode( "ascii" )

	password = "sar"
	message = "{}{}\r\n".format( szasar.Command.Password, password )
	s.sendall( message.encode( "ascii" ) )
	message = szasar.recvline( s ).decode( "ascii" )

	file_to_rename = ""

	while True:
		try:
			stdin = sys.stdin.readline().split()
			event = stdin[0]
			name = stdin[1]

			if event == "DIR_CREATED":
				message = "{}{}\r\n".format( szasar.Command.Create_Dir, name )
				s.sendall( message.encode( "ascii" ) )
				message = szasar.recvline( s ).decode( "ascii" )

				if not iserror( message ):
					print( "El directorio {} se ha creado correctamente.".format( name ) )

			elif event == "DIR_DELETED":
				message = "{}{}\r\n".format( szasar.Command.Delete_Dir, name )
				s.sendall( message.encode( "ascii" ) )
				message = szasar.recvline( s ).decode( "ascii" )

				if not iserror( message ):
					print( "El directorio {} se ha eliminado correctamente.".format( name ) )

			elif event == "FILE_CREATED" or event == "FILE_MODIFIED":
				if os.path.isfile("files/." + name + ".swp"):
					continue
				try:
					filesize = os.path.getsize( "files/" + name )
					with open( "files/" + name, "rb" ) as f:
						filedata = f.read()
						f.close()
				except:
					print( "No se ha podido acceder al fichero {}.".format( name ) )
					continue

				message = "{}{}?{}\r\n".format( szasar.Command.Upload, name, filesize )
				s.sendall( message.encode( "ascii" ) )
				message = szasar.recvline( s ).decode( "ascii" )
				print (message)

				if iserror( message ):
					continue

				message = "{}\r\n".format( szasar.Command.Upload2 )
				s.sendall( message.encode( "ascii" ) )
				s.sendall( filedata )
				message = szasar.recvline( s ).decode( "ascii" )

				if not iserror( message ):
					print( "El fichero {} se ha enviado correctamente.".format( name ) )

			elif event == "FILE_DELETED":
				if name.startswith( "." ):
					file_being_edited = name.split(".")[1]

					try:
						filesize = os.path.getsize( "files/" + file_being_edited )
						with open( "files/" + file_being_edited, "rb" ) as f:
							filedata = f.read()
							f.close()
					except:
						print( "No se ha podido acceder al fichero {}.".format( file_being_edited ) )
						continue

					message = "{}{}?{}\r\n".format( szasar.Command.Upload, file_being_edited, filesize )
					s.sendall( message.encode( "ascii" ) )
					message = szasar.recvline( s ).decode( "ascii" )

					if iserror( message ):
						continue

					message = "{}\r\n".format( szasar.Command.Upload2 )
					s.sendall( message.encode( "ascii" ) )
					s.sendall( filedata )
					message = szasar.recvline( s ).decode( "ascii" )

					if not iserror( message ):
						print( "El fichero {} se ha enviado correctamente.".format( file_being_edited ) )

				message = "{}{}\r\n".format( szasar.Command.Delete, name )
				s.sendall( message.encode( "ascii" ) )
				message = szasar.recvline( s ).decode( "ascii" )
				if not iserror( message ):
					print( "El fichero {} se ha borrado correctamente.".format( name ) )

			elif event == "FILE_MOVED_FROM":
				file_to_rename = name

			elif event == "FILE_MOVED_TO":
				message = "{}{}\r\n".format( szasar.Command.Rename_File, file_to_rename + " " + name )
				s.sendall( message.encode( "ascii" ) )
				message = szasar.recvline( s ).decode( "ascii" )

				if not iserror( message ):
					print( "El fichero {} se ha renombrado correctamente.".format( name ) )
			
			elif event == "FILE_ATTRIB_CHANGED":
				status = os.stat( "files/" + name )
				message = "{}{}\r\n".format( szasar.Command.Attr_Modified, name + " " + str( status.st_mode ) + " " + str( status.st_mtime ) + " " + str( status.st_atime ) )
				s.sendall( message.encode( "ascii" ) )
				message = szasar.recvline( s ).decode( "ascii" )

				if not iserror( message ):
					print( "Los atributos del fichero {} se ha actualizado correctamente.".format( name ) )

		except ConnectionRefusedError:
			s.close()
			s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			s.connect( (SERVER, PORT) )

		except EOFError:
			s.close()
			s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			s.connect( (SERVER, PORT) )


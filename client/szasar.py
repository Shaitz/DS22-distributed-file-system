class Command:
	User, Password, List, Download, Download2, Upload, Upload2, Delete, Exit, Create_Dir, Delete_Dir, Rename_File, Attr_Modified = ("USER", "PASS", "LIST", "DOWN", "DOW2", "UPLO", "UPL2", "DELE", "EXIT", "CDIR", "DDIR", "RFIL", "ATTR")

def recvline( s, removeEOL = True ):
	line = b''
	CRreceived = False
	while True:
		c = s.recv( 1 )
		if c == b'':
			raise EOFError( "Connection closed by the peer before receiving an EOL." )
		line += c
		if c == b'\r':
			CRreceived = True
		elif c == b'\n' and CRreceived:
			if removeEOL:
				return line[:-2]
			else:
				return line
		else:
			CRreceived = False

def recvall( s, size ):
	message = b''
	while( len( message ) < size ):
		chunk = s.recv( size - len( message ) )
		if chunk == b'':
			raise EOFError( "Connection closed by the peer before receiving the requested {} bytes.".format( size ) )
		message += chunk
	return message

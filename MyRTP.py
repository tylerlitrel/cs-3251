# This file will contain all the logic necessary for the RTP protocol

import hashlib

class MyRTP:

	# This is for caching out-of-order packets
	cache = []
	# This is the sequence number we are expecting
	expectedSeq = -1
	# This is the file that we will write data to
	fileName = "arbitraryName.txt"
	
	# This will set the file name we will write to
	def setFileName(newFileName):
		fileName = newFileName
		
	# This method is used in order to create a socket
	def createRTPSocket():

		# Return an RTP socket
		return socket

	# This method associates a port on the machine with the socket
	def bindRTPSocket(address):
		# Extract the IP address and the port number from the address tuple
		ipAddress = address[0]
		portNumber = address[1]

		
	# This function is used to create a socket by the server to communicate with a specific client
	def acceptRTPConnection():
		#simple...

	# This function is used to receive data
	def receiveRTP(numBytes):
		#handle lost, out of order, and corrupt packets
		#sequence number should be somewhere
		if !checkSumOkay(this):
			return
		addToCache(this)
		if expectedSeq == sequenceNumberHere:
			writeOutputFromCache()
			#also update sequence number
		acknowledge(this)

	# This makes sure the checksum is okay
	def checkSumOkay(byteArray):
		
		
		
		
	# Adds data to cache and ensures ascending order of sequence numbers
	def addToCache(byteArray):
		cache.append(byteArray)
		cache.sortBySequenceNumbers()
		
	# Writes output to appropriate file
	def writeOutputFromCache():
		for i in cache:
			file = open(fileName, 'wb')
			file.write(i)#may have to think about how to best get the data
						#maybe a data object because I am all about that OOP
	
	# This function allows the socket to begin listening for connection requests
	def listenRTP():
		#simple...


	# This function connects to the specified IP address and port
	def connectRTP(address):
		# Extract the IP address and the port number from the address tuple
		ipAddress = address[0]
		portNumber = address[1]

		# Perform the initial handshake to set up the connection


	# This function will be used to send data
	def sendRTP(message):
		#simple?
		
	# This function will be used to close a connection
	def closeRTPSocket():
		#protocol in document

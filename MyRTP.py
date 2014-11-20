# This file will contain all the logic necessary for the RTP protocol

import hashlib

class MyRTP:

	# This is for caching out-of-order packets
	recvCache = []
	# This stores packets we have not received an Ack for
	sendCache = []
	# Our current sequence number
	ourSeq = -1
	# This is the sequence number we are expecting
	expectedSeq = -1
	# This is the file that we will write data to
	fileName = ""
	# This is default packet length in bytes. It can be changed
	packetLength = 65,535
	# This is the default window size
	windowSize = 1024
	
	def setWindowSize(newWindowSize):
		windowSize = newWindowSize
		
	def setPacketLength(newPacketLength):
		packetLength = newPacketLength
	
	# This will set the file name we will write to
	def setFileName(newFileName):
		fileName = newFileName
		
	# This method is used in order to create a socket
	def createRTPSocket():
		udp stuff
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
		this can only be called if listen has been called (remember that boolean)
			udp block on receive - ie it is waitin to here a SYN
			once it gets the syn it sends a challenge which is a randomly
			generated integer
			udp block up in here 
			timeout and try twice more then if still fail- kill it
			waiting to receive the challenge response
			if it is correct then we ack and connection is go
			this wil return a socket up in this shiznit
			if it is not correct then we go back to the top in some fashion

	# This function is used to receive data
	def receiveRTP(numBytes):
		#handle lost, out of order, and corrupt packets
		
		we do shit here with UDP to extract our packet
		call recieve with a udp packet and then manipulating
		the data which will be our packet below
		
		#sequence number should be somewhere
		if !checkSumOkay(this):
			return
		addToCache(this)
		sequenceNumberHere = getSeqFromByteArray(dataFromUDP)
		if expectedSeq == sequenceNumberHere:
			#writeOutputfromcache will update the current sequence number
			#and be based on the last packet in the cache
			sequenceNumber = writeOutputFromCache()			
		acknowledge(this)

	# This makes sure the checksum is okay
	def checkSumOkay(byteArray):
		index to the spot
		fill it out with 0;s
		store the given checksum
		compare that to our checksum that we calculate here using sha256
		return true or false
		
		
	# Adds data to cache and ensures ascending order of sequence numbers
	def addToCache(byteArray):
		cache.append(byteArray)
		cache.sortBySequenceNumbers()
		
	# Writes output to appropriate file
	def writeOutputFromCache():
		for i in cache:   
			#will update sequence per packet written and compare that to next packet
			#eg get 1. have 2,3,4,7.  we only write 1234 and 7 stays cached
			file = open(fileName, 'wb')
			file.write(i)#may have to think about how to best get the data
						#maybe a data object because I am all about that OOP
	#somewhere figure out when the file is fully sent
	
	
	# This function allows the socket to begin listening for connection requests
	def listenRTP():
		#simple...
		boolean that says we can accept things


	# This function connects to the specified IP address and port
	def connectRTP(address):
		# Extract the IP address and the port number from the address tuple
		ipAddress = address[0]
		portNumber = address[1]

		# Perform the initial handshake to set up the connection

		send a syn to the server
		udp block
		wait for the challenge
		timeout and try twice more then if still fail- kill it
		send the challenge back
		wait for ack
		timeout and try twice more then if still fail- kill it
		get ack and connect to given socket
		dunzo

	# This function will be used to send data
	def sendRTP(message):
		#simple?
		loop through byte array
		divide the length by (packetsize*windowsize)
		while(sendCache is not empty and notallpackets are sent):
			s
		
		
		
		
		
	# This function will be used to close a connection
	def closeRTPSocket():
		#protocol in document
		
		
		
		
		
		
		
need to create a packet object with sequence and raw data

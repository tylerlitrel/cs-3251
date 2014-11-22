# This file will contain all the logic necessary for the RTP protocol

import hashlib
import random

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
	packetLength = 65535
	# This is the default window size
	windowSize = 1024
    # This is the UDP socket that we will use underneath our RTP protocol
    udpSocket = None
    # This byte array contains the following bytes in order for use in the packet: SYN, ACK, FIN, CNG, CNG+ACK, SYN+ACK, FIN+ACK
    headerFlags = bytearray.fromhex('80 40 20 10 50 90 30')
		
	# this will set the window size
	def setWindowSize(newWindowSize):
		windowSize = newWindowSize
		
	# this will set the packet length
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
		'''
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
        '''
        # Use a blocking UDP call to wait for a SYN packet to arrive
        incomingMessage, incomingAddress = udpSocket.recvfrom_into(packetLength)

        # If the packet was a SYN packet, generate a random number for the CHALLENGE+ACK reply
        randomInt = random.randint(1, 2056)

        # Check to see if the packet is a SYN packet (indicated in 29th byte of header)
        if(incomingMessage[29] == headerFlags[0] and checkSumOkay(incomingMessage)):
            # Retrieve the needed information from the incoming packet
            incomingSeqNumber = int.from_bytes(incomingMessage[4:8], byteorder = 'big')
            incomingAckNumber = int.from_bytes(incomingMessage[8:12], byteorder = 'big')
            incomingSourcePort = int.from_bytes(incomingMessage[0:2], byteorder = 'big')
            incomingDestinationPort = int.from_bytes(incomingMessage[2:4], byteorder = 'big')

            # Modify the fields for the outgoing CHALLENGE+ACK packet
            outgoingSeqNumber = incomingAckNumber
            outgoingAckNumber = incomingSeqNumber + 1
            outgoingSourcePort = incomingDestinationPort
            outgoingDestinationPort = incomingSourcePort
            outgoingPacketLength = 32 + 4

            # Form the entire CHALLENGE+ACK packet
            outgoingPacket = bytearray()
            for eachByte in outgoingSourcePort.to_bytes(2, byteorder = 'big'):
                outgoingpacket.append(eachByte)
            for eachByte in outgoingDestinationPort.to_bytes(2, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in outgoingSeqNumber.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in outgoingAckNumber.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in (0).to_bytes(8, byteorder = 'big'): # put 0s in for the checksum for now
                outgoingPacket.append(eachByte)
            for eachByte in outgoingWindow.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in outgoingLength.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            outgoingPacket.append(headerFlags[4])
            for eachByte in (0).to_bytes(3, byteorder = 'big'): # for the reserved portion
                outgoingPacket.append(eachByte)
            for eachByte in randomInt.to_bytes(4, byteorder = 'big')
                outgoingPacket.append(eachByte)

            # Calculate the checksum and insert it into the packet
            checksum = calculateChecksum(outgoingPacket)
            index = 12
            for eachByte in checksum:
               outgoingPacket[index] = int.from_bytes(eachByte, byteorder = 'big')
               index++

            # Send the CHALLENGE+ACK packet
            udpSocket.sendto(outgoingPacket, incomingAddress)
        else:
            # The packet was not a SYN or the packet was corrupt 
            return

        # Use a blocking UDP call to wait for the answer to come back
        incomingMessage2, incomingAddress2 = udpSocket.recvfrom_into(packetLength)
        udpSocket.settimeout(5)
        if incomingAddress2 == incomingAddress and int.from_bytes(incomingMessage2[33:37], byteorder = 'big') == randomInt:
            # We received the correct answer to the challenge
            # Retrieve the needed information from the incoming packet
            incomingSeqNumber = int.from_bytes(incomingMessage[4:8], byteorder = 'big')
            incomingAckNumber = int.from_bytes(incomingMessage[8:12], byteorder = 'big')
            incomingSourcePort = int.from_bytes(incomingMessage[0:2], byteorder = 'big')
            incomingDestinationPort = int.from_bytes(incomingMessage[2:4], byteorder = 'big')

            # Modify the fields for the outgoing SYN+ACK packet
            outgoingSeqNumber = incomingAckNumber
            outgoingAckNumber = incomingSeqNumber + 1
            outgoingSourcePort = incomingDestinationPort
            outgoingDestinationPort = incomingSourcePort
            outgoingPacketLength = 32

            # Form the entire SYN+ACK packet
            outgoingPacket = bytearray()
            for eachByte in outgoingSourcePort.to_bytes(2, byteorder = 'big'):
                outgoingpacket.append(eachByte)
            for eachByte in outgoingDestinationPort.to_bytes(2, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in outgoingSeqNumber.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in outgoingAckNumber.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in (0).to_bytes(8, byteorder = 'big'): # put 0s in for the checksum for now
                outgoingPacket.append(eachByte)
            for eachByte in outgoingWindow.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in outgoingLength.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            outgoingPacket.append(headerFlags[5])
            for eachByte in (0).to_bytes(3, byteorder = 'big'): # for the reserved portion
                outgoingPacket.append(eachByte)

            # Calculate the checksum and insert it into the packet
            checksum = calculateChecksum(outgoingPacket)
            index = 12
            for eachByte in checksum:
               outgoingPacket[index] = int.from_bytes(eachByte, byteorder = 'big')
               index++

            # Send the SYN+ACK packet
            udpSocket.sendto(outgoingPacket, incomingAddress)
        else:
            return

        # Use a blocking UDP call to wait for the ACK to come from the client
        incomingMessage3, incomingAddress2 = udpSocket.recvfrom_into(packetLength)
        udpSocket.settimeout(5)
        if incomingAddress3 == incomingAddress and incomingMessage[29] == headerFlags[1]:
            # Retrieve the needed information from the incoming packet
            incomingSeqNumber = int.from_bytes(incomingMessage[4:8], byteorder = 'big')
            incomingAckNumber = int.from_bytes(incomingMessage[8:12], byteorder = 'big')
            incomingSourcePort = int.from_bytes(incomingMessage[0:2], byteorder = 'big')
            incomingDestinationPort = int.from_bytes(incomingMessage[2:4], byteorder = 'big')

            # Modify the fields for the outgoing ACK packet
            outgoingSeqNumber = incomingAckNumber
            outgoingAckNumber = incomingSeqNumber + 1
            outgoingSourcePort = incomingDestinationPort
            outgoingDestinationPort = incomingSourcePort
            outgoingPacketLength = 32

            # Form the entire ACK packet
            outgoingPacket = bytearray()
            for eachByte in outgoingSourcePort.to_bytes(2, byteorder = 'big'):
                outgoingpacket.append(eachByte)
            for eachByte in outgoingDestinationPort.to_bytes(2, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in outgoingSeqNumber.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in outgoingAckNumber.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in (0).to_bytes(8, byteorder = 'big'): # put 0s in for the checksum for now
                outgoingPacket.append(eachByte)
            for eachByte in outgoingWindow.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in outgoingLength.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            outgoingPacket.append(headerFlags[1])
            for eachByte in (0).to_bytes(3, byteorder = 'big'): # for the reserved portion
                outgoingPacket.append(eachByte)

            # Calculate the checksum and insert it into the packet
            checksum = calculateChecksum(outgoingPacket)
            index = 12
            for eachByte in checksum:
               outgoingPacket[index] = int.from_bytes(eachByte, byteorder = 'big')
               index++

            # Send the ACK packet
            udpSocket.sendto(outgoingPacket, incomingAddress)
        else:
            return

        # The handshake has been successfully completed, return a socket for communicating with the client
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return clientSocket

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

	def calculateChecksum(packet):
		emptyArray = bytearray(8)
		myBytes = packet[0:12] 
		for i in emptyArray:
			myBytes.append(i)
		for i in packet[20:]:
			myBytes.append(i)
		hasher = hashlib.sha256()
		hasher.update(myBytes)
		checksum = hasher.digest()
		return checksum[0:64]	
		
	# This makes sure the checksum is okay
	def checkSumOkay(packet):
		checksum = packet[12:20]
		ourChecksum = calculateChecksum(packet)
		return (checksum == ourChecksum)		
		
	# Adds data to cache and ensures ascending order of sequence numbers
	def addToCache(packet):
		cache.append(packet)
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
        '''
		send a syn to the server
		udp block
		wait for the challenge
		timeout and try twice more then if still fail- kill it
		send the challenge back
		wait for ack
		timeout and try twice more then if still fail- kill it
		get ack and connect to given socket
		dunzo
        '''

        # First, send a SYN packet to the server
        # Form the entire SYN packet
        outgoingPacket = bytearray()
        for eachByte in outgoingSourcePort.to_bytes(2, byteorder = 'big'):
            outgoingpacket.append(eachByte)
        for eachByte in outgoingDestinationPort.to_bytes(2, byteorder = 'big'):
            outgoingPacket.append(eachByte)
        for eachByte in (0).to_bytes(4, byteorder = 'big'): #sequence number
            outgoingPacket.append(eachByte)
        for eachByte in (0).to_bytes(4, byteorder = 'big'): #ack number
            outgoingPacket.append(eachByte)
        for eachByte in (0).to_bytes(8, byteorder = 'big'): # put 0s in for the checksum for now
            outgoingPacket.append(eachByte)
        for eachByte in outgoingWindow.to_bytes(4, byteorder = 'big'):
            outgoingPacket.append(eachByte)
        for eachByte in (32).to_bytes(4, byteorder = 'big'): #length
            outgoingPacket.append(eachByte)
        outgoingPacket.append(headerFlags[0])
        for eachByte in (0).to_bytes(3, byteorder = 'big'): # for the reserved portion
            outgoingPacket.append(eachByte)

        # Calculate the checksum and insert it into the packet
        checksum = calculateChecksum(outgoingPacket)
        index = 12
        for eachByte in checksum:
           outgoingPacket[index] = int.from_bytes(eachByte, byteorder = 'big')
           index++

        # Send the SYN packet
        udpSocket.sendto(outgoingPacket, incomingAddress)
        
        # Use a blocking UDP call to wait for the CHALLENGE+ANSWER packet to come back
        incomingMessage, incomingAddress = udpSocket.recvfrom_into(packetLength)

        # Check to see if the packet is a CHALLENGE+ACK packet (indicated in 29th byte of header)
        if(incomingMessage[29] == headerFlags[4] and checkSumOkay(incomingMessage)):
            # Retrieve the needed information from the incoming packet
            incomingSeqNumber = int.from_bytes(incomingMessage[4:8], byteorder = 'big')
            incomingAckNumber = int.from_bytes(incomingMessage[8:12], byteorder = 'big')
            incomingSourcePort = int.from_bytes(incomingMessage[0:2], byteorder = 'big')
            incomingDestinationPort = int.from_bytes(incomingMessage[2:4], byteorder = 'big')
            incomingChallengeNumber = int.from_bytes(incomingMessage[32:36], byteorder = 'big')

            # Modify the fields for the outgoing CHALLENGE+ACK packet
            outgoingSeqNumber = incomingAckNumber
            outgoingAckNumber = incomingSeqNumber + 1
            outgoingSourcePort = incomingDestinationPort
            outgoingDestinationPort = incomingSourcePort
            outgoingPacketLength = 32 + 4

            # Form the entire CHALLENGE+ACK packet
            outgoingPacket = bytearray()
            for eachByte in outgoingSourcePort.to_bytes(2, byteorder = 'big'):
                outgoingpacket.append(eachByte)
            for eachByte in outgoingDestinationPort.to_bytes(2, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in outgoingSeqNumber.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in outgoingAckNumber.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in (0).to_bytes(8, byteorder = 'big'): # put 0s in for the checksum for now
                outgoingPacket.append(eachByte)
            for eachByte in outgoingWindow.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in outgoingLength.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            outgoingPacket.append(headerFlags[1])
            for eachByte in (0).to_bytes(3, byteorder = 'big'): # for the reserved portion
                outgoingPacket.append(eachByte)
            for eachByte in incomingChallengeNumber.to_bytes(4, byteorder = 'big')
                outgoingPacket.append(eachByte)

            # Calculate the checksum and insert it into the packet
            checksum = calculateChecksum(outgoingPacket)
            index = 12
            for eachByte in checksum:
               outgoingPacket[index] = int.from_bytes(eachByte, byteorder = 'big')
               index++

            # Send the CHALLENGE+ACK packet
            udpSocket.sendto(outgoingPacket, incomingAddress)
        else:
            # The packet was not a CHALLENGE+ACK or the packet was corrupt 
            return

        # Use a blocking UDP call to wait for the SYN+ACK to come back
        incomingMessage2, incomingAddress2 = udpSocket.recvfrom_into(packetLength)
        udpSocket.settimeout(5)

        # Check to see if the packet is a SYN+ACK packet (indicated in 29th byte of header)
        if(incomingMessage[29] == headerFlags[5] and checkSumOkay(incomingMessage)):
            # Retrieve the needed information from the incoming packet
            incomingSeqNumber = int.from_bytes(incomingMessage[4:8], byteorder = 'big')
            incomingAckNumber = int.from_bytes(incomingMessage[8:12], byteorder = 'big')
            incomingSourcePort = int.from_bytes(incomingMessage[0:2], byteorder = 'big')
            incomingDestinationPort = int.from_bytes(incomingMessage[2:4], byteorder = 'big')

            # Modify the fields for the outgoing SYN+ACK packet
            outgoingSeqNumber = incomingAckNumber
            outgoingAckNumber = incomingSeqNumber + 1
            outgoingSourcePort = incomingDestinationPort
            outgoingDestinationPort = incomingSourcePort
            outgoingPacketLength = 32

            # Form the entire CHALLENGE+ACK packet
            outgoingPacket = bytearray()
            for eachByte in outgoingSourcePort.to_bytes(2, byteorder = 'big'):
                outgoingpacket.append(eachByte)
            for eachByte in outgoingDestinationPort.to_bytes(2, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in outgoingSeqNumber.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in outgoingAckNumber.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in (0).to_bytes(8, byteorder = 'big'): # put 0s in for the checksum for now
                outgoingPacket.append(eachByte)
            for eachByte in outgoingWindow.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            for eachByte in outgoingLength.to_bytes(4, byteorder = 'big'):
                outgoingPacket.append(eachByte)
            outgoingPacket.append(headerFlags[1])
            for eachByte in (0).to_bytes(3, byteorder = 'big'): # for the reserved portion
                outgoingPacket.append(eachByte)

            # Calculate the checksum and insert it into the packet
            checksum = calculateChecksum(outgoingPacket)
            index = 12
            for eachByte in checksum:
               outgoingPacket[index] = int.from_bytes(eachByte, byteorder = 'big')
               index++

            # Send the SYN+ACK packet
            udpSocket.sendto(outgoingPacket, incomingAddress)
        else:
            # The packet was not a CHALLENGE+ACK or the packet was corrupt 
            return

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

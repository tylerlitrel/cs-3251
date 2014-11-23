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
    # This says whether we can accept connections
    canListen = False
    # This is default packet length in bytes. It can be changed
    maxPacketLength = 65535
    # This is the default window size
    maxWindowSize = 1024
    # This will be the ack number to be put in outgoing packets
    globalAckNumber = 0
    # This will be the sequence number to be put in outgoing packets
    globalSeqNumber = 0
    # THis will be the source port included in outgoing packets
    globalSourcePort = 0
    # This will be the destination port included in outgoing packets
    globalDestinationPort = 0
    # This is the UDP socket that we will use underneath our RTP protocol
    udpSocket = None
    # This byte array contains the following bytes in order for use in the packet: SYN, ACK, FIN, CNG, CNG+ACK, SYN+ACK, FIN+ACK
    headerFlags = bytearray.fromhex('80 40 20 10 50 C0 60 08')
        
    # this will set the window size
    def setMaxWindowSize(newWindowSize):
        maxWindowSize = newWindowSize
        
    # this will set the packet length
    def setMaxPacketLength(newPacketLength):
        maxPacketLength = newPacketLength
    
    # This will set the file name we will write to
    def setFileName(newFileName):
        fileName = newFileName
        
    # This method is used in order to create a socket
    def createRTPSocket():
        udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    # This method associates a port on the machine with the socket
    def bindRTPSocket(address):
        # Extract the IP address and the port number from the address tuple
        ipAddress = address[0]
        portNumber = address[1]
    
    def formPacket(sourcePort, destinationPort, seqNum, ackNum, windowSize, lengthOfPacket, flagByte, payload):
        outgoingPacket = bytearray()
        for eachByte in sourcePort.to_bytes(2, byteorder = 'big'):
            outgoingpacket.append(eachByte)
        for eachByte in destinationPort.to_bytes(2, byteorder = 'big'):
            outgoingPacket.append(eachByte)
        for eachByte in seqNum.to_bytes(4, byteorder = 'big'):
            outgoingPacket.append(eachByte)
        for eachByte in ackNum.to_bytes(4, byteorder = 'big'):
            outgoingPacket.append(eachByte)
        for eachByte in (0).to_bytes(8, byteorder = 'big'): # put 0s in for the checksum for now
            outgoingPacket.append(eachByte)
        for eachByte in windowSize.to_bytes(4, byteorder = 'big'):
            outgoingPacket.append(eachByte)
        for eachByte in lengthOfPacket.to_bytes(4, byteorder = 'big'):
            outgoingPacket.append(eachByte)
        outgoingPacket.append(flagByte)
        for eachByte in (0).to_bytes(3, byteorder = 'big'): # for the reserved portion
            outgoingPacket.append(eachByte)
        for eachByte in payload:
            outgoingPacket.append(eachByte)

        # Calculate the checksum and insert it into the packet
        checksum = calculateChecksum(outgoingPacket)
        index = 12
        for eachByte in checksum:
           outgoingPacket[index] = int.from_bytes(eachByte, byteorder = 'big')
           index = index + 1
        return outgoingPacket
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
        if canListen is False:
            return
        # Use a blocking UDP call to wait for a SYN packet to arrive
        incomingMessage = bytearray()
        packetLength, incomingAddress = udpSocket.recvfrom_into(incomingMessage)
        # If the packet was a SYN packet, generate a random number for the CHALLENGE+ACK reply
        randomInt = random.randint(1, 4096)

        # Check to see if the packet is a SYN packet (indicated in 28th byte of header)
        if(incomingMessage[28] == headerFlags[0] and checkSumOkay(incomingMessage)):
            # Retrieve the needed information from the incoming packet
            globalSeqNumber = int.from_bytes(incomingMessage[4:8], byteorder = 'big')
            globalAckNumber = int.from_bytes(incomingMessage[8:12], byteorder = 'big')
            globalDestinationPort = int.from_bytes(incomingMessage[0:2], byteorder = 'big')
            globalSourcePort = int.from_bytes(incomingMessage[2:4], byteorder = 'big')

            # Modify the fields for the outgoing CHALLENGE+ACK packet
            outgoingSeqNumber = incomingAckNumber
            outgoingAckNumber = incomingSeqNumber + 1
            outgoingPacketLength = 32 + 4

            # Form the entire CHALLENGE+ACK packet
            outgoingPacket = formPacket(globalSourcePort, globalDestinationPort,  outgoingSeqNumber,  
                outgoingAckNumber, maxWindowSize,  outgoingPacketLength, headerFlags[4], int.from_bytes(randomInt, byteorder = 'big'))

            # Send the CHALLENGE+ACK packet
            udpSocket.sendto(outgoingPacket, incomingAddress)
        else:
            # The packet was not a SYN or the packet was corrupt 
            return

        # Use a blocking UDP call to wait for the answer to come back
        incomingMessage2 = bytearray()
        packetLength, incomingAddress2 = udpSocket.recvfrom_into(incomingMessage2)
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
            outgoingPacket = formPacket(outgoingSourcePort, outgoingDestinationPort,  outgoingSeqNumber,  
                outgoingAckNumber, maxWindowSize,  outgoingPacketLength, headerFlags[5], bytearray())
            # Send the SYN+ACK packet
            udpSocket.sendto(outgoingPacket, incomingAddress)
        else:
            return

        # Use a blocking UDP call to wait for the ACK to come from the client
        incomingMessage3, incomingAddress2 = udpSocket.recvfrom_into(packetLength)
        udpSocket.settimeout(5)
        if incomingAddress3 == incomingAddress and incomingMessage[28] == headerFlags[1]:
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
            outgoingPacket = formPacket(outgoingSourcePort, outgoingDestinationPort,  outgoingSeqNumber,  
                outgoingAckNumber, maxWindowSize,  outgoingPacketLength, headerFlags[1], bytearray())

            # Send the ACK packet
            udpSocket.sendto(outgoingPacket, incomingAddress)
        else:
            return

        # The handshake has been successfully completed, return a socket for communicating with the client
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return clientSocket

    # This function is used to receive data
    def receiveRTP(numberOfBytes):
        #handle lost, out of order, and corrupt packets
        #sequence number should be somewhere
        incomingMessage = bytearray()
        thisPackLen, incomingAddress = udpSocket.recvfrom_into(incomingMessage)
            
        returnData = bytearray()
            
        #closing stuff
        #send ack
        # Check to see if the packet is a FIN packet (indicated in 28th byte of header)
        if(incomingMessage[28] == headerFlags[2] and checkSumOkay(incomingMessage)):
            # Retrieve the needed information from the incoming packet
            incomingSeqNumber = int.from_bytes(incomingMessage[4:8], byteorder = 'big')
            incomingAckNumber = int.from_bytes(incomingMessage[8:12], byteorder = 'big')
            incomingSourcePort = int.from_bytes(incomingMessage[0:2], byteorder = 'big')
            incomingDestinationPort = int.from_bytes(incomingMessage[2:4], byteorder = 'big')

            outgoingSeqNumber = incomingAckNumber
            outgoingAckNumber = incomingSeqNumber + 1
            outgoingSourcePort = incomingDestinationPort
            outgoingDestinationPort = incomingSourcePort
            outgoingPacketLength = 32

            # Form the entire packet
            outgoingPacket = formPacket(outgoingSourcePort, outgoingDestinationPort,  outgoingSeqNumber,  
                outgoingAckNumber, maxWindowSize,  outgoingPacketLength, headerFlags[1], byteArray())

            # Send the ACK packet
            udpSocket.sendto(outgoingPacket, incomingAddress)
        
            #send fin
            incomingSeqNumber = int.from_bytes(incomingMessage[4:8], byteorder = 'big')
            incomingAckNumber = int.from_bytes(incomingMessage[8:12], byteorder = 'big')
            incomingSourcePort = int.from_bytes(incomingMessage[0:2], byteorder = 'big')
            incomingDestinationPort = int.from_bytes(incomingMessage[2:4], byteorder = 'big')

            outgoingSeqNumber = incomingAckNumber
            outgoingAckNumber = incomingSeqNumber + 1
            outgoingSourcePort = incomingDestinationPort
            outgoingDestinationPort = incomingSourcePort
            outgoingPacketLength = 32

            # Form the entire packet
            outgoingPacket = formPacket(outgoingSourcePort, outgoingDestinationPort,  outgoingSeqNumber,  
                outgoingAckNumber, maxWindowSize,  outgoingPacketLength, headerFlags[2], byteArray())

            # Send the packet
            udpSocket.sendto(outgoingPacket, incomingAddress)
            
            # Wait for an ACK packet
            incomingMessage = bytearray()
            thisPackLen, incomingAddress = udpSocket.recvfrom_into(incomingMessage)
            if(incomingMessage[28] == headerFlags[1] and checkSumOkay(incomingMessage)):
                udpSocket.close()
                canListen = False
                return
        else:
        ''' edge case where fin packet is bad and we go in here anyways. will add while loop at top or incorporate this some how'''
            while(True):
                if(checksumOkay(incomingMessage) is False):
                    a=1    #do nothing
                else:
                    incomingSeqNumber = int.from_bytes(incomingMessage[4:8], byteorder = 'big')
                    incomingAckNumber = int.from_bytes(incomingMessage[8:12], byteorder = 'big')
                    incomingSourcePort = int.from_bytes(incomingMessage[0:2], byteorder = 'big')
                    incomingDestinationPort = int.from_bytes(incomingMessage[2:4], byteorder = 'big')

                    outgoingSeqNumber = incomingAckNumber + 1
                    outgoingAckNumber = incomingSeqNumber + len(incomingMessage) - 32
                    outgoingSourcePort = incomingDestinationPort
                    outgoingDestinationPort = incomingSourcePort
                    outgoingPacketLength = 32

                    # Form the entire packet
                    outgoingPacket = formPacket(outgoingSourcePort, outgoingDestinationPort,  outgoingSeqNumber,  
                        outgoingAckNumber, maxWindowSize,  outgoingPacketLength, headerFlags[1], byteArray())

                    # Send the ACK packet
                    udpSocket.sendto(outgoingPacket, incomingAddress)
                    for eachByte in incomingMessage[32:]:
                        if(numberOfBytes > 0):
                            returnData.append(eachByte)
                            numberOfBytes = numberOfBytes - 1
                        else:
                            break
                            
                            
                        ''' how do we let the server know if we are done before the file???'''
                        ''' do we say nothing and let it time out?'''
                            
                            
                    if numberOfBytes <= 0:
                        break
                    if(incomingMessage[28] == headerFlag[7]):
                        break
                incomingMessage = bytearray()
                thisPackLen, incomingAddress = udpSocket.recvfrom_into(incomingMessage)
                globalSeqNumber = globalSeqNumber + 1
                globalAckNumber = int.from_bytes(incomingMessage[4:8], byteorder = 'big') + int.from_bytes(incomingMessage[24:28], byteorder = 'big') - 32
            return returnData
    #addToCache(this)
    #sequenceNumberHere = getSeqFromByteArray(dataFromUDP)
    #if expectedSeq == sequenceNumberHere:
        #writeOutputfromcache will update the current sequence number
        #and be based on the last packet in the cache
    #    sequenceNumber = writeOutputFromCache()         
    #acknowledge(this)

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
        canListen = True


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
        outgoingPacket = formPacket(outgoingSourcePort, outgoingDestinationPort,  0,  
            0, maxWindowSize,  32, headerFlags[0], bytearray())

        # Send the SYN packet
        udpSocket.sendto(outgoingPacket, incomingAddress)
        
        # Use a blocking UDP call to wait for the CHALLENGE+ANSWER packet to come back
        incomingMessage, incomingAddress = udpSocket.recvfrom_into(packetLength)

        # Check to see if the packet is a CHALLENGE+ACK packet (indicated in 28th byte of header)
        if(incomingMessage[28] == headerFlags[4] and checkSumOkay(incomingMessage)):
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
            outgoingPacketLength = 32

            # Form the entire CHALLENGE+ACK packet
            outgoingPacket = formPacket(outgoingSourcePort, outgoingDestinationPort,  outgoingSeqNumber,  
                outgoingAckNumber, maxWindowSize,  outgoingPacketLength, headerFlags[1], int.from_bytes(incomingChallengeNumber, byteorder = 'big'))

            # Send the CHALLENGE+ACK packet
            udpSocket.sendto(outgoingPacket, incomingAddress)
        else:
            # The packet was not a CHALLENGE+ACK or the packet was corrupt 
            return

        # Use a blocking UDP call to wait for the SYN+ACK to come back
        incomingMessage2 = bytearray()
        packetLength, incomingAddress2 = udpSocket.recvfrom_into(incomingMessage2)
        udpSocket.settimeout(5)

        # Check to see if the packet is a SYN+ACK packet (indicated in 28th byte of header)
        if(incomingMessage[28] == headerFlags[5] and checkSumOkay(incomingMessage)):
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

            # Syn + Ack comment
            outgoingPacket = formPacket(outgoingSourcePort, outgoingDestinationPort,  outgoingSeqNumber,  
                outgoingAckNumber, maxWindowSize,  outgoingPacketLength, headerFlags[1], bytearray())

            # Send the SYN+ACK packet
            udpSocket.sendto(outgoingPacket, incomingAddress)
        else:
            # The packet was not a CHALLENGE+ACK or the packet was corrupt 
            return

    # This function will be used to send data
    def sendRTP(message):
        '''
        #simple?
        loop through byte array
        divide the length by (packetsize*windowsize)
        while(sendCache is not empty and notallpackets are sent):
            s
        '''
        # Figure out the number of packets needed to send the message
        messageLength = len(message)
        numPacketsNeeded = math.ceil(messageLength / (maxPacketLength - 32))
        
        numPacketsSent = 0
        while numPacketsSent < numPacketsNeeded:
            # Modify the fields for the outgoing packet
            if(messageLength > maxPacketLength - 32):
                outgoingPacketLength = maxPacketLength
            else:
                outgoingPacketLength = messageLength + 32

            # Form the packet
            outgoingPacket = formPacket(globalSourcePort, globalDestinationPort, globalSeqNumber,  
                globalAckNumber, maxWindowSize,  outgoingPacketLength, headerFlags[1], message[(numPacketsSent * (maxPacketLength - 32)):((numPacketsSent) * (maxPacketLength - 32) + outgoingPacketLength - 32])

            # Send the packet
            udpSocket.sendto(outgoingPacket, incomingAddress)

            # Wait for an ACK for the packet
            ackPacket = bytearray()
            packetLength, address = udpSocket.revcfrom_into(ackPacket)
            if(ackPacket[28] == headerFlags[1] and int.from_bytes(ackPacket[8:12], byteorder = 'big') == globalSeqNumber + messageLength - 32 and checkSumOkay(ackPacket)):
                # Increment the number of packets sent
                numPacketsSent = numPacketsSent + 1
                messageLength = messageLength - outgoingPacketLength + 32
                globalSeqNumber = globalSeqNumber + outgoingPacketLength - 32
                globalAckNumber = int.from_bytes(ackPacket[4:8], byteorder = 'big') + 1
        
    # This function will be used to close a connection
    def closeRTPSocket():
        # Send the FIN packet
        
        '''  
        ##
        ## figure out where variables come from
        ##
        ##
        '''
        
        outgoingPacket = formPacket(outgoingSourcePort, outgoingDestinationPort,  outgoingSeqNumber,  
            outgoingAckNumber, maxWindowSize,  outgoingPacketLength, headerFlags[2], bytearray())
        
        # Send the FIN packet
        udpSocket.sendto(outgoingPacket, incomingAddress)

        # Wait for the reply to the FIN
        incomingMessage = bytearray()
        packetLength, incomingAddress = udpSocket.recvfrom_into(incomingMessage)

        # Check if the packet is an ACK
        if(incomingMessage[28] == headerFlags[1] and checkSumOkay(incomingMessage)):
            
            ## needs to wait for a fin to send an ack
            
            packetLength, incomingAddress = udpSocket.recvfrom_into(incomingMessage)
            
            #hfs need some wort of while loop in case we get a non fin. also we need this in many other places possibly
            
            if(incomingMessage[28] == headerFlags[2] and checkSumOkay(incomingMessage)):
                        
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

                # Send uh Ack
                outgoingPacket = formPacket(outgoingSourcePort, outgoingDestinationPort,  outgoingSeqNumber,  
                    outgoingAckNumber, maxWindowSize,  outgoingPacketLength, headerFlags[1], bytearray())

                # Send the Ack attack packet
                udpSocket.sendto(outgoingPacket, incomingAddress)

                # Wait for a timeout period
                time.sleep(5)

                # Close the socket
                canListen = false
                udpSocket.close()
        # Check if the packet is a FIN
        if(incomingMessage[28] == headerFlags[2] and checkSumOkay(incomingMessage)):
            # Send an ACK
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

            # Send a ACK 
            outgoingPacket = formPacket(outgoingSourcePort, outgoingDestinationPort,  outgoingSeqNumber,  
                outgoingAckNumber, maxWindowSize,  outgoingPacketLength, headerFlags[1], bytearray())

            # Send the ACK packet
            udpSocket.sendto(outgoingPacket, incomingAddress)

            # Wait for an ACK
            incomingMessage = bytearray()
            packetLength, incomingAddress = udpSocket.recvfrom_into(incomingMessage)
            if(incomingMessage[28] == headerFlags[1] and checkSumOkay(incomingMessage)):
                # Wait for a timeout period
                time.sleep(5)

                # Close the socket
                canListen = false
                udpSocket.close()
        # Check if the packet is a FIN+ACK
        if(incomingMessage[28] == headerFlags[6] and checkSumOkay(incomingMessage)):
            # Send an ACK
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

            # Send a ACK 
            outgoingPacket = formPacket(outgoingSourcePort, outgoingDestinationPort,  outgoingSeqNumber,  
                outgoingAckNumber, maxWindowSize,  outgoingPacketLength, headerFlags[1], bytearray())

            # Send the ACK packet
            udpSocket.sendto(outgoingPacket, incomingAddress)

            # Wait for an ACK
            incomingMessage = bytearray()
            packetLength, incomingAddress = udpSocket.recvfrom_into(incomingMessage)

            # Wait for a timeout period
            time.sleep(5)

            # Close the socket
            canListen = false
            udpSocket.close()
        
#need to create a packet object with sequence and raw data

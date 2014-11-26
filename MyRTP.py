# This file will contain all the logic necessary for the RTP protocol

import hashlib
import math
import random
import socket
import time
def calculateChecksum( packet):
        emptyArray = bytearray(8)
        myBytes = bytearray(12)
        counter = 0
        while counter < 12:
            myBytes[counter] = packet[counter]
            counter = counter + 1
        #myBytes = packet[0:12] 
        for i in emptyArray:
            myBytes.append(i)
        for i in packet[20:]:
            myBytes.append(i)
        hasher = hashlib.sha256()
        hasher.update(myBytes)
        checksum = hasher.digest()
        return checksum[0:8]   

# This makes sure the checksum is okay
def checkSumOkay(packet):
    checksum = packet[12:20]
    ourChecksum = calculateChecksum(packet)
    return (checksum == ourChecksum) 
        
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
    maxPacketLength = 10000
    # This is the default window size
    maxWindowSize = 1024
    # This will be the ack number to be put in outgoing packets
    globalAckNumber = 0
    # This will be the sequence number to be put in outgoing packets
    globalSeqNumber = 0
    # THis will be the source port included in outgoing packets
    globalSourcePort = 0
    # This will be the destination port included in outgoing packets
    globalDestinationPort = 3
    # This is the UDP socket that we will use underneath our RTP protocol
    udpSocket = None
    # This byte array contains the following bytes in order for use in the packet: SYN, ACK, FIN, CNG, CNG+ACK, SYN+ACK, FIN+ACK, End of message
    headerFlags = bytearray.fromhex('80 40 20 10 50 C0 60 08')
    # this is for net emu
    emuIpNumber = ''  
    # this is the port
    emuPortNumber = 0
    
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
    def bindRTPSocket(self, address, portNum):
        # Extract the IP address and the port number from the address tuple
        ipAddress = address
        portNumber = portNum 
    
    def formPacket(self, sourcePort, destinationPort, seqNum, ackNum, windowSize, lengthOfPacket, flagByte, payload):
        outgoingPacket = bytearray()
        for eachByte in sourcePort.to_bytes(2, byteorder = 'big'):
            outgoingPacket.append(eachByte)
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
           outgoingPacket[index] = eachByte
           index = index + 1
        return outgoingPacket
    # This function is used to create a socket by the server to communicate with a specific client
    def acceptRTPConnection(self, localPort, netEmuIp, netEmuPort):
    

        global udpSocket
        udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpSocket.bind(('',localPort))
        udpSocket.settimeout(2)
        global emuIpNumber
        global emuPortNumber
        emuIpNumber = netEmuIp
        emuPortNumber = netEmuPort
        print('check listen')
        print(canListen)
        if canListen is False:
            return False
        # Use a blocking UDP call to wait for a SYN packet to arrive
        print('listening for connections')
        # If the packet was a SYN packet, generate a random number for the CHALLENGE+ACK reply
        randomInt = random.randint(1, 4096)
        while True:
            try:
                incomingMessage = udpSocket.recv(self.maxPacketLength)
            except:
                incomingMessage = None
            print('got first packet')
            print(incomingMessage)
           
           
            if incomingMessage is None:
                continue
            if(incomingMessage[28] == self.headerFlags[0] and checkSumOkay(incomingMessage)):
                break
        # Give access to the global variables
        global globalAckNumber
        global globalSeqNumber
        global globalDestinationPort
        global globalSourcePort
        # Retrieve the needed information from the incoming packet
        globalAckNumber = int.from_bytes(incomingMessage[4:8], byteorder = 'big') # Sequence number from incoming packet
        globalSeqNumber = 0
        globalDestinationPort = int.from_bytes(incomingMessage[0:2], byteorder = 'big')
        globalSourcePort = int.from_bytes(incomingMessage[2:4], byteorder = 'big')

        # Modify the fields for the outgoing CHALLENGE+ACK packet
        globalAckNumber = globalAckNumber + 1
        outgoingPacketLength = 32 + 4
        # Check to see if the packet is a SYN packet (indicated in 28th byte of header)
        while True:
            

            print('ack number for CHALLENGE+ACK: ' + str(globalAckNumber))
            print('seq number for CHALLENGE+ACK: ' + str(globalSeqNumber))

            # Form the entire CHALLENGE+ACK packet
            outgoingPacket = self.formPacket(globalSourcePort, globalDestinationPort,  globalSeqNumber, globalAckNumber, self.maxWindowSize, outgoingPacketLength, self.headerFlags[4], randomInt.to_bytes(4, byteorder = 'big'))

            # Send the CHALLENGE+ACK packet
            udpSocket.sendto(outgoingPacket, (emuIpNumber,emuPortNumber))
            # Use a blocking UDP call to wait for the answer to come back
            try:
                incomingMessage2 = udpSocket.recv(self.maxPacketLength)
            except:
                incomingMessage2 = None
            if incomingMessage2 is None:
                continue
            if int.from_bytes(incomingMessage2[33:37], byteorder = 'big') == randomInt:
                break
            

            # We received the correct answer to the challenge
            # Retrieve the needed information from the incoming packet
        globalAckNumber = int.from_bytes(incomingMessage[4:8], byteorder = 'big') # Sequence number from incoming packet
        globalSeqNumber = globalSeqNumber + 4 # int.from_bytes(incomingMessage[8:12], byteorder = 'big')

        # Modify the fields for the outgoing SYN+ACK packet
        globalAckNumber = globalAckNumber + 5
        outgoingPacketLength = 32
        while True:
            

            print('ack number for SYN+ACK: ' + str(globalAckNumber))
            print('seq number for SYN+ACK: ' + str(globalSeqNumber))

            # Form the entire SYN+ACK packet
            outgoingPacket = self.formPacket(globalSourcePort, globalDestinationPort,  globalSeqNumber,  
                globalAckNumber, self.maxWindowSize, outgoingPacketLength, self.headerFlags[5], bytearray())

            # Send the SYN+ACK packet
            udpSocket.sendto(outgoingPacket, (emuIpNumber,emuPortNumber))
        

        # Use a blocking UDP call to wait for the ACK to come from the client
            try:
                incomingMessage3 = udpSocket.recv(self.maxPacketLength)
            except:
                incomingMessage3 = None
            if incomingMessage3 is None:
                continue
            if incomingMessage3[28] == self.headerFlags[1]:
                break
           
        # Increment the ACK and SEQ number
        globalAckNumber = globalAckNumber + 1
        globalSeqNumber = globalSeqNumber + 1

        print('ack number at end of accept: ' + str(globalAckNumber))
        print('seq number at end of accept: ' + str(globalSeqNumber))

        # The handshake has been successfully completed, return true 
        return True


    # This function is used to receive data
    def receiveRTP(self, numberOfBytes):
        # Give access to the global variables
        global globalAckNumber
        global globalSeqNumber
        
        #handle lost, out of order, and corrupt packets
        #sequence number should be somewhere
        shouldClose = False
        shouldRecv = False
        while True:
            try:
                incomingMessage = udpSocket.recv(self.maxPacketLength)
            except:
                incomingMessage = None
            if incomingMessage is None:
                continue
            if(incomingMessage[28] == self.headerFlags[2] and checkSumOkay(incomingMessage)):
                shouldClose = True
                break
            print('acknowledgement number: ' + str(int.from_bytes(incomingMessage[4:8], byteorder = 'big')))
            print('globalAckNumber: ' + str(globalAckNumber))
            if (checkSumOkay(incomingMessage) and int.from_bytes(incomingMessage[4:8], byteorder = 'big') == globalAckNumber and (incomingMessage[28] == self.headerFlags[1] or incomingMessage[28] == self.headerFlags[7])):
                shouldRecv = True
                break
        returnData = bytearray()
            
        #closing stuff
        #send ack
        # Check to see if the packet is a FIN packet (indicated in 28th byte of header)
        if(shouldClose):
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
            outgoingAckPacket = self.formPacket(outgoingSourcePort, outgoingDestinationPort,  outgoingSeqNumber,  
                outgoingAckNumber, self.maxWindowSize,  outgoingPacketLength, self.headerFlags[1], bytearray())

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
            outgoingFinPacket = self.formPacket(outgoingSourcePort, outgoingDestinationPort,  outgoingSeqNumber,  
                outgoingAckNumber, self.maxWindowSize, outgoingPacketLength, self.headerFlags[2], bytearray())

            while True:
                # Send the ACK packet
                udpSocket.sendto(outgoingAckPacket, (emuIpNumber,emuPortNumber))
                # Send the packet
                udpSocket.sendto(outgoingFinPacket, (emuIpNumber, emuPortNumber))
                
                # Wait for an ACK packet
                try:
                    incomingMessage = udpSocket.recv(self.maxPacketLength)
                except:
                    incomingMessage = None
                if incomingMessage is None:
                    continue
                if (incomingMessage[28] == self.headerFlags[1] and checkSumOkay(incomingMessage)):
                    break


            udpSocket.close()
            canListen = False
            return
        else:
            while(True):
                outgoingPacketLength = 32
                
                globalAckNumber = globalAckNumber + len(incomingMessage) - 32

                # Form the entire ACK packet
                outgoingPacket = self.formPacket(self.globalSourcePort, self.globalDestinationPort,  globalSeqNumber,  
                    globalAckNumber, self.maxWindowSize,  outgoingPacketLength, self.headerFlags[1], bytearray())

                for eachByte in incomingMessage[32:]:
                    if(numberOfBytes > 0):
                        returnData.append(eachByte)
                        numberOfBytes = numberOfBytes - 1
                    else:
                        break
                        
                if numberOfBytes <= 0:
                    break
                if(incomingMessage[28] == self.headerFlags[7]):
                    udpSocket.sendto(outgoingPacket, (emuIpNumber,emuPortNumber))
                    index = 1
                    while index < 4:
                        index = index + 1
                        try:
                            incomingMessage = udpSocket.recv(self.maxPacketLength)
                        except:
                            incomingMessage = None
                        if incomingMessage is None:
                            continue
                        # Check to see if the packet is a Data packet (indicated in 28th byte of header)
                        elif (incomingMessage[28] == self.headerFlags[7] and checkSumOkay(incomingMessage)):
                            udpSocket.sendto(outgoingPacket, (emuIpNumber,emuPortNumber))
                            index = 1
                    globalSeqNumber = globalSeqNumber + 1                    
                    break
                while True:
                    # Send the ACK packet
                    print('waiting for new packet')
                    udpSocket.sendto(outgoingPacket, (emuIpNumber, emuPortNumber))
                    try:
                        incomingMessage = udpSocket.recv(self.maxPacketLength)
                    except:
                        incomingMessage = None
                    if (incomingMessage == None):
                        continue
                    print('expected ack number: ' + str(globalAckNumber))
                    print('ack Number: ' + str(int.from_bytes(incomingMessage[4:8], byteorder = 'big')))
                    if( int.from_bytes(incomingMessage[4:8], byteorder = 'big') == globalAckNumber and checkSumOkay(incomingMessage)):
                        globalSeqNumber = globalSeqNumber + 1
                        break
        return returnData
    #addToCache(this)
    #sequenceNumberHere = getSeqFromByteArray(dataFromUDP)
    #if expectedSeq == sequenceNumberHere:
        #writeOutputfromcache will update the current sequence number
        #and be based on the last packet in the cache
    #    sequenceNumber = writeOutputFromCache()         
    #acknowledge(this)

          
        
    # Adds data to cache and ensures ascending order of sequence numbers
    def addToCache(self, packet):
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
    def listenRTP(self):
        global canListen        
        canListen = True


    # This function connects to the specified IP address and port
    def connectRTP(self, portNum, netEmuIP, netEmuPort):
        # Extract the IP address and the port number from the address tuple
        global emuIpNumber
        global emuPortNumber
        emuIpNumber = netEmuIP
        emuPortNumber = netEmuPort

        global udpSocket
        udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpSocket.bind(('',portNum))
        udpSocket.settimeout(2)

        # Give access to the global variables
        global globalAckNumber
        global globalSeqNumber

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
        globalSeqNumber = 0
        globalAckNumber = 0
        outgoingPacket = self.formPacket(self.globalSourcePort, self.globalDestinationPort,  0,  
            0, self.maxWindowSize,  32, self.headerFlags[0], bytearray())

        # Send the SYN packet
        while True:
            print('ack number for SYN: ' + str(globalAckNumber))
            print('seq number for SYN: ' + str(globalSeqNumber))
            udpSocket.sendto(outgoingPacket, (emuIpNumber,emuPortNumber))
            print('sent first packet')
           
            # Use a blocking UDP call to wait for the CHALLENGE+ACK packet to come back
            try:
                incomingMessage = udpSocket.recv(self.maxPacketLength)
            except:
                incomingMessage = None
            if incomingMessage is None:
                continue
            if(incomingMessage[28] == self.headerFlags[4] and checkSumOkay(incomingMessage)):
                break

        # Check to see if the packet is a CHALLENGE+ACK packet (indicated in 28th byte of header)
        #if(incomingMessage[28] == self.headerFlags[4] and checkSumOkay(incomingMessage)):
            # Retrieve the needed information from the incoming packet
        globalAckNumber = globalAckNumber + 4
        globalSeqNumber = globalSeqNumber + 1 
        incomingChallengeNumber = int.from_bytes(incomingMessage[32:36], byteorder = 'big')

        # Modify the fields for the outgoing ACK packet
        outgoingPacketLength = 32 + 4
        while True:
            

            # Form the entire ACK packet
            print('ack number for answer: ' + str(globalAckNumber))
            print('seq number for answer: ' + str(globalSeqNumber))
            outgoingPacket = self.formPacket(self.globalSourcePort, self.globalDestinationPort,  globalSeqNumber,  
                globalAckNumber, self.maxWindowSize,  outgoingPacketLength, self.headerFlags[1], incomingChallengeNumber.to_bytes(4, byteorder = 'big'))

            # Send the ACK packet
            udpSocket.sendto(outgoingPacket, (emuIpNumber,emuPortNumber))
        

        # Use a blocking UDP call to wait for the SYN+ACK to come back
            try:
                incomingMessage2 = udpSocket.recv(self.maxPacketLength)
            except:
                incomingMessage2 = None
            if incomingMessage2 is None:
                continue
            # Check to see if the packet is a SYN+ACK packet (indicated in 28th byte of header)
            if(incomingMessage2[28] == self.headerFlags[5] and checkSumOkay(incomingMessage2)):
                break

      
        
    
        # Retrieve the needed information from the incoming packet
        globalAckNumber = globalAckNumber + 1
        globalSeqNumber = globalSeqNumber + 4

        # Modify the fields for the outgoing ACK packet
        outgoingPacketLength = 32

        print('ack number for ACK: ' + str(globalAckNumber))
        print('seq number for ACK: ' + str(globalSeqNumber))

        # Form the ACK Packet
        outgoingPacket = self.formPacket(self.globalSourcePort, self.globalDestinationPort,  globalSeqNumber,  
            globalAckNumber, self.maxWindowSize,  outgoingPacketLength, self.headerFlags[1], bytearray())

        # Send the ACK packet
        udpSocket.sendto(outgoingPacket, (emuIpNumber,emuPortNumber))
        index1 = 1
        while index1 < 4:
            index1 = index1 + 1
            try:
                incomingMessage2 = udpSocket.recv(self.maxPacketLength)
            except:
                incomingMessage2 = None
            if incomingMessage2 is None:
                continue
            # Check to see if the packet is a SYN+ACK packet (indicated in 28th byte of header)
            elif (incomingMessage2[28] == self.headerFlags[5] and checkSumOkay(incomingMessage2)):
                udpSocket.sendto(outgoingPacket, (emuIpNumber,emuPortNumber))
                index1 = 1
        # Increment the sequence number after the final ACK was sent
        globalSeqNumber = globalSeqNumber + 1

        print('ack number at end of connect: ' + str(globalAckNumber))
        print('seq number at end of connect: ' + str(globalSeqNumber))

            
        

    # This function will be used to send data
    def sendRTP(self, message):
        '''
        #simple?
        loop through byte array
        divide the length by (packetsize*windowsize)
        while(sendCache is not empty and notallpackets are sent):
            s
        '''
        print('starting our send method')

        # Give access to the global variables
        global globalAckNumber
        global globalSeqNumber

        # Figure out the number of packets needed to send the message
        messageLength = len(message)
        numPacketsNeeded = math.ceil(messageLength / (self.maxPacketLength - 32))
        
        numPacketsSent = 0
        while numPacketsSent < numPacketsNeeded:
            # Modify the fields for the outgoing packet
            if(messageLength > self.maxPacketLength - 32):
                outgoingPacketLength = self.maxPacketLength
                outgoingFlag = self.headerFlags[1]
            else:
                outgoingPacketLength = messageLength + 32
                outgoingFlag = self.headerFlags[7]

            # Form the packet
            outgoingPacket = self.formPacket(self.globalSourcePort, self.globalDestinationPort, globalSeqNumber,  
                globalAckNumber, self.maxWindowSize,  outgoingPacketLength, outgoingFlag, message[(numPacketsSent * (self.maxPacketLength - 32)):(numPacketsSent * (self.maxPacketLength - 32) + outgoingPacketLength - 32)])

            # Send the packet
            while True:
                print('sending packet sequence number: ' + str(globalSeqNumber))
                udpSocket.sendto(outgoingPacket, (emuIpNumber,emuPortNumber))

                # Wait for an ACK for the packet
                try:
                    ackPacket = udpSocket.recv(self.maxPacketLength)
                except:
                    ackPacket = None
                if ackPacket is None:
                    continue
                print ("one of if states is screeeewed")
                if(ackPacket[28] == self.headerFlags[1] and int.from_bytes(ackPacket[8:12], byteorder = 'big') == (globalSeqNumber + outgoingPacketLength - 32) and checkSumOkay(ackPacket)):
                    break
            print('expected ack number at end of send loop: ' + str(globalSeqNumber + outgoingPacketLength - 32))

        
            print('received an ACK with correct ack number - line 521ish')
            # Increment the number of packets sent
            numPacketsSent = numPacketsSent + 1
            messageLength = messageLength - outgoingPacketLength + 32
            globalSeqNumber = globalSeqNumber + outgoingPacketLength - 32
            globalAckNumber = globalAckNumber + 1
        
    # This function will be used to close a connection
    def closeRTPSocket(self):
        # Send the FIN packet
        
        # Give access to the global variables
        global globalAckNumber
        global globalSeqNumber
        global canListen
        
        outgoingPacket = self.formPacket(self.globalSourcePort, self.globalDestinationPort,  globalSeqNumber,  
            globalAckNumber, self.maxWindowSize, 32, self.headerFlags[2], bytearray())
        
        # Send the FIN packet
        while True:
            udpSocket.sendto(outgoingPacket, (emuIpNumber,emuPortNumber))

            # Wait for the reply to the FIN
            try:
                incomingMessage = udpSocket.recv(self.maxPacketLength)
            except:
                incomingMessage = None

            if incomingMessage is None:
                continue
            if checkSumOkay(incomingMessage) and (incomingMessage[28] == self.headerFlags[2] or incomingMessage[28] == self.headerFlags[1] or incomingMessage[28] == self.headerFlags[6]):
                break

        # Check if the packet is a FIN
        if(incomingMessage[28] == self.headerFlags[2] and checkSumOkay(incomingMessage)):
            # Send an ACK
            # Retrieve the needed information from the incoming packet
            globalSeqNumber = globalSeqNumber + 1
            globalAckNumber = globalAckNumber + 1
            outgoingPacketLength = 32

            # Send a ACK 
            outgoingPacket = self.formPacket(self.globalSourcePort, self.globalDestinationPort,  globalSeqNumber,  
                globalAckNumber, self.maxWindowSize,  outgoingPacketLength, self.headerFlags[1], bytearray())

            # Send the ACK packet
            print(outgoingPacket)
            while True:
                udpSocket.sendto(outgoingPacket, (emuIpNumber,emuPortNumber))

                # Wait for an ACK
                try:
                    incomingMessage = udpSocket.recv(self.maxPacketLength)
                except:
                    incomingMessage = None

                if incomingMessage is None:
                    continue
                if incomingMessage[28] == self.headerFlags[1] and checkSumOkay(incomingMessage):
                    break

            # Wait for a timeout period
            time.sleep(5)

            # Close the socket
            canListen = False
            udpSocket.close()
        # Check if the packet is an ACK
        elif(incomingMessage[28] == self.headerFlags[1] and checkSumOkay(incomingMessage)):
            ## needs to wait for a fin to send an ack
            while True:
                try:
                    incomingMessage = udpSocket.recv(self.maxPacketLength)
                except:
                    incomingMessage = None

                if incomingMessage is None:
                    continue

                if(incomingMessage[28] == self.headerFlags[2] and checkSumOkay(incomingMessage)):
                    break
            
            if(incomingMessage[28] == self.headerFlags[2] and checkSumOkay(incomingMessage)):
                # Retrieve the needed information from the incoming packet
                globalSeqNumber = globalSeqNumber + 1
                globalAckNumber = globalAckNumber + 1
                outgoingPacketLength = 32

                # Send an Ack
                outgoingPacket = self.formPacket(self.globalSourcePort, self.globalDestinationPort,  globalSeqNumber,  
                    globalAckNumber, self.maxWindowSize,  outgoingPacketLength, self.headerFlags[1], bytearray())

                index = 1
                while index < 4:
                    index = index + 1
                    try:
                        incomingMessage = udpSocket.recv(self.maxPacketLength)
                    except:
                        incomingMessage = None
                    if incomingMessage is None:
                        continue
                    # Check to see if the packet is a ACK packet (indicated in 28th byte of header)
                    elif (incomingMessage[28] == self.headerFlags[1] and checkSumOkay(incomingMessage)):
                        udpSocket.sendto(outgoingPacket, (emuIpNumber,emuPortNumber))
                        index = 1

                # Wait for a timeout period
                time.sleep(5)

                # Close the socket
                canListen = False
                udpSocket.close()
        # Check if the packet is a FIN+ACK
        elif(incomingMessage[28] == self.headerFlags[6] and checkSumOkay(incomingMessage)):
            # Send an ACK
            # Retrieve the needed information from the incoming packet
            globalSeqNumber = globalSeqNumber + 1
            globalAckNumber = globalAckNumber + 1
            outgoingPacketLength = 32

            # Send a ACK 
            outgoingPacket = self.formPacket(self.globalSourcePort, self.globalDestinationPort,  globalSeqNumber,  
                globalAckNumber, self.maxWindowSize,  outgoingPacketLength, self.headerFlags[1], bytearray())

            # Send the ACK packet
            while True:
                udpSocket.sendto(outgoingPacket, (emuIpNumber,emuPortNumber))

                # Wait for an ACK
                try:
                    incomingMessage = udpSocket.recv(self.maxPacketLength)
                except:
                    incomingMessage = None

                if incomingMessage is None:
                    continue

                if incomingMessage[28] == self.headerFlags[1] and checkSumOkay(incomingMessage):
                    break

            # Wait for a timeout period
            time.sleep(5)

            # Close the socket
            canListen = False
            udpSocket.close()
        
#need to create a packet object with sequence and raw data

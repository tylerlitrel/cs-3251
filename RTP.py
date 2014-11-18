# This file will contain all the logic necessary for the RTP protocol

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


# This function is used to receive data
def receiveRTP(numBytes):


# This function allows the socket to begin listening for connection requests
def listenRTP():


# This function connects to the specified IP address and port
def connectRTP(address):
    # Extract the IP address and the port number from the address tuple
    ipAddress = address[0]
    portNumber = address[1]

    # Perform the initial handshake to set up the connection


# This function will be used to send data
def sendRTP(message):


# This function will be used to close a connection
def closeRTPSocket():
    

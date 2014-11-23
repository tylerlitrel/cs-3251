# The server application for the File Transfer Application (FTA) portion of the assignment
#
# Author: Keegan Nesbitt
# Last Modified: 11/13/2014
# Course: CS 3251 

# Import the file containing the functions for the RTP protocol and any other necessary modules
import MyRTP
import sys

# Create a variable to contain a socket and other necessary variables
socket = None
windowSize = 100
currentSegmentsOut = 0 # This field will be used to ensure the window size is not exceeded

# Get the command line arguments when the fta-server.py script is run, and initialize the server
serverPortNumber = int(sys.argv[1])
netEmuIP = sys.argv[2]
netEmuPort = int(sys.argv[3])


# This function will be used to initialize the server with the specified options
def initializeServer(netEmuPort, netEmuIP, portNumber):
    # Set the necessary configuration values from the defaults and parameter
    netEmuPortNumber = netEmuPort
    netEmuIPAddress = netEmuIP
    serverPortNumber = portNumber

    # Create a socket for the server
    global socket
    socket = MyRTP.MyRTP()

    # Bind the socket to a the local address
    socket.bindRTPSocket("127.0.0.1", serverPortNumber)

    # Allow the socket to accept incoming connections
    socket.listenRTP()

# This function will be used to modify the window size being used by the application
def setWindowSize(newWindowSize):
    windowSize = newWindowSize
    global socket
    socket.setMaxWindowSize(newWindowSize)

# This function will be used to gracefully shutdown the FTA-Server
def terminateServer():
    global socket
    socket.closeRTPSocket()

    
initializeServer(netEmuPort, netEmuIP, serverPortNumber)

# Include some way to both check for the user input commands and checking for incoming connections

while True:
    # Check for the user to input commands
    userInput = input('Enter a command for the FTA Server:\n')

    # Check for the type of command input by the user
    command = userInput.split(' ')[0]
    if command == 'terminate':
        terminateServer()
    elif command == 'window':
        setWindowSize(userInput.split(' ')[1])
    elif command == 'exit':
        sys.exit()
    else:
        print('Not a valid command')

    # Wait for a client to connect to the server
    print(serverPortNumber)
    print(netEmuIP)
    print(netEmuPort)
    socket.acceptRTPConnection(serverPortNumber, netEmuIP, netEmuPort)

    # Once a client connects, wait for commands
    command = socket.receiveRTP(800000)

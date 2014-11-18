# The client application for the File Transfer Application (FTA) portion of the assignment
#
# Author: Keegan Nesbitt
# Last Modified: 11/17/2014
# CourseL CS 3251 B

# Import the file containing the functions for the RTP protocol and any other necessary modules
import RTP
import sys

# Retrieve the values from the command line arguments
clientPortNumber = sys.argv[1]
netEmuIP = sys.argv[2]
netEmuPort = sys.argv[3]

# Declare a variable that can later be used for an RTP socket
socket = None
windowSize = 100
currentSegmentsOut = 0 # This field will be used to ensure the window size is not exceeded

while True:
    # Check for the user to input commands
    userInput = raw_input('Enter a command for the FTA client:\n')

    # Check for the type of command input by the user
    command = user_input.split(' ')[0]
    if command == 'connect':
        connect()
    elif command == 'get':
        retrieveFile(user_input.split(' ')[1])
    elif command == 'put':
        sendFile(user_input.split(' ')[1])
    elif command == 'window':
        setWindowSize(int(user_input.split(' ')[1]))
    elif command == 'disconnect':
        disconnect()
    elif command == 'exit':
        sys.exit()
    else:
        print 'Not a valid command'

# Connects to the FTA server running on the same IP host
def connect():
    # Create an RTP socket to be used
    socket = RTP.createRTPSocket()
    
    # Form a connection with the server
    socket.connectRTP(("127.0.0.1", clientPortNumber + 1))

    # Print a confirmation to the user
    print 'Connection formed successfully'

# This function retrieves the specified file from the server
def retrieveFile(filename):
    # First tell the server that it needs to send a file
    sendRTP('serverToClient')

    # Receive the file from the server
    fileByteArray = receiveRTP(8000000)

    # Write the file to the directory
    file = open(filename, 'wb')
    file.write(fileByteArray)

    # Print a confirmation to the user
    print 'File has been received from the server'

# This function sends a file to the server
def sendFile(filename):
    # First tell the server that it is receiving a file
    sendRTP('clientToServer')

    # Load the file into a byte array
    fileByteArray = open(filename, 'rb').read()

    # Send the file to the server
    sendRTP(fileByteArray)

    # Print a confirmation to the user
    print 'File has been sent to the server'

# This function will be used to modify the window size being used by the application
def setWindowSize(newWindowSize):
    # Update the window size
    windowSize = newWindowSize

    # Print a confirmation to the user
    print 'The window size has been updated'

# This function is used to close the connection to the server
def disconnect()
    # Disconnect from the server
    socket.closeRTPSocket()

    # Print a confirmation to the user
    print 'Successfully disconnected from server'

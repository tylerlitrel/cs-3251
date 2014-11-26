We are now doing a stop and wait protocol. There is no pipeline.
Every statement about window size is left in for expansion purposes.
It is not currently implemented.

We added a flag, EOF. End of file. This marks the end of the transfer.
It is the fifth flag bit. Reserved bits are reduced by 1.
We found that it makes file transfer more reliable. 

General Usage:
In order to run the application you will have to use Python 3. This is a 
result of our implementation using the bytearray features of Python.
python3 fta_server.py X A P
python3 fta_client.py X A P

1.start the client as specified in the syllabus.
2.start the server as specified in the syllabus.
3.type 'connect' and the client will connect to the server
    the client will specify when connection has been established.
4.to get a file from the server , the client will
    write 'get <filename.filetype>'.
    the file specified must be in the server's directory.
    the file will then be sent.
5.to send a file to the server, the client will write
   'post <filename.filetype>'.
   the file specified must be in the client's directory.
   the file will then be sent.
6.to end the connection, type 'disconnect' in the client.
7.this will end the connection.

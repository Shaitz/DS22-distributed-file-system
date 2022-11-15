# DS22-distributed-file-system (DO)

This is an implementation of a file hosting system for the course of *Distributed Systems*.

The system is divided in two parts: *Server* and *Client*. 
The client is monitorized with *[inotify](https://man7.org/linux/man-pages/man7/inotify.7.html)* and is implemented in **C**. <br>
The server and client are implemented in **Python**


## Deployment and Execution ##

### Server ###

First we need to open a terminal and start the server by executing the ***serv_fich.py*** file located in the **server** directory: <br>
```
python serv_fich.py
```

### Client ###

After the server is running, we can open another terminal and start the client by executing the built **C** file called ***prueba_inotify*** inside the **client** directory and specifying the directory to monitor as an argument: <br>
```
./prueba_inotify <directory>
```

Now that the server and client are running, we can start making changes in the directory monitored by *inotify* inside the client and the contents should be replicated inside the server directory.<br>
NOTE: the directories created inside the monitored directory are not monitored so changes made there won't be replicated.

## Modifications ##

The file *serv_fich.py* contains a line specifying the directory that should replicate the contents of the client, this can be changed:
```
FILES_PATH = "files"
```
By default it is the directory ***files***. <br><br>

# CS433-Dynamic-VPN
A system to simpulate a peer to peer network of vpn servers, and a client to switch between the various servers in the network.

Python 3.10 or higher required

Library Dependecies:
- socket
- threading
- json
- time
- random
- tkinter (pip install tk)

Steps to run the demo:
1. Open at least 3 (can be more) terminal windows and navigate to the projects root folder
2. Run 'python3 ./rendezvous.py' in one of the terminal windows
3. In all of the other terminal windows, run 'python3 ./server_vpn.py'
4. Once the rendezvous server and all of the vpn servers are running, open another terminal window and navigate to the projects root folder
5. Run 'python3 ./client_vpn.py'
6. In the user interface, select the number of seconds between switching servers
7. Select between 'Low Connections' and 'Random Server'

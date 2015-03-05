# fashion-police
BitTorrent but not BitTorrent
# Tracker protocol
Command: post  
Argument: The torrent file (JSON)  
retrun: success or failure, failure may be due to the torrent already existing  

Command: get  
Argument: The torrent file name  
return: the torrent or failure if the torrent doesn't exist  

Command: query  
Argument: keyword or empty string (for all the torrents?)  
return: a list of torrent names  

Command: peer  
Argument: torrent file name  
return: a list of possible peers or failure if the torrent doesn't exist  

Command: uploading (better name?)  
Argument: the torrent name and piece ID  
return: success or failure, failure may be due to torrent not existing or an invalid piece ID  

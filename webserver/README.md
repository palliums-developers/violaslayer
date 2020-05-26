#webserver 
nginx + gunicorn + flask

#install
install gunicorn: apt install gunicorn
install flask: apt install flask==1.1.1
install nginx: apt install nginx

#Example
##get transactions. state = start 
http://host:port/?opt=get&type=b2v&state=start&address=2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB

##get transactions. state = end
http://host:port/?opt=get&type=b2v&state=end&address=2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB

##get v2b transactions. state = mark
http://host:port/?opt=get&type=mark&state=start&address=2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB

##check transaction is complete
http://host:port/?opt=check&type=b2v&address=0000000000000000000000000000000023e5d616f55614100b83ddece7a4c005&sequence=20200426002

##send btc transaction. state = start
##send btc transaction. state = end
##send btc transaction. state = mark

# Carbon Black Response: Process GeoIP 
The objective of this project is to find suspicious network connections made from specified processes. This script works by taking a collection of Carbon Black Response queries, paging through the results, extracting out the network connections (netconns) and appending GeoIP data to each network connection record. 

This script is related to the following blog post: https://blog.stillztech.com/2018/10/carbon-black-response-process-geoip.html 

## Requirements
In order to use this script, you will need to download the Maxmind database for `geocity`. For development/testing purposes we can use the following link below to download the `GeoLite2-City.mmdb` database:
> https://dev.maxmind.com/geoip/geoip2/geolite2/ 

To use this database, you will need to install the `geoip2` python package.
> pip3 install geoip2

## Usage
Update the `config.json` file with your Carbon Black URL and API token. Then update the `queries` section of the json file with the queries you'd like to extract and add GeoIP information too. Each query currently gets its own output file.  
> python3 main.py
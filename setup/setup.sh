#################################################
## Author: David Ribeiro			#
## Date: 11/17/2018				#
## Purpose: Automate Application Setup		#
## Prerequisites:				#
##	- log in as root			#
##	- chmod +x setup.sh			#
##	- run ./setup.sh			#
#################################################


#################################################
## Assign the data directory as a variable	#
#################################################
cd ../data
data_directory=$PWD


#################################################
## Run the python script to update import	#
## scripts with approriate directories		#
#################################################
cd ../setup
python3 update_import_data.py $data_directory


#################################################
## Update/Upgrade OS				#
#################################################
yes | apt-get update
yes | apt-get upgrade


#################################################
## Install python3 and pip3 to install packages	#
#################################################
yes | apt-get install python3
yes | apt-get install python3-pip


#################################################
## Install python3 packages			#
#################################################
yes | pip3 install numpy
yes | pip3 install sklearn
yes | pip3 install pandas
yes | pip3 install Flask
yes | pip3 install flask-mysql

#################################################
## Install mariadb				#
#################################################
yes | apt-get install mariadb-server


#################################################
## Run scripts to setup database		#
#################################################
mysql < database_setup.sql
mysql cse6242 < schema.sql
mysql cse6242 < import_data.sql



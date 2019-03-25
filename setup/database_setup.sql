#################################################
##Author: David Ribeiro				#
##Date: 11/05/2018				#
##Purpose: Automate Database & Account Creation	#
#################################################


#################################################
## Drop Database If Exists			#
## Create Database				#
#################################################

DROP DATABASE IF EXISTS cse6242;
CREATE DATABASE cse6242 CHARACTER SET UTF8;
SET GLOBAL sql_mode = "MYSQL40";


#################################################
## Create User & Grant All Privileges		#
#################################################

GRANT ALL ON *.* TO cse6242@localhost IDENTIFIED BY 'cse6242';


#################################################
## Flush Privileges To Ensure They Take Affect	#
#################################################

FLUSH PRIVILEGES;



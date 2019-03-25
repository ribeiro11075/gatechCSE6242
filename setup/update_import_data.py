#################################################
## Author: David Ribeiro			#
## Date: 11/17/2018				#
## Purpose: Update import_data.sql file to	#
##	point to the correct directory		#
#################################################


#################################################
## Import libraries				#
#################################################
import sys
import re


#################################################
## Assign data directory from script input	#
#################################################
data_directory = sys.argv[1]


#################################################
## Open import file and update directories	#
#################################################
with open('import_data.sql') as f:
	new_text = f.read()
	new_text = re.sub(r'infile.*carrier_codes_no_dupes.csv', 'infile ' + "'" + data_directory + '/carrier_codes_no_dupes.csv', new_text)
	new_text = re.sub(r'infile.*airport_info_no_dupes.csv', 'infile ' + "'" + data_directory + '/airport_info_no_dupes.csv', new_text)
	new_text = re.sub(r'infile.*flights_data_toy.csv', 'infile ' + "'" + data_directory + '/flights_data_toy.csv', new_text)


#################################################
## Save the new directories			#
################################################# 
with open('import_data.sql', "w") as f:
	f.write(new_text)



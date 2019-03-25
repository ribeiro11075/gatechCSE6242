#################################################
## Author: David Ribeiro			#
## Date: 11/05/2018				#
## Purpose: Automate Data Import		#
#################################################


#################################################
## Set Database					#
#################################################

use cse6242;


#################################################
## Import Data					#
#################################################

load data infile '/home/ubuntu/Desktop/airline_predictor/data/carrier_codes_no_dupes.csv' into table carrier_codes
fields terminated by ','
enclosed by '"'
ignore 1 lines;

load data infile '/home/ubuntu/Desktop/airline_predictor/data/airport_info_no_dupes.csv' into table airports
fields terminated by ','
enclosed by '"'
ignore 1 lines;

load data infile '/home/ubuntu/Desktop/airline_predictor/data/flights_data_toy.csv' into table flights_simple
fields terminated by ','
enclosed by '"'
ignore 1 lines
SET arr_actual = nullif(@arr_actual, '');



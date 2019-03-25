#################################################
## Author: David Ribeiro			#
## Date: 11/05/2018				#
## Purpose: Automate Schema Build		#
#################################################


#################################################
## Set Database					#
#################################################

use cse6242;


#################################################
## Create Tables				#
#################################################

create table carrier_codes (
	airline_id 			int 		not null	primary key,
	carrier_code 			varchar(3)	not null,
	carrier_name 			varchar(100)	not null
);


create table carrier_codes_hist (
	airline_id 			int 		not null,
	carrier_code 			varchar(3)	not null,
	carrier_name 			varchar(100)	not null,
	seq				int		not null,
	primary key (airline_id, seq)
);


create table airports (
	airport_seq_id			int		not null	primary key,	
	airport_id			int		not null,
	airport				varchar(3)	not null,
	airport_name			varchar(80)	not null,
	airport_city_name		varchar(80)	not null,
	airport_country			varchar(30)	not null,
	airport_state			varchar(100)	null,
	airport_state_code		varchar(2)	null,
	city_market_name		varchar(80)	not null,
	latitude_degrees		int		not null,
	latitude_hemisphere		varchar(1)	not null,
	latitude_minutes		int		not null,
	latitude_seconds		int		not null,
	latitude			DECIMAL(10, 8)	not null,
	longitude_degrees		int		not null,
	longitude_hemisphere		varchar(1)	not null,
	longitude_minutes		int		not null,
	longitude_seconds		int		not null,
	longitude			DECIMAL(11, 8)	not null,
	utc_local_time_variation	int		null,
	airport_start_date		date		not null,
	airport_thru_date		date		null,
	airport_is_closed		int		not null,
	airport_is_latest		int		not null
);


create table airports_hist (
	airport_seq_id			int		not null	primary key,
	airport_id			int		not null,
	airport				varchar(3)	not null,
	airport_name			varchar(80)	not null,
	airport_full_name		varchar(80)	not null,
	airport_country			varchar(30)	not null,
	airport_state			varchar(30)	null,
	airport_state_code		varchar(2)	null,
	city_market_name		varchar(80)	not null,
	latitude_degrees		int		not null,
	latitude_hemisphere		varchar(1)	not null,
	latitude_minutes		int		not null,
	latitude_seconds		int		not null,
	latitude			DECIMAL(10, 8)	not null,
	longitude_degrees		int		not null,
	longitude_hemisphere		varchar(1)	not null,
	longitude_minutes		int		not null,
	longitude_seconds		int		not null,
	longitude			DECIMAL(11, 8)	not null,
	utc_local_time_variation	int		null,
	airport_start_date		date		not null,
	airport_thru_date		date		null,
	airport_is_closed		int		not null,
	airport_is_latest		int		not null,
	seq				int
);


create table flights (
	day_of_week			int		not null,
	airline_id			int		not null,
	carrier				int		not null,
	origin_airport_id		int		not null,
	dest_airport_id			int		not null,
	cancelled_status		varchar(5)	not null,
	cancellation_code		int		not null,
	diverted_status			varchar(5)	not null,
	diverted_reached_dest		int		not null,
	od_pair_delay			decimal(13, 10)	not null,
	airport_out_delay		decimal(13, 10)	not null,
	delayed_status			varchar(5)	not null,
	missing_od_pair_delay		varchar(5)	not null,
	airport_cancel_ratio_binned	int		not null,
	od_cancel_ratio_binned		int		not null,
	dep_scheduled_fed_holiday	varchar(5)	not null,
	arr_scheduled_fed_holiday	varchar(5)	not null,
	dep_scheduled_year		int		not null,
	dep_scheduled_month		int		not null,
	dep_scheduled_week		int		not null,
	dep_scheduled_day		int		not null,
	dep_scheduled_day_of_week	int		not null,
	dep_scheduled_day_of_year	int		not null,
	dep_scheduled_month_end		varchar(5)	not null,
	dep_scheduled_month_start	varchar(5)	not null,
	dep_scheduled_quarter_end	varchar(5)	not null,
	dep_scheduled_quarter_start	varchar(5)	not null,
	dep_scheduled_year_end		varchar(5)	not null,
	dep_scheduled_year_start	varchar(5)	not null,
	dep_scheduled_hour		int		not null,
	dep_scheduled_minute		int		not null,
	dep_scheduled_second		int		not null,
	dep_scheduled_elapsed		int		not null,
	arr_scheduled_year		int		not null,
	arr_scheduled_month		int		not null,
	arr_scheduled_week		int		not null,
	arr_scheduled_day		int		not null,
	arr_scheduled_day_of_week	int		not null,
	arr_scheduled_day_of_year	int		not null,
	arr_scheduled_month_end		varchar(5)	not null,
	arr_scheduled_month_start	varchar(5)	not null,
	arr_scheduled_quarter_end	varchar(5)	not null,
	arr_scheduled_quarter_start	varchar(5)	not null,
	arr_scheduled_year_end		varchar(5)	not null,
	arr_scheduled_year_start	varchar(5)	not null,
	arr_scheduled_hour		int		not null,
	arr_scheduled_minute		int		not null,
	arr_scheduled_second		int		not null,
	arr_scheduled_elapsed		int		not null,
	dep_delay_minutes		int		not null,
	airport_cancel_ratio		decimal(11, 10)	not null,
	arr_actual			timestamp	not null,
	arr_delay_minutes		int		not null,
	arr_scheduled			timestamp	not null,
	carrier_delay			int		not null,
	dep_actual			timestamp	not null,
	dep_scheduled			timestamp	not null,
	dep_scheduled_rounded_up	timestamp	not null,
	late_aircraft_delay		int		not null,
	od_cancel_ratio			decimal(11, 10)	null,
	on_time				varchar(5)	not null
);


create table flights_simple (
	day_of_week			int		not null,
	airline_id			int		not null,
	origin_airport_id		int		not null,
	dest_airport_id			int		not null,
	dep_delay_minutes		int		not null,
	cancelled_status		varchar(5)	not null,
	diverted_status			varchar(5)	not null,
	dep_actual			timestamp	not null,
	dep_scheduled			timestamp	not null,
	arr_scheduled			timestamp	not null,
	arr_actual			timestamp,
	hour_floor		timestamp		not null,
	od_pair_delay			decimal(13, 10)	not null,
	airport_out_delay		decimal(13, 10)	not null,
	od_cancel_ratio			decimal(11, 10)	null,
	airport_cancel_ratio		decimal(11, 10)	not null,
	delayed_status			varchar(5)	not null,
	missing_od_pair_delay		varchar(5)	not null,
	month		int		not null,
	on_time				varchar(5)	not null
);



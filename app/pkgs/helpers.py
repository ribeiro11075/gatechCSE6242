#########################################################
## Import libraries					#
#########################################################
from datetime import datetime, timedelta


#########################################################
##							#
#########################################################
def hour_rounder(t):

	return t.replace(second = 0, microsecond = 0, minute = 0, hour = t.hour) + timedelta(hours = t.minute // 30)


#########################################################
##							#
#########################################################
def parse_json_date(t):

	return datetime.strptime(t, '%Y-%m-%d %H:%M:%S')


#########################################################
##							#
#########################################################
def hour_floor(t):

	return t.replace(microsecond = 0, second = 0, minute = 0)


#########################################################
##							#
#########################################################
def add_days(date, time_interval):

	date += timedelta(days = time_interval)

	return date


#########################################################
##							#
#########################################################
def package_result(single_result, str_cols, keys):

	single_result = list(single_result)

	for i in str_cols:
		single_result[i] = str(single_result[i])

	return dict(zip(keys, single_result))



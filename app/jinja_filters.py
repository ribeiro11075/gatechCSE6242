#########################################################
## Import custom libraries				#
#########################################################
from pkgs import helpers


#########################################################
## Import libraries					#
#########################################################
from datetime import datetime


#########################################################
# Jinja2 template filter to convert			#
# date.time into date format				#
#########################################################
def format_date(d):
	if isinstance(d, str):
		d = datetime.strptime(d, '%Y-%m-%d %H:%M:%S')

	return datetime.strftime(d, '%B %d, %Y %I:%M %p')


#########################################################
# Jinja2 template filter to convert			#
# date.time into single hour				#
#########################################################
def format_hour(d):
	if isinstance(d, str):
		d = datetime.strptime(d, '%Y-%m-%d %H:%M:%S')

	return datetime.strftime(d, '%I %p')


#########################################################
# Jinja2 template filter to convert			#
# date.time into single hour				#
#########################################################
def get_hour(d):
	if isinstance(d, str):
		d = datetime.strptime(d, '%Y-%m-%d %H:%M:%S')

	return datetime.strftime(d, '%H')


#########################################################
# Jinja2 template filter to convert			#
# date.time into single hour				#
#########################################################
def format_datepicker(d):
	if isinstance(d, str):
		d = datetime.strptime(d, '%Y-%m-%d %H:%M:%S')

	return datetime.strftime(d, '%m/%d/%Y')


#########################################################
# Jinja2 template filter to convert			#
# date.time into single hour				#
#########################################################
def get_startdate(d):
	if isinstance(d, str):
		d = datetime.strptime(d, '%Y-%m-%d %H:%M:%S')

	curr_date = helpers.hour_rounder(datetime.now())

	return '-' + str((curr_date - d).days) + 'd'

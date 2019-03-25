#########################################################
##Date: 10/28/2018					#
##Purpose: Holds Python functions for SQL queries 	#
#########################################################
import numpy as np
from pkgs import helpers


#########################################################
##							#
#########################################################
def connect_db(db):

	conn = db.connect()
	cursor = conn.cursor()

	return conn, cursor


#########################################################
##							#
#########################################################
def get_min_date(cursor, time_interval):
	
	query = 'SELECT MIN(dep_scheduled) FROM flights_simple'

	cursor.execute(query)
	min_dt = cursor.fetchone()[0]

	# Increment because we need historical data for predictions. The interval should be what the model expects for length of training data.
	min_dt = helpers.add_days(min_dt, time_interval)

	# Return as string since that's expected in the template
	min_dt = str(min_dt)

	return min_dt


#########################################################
##							#
#########################################################
def get_max_date(cursor):

	query = 'SELECT MAX(dep_scheduled) FROM flights_simple'

	# We need this because we don't have data to make predictions for today; we need to stop the UI when data ends.
	cursor.execute(query)
	max_dt = cursor.fetchone()[0]

	# Return as string since that's expected in the template
	max_dt = str(max_dt)

	return max_dt


#########################################################
##							#
#########################################################
def get_classify_train_data(cursor, start_date, time_interval):
	# Gets the training data from start_date working back the number of days specified in interval
	# Feature variables = od_pair_delay, airport_out_delay, od_cancel_ratio, airport_cancel_ratio
	# Response variables = on_time, delayed_status, cancelled_status
	query = 'SELECT od_pair_delay, airport_out_delay, od_cancel_ratio, airport_cancel_ratio, on_time, delayed_status, cancelled_status ' \
		    'FROM flights_simple WHERE dep_scheduled BETWEEN %s - INTERVAL {} DAY AND %s'.format(time_interval)

	cursor.execute(query, (start_date, start_date))
	all_data = np.array(cursor.fetchall())

	# In case we only return one result, must make two dimensional
	if len(all_data) == 1:
		all_data = all_data.reshape((1, len(all_data)))

	# Split into X and y
	feature_cols = (0, 1, 2, 3)
	response_cols = (4, 5, 6)

	train_X = all_data[:, feature_cols]
	train_y = all_data[:, response_cols]

	# Convert from string to bool
	train_y = train_y == 'True'

	return train_X, train_y


#########################################################
##							#
#########################################################
def get_reg_train_data(cursor, start_date, time_interval):
	# Gets the training data from start_date working back the number of days specified in interval
	# Feature variables = od_pair_delay, airport_out_delay, od_cancel_ratio, airport_cancel_ratio
	# Response variables = on_time, delayed_status, cancelled_status
	# This time train on only delayed flights
	query = 'SELECT od_pair_delay, airport_out_delay, od_cancel_ratio, airport_cancel_ratio, dep_delay_minutes ' \
		    'FROM flights_simple WHERE (dep_scheduled BETWEEN %s - INTERVAL {} DAY AND %s) AND delayed_status = "True"'.format(time_interval)

	cursor.execute(query, (start_date, start_date))

	all_data = np.array(cursor.fetchall())

	# In case we only return one result, must make two dimensional
	if len(all_data) == 1:
		all_data = all_data.reshape((1, len(all_data)))

	# Split into X and y
	feature_cols = (0, 1, 2, 3)
	response_cols = (4,)
	train_X = all_data[:, feature_cols]
	# Ravel b/c sklearn expects a 1-d array for regression
	train_y = np.ravel(all_data[:, response_cols])

	return train_X, train_y


#########################################################
##							#
#########################################################
def get_classify_predict_data(cursor, time, origin, destination):

	# Fills  in the extra data needed to make a prediction (such as airport delay info)
	# Get hour floor because we use hourly blocks for calculating the delay info
	dt = helpers.parse_json_date(time)
	dt = helpers.hour_floor(dt)
	dt = str(dt)

	query = 'SELECT od_pair_delay, airport_out_delay, od_cancel_ratio, airport_cancel_ratio ' \
		    'FROM flights_simple ' \
		    'WHERE origin_airport_id = %s AND dest_airport_id = %s ' \
		    'AND dep_scheduled BETWEEN %s  AND %s + INTERVAL 60 MINUTE ' \
		    'LIMIT 1'

	cursor.execute(query, (origin, destination, dt, dt))
	results = cursor.fetchone()

	if results is not None:
		# Reshape for sklearn
		results = np.array(results)
		results = results.reshape((1, len(results)))

	return results


#########################################################
##							#
#########################################################
def get_reg_predict_data(cursor, time, origin, destination):

	# Fills  in the extra data needed to make a prediction (such as airport delay info)
	# Get hour floor because we use hourly blocks for calculating the delay info
	dt = helpers.parse_json_date(time)
	dt = helpers.hour_floor(dt)
	dt = str(dt)

	query = 'SELECT od_pair_delay, airport_out_delay, od_cancel_ratio, airport_cancel_ratio ' \
		    'FROM flights_simple ' \
		    'WHERE origin_airport_id = %s AND dest_airport_id = %s ' \
		    'AND dep_scheduled BETWEEN %s  AND %s + INTERVAL 60 MINUTE ' \
		    'LIMIT 1'

	cursor.execute(query, (origin, destination, dt, dt))
	results = cursor.fetchone()

	if results is not None:
		# Reshape for sklearn
		results = np.array(results)
		results = results.reshape((1, len(results)))

	return results


#########################################################
##							#
#########################################################
def get_airports(cursor, time):

	# Gets airports active during the current hour
	# Get hour floor because we are using hourly blocks
	dt = helpers.parse_json_date(time)
	dt = helpers.hour_floor(dt)

	# We need to combine the origin / dest pairs to get distinct values; what airports have
	# taking off or departing flights this hour?
	query = 'SELECT a.airport_id, a.airport, a.airport_name, a.airport_city_name, a.airport_state, ' \
				'a.airport_state_code, a.utc_local_time_variation, a.latitude, a.longitude ' \
		    'FROM airports AS a ' \
		    'INNER JOIN ' \
		    '(SELECT DISTINCT(all_ap.airport_id) FROM (' \
					'SELECT origin_airport_id AS airport_id FROM flights_simple UNION SELECT dest_airport_id AS airport_id ' \
					'FROM flights_simple WHERE flights_simple.dep_scheduled BETWEEN %s  AND %s + INTERVAL 60 MINUTE ' \
			    ') as all_ap' \
			') AS hourly_aps ' \
			'ON a.airport_id = hourly_aps.airport_id'

	cursor.execute(query, (dt, dt))
	results = cursor.fetchall()

	# The last two columns (lat/long) need to be converted to strings because Decimal types aren't JSON serializable
	str_cols = [-1, -2]

	# Give keys to make usable at front end
	keys = ['airport_id', 'airport_code', 'airport_name', 'airport_city_name', 'airport_state', 'airport_state_code', 'utc_local_time_variation', 'latitude', 'longitude']

	if results is not None:
		results = [helpers.package_result(single_result = r, str_cols = str_cols, keys = keys) for r in results]
		results = {'airports': results}

	return results


#########################################################
##							#
#########################################################
def get_network(cursor, time):
	
	# Gets the network state for the current hour
	# Get hour floor because we are using hourly blocks
	dt = helpers.parse_json_date(time)
	dt = helpers.hour_floor(dt)

	# The min functions here ensure we only get one result; these stats are the same for each OD pair given at hour
	query = 'SELECT origin_airport_id, dest_airport_id, MIN(od_pair_delay), MIN(od_cancel_ratio) ' \
			'FROM flights_simple ' \
			'WHERE dep_scheduled BETWEEN %s  AND %s + INTERVAL 60 MINUTE ' \
			'GROUP BY origin_airport_id, dest_airport_id'

	cursor.execute(query, (dt, dt))
	results = cursor.fetchall()

	# The last two columns (lat/long) need to be converted to strings because Decimal types aren't JSON serializable
	str_cols = [-1, -2]

	# Give keys to make usable at front end
	keys = ['origin_id', 'dest_id', 'od_pair_delay', 'od_cancel_ratio']

	if results is not None:
		results = [helpers.package_result(single_result = r, str_cols = str_cols, keys = keys) for r in results]
		results = {'network': results}

	return results



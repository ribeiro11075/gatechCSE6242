#########################################################
# Import custom libraries				#
#########################################################
import config
import data
import jinja_filters
import model
from pkgs import api_lib


#########################################################
# Import libraries					#
#########################################################
from flask import Flask, render_template, request
from flaskext.mysql import MySQL


#########################################################
# Initialize application & database			#
#########################################################
app = Flask(__name__)
app.config.from_object('config.dev_config')
mysql = MySQL()
mysql.init_app(app)


#########################################################
## Map Jinja2 templates					#
#########################################################
app.jinja_env.filters['format_date'] = jinja_filters.format_date
app.jinja_env.filters['format_hour'] = jinja_filters.format_hour
app.jinja_env.filters['get_hour'] = jinja_filters.get_hour
app.jinja_env.filters['format_datepicker'] = jinja_filters.format_datepicker
app.jinja_env.filters['get_startdate'] = jinja_filters.get_startdate


#########################################################
##							#
#########################################################
@app.route('/')
def index():
	
	conn, cursor = data.connect_db(db = mysql)

	min_date = data.get_min_date(cursor = cursor, time_interval = app.config['TRAINING_INTERVAL'])
	max_date = data.get_max_date(cursor = cursor)

	# For now, we should just default to the last date in the time range on page load since we have no current data.
	curr_time = max_date

	# As currently built, we will only operate on historical data, so we can always go to the final hour
	max_time = app.config['MAX_TIME']

	conn.close()

	return render_template('filters.html', curr_time = curr_time, min_date = min_date, max_time = max_time, max_date = max_date)


#########################################################
##							#
#########################################################
@app.route('/api/airports-url-parameters', methods=['GET'])
def airports_parameters():

	conn, cursor = data.connect_db(db = mysql)

	required_params = ['datetime']
	model_params = request.args.to_dict()

	params_check = api_lib.params_checker(required_params = required_params, model_params = model_params, input_type = 'url').params_exist_populated()

	if not params_check.check:
		return api_lib.request_sender(data = None, status_code = 400, message = params_check.message).get_response()

	airports = data.get_airports(cursor = cursor, time = model_params['datetime'])

	response = api_lib.request_sender(data = airports, status_code = 200, message = params_check.message).get_response()

	conn.close()

	return response


#########################################################
##							#
#########################################################
@app.route('/api/network-url-parameters', methods=['GET'])
def network_parameters():

	conn, cursor = data.connect_db(db = mysql)

	required_params = ['datetime']
	model_params = request.args.to_dict()

	params_check = api_lib.params_checker(required_params = required_params, model_params = model_params, input_type = 'url').params_exist_populated()
	
	if not params_check.check:
		return api_lib.request_sender(data = None, status_code = 400, message = params_check.message).get_response()

	# Query database for given data
	network = data.get_network(cursor = cursor, time = model_params['datetime'])

	response = api_lib.request_sender(data = network, status_code = 200, message = params_check.message).get_response()

	conn.close()

	return response


#########################################################
##							#
#########################################################
@app.route('/api/classify-url-parameters', methods=['GET'])
def classify_parameters():

	conn, cursor = data.connect_db(db = mysql)

	required_params = ['datetime', 'origin', 'dest']
	model_params = request.args.to_dict()

	params_check = api_lib.params_checker(required_params = required_params, model_params = model_params, input_type = 'url').params_exist_populated()

	if not params_check.check:
		return api_lib.request_sender(data = None, status_code = 400, message = params_check.message).get_response()

	# Query database for given data then classify
	train_X, train_Y = data.get_classify_train_data(cursor = cursor, start_date = model_params['datetime'], time_interval = 20)

	predict_X = data.get_classify_predict_data(cursor = cursor, time = model_params['datetime'], origin = model_params['origin'], destination = model_params['dest'])

	# Check to make sure we have data
	if predict_X is not None:
		prediction = model.classify_fit_predict(X_train = train_X, y_train = train_Y, X_predict = predict_X)
	else:
		# We can't make a prediction without all the data
		prediction = None

	response = api_lib.request_sender(data = prediction, status_code = 200, message = params_check.message).get_response()

	conn.close()

	return response


#########################################################
##							#
#########################################################
@app.route('/api/reg-url-parameters', methods=['GET'])
def regression_parameters():

	conn, cursor = data.connect_db(db = mysql)

	required_params = ['datetime', 'origin', 'dest']
	model_params = request.args.to_dict()

	params_check = api_lib.params_checker(required_params = required_params, model_params = model_params, input_type = 'url').params_exist_populated()

	if not params_check.check:
		return api_lib.request_sender(data = None, status_code = 400, message = params_check.message).get_response()

	# Query database for given data then classify
	train_X, train_Y = data.get_reg_train_data(cursor = cursor, start_date = model_params['datetime'], time_interval = 10)

	predict_X = data.get_reg_predict_data(cursor = cursor, time = model_params['datetime'], origin = model_params['origin'], destination = model_params['dest'])


	# Check to make sure we have data
	if predict_X is not None:
		prediction = model.reg_fit_predict(X_train = train_X, y_train = train_Y, X_predict = predict_X)
	else:
		# We can't make a prediction without all the data
		prediction = None

	response = api_lib.request_sender(data = prediction, status_code = 200, message = params_check.message).get_response()

	conn.close()

	return response


#########################################################
##							#
#########################################################
@app.route('/api/model-json-parameters', methods=['POST'])
def model_json():

	# TODO update this with the framework used for GET above or just delete so we're not doubling up on everything
	required_params = ['id']

	if request.method == 'POST':
		model_params = request.get_json()

		# list of dictionaries
		if isinstance(model_params, list):
			for item_params in model_params:

				params_check = api_lib.params_checker(required_params = required_params, model_params = item_params, input_type = 'json').params_exist_populated()

				if not params_check.check:
					return api_lib.request_sender(data = None, status_code = 400, message = params_check.message).get_response()
		# dictionary
		elif isinstance(model_params, dict):

			params_check = api_lib.params_checker(required_params = required_params, model_params = item_params, input_type = 'json').params_exist_populated()

			if not params_check.check:
				return api_lib.request_sender(data = None, status_code = 400, message = params_check.message).get_response()

		return api_lib.request_sender(data = data, status_code = 200, message = params_check.message).get_response()
	else:
		raise api_lib.request_sender(data = None, status_code = 400, message = 'Something went wrong')


#########################################################
## Initialize application				#
#########################################################
if __name__ == '__main__':
	app.run()



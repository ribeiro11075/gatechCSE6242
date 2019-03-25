#########################################################
## Import libraries					#
#########################################################
from flask import jsonify


#########################################################
##							#
#########################################################
class params_checker():

	def __init__(self, required_params, model_params, input_type):
		self.required_params = required_params
		self.model_params = model_params
		self.input_type = input_type
		self.message = 'success'
		self.check = True


	def params_exist_populated(self):

		if not all(param in self.model_params for param in self.required_params):
			self.message = 'Required to supply the {} parameter(s) with a value for each in the {}'.format(', '.join(self.required_params), self.input_type)
			self.check = False

			return self

		for param in self.required_params:
			if not self.model_params[param] or not self.model_params.get(param):
				self.message = 'Required to populate a value for the {} parameter in the {}'.format(param, self.input_type)
				self.check = False

				return self

		return self


#########################################################
##							#
#########################################################
class request_sender():

	def __init__(self, data, status_code, message):
		self.data = data
		self.status_code = status_code
		self.message = message


	def get_response(self):
		response =	{
				'data':		self.data,
				'message':	self.message
				}

		return jsonify(response), self.status_code



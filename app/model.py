#########################################################
## Import libraries					#
#########################################################
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeRegressor
import numpy as np


#########################################################
## Random forest fitting & prediction			#
#########################################################
def classify_fit_predict(X_train, y_train, X_predict):

	# Given a vector of features, fits a RF and returns predictions based on historical data
	# Default parameters for now; will update with final model params
	rf = RandomForestClassifier(n_estimators = 10)

	rf.fit(X_train, y_train)
	prediction = rf.predict_proba(X_predict)

	# By default, predictions are in a binary [[prob_class, prob_not_class], [prob_class, prob_not_class]]
	# format for all classes. This just puts the output into a more user-friendly format: [prob_1 ,prob_2]
	prediction = np.array(prediction)[:, :, 1].T

	cols = ['od_pair_delay', 'airport_out_delay', 'od_cancel_ratio', 'airport_cancel_ratio']
	feature_importance = dict(zip(cols, rf.feature_importances_))
	# Cast decimals b/c they aren't JSON serializable
	feature_vals = [str(x) for x in np.ravel(X_train)]
	feature_vals = dict(zip(cols, feature_vals))

	return {
		'prediction': {
			'on-time': prediction[0][0],
			'delayed': prediction[0][1],
			'cancelled': prediction[0][2]
		},
		'feature_importance': feature_importance,
		'feature_values': feature_vals
	}


#########################################################
## Random forest fitting & prediction			#
#########################################################
def reg_fit_predict(X_train, y_train, X_predict):

	# Given a vector of features, fits a RF and returns predictions based on historical data
	# Default parameters for now; will update with final model params
	dt = DecisionTreeRegressor()

	dt.fit(X_train, y_train)
	prediction = dt.predict(X_predict)

	cols = ['od_pair_delay', 'airport_out_delay', 'od_cancel_ratio', 'airport_cancel_ratio']
	feature_importance = dict(zip(cols, dt.feature_importances_))
	# Cast decimals b/c they aren't JSON serializable
	feature_vals = [str(x) for x in np.ravel(X_train)]
	feature_vals = dict(zip(cols, feature_vals))

	return {
		'prediction': prediction[0],
		'feature_importance': feature_importance,
		'feature_values': feature_vals
	}

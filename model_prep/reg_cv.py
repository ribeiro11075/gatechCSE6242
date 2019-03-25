import numpy as np
import pandas as pd
import pickle
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, make_scorer
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import PredefinedSplit
import os


def load_data(path):
    """This contains tasks that need to be performed only once when the data is loaded."""
    print("\nLoading data.\n")

    # Columns that need to be read as date-times
    date_cols = [
        "DepActual",
        "DepScheduled",
        "ArrScheduled",
        "ArrActual",
        "HourFloor"
    ]

    # Read dates in as DT objects
    flights = pd.read_csv(path, parse_dates=date_cols, nrows=5000000)
    # Trim down to flights that were delayed
    flights = flights.loc[flights["Delayed"] == True, :]

    # Get every third observation for testing
    test_interval = 3
    # Find out how many times we need to repeat our sequence
    repeats = (flights.shape[0] // test_interval) + 1
    # Generate a mask where every third observation is for testing like: [validation, validation, testing] * repeats
    pattern = [0] * test_interval
    pattern[-1] = 1
    test_mask = pattern * repeats
    # We might be over by a few, so downsize to match the data
    test_mask = np.array(test_mask[:flights.shape[0]], dtype=bool)
    # Negate to get the training set
    flights_train = flights[~test_mask]
    flights_test = flights[test_mask]

    return flights_train, flights_test


def select_cols(train, test, cols):
    # Reduce to just the columns we care about
    # Drop remaining NA too; do this here because we only want to consider the subset of columns
    train = train.loc[:, cols].dropna()
    test = test.loc[:, cols].dropna()

    return train, test


def grid_search(train, model, strategy):

    if strategy == "stratify":
        n_folds = 5
        # Find out how many times we need to repeat our sequence
        repeats = (train.shape[0] // n_folds) + 1
        # Generate a list of repeated CV assignments
        cv_assignments = list(range(0, n_folds)) * repeats
        # We might be over by a few, so downsize to match the data
        cv_assignments = np.array(cv_assignments[:train.shape[0]])
        cv = PredefinedSplit(test_fold=cv_assignments)

    elif strategy == "validation_set":
        # TODO implement this to use entire years as validation set.
        pass

    else:
        raise Exception("Must provide a CV strategy.")

    # Setup grid search with proper parameters
    clf = GridSearchCV(
        estimator=model["estimator"],
        param_grid=model["params"],
        scoring={
            "r2": make_scorer(r2_score),
            "mse": make_scorer(mean_squared_error)
        },
        # Use Log Loss for determining the "best" classifier
        refit="r2",
        cv=cv,
        return_train_score=True
    )

    # Get rid of response columns
    X = train.drop(response_cols, axis=1)
    # Last three columns have outcomes
    y = np.ravel(train[response_cols])
    clf.fit(X, y)

    return clf


if __name__ == "__main__":
    all_cols = {
        "f1": [
            "AirportCancelRatio",
            "AirportOutDelay",
            "DepDelayMinutes",
        ],
        "f2": [
            "OD-PairDelay",
            "AirportOutDelay",
            "OD-CancelRatio",
            "AirportCancelRatio",
            "DepDelayMinutes",
        ],
        "f3": [
            "OD-PairDelay",
            "AirportOutDelay",
            "OD-CancelRatio",
            "AirportCancelRatio",
            "MissingOD-PairDelay",
            "DepDelayMinutes",
        ],
    }

    response_cols = ["DepDelayMinutes"]

    all_models = {
        "DT": {
            "estimator": DecisionTreeRegressor(),
            "params": {
                "min_impurity_decrease": [0.01, 0.05, 0.1, 0.2, 0.5]
            }
        },
        "rf": {
            "estimator": RandomForestRegressor(),
            "params": {
                "n_estimators": [10],
                #"max_features": ["sqrt", None]
            }
        },
    }

    all_results = {}

    data_path = os.path.join("..", "data")
    print(os.getcwd())
    train_base, test_base = load_data(os.path.join(data_path, "all_flights_wrangled.csv"))

    # Loop over all feature vectors
    for f_name, cols in all_cols.items():
        train_iter, test_iter = select_cols(train_base, test_base, cols)
        # Loop over all models
        for m_name, model in all_models.items():
            print("Starting grid search for...")
            print("Feature Vector: {}, Model: {}".format(f_name, m_name))
            print()
            clf = grid_search(train_iter, model, strategy="stratify")

            prob_predictions = np.array(clf.predict(test_iter.drop(response_cols, axis=1)))

            all_results[(f_name, m_name)] = {
                "cv_results": clf.cv_results_,
                "test_results": {
                    "r2": r2_score(
                        test_iter[response_cols],  # True output
                        prob_predictions  # Predicted output
                    ),
                    "mse": mean_squared_error(
                        test_iter[response_cols],  # True output
                        prob_predictions  # Predicted output
                    )
                }
            }

    pickle.dump(all_results, open("reg_cv_results.p", "wb"))

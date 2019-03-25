# Airline Delay & Cancellation Prediction Project

## Description
The application was built to help customers, businesses, and airlines predict the probability of a flight being on-time, cancelled, or delayed.  The application will also give interested parties an anticipated waiting time if a flight is expected to be delayed. Additionally, all factors used in the models are displayed with the relative level of importance to help build end-user confidence.

## Installation
This directory contains the scripts required to install dependencies and setup the database schema.  The following steps should be followed to properly setup your system, with the assumption you are running an Ubuntu OS (>= v16.04):

1. Run the following command to log in as root: `sudo su - root`
2. Navigate to `airline_predictor/setup`.
3. Run the following command to grant permissions to run the bash file: `chmod +x setup.sh`
4. Run the following command to execute the setup bash file: `run ./setup.sh`

**Note**: This repo only includes a toy dataset. However, scripts are included within the repo to scrape and prepare the full dataset. If you would like the full dataset, navigate to `airline_predictor/data_prep` and run `python3 main.py`. You will need to update the path for the `flights_simple` table in `import_data.sql` to point to the newly-generated file once the scripts complete. The script will likely take several hours to run.

## Execution
The following steps should be followed to run a local instance of the application, with the assumption you are running on an Ubuntu OS (>= 16.04):

1. Navigate to the following directory: `airline_predictor/app`
2. Run the following command to run a local Flask web server: `python3 app.py`
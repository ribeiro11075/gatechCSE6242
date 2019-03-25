import pandas as pd
import numpy as np
from datetime import datetime
import os


# Initial time fields from database; used across multiple functions
time_fields = ["DepTime", "CRSDepTime", "CRSArrTime", "ArrTime"]
# Path for data folder
data_path = os.path.join("..", "data")


def prep_data(flights, airport_info):
    # Add airport TZ info
    flights = flights.merge(airport_info, left_on="OriginAirportID", right_on="AIRPORT_ID")
    # Initially we added origin data so there will be overlap, fix the origin and arrival airport names here
    flights = flights.merge(airport_info, left_on="DestAirportID", right_on="AIRPORT_ID",
                            suffixes=("_ORIGIN", "_DEST"))

    # Drop NA because we can"t use them...
    flights.dropna(subset=["UTC_LOCAL_TIME_VARIATION_ORIGIN", "UTC_LOCAL_TIME_VARIATION_ORIGIN"])
    # Excluding actual arrival / departure times because cancelled flights won"t have them
    flights = flights.dropna(subset=["CRSDepTime", "CRSArrTime"])

    return flights


def get_tz(flights):
    """
    Extracts time zone hourly difference as an into from the initial string columns.
    Note that the initial time zone string is in HH:MM format, for example:

    SAV is -500, indicating 5 hours behind UTC.

    Also note all time zones are rounded to the hour (there are no 30 minute differences to deal with).
    """
    # Extract time zone hourly differences
    flights["TZ_ORIGIN"] = flights["UTC_LOCAL_TIME_VARIATION_ORIGIN"].str.slice(0, 3).astype(np.int8)
    flights["TZ_DEST"] = flights["UTC_LOCAL_TIME_VARIATION_DEST"].str.slice(0, 3).astype(np.int8)

    # Drop now-unneeded columns
    flights = flights.drop(columns=["UTC_LOCAL_TIME_VARIATION_DEST", "UTC_LOCAL_TIME_VARIATION_ORIGIN"])

    return flights


def convert_to_dt(flights):
    """Converts the date/time data from disparate cols to datetime format for better usability."""

    # Update to more user-friendly names while we"re here
    new_names = ["DepActual", "DepScheduled", "ArrScheduled", "ArrActual"]

    # Convert all times and dates to pandas format for ease of use
    # Convert for pandas date time functionality
    flights = flights.rename(columns={"DayofMonth": "Day"})

    for field, new_name in zip(time_fields, new_names):
        flights["Hour"] = flights[field].str.slice(0, 2)
        flights["Minute"] = flights[field].str.slice(2, stop=None)
        flights[new_name] = pd.to_datetime(flights.loc[:, ("Hour", "Minute", "Year", "Month", "Day")])

    return flights


def add_dst_cols(flights):
    # Add DST bool column (these calculations are done according to local time, i.e. DST starts/ends at 2am local)
    # https://en.wikipedia.org/wiki/Daylight_saving_time_in_the_United_States
    dst_start_stop = {
        2016: {
            "DST_start": datetime(2016, 3, 13, 2),
            "DST_end": datetime(2016, 11, 6, 2)
        },
        2017: {
            "DST_start": datetime(2017, 3, 12, 2),
            "DST_end": datetime(2017, 11, 5, 2)
        },
        2018: {
            "DST_start": datetime(2018, 3, 11, 2),
            "DST_end": datetime(2018, 11, 4, 2)
        }
    }

    # Add DST info to DF
    dst_start_stop = pd.DataFrame.from_dict(dst_start_stop, orient="index")
    flights = flights.merge(dst_start_stop, how="left", left_on="Year", right_index=True)

    no_dst_states = {"AZ", "HI"}

    def check_dst(df, field):
        """Checks if DST was observed for the given time field."""
        past_start = df["DST_start"] <= df[field]
        before_end = df[field] <= df["DST_end"]
        in_dates = past_start & before_end
        observes = ~df["AIRPORT_STATE_CODE_ORIGIN"].isin(no_dst_states)
        return in_dates & observes

    flights["DST_ORIGIN"] = check_dst(flights, "DepActual")
    flights["DST_DEST"] = check_dst(flights, "ArrActual")

    # Add bool to time zone to increment if needed (since true means observing DST and = 1)
    flights["TZ_ORIGIN"] += flights["DST_ORIGIN"]
    flights["TZ_DEST"] += flights["DST_DEST"]

    # Drop now-unneeded columns
    flights = flights.drop(columns=["Hour", "Minute", "Year", "Month", "Day", "AIRPORT_STATE_CODE_ORIGIN",
                                    "AIRPORT_STATE_CODE_DEST", "DST_start", "DST_end", "AIRPORT_ID_ORIGIN",
                                    "AIRPORT_ID_DEST"] + time_fields)

    return flights


def convert_to_utc(flights):
    """Does the final conversion to UTC."""
    # Convert to UTC
    time_cols = ["DepActual", "DepScheduled", "ArrScheduled", "ArrActual"]
    # To ensure we index the proper TZ associated with each above (origin vs. destination)
    time_zones = ["TZ_ORIGIN", "TZ_ORIGIN", "TZ_DEST", "TZ_DEST"]

    # Make time deltas just once to save time in loop
    time_deltas = {
        "TZ_ORIGIN": pd.to_timedelta(flights["TZ_ORIGIN"], unit="h"),
        "TZ_DEST": pd.to_timedelta(flights["TZ_DEST"], unit="h")
    }

    for col, time_zone in zip(time_cols, time_zones):
        flights[col] = flights[col] + time_deltas[time_zone]

    # Drop now-unneeded columns
    flights = flights.drop(columns=["DST_ORIGIN", "DST_DEST", "TZ_ORIGIN", "TZ_DEST"])
    return flights


def calc_delays(flights):
    """
    Calculates OD-pair delays and airport delays per:
    http://www.mit.edu/~hamsa/pubs/GopalakrishnanBalakrishnanATM2017.pdf
    """

    # Convert index to date time because we need it for grouping operations below
    flights_departed = flights.dropna(subset=["DepActual"])
    flights_departed.index = pd.DatetimeIndex(flights_departed["DepActual"])

    pair_delays = (flights_departed
                   .groupby(["OriginAirportID", "DestAirportID"])
                   # First group by Origin-Dest then group by hour
                   .resample("H")["DepDelayMinutes"]
                   # Get the median delay for each origin-destination pair for every hour
                   .median()
                   # NA are just when this pair doesn"t have a flight at that time.
                   .dropna())

    # Turn to df so we can merge
    pair_delays = pd.DataFrame(pair_delays)
    # Rename because this is the median delay for the origin-destination pair
    pair_delays = pair_delays.rename({"DepDelayMinutes": "OD-PairDelay"}, axis="columns")
    # Get floor of every hour to rejoin
    flights["HourFloor"] = flights["DepScheduled"].dt.floor("H")
    # Increment by one hour because we want to predict with historical data (what was the state one hour ago?)
    # Since we join on this column, it means data from one hour behind will be joined to the scheduled departure time
    flights["HourFloor"] = flights["HourFloor"] + pd.Timedelta(1, unit="h")

    # Merge data back
    flights = flights.merge(
        pair_delays,
        how="left",
        left_on=["OriginAirportID", "DestAirportID", "HourFloor"],
        right_index=True
    )

    ap_outbound_delays = (flights_departed.groupby(["OriginAirportID"])
                          # First group by Origin then group by hour
                          .resample("H")["DepDelayMinutes"]
                          # Get the median delay for all outgoing flights for each hour
                          .median()
                          # NA are just when this pair doesn"t have a flight at that time.
                          .dropna())

    # Turn to df so we can merge
    ap_outbound_delays = pd.DataFrame(ap_outbound_delays)
    ap_outbound_delays = ap_outbound_delays.rename({"DepDelayMinutes": "AirportOutDelay"},
                                                   axis="columns")

    # Merge data back
    flights = flights.merge(
        ap_outbound_delays,
        how="left",
        left_on=["OriginAirportID", "HourFloor"],
        right_index=True
    )

    return flights


def calc_cancellations(flights):
    """
    Calculates ratio of flights cancelled for city pairs and total for each airport:
    """

    # Convert index to date time because we need it for grouping operations below
    flights.index = pd.DatetimeIndex(flights["DepScheduled"])

    pair_cancellations = (
        flights
        .groupby(["OriginAirportID", "DestAirportID"])
        # First group by Origin-Dest then group by hour
        .resample("H")["Cancelled"]
        # Get the median delay for each origin-destination pair for every hour
        .median()
        # NA are just when this pair doesn"t have a flight at that time.
        .dropna()
    )

    # Turn to df so we can merge
    pair_cancellations = pd.DataFrame(pair_cancellations)
    # Rename because this is the median delay for the origin-destination pair
    pair_cancellations = pair_cancellations.rename({"Cancelled": "OD-CancelRatio"}, axis="columns")
    # Get floor of every hour to rejoin
    flights["HourFloor"] = flights["DepScheduled"].dt.floor("H")
    # Increment by one hour because we want to predict with historical data (what was the state one hour ago?)
    # Since we join on this column, it means data from one hour behind will be joined to the scheduled departure time
    flights["HourFloor"] = flights["HourFloor"] + pd.Timedelta(1, unit="h")

    # Merge data back
    flights = flights.merge(
        pair_cancellations,
        how="left",
        left_on=["OriginAirportID", "DestAirportID", "HourFloor"],
        right_index=True
    )

    ap_outbound_delays = (
        flights.groupby(["OriginAirportID"])
        # First group by Origin then group by hour
        .resample("H")["Cancelled"]
        # Get the median delay for all outgoing flights for each hour
        .median()
        # NA are just when this pair doesn"t have a flight at that time.
        .dropna()
    )

    # Turn to df so we can merge
    ap_outbound_delays = pd.DataFrame(ap_outbound_delays)
    ap_outbound_delays = ap_outbound_delays.rename({"Cancelled": "AirportCancelRatio"},
                                                   axis="columns")

    # Merge data back
    flights = flights.merge(
        ap_outbound_delays,
        how="left",
        left_on=["OriginAirportID", "HourFloor"],
        right_index=True
    )

    return flights


def feature_engineering(chunk):
    # TODO Put the final feature engineering implementation here, as determined by Tich's Notebook experimentation
    # Find delayed flights
    delay_threshold = 60
    chunk["Delayed"] = (
            (chunk["DepDelayMinutes"] >= delay_threshold) &
            # Only include flights that weren't eventually cancelled
            ~(chunk["Cancelled"])
    )

    # Add flag for missing delay info; this could be informative because it might indicate no flights are taking
    # off due to severe weather, etc.
    chunk["MissingOD-PairDelay"] = np.isnan(chunk["OD-PairDelay"])

    # Impute missing values because many cancelled flights are missing data from the preceding hour
    # However, we still want to include them so we can somewhat accurately predict cancelled flights too
    # Ideally, we would add a better imputation method
    chunk["DepDelayMinutes"] = chunk["DepDelayMinutes"].fillna(chunk["DepDelayMinutes"].mean())
    chunk["OD-PairDelay"] = chunk["OD-PairDelay"].fillna(chunk["OD-PairDelay"].mean())
    chunk["AirportOutDelay"] = chunk["AirportOutDelay"].fillna(chunk["AirportOutDelay"].mean())
    chunk["DepDelayMinutes"] = chunk["DepDelayMinutes"].fillna(chunk["DepDelayMinutes"].mean())
    chunk["OD-CancelRatio"] = chunk["OD-CancelRatio"].fillna(chunk["OD-CancelRatio"].mean())
    chunk["AirportCancelRatio"] = chunk["AirportCancelRatio"].fillna(chunk["AirportCancelRatio"].mean())

    # Get month because there seem to be seasonality trends affecting CV but not test result
    chunk["Month"] = chunk["DepScheduled"].dt.month

    # Only on time if neither delayed nor cancelled
    chunk["OnTime"] = ~chunk["Delayed"] & ~chunk["Cancelled"]

    # Keep only routes with appreciable amounts of data
    chunk.index = pd.DatetimeIndex(chunk["DepScheduled"])
    pairs_by_day = chunk.groupby(["OriginAirportID", "DestAirportID"]).resample("D")
    avg_per_day = pairs_by_day.size().groupby(["OriginAirportID", "DestAirportID"]).mean()
    popular_routes = (
        (avg_per_day >= 5)
        .rename("PopularRoute")
        .reset_index()
    )
    chunk = chunk.merge(popular_routes, on=["OriginAirportID", "DestAirportID"])
    chunk = chunk.loc[chunk["PopularRoute"] == 1, :]
    # Popular Route indicator no longer needed
    chunk = chunk.drop(["PopularRoute"], axis=1)

    return chunk


def process_chunk(chunk, airport_info):
    """Processes a subset of data."""
    print("Prepping data.")
    chunk = prep_data(chunk, airport_info)
    print("Getting time zones.")
    chunk = get_tz(chunk)
    print("Converting to datetimes.")
    chunk = convert_to_dt(chunk)
    print("Adding DST columns.")
    chunk = add_dst_cols(chunk)
    print("Doing final conversion to UTC.")
    chunk = convert_to_utc(chunk)
    print("Calculating delays.")
    chunk = calc_delays(chunk)
    print("Calculating cancellations.")
    chunk = calc_cancellations(chunk)
    print("Feature engineering.")
    chunk = feature_engineering(chunk)
    return chunk


def main():

    out_filename = "all_flights_wrangled.csv"

    # For printing incremental output
    pd.set_option("display.max_columns", 30)

    dtypes = {
        "Cancelled": bool,
        "Diverted": bool,
        "CancellationCode": "O",  # Read as string otherwise mixed data type warning
        "DepTime": "O",  # Times as strings to not lose digits
        "CRSDepTime": "O",
        "CRSArrTime": "O",
        "ArrTime": "O"
    }

    # The flights make for a large CSV so we"ll do this by chunks, while keeping the airport data in memory because
    # it"s smaller.
    print("Loading data.")
    print()

    all_flights = pd.read_csv(os.path.join(data_path, "all_flights.csv"), dtype=dtypes, chunksize=500000)
    # Load airport TZ info
    airp_info = pd.read_csv(os.path.join(data_path, "airport_info_no_dupes.csv"), dtype={"UTC_LOCAL_TIME_VARIATION": "O"},
                            usecols=["AIRPORT_ID", "UTC_LOCAL_TIME_VARIATION", "AIRPORT_STATE_CODE",
                                     "AIRPORT_IS_LATEST"])
    # Get rid of older airport data otherwise we"ll have multiple matches on the join and DF will be giant
    airp_info = airp_info.loc[airp_info["AIRPORT_IS_LATEST"] == 1, :]
    # Now get rid of unneeded column
    airp_info = airp_info.drop(columns=["AIRPORT_IS_LATEST"])

    # Process first subset separately to get headers
    print("Chunk 1:")
    subset = next(all_flights)
    subset = process_chunk(subset, airp_info)
    print("Saving to CSV.")
    print("First Five Rows:")
    print()
    print(subset.head())
    print()

    # Overwrite any file existing (hence the w); include headers because first
    out_path = os.path.join(data_path, out_filename)
    subset.to_csv(out_path, mode="w", header=True, index=False)

    for i, subset in enumerate(all_flights):
        print("Chunk {}:".format(i + 2))  # Adding 2 because we already did 1 and 0-indexed
        subset = process_chunk(subset, airp_info)
        print("Saving to CSV.")
        print("First Five Rows:")
        print()
        print(subset.head())
        print()

        # Append and exclude header since we already have one
        subset.to_csv(out_path, mode="a", header=False, index=False)

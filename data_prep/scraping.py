import requests
import zipfile
import os
import csv
from shutil import rmtree
import time

output_path = os.path.join("..", "data", "all_flights.csv")


def scrape_month(year, month, cols):
    """
    Year: 4 digit int or string
    Month: 1 or 2 digit int; January is 1
    """
    print("Scraping {}-{}".format(year, month))

    # Create temporary folder for zipping and unzipping files
    os.makedirs("temp_data", exist_ok=True)
    zip_path = os.path.join("temp_data", "{}-{}.zip".format(year, month))

    # Get file
    def download_file():
        file_name = "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{}_{}.zip"
        url_string = "http://transtats.bts.gov/PREZIP/" + file_name
        url = url_string.format(year, month)
        r = requests.get(url)
        # Write zip to disk
        open(zip_path, "wb").write(r.content)

    def extract_file():
        zip_ref = zipfile.ZipFile(zip_path, "r")
        zip_ref.extractall("temp_data")
        zip_ref.close()

    attempts = 0
    complete = False
    max_attempts = 5
    while attempts < max_attempts and not complete:
        try:
            download_file()
            extract_file()
            complete = True
        except zipfile.BadZipFile:
            # File was corrupted, try again
            attempts += 1
            print("Zip file is corrupted or data does not exist at url, attempt #{}".format(attempts))
            # Just in case we"re being cut off...
            time.sleep(15)
            if attempts >= max_attempts:
                print("Maximum attempts reached. Moving to next month.")
                return

    month_file_name = "On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_{}_{}.csv"
    month_path = os.path.join("temp_data", month_file_name.format(year, month))
    with open(month_path) as month_csv:
        with open(output_path, "a") as all_csv:
            # Using dictreader so we don"t end up with multiple headers in the middle of the file
            reader = csv.DictReader(month_csv)
            writer = csv.DictWriter(all_csv, fieldnames=cols, extrasaction="ignore")
            for row in reader:
                writer.writerow(row)

    # Delete the temporary directory
    rmtree("temp_data")


def main():
    # Delete all_flights csv so we aren"t appending repeats
    try:
        os.remove(output_path)
    except FileNotFoundError:
        pass

    # Removing NAS Delay and WX Delay because you can"t tell which is weather related (NAS includes weather)
    # Per http://aspmhelp.faa.gov/index.php/Types_of_Delay
    cols = [
        "Year",
        "Month",
        "DayofMonth",
        "DayOfWeek",
        "DOT_ID_Reporting_Airline",
        "OriginAirportID",
        "DestAirportID",
        "CRSDepTime",
        "DepTime",
        "DepDelayMinutes",
        "CRSArrTime",
        "ArrTime",
        "Cancelled",
        "Diverted"
    ]

    # Write the header initially but not on repeat loops (will cause duplicate headers part way through)
    with open(output_path, "a") as all_csv:
        writer = csv.DictWriter(all_csv, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()

    # Limit data initially because the file gets too big for laptop memory
    for year in range(2013, 2019):
        for i in range(1, 13):
            scrape_month(year, i, cols)
'''

Energy Efficiency Targeting Tool Copyright (c) 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Intellectual Property Office at  IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department of Energy and the U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit other to do so. 

'''

from constants import Constants
import pandas as pd
import numpy as np
import os
from ish_parser import ish_report, ish_reportException
from ftplib import FTP
import gzip


class Weather:

    def __init__(self, coord):
        self.coord = coord
        self.latitude, self.longitude = coord  # geo-coded address
        self.find_closest_weather_station()

    def process(self, df_periods):
        df_periods['start_dates'] = pd.to_datetime(df_periods['start_dates'], utc=True)
        df_periods['end_dates'] = pd.to_datetime(df_periods['end_dates'], utc=True)
        self.df_periods = df_periods
        self.v_start_dates = self.df_periods.loc[:, 'start_dates']
        self.v_end_dates = self.df_periods.loc[:, 'end_dates']
        self.start_year = pd.DatetimeIndex(np.sort(self.v_start_dates)).year[0]
        self.end_year = pd.DatetimeIndex(np.sort(self.v_end_dates)).year[-1]

    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        # Get radians from decimals
        r_lat1, r_lon1, r_lat2, r_lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

        # Calculate the distance between the two locations
        temp = np.sin((r_lat2 - r_lat1) / 2) ** 2 + np.cos(r_lat1) * np.cos(r_lat2) * np.sin((r_lon2 - r_lon1) / 2) ** 2
        distance = 2 * Constants.earth_radius * np.arcsin(np.sqrt(temp))
        return (distance)

    def find_closest_weather_station(self, df_weather_station_list=Constants.df_cn_weather_station):
        self.v_coord = np.asarray(df_weather_station_list[['latitude', 'longitude']].values)
        # Find the closest and second closest weather station (backup if the closest doesn't work)
        v_distance = [Weather.haversine_distance(self.latitude, self.longitude, coord[0], coord[1])
                      for coord in self.v_coord]
        closest_index = np.argmin(v_distance)
        second_closest_index = np.argpartition(v_distance, 2)[2]
        third_closest_index = np.argpartition(v_distance, 3)[2]

        self.closest_weather_station_ID = df_weather_station_list.loc[closest_index, 'station_ID']
        self.closest_weather_station_name = df_weather_station_list.loc[closest_index, 'station_name']
        self.second_closest_weather_station_ID = df_weather_station_list.loc[second_closest_index, 'station_ID']
        self.second_closest_weather_station_name = df_weather_station_list.loc[second_closest_index, 'station_name']
        self.third_closest_weather_station_ID = df_weather_station_list.loc[third_closest_index, 'station_ID']
        self.third_closest_weather_station_name = df_weather_station_list.loc[third_closest_index, 'station_name']

    def download_weather_NOAA(self):
        print("Downloading weather data...")
        try:
            self.v_T_F, self.v_T_C = self.process_downloaded_weather(self.closest_weather_station_ID)
        except:
            try:
                print("Weather from the closest weather station not available...")
                print("Trying to download the third second data from the third closest weather station.")
                self.v_T_F, self.v_T_C = self.process_downloaded_weather(self.second_closest_weather_station_ID)
            except:
                print("Weather from the second closest weather station not available...")
                print("Trying to download the third weather data from the third closest weather station.")
                self.v_T_F, self.v_T_C = self.process_downloaded_weather(self.third_closest_weather_station_ID)

    def use_downloaded_weather(self):
        s_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        try:
            self.v_T_F, self.v_T_C = self.process_cached_weather(self.closest_weather_station_ID, s_path)
        except:
            try:
                print("Weather from the closest weather station not available...")
                print("Trying to process the third second data from the third closest weather station.")
                self.v_T_F, self.v_T_C = self.process_cached_weather(self.second_closest_weather_station_ID, s_path)
            except:
                print("Weather from the second closest weather station not available...")
                print("Trying to process the third weather data from the third closest weather station.")
                self.v_T_F, self.v_T_C = self.process_cached_weather(self.third_closest_weather_station_ID, s_path)
    
    def process_cached_weather(self, weather_station_ID, s_path):
        for year in range(self.start_year, self.end_year + 1):
            print("Process weather data for year: " + str(year))
            # Read pre-processed weather files from weather file folders
            file_name = (s_path + "/Data/Weather/" + str(year) + "/" +
                         str(year) + "_" + weather_station_ID + '.csv')
    
            if (year == self.start_year):
                df_new = pd.read_csv(file_name)
            else:
                df_new = df_new.append(pd.read_csv(file_name), ignore_index=True)
        df_new['Datetime'] = df_new['Datetime'].astype('datetime64[ns]')
        df_new['Date'] = df_new['Datetime'].dt.date
        v_T_F, v_T_C = self.aggregate_weather(df_new)
        return(v_T_F, v_T_C)

    def process_downloaded_weather(self, weather_station_ID):

        # Helper functions
        def download_sub_hourly_weather(station_ID, year):
            ftp = FTP('ftp.ncdc.noaa.gov')
            ftp.login()
            ftp_path = '/pub/data/noaa/' + str(year)  # Hourly
            ftp.cwd(ftp_path)
            # Save gz files locally
            file_name_noaa = 'RETR ' + station_ID + '-' + str(year) + '.gz'
            file_name_local = station_ID + '-' + str(year) + '.gz'
            ftp.retrbinary(file_name_noaa, open(file_name_local, 'wb').write)

        def save_as_csv(stationID, year):
            file_name_gz = stationID + '-' + str(year) + '.gz'
            file_name_csv = stationID + '-' + str(year) + '.csv'
            with gzip.open(file_name_gz, 'rb') as infile:
                with open(file_name_csv, 'wb') as outfile:
                    for line in infile:
                        outfile.write(line)
            os.remove(file_name_gz)

        def get_ish_report_helper(raw_rpt):
            return (ish_report().loads(raw_rpt))

        def get_ish_report_datetime_helper(raw_rpt):
            return (raw_rpt.datetime)

        def get_ish_report_temperature_helper(raw_rpt):
            return (raw_rpt.air_temperature.get_fahrenheit())
        
        for year in range(self.start_year, self.end_year + 1):
            print("--->" + str(year))
            download_sub_hourly_weather(weather_station_ID, year)
            save_as_csv(weather_station_ID, year)
            raw_csv = weather_station_ID + '-' + str(year) + '.csv'
            if (year == self.start_year):
                df_raw = pd.read_csv(raw_csv, names=['Old'])
            else:
                df_raw = df_raw.append(pd.read_csv(raw_csv, names=['Old']),
                                       ignore_index=True)
            # Cleaning up
            os.remove(raw_csv)
        # Parse ish text data to readable weather data
        print("Processing downloaded data...")
        v_rpt = list(map(get_ish_report_helper, df_raw['Old']))
        v_noaa_datetime = np.array(list(map(get_ish_report_datetime_helper, v_rpt)))
        v_noaa_temperature_F = np.array(list(map(get_ish_report_temperature_helper, v_rpt)))
        # Sanitize the array
        v_noaa_temperature_F = pd.to_numeric(v_noaa_temperature_F, errors='coerce')
        df_new = pd.DataFrame({'Datetime': v_noaa_datetime, 'Temperature': v_noaa_temperature_F})
        df_new['Date'] = df_new['Datetime'].dt.date
        v_T_F, v_T_C = self.aggregate_weather(df_new)
        return(v_T_F, v_T_C)

    def aggregate_weather(self, df_daily):
        # Get daily weather data

        # Remove time zone information
        self.v_start_dates = np.array(self.v_start_dates, dtype=np.datetime64)
        self.v_end_dates = np.array(self.v_end_dates, dtype=np.datetime64)
        df_daily['Datetime'] = np.array(df_daily['Datetime'], dtype=np.datetime64)

        df_daily = df_daily.loc[(df_daily['Datetime'] >=min(self.v_start_dates)) &
                                (df_daily['Datetime'] <= max(self.v_end_dates))]

        # Aggregate the weather data to the billing periods level.
        v_avg_period_T_F = np.empty(0, dtype=float)
        v_start_dates = np.array(self.v_start_dates)
        v_end_dates = np.array(self.v_end_dates)
        v_temp_datetime = np.array(df_daily['Datetime'], dtype=np.datetime64)
        for i in range(len(self.v_start_dates)):
            df_temp = df_daily.loc[(v_temp_datetime >= v_start_dates[i]) &
                                   (v_temp_datetime <= v_end_dates[i])]
            v_avg_period_T_F = np.append(v_avg_period_T_F, df_temp['Temperature'].mean())
        v_avg_period_T_C = (v_avg_period_T_F - 32) / 1.8

        return (v_avg_period_T_F, v_avg_period_T_C)
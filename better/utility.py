'''

Energy Efficiency Targeting Tool Copyright (c) 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Intellectual Property Office at  IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department of Energy and the U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit other to do so. 

'''

from better import constants

import numpy as np


class Utility:
    def __init__(self, utility_type, df_raw_data):
        self.utility_type = utility_type
        if (df_raw_data is not None):
            self.df_raw_data = df_raw_data.copy()

    def process(self):
        # Convert energy consumption unit to kWh
        if (self.df_raw_data.columns[2] == 'MWh 兆瓦时' and
                self.utility_type == 'electricity'):
            self.df_raw_data.ix[:, 2] *= constants.Constants.MWH_to_kWh
        elif (self.df_raw_data.columns[2] == 'Cubic Meters 立方米' and
              self.utility_type == 'natural gas'):
            self.df_raw_data.ix[:, 2] *= constants.Constants.M3_to_kWh
        elif (self.df_raw_data.columns[2] == 'GJ 吉焦'):
            self.df_raw_data.ix[:, 2] *= constants.Constants.GJ_to_kWh
        elif (self.df_raw_data.columns[2] == 'MJ 兆焦'):
            self.df_raw_data.ix[:, 2] *= constants.Constants.MJ_to_kWh
        elif (self.df_raw_data.columns[2] == 'Btu 英热'):
            self.df_raw_data.ix[:, 2] *= constants.Constants.Btu_to_kWh
        elif (self.df_raw_data.columns[2] == 'MMBtu 百万英热'):
            self.df_raw_data.ix[:, 2] *= constants.Constants.MMBtu_to_kWh
        elif (self.df_raw_data.columns[2] == 'Therms 撒姆'):
            self.df_raw_data.ix[:, 2] *= constants.Constants.Therms_to_kWh
        elif (self.df_raw_data.columns[2] == 'Decatherms 十撒姆'):
            self.df_raw_data.ix[:, 2] *= constants.Constants.Decatherms_to_kWh
        # Get date-related vectors
        self.df_raw_data.columns = ['start_dates', 'end_dates', 'kWh', 'Cost']

        # Sort data by billing end dates
        self.df_raw_data = self.df_raw_data.sort_values(by=['end_dates'])
        self.df_raw_data_last_year = self.df_raw_data.tail(12)

        self.df_raw_data['Days'] = (self.df_raw_data['end_dates'] - self.df_raw_data['start_dates']).dt.days
        # Make sure days are greater than 0!
        self.daily_kWh = self.df_raw_data['kWh'] / self.df_raw_data['Days']
        self.df_periods = self.df_raw_data.loc[:, ['start_dates', 'end_dates']]
        self.days = np.array(self.df_raw_data['Days'], dtype=float)
        self.daily_kWh_all_periods = self.df_raw_data['kWh'].sum() / self.df_raw_data['Days'].sum()

        # Get the unit price of the utility [cost/kWh]
        if (np.sum(self.df_raw_data['Cost']) > 0):
            self.utility_unit_price = np.sum(self.df_raw_data['Cost']) / np.sum(self.df_raw_data['kWh'])

        # Get the most recent year's data
        self.df_recent_annual_sorted_data = self.df_raw_data.sort_values(by=['start_dates']).tail(12)
        self.recent_annual_consumption = int(self.df_recent_annual_sorted_data['kWh'].sum())
        self.recent_annual_cost = int(self.df_recent_annual_sorted_data['Cost'].sum())
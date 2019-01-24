'''

Energy Efficiency Targeting Tool Copyright (c) 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Intellectual Property Office at  IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department of Energy and the U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit other to do so. 

'''

import os
import pandas as pd
import numpy as np
from collections import OrderedDict

import constants
import building
import utility
import weather
import benchmark


class Portfolio:

    def __init__(self, name):
        self.name = name

    def read_raw_data_from_csv(self, filename):
        # clean up the raw data and save it as a dataframe
        return 42

    def read_raw_data_from_xlsx(self, filename):
        # clean up the raw data and save it as a dataframe
        self.df_meta = pd.read_excel(filename, sheet_name="Metadata", skiprows=[0, 1], usecols="A:I")
        self.df_detail = pd.read_excel(filename, sheet_name="Utility", skiprows=[0, 1], usecols="A:G",
                                       parse_dates=[1, 2], infer_datetime_format=True)
        # Change column names in the dataframe
        self.df_meta.columns = ["building_ID", "building_name", "building_address", "building_area",
                                "building_space_type_1st", "building_space_type_2nd", "building_cooling_fuel_type",
                                "building_heating_fuel_type", "currency"]
        self.df_detail.columns = ["building_ID", "bill_start_dates", "bill_end_dates", "energy_type",
                                  "energy_unit", "energy_consumption", "energy_cost"]

        # Drop rows where necessary values are missing
        self.df_meta = self.df_meta[np.isfinite(self.df_meta['building_ID'])]
        self.df_detail = self.df_detail[np.isfinite(self.df_detail['building_ID'])]

    def get_utility_by_building_id_and_energy_type(self, building_ID, energy_type):
        # energy_type: 1 ~ electricity; 2 ~ fossil fuel
        df_temp = self.df_detail.loc[self.df_detail['building_ID'] == building_ID]
        df_temp = df_temp[['bill_start_dates', 'bill_end_dates', 'energy_type',
                           'energy_unit', 'energy_consumption', 'energy_cost']]
        if (energy_type == 1):
            df_temp = df_temp.loc[df_temp['energy_type'] == 'Electricity - Grid Purchased']
            if df_temp.empty: return None
        else:
            df_temp = df_temp.loc[df_temp['energy_type'] != 'Electricity - Grid Purchased']
            if df_temp.empty: return None

            '''
            Need to address how to combine multiple fossil fuel with different billing periods
            Current solution: proportionally allocate the by the number of days in each calendar month
            '''
        # Convert the energy unit to kwh
        df_temp.loc[df_temp['energy_unit'] == 'MJ', 'energy_consumption'] *= constants.Constants.MJ_to_kWh
        df_temp.loc[df_temp['energy_unit'] == 'GJ', 'energy_consumption'] *= constants.Constants.GJ_to_kWh
        df_temp.loc[df_temp['energy_unit'] == 'MWh', 'energy_consumption'] *= constants.Constants.MWH_to_kWh
        df_temp.loc[df_temp['energy_unit'] == 'Btu', 'energy_consumption'] *= constants.Constants.Btu_to_kWh
        df_temp.loc[df_temp['energy_unit'] == 'MMBtu', 'energy_consumption'] *= constants.Constants.MMBtu_to_kWh
        df_temp.loc[df_temp['energy_unit'] == 'Cubic Meters', 'energy_consumption'] *= constants.Constants.M3_to_kWh
        df_temp.loc[df_temp['energy_unit'] == 'Therms', 'energy_consumption'] *= constants.Constants.Therms_to_kWh
        df_temp.loc[df_temp['energy_unit'] == 'Decatherms', 'energy_consumption'] *= constants.Constants.Decatherms_to_kWh

        # Format the dataframe to match he raw utility data frame
        df_temp = df_temp[['bill_start_dates', 'bill_end_dates', 'energy_consumption', 'energy_cost']]
        df_temp.columns = ["Monthly Billing Start Date", "Monthly Billing End Date",
                           "kWh", "Cost"]

        return (df_temp)

    def get_building_info_by_id(self, building_ID):
        try:
            df_temp = self.df_meta.loc[self.df_meta['building_ID'] == building_ID]
            building_info = df_temp.iloc[0]['building_name'], \
                            df_temp.iloc[0]['building_address'], \
                            df_temp.iloc[0]['building_space_type_1st'], \
                            df_temp.iloc[0]['building_area'], \
                            df_temp.iloc[0]['currency']
        except:
            building_info = None
            print('Cannot find the building with ID: ' + str(building_ID))
        return building_info

    def fit_model_for_buildings(self):
        # Fit change-point model for all buildings by default
        return 42

    def summarize_portfolio(self):
        # Summarize the portfolio
        return 42

    def get_building_by_id(self, building_id):
        # Get a specific building object by its id
        return 42

    def get_portfolio_raw_data_by_spaceType_and_utilityType(self, space_type, utility_type):
        # Save the raw utility data in dictionaries
        dict_raw_utility = {}
        dict_raw_fossil_fuel = {}
        df_temp_meta = self.df_meta
        # Warning: duplicate building ID will be droped!
        df_temp_meta = df_temp_meta.drop_duplicates('building_ID')
        df_temp_meta = df_temp_meta[(df_temp_meta['building_space_type_1st'] == space_type) &
                                    (df_temp_meta['building_ID'].notnull()) &
                                    (df_temp_meta['building_address'].notnull()) &
                                    (df_temp_meta['building_area'].notnull())]

        # Add raw utility date into the dictionaries
        for i in df_temp_meta['building_ID']:
            if (utility_type == 1):
                df_temp_detail_utility = (self.get_utility_by_building_id_and_energy_type(i, 1))
                utility_temp = utility.Utility('electricity', df_temp_detail_utility)
            else:
                df_temp_detail_utility = (self.get_utility_by_building_id_and_energy_type(i, 2))
                utility_temp = utility.Utility('fossil fuel', df_temp_detail_utility)

            index = df_temp_meta[df_temp_meta['building_ID'] == i].index.tolist()[0]

            dict_temp_utility = {i: (df_temp_meta.iloc[index]['building_address'],
                                     df_temp_meta.iloc[index]['building_area'],
                                     space_type,
                                     df_temp_meta.iloc[index]['currency'],
                                     utility_type,
                                     utility_temp
                                     )}
            dict_raw_utility.update(dict_temp_utility)
        return (dict_raw_utility)

    @staticmethod
    def generate_building_models(dict_raw_utility, cached_weather):
        # This function may take several minutes, print the progress
        v_building_ID = list(dict_raw_utility.keys())
        v_EUI = np.empty(0)
        v_Model = np.empty(0)
        v_beta_base = np.empty(0)
        v_beta_betc = np.empty(0)
        v_beta_beth = np.empty(0)
        v_beta_cdd = np.empty(0)
        v_beta_hdd = np.empty(0)
        i = 0
        for bldg_id in v_building_ID:
            i += 1
            print('----------------------------------------------------')
            print("Fitting change-point model for all buildings.")
            print("Building ID: " + str(bldg_id))

            bldg_name = str(bldg_id) + '_dummy_name'
            bldg_address = dict_raw_utility[bldg_id][0]
            bldg_area = dict_raw_utility[bldg_id][1]
            bldg_type = dict_raw_utility[bldg_id][2]
            currency = dict_raw_utility[bldg_id][3]
            utility_type = 'electricity' if dict_raw_utility[bldg_id][4] == 1 else 'fossil fuel'
            utility_temp = dict_raw_utility[bldg_id][5]

            if (hasattr(utility_temp, "df_raw_data")):
                # Proceed only if there is utility data for the current building
                building_temp = building.Building(bldg_id, bldg_name, bldg_address, bldg_type, bldg_area, currency)
                weather_temp = weather.Weather(building_temp.coord)
                building_temp.add_utility(utility_temp)
                building_temp.add_weather(cached_weather, weather_temp)
                has_fit = building_temp.fit_inverse_model()
                if (has_fit):
                    v_EUI = np.append(v_EUI, np.nan)
                    v_Model = np.append(v_Model, str(bldg_id))
                    v_beta_base = np.append(v_beta_base, building_temp.im_electricity.coeffs['base'])
                    v_beta_betc = np.append(v_beta_betc, building_temp.im_electricity.coeffs['ccp'])
                    v_beta_beth = np.append(v_beta_beth, building_temp.im_electricity.coeffs['hcp'])
                    v_beta_cdd = np.append(v_beta_cdd, building_temp.im_electricity.coeffs['csl'])
                    v_beta_hdd = np.append(v_beta_hdd, building_temp.im_electricity.coeffs['hsl'])
                print(str(i) + '/' + str(len(v_building_ID)) + " completed.")
            else:
                print("No " + utility_type + " utility data found for current building, ",
                      str(i) + '/' + str(len(v_building_ID)) + " completed.")

        d_bench_coeffs = {'EUI': v_EUI,
                          'Model': v_Model,
                          'beta_base': v_beta_base,
                          'beta_betc': v_beta_betc,
                          'beta_beth': v_beta_beth,
                          'beta_cdd': v_beta_cdd,
                          'beta_hdd': v_beta_hdd}
        df_bench_coeffs = pd.DataFrame(d_bench_coeffs)
        return df_bench_coeffs

    @staticmethod
    def generate_benchmark_stats(df_building_models):
        df_bench_stats = pd.DataFrame(columns=['beta_median', 'beta_standard_deviation'])
        df_bench_stats.index.name = "coefficient"
        median_BASE, std_BASE = benchmark.Benchmark.generate_benchmark_stats('BASE', df_building_models['beta_base'])
        median_CSL, std_CSL = benchmark.Benchmark.generate_benchmark_stats('CSL', df_building_models['beta_cdd'])
        median_CCP, std_CCP = benchmark.Benchmark.generate_benchmark_stats('CCP', df_building_models['beta_betc'])
        median_HSL, std_HSL = benchmark.Benchmark.generate_benchmark_stats('HSL', df_building_models['beta_hdd'])
        median_HCP, std_HCP = benchmark.Benchmark.generate_benchmark_stats('HCP', df_building_models['beta_beth'])
        df_bench_stats.at['beta_base', 'beta_median'], df_bench_stats.at['beta_base', 'beta_standard_deviation'] = median_BASE, std_BASE
        df_bench_stats.at['beta_cdd', 'beta_median'], df_bench_stats.at['beta_cdd', 'beta_standard_deviation'] = median_CSL, std_CSL
        df_bench_stats.at['beta_betc', 'beta_median'], df_bench_stats.at['beta_betc', 'beta_standard_deviation'] = median_CCP, std_CCP
        df_bench_stats.at['beta_hdd', 'beta_median'], df_bench_stats.at['beta_hdd', 'beta_standard_deviation'] = median_HSL, std_HSL
        df_bench_stats.at['beta_beth', 'beta_median'], df_bench_stats.at['beta_beth', 'beta_standard_deviation'] = median_HCP, std_HCP
        return df_bench_stats

    @staticmethod
    def generate_benchmark_stats_wrapper(dict_raw_utility, cached_weather):
        df_building_models = Portfolio.generate_building_models(dict_raw_utility, cached_weather)
        df_bench_stats = Portfolio.generate_benchmark_stats(df_building_models)
        return df_bench_stats


    def prepare_portfolio_report_data(self, v_single_buildings, report_path, save_portfolio_results):
        # This function prepares the data for portfolio report
        print(v_single_buildings)
        # Count of effective building in the porfolio
        count = 0
        total_area = 0
        total_annual_consumption_e = 0
        total_annual_consumption_f = 0
        total_annual_cost_e = 0
        total_annual_cost_f = 0
        total_annual_cost_savings= 0
        # Lists of building details data
        v_single_ids = []
        v_single_names = []
        v_single_address = []
        v_single_area = []
        v_single_annual_consumption_e = []
        v_single_annual_consumption_f = []
        v_single_annual_cost_e = []
        v_single_annual_cost_f = []
        v_single_eui_e = []
        v_single_eui_f = []
        v_single_cost_savings = []
        v_single_cost_savings_pct = []
        v_rpt_path = []

        for single_building in v_single_buildings:
            if single_building != None:
                count += 1
                total_area += single_building.bldg_area
                v_single_ids.append(single_building.bldg_id)
                v_single_names.append(single_building.bldg_name)
                v_single_address.append(single_building.bldg_address)
                v_single_area.append(int(single_building.bldg_area))
                rpt_path = (str(single_building.bldg_id) + '_' + single_building.bldg_address + '_' + single_building.bldg_name + '_report.html').replace(' ', '_')
                v_rpt_path.append(rpt_path)

                if hasattr(single_building, "recent_annual_electricity_kWh"):
                    total_annual_consumption_e += single_building.recent_annual_electricity_kWh
                    v_single_annual_consumption_e.append(single_building.recent_annual_electricity_kWh)
                else:
                    v_single_annual_consumption_e.append("NA")

                if hasattr(single_building, "recent_annual_fossil_fuel_kWh"):
                    total_annual_consumption_f += single_building.recent_annual_fossil_fuel_kWh
                    v_single_annual_consumption_f.append(single_building.recent_annual_fossil_fuel_kWh)
                else:
                    v_single_annual_consumption_f.append("NA")

                if hasattr(single_building, "recent_annual_electricity_cost"):
                    total_annual_cost_e += single_building.recent_annual_electricity_cost
                    v_single_annual_cost_e.append(single_building.recent_annual_electricity_cost)
                else:
                    v_single_annual_cost_e.append("NA")

                if hasattr(single_building, "recent_annual_fossil_fuel_cost"):
                    total_annual_cost_f += single_building.recent_annual_fossil_fuel_cost
                    v_single_annual_cost_f.append(single_building.recent_annual_fossil_fuel_cost)
                else:
                    v_single_annual_cost_f.append("NA")

                if hasattr(single_building, "recent_annual_electricity_EUI"):
                    v_single_eui_e.append(int(single_building.recent_annual_electricity_EUI))
                else:
                    v_single_eui_e.append('NA')

                if hasattr(single_building, "recent_annual_fossil_fuel_EUI"):
                    v_single_eui_f.append(int(single_building.recent_annual_fossil_fuel_EUI))
                else:
                    v_single_eui_f.append("NA")

                if hasattr(single_building, "total_cost_savings"):
                    total_annual_cost_savings += single_building.total_cost_savings
                    v_single_cost_savings.append(int(single_building.total_cost_savings))
                else:
                    v_single_cost_savings.append("NA")

                if hasattr(single_building, "total_energy_savings_pct"):
                    v_single_cost_savings_pct.append(int(single_building.total_energy_savings_pct))
                else:
                    v_single_cost_savings_pct.append("NA")



        self.n_buildings = count
        self.total_area = total_area
        self.total_annual_consumption_e = total_annual_consumption_e
        self.total_annual_consumption_f = total_annual_consumption_f
        self.total_annual_cost_e = total_annual_cost_e
        self.total_annual_cost_f = total_annual_cost_f
        self.total_annual_cost_savings = total_annual_cost_savings
        if total_area > 0: self.portfolio_eui_e = round(self.total_annual_consumption_e/total_area, 0)
        if total_area > 0: self.portfolio_eui_f = round(self.total_annual_consumption_f/total_area, 0)


        print(v_single_ids)
        print(v_single_names)
        print(v_single_address)
        print(v_single_area)
        print(v_single_annual_consumption_e)
        print(v_single_annual_consumption_f)
        print(v_single_annual_cost_e)
        print(v_single_annual_cost_f)
        print(v_single_eui_e)
        print(v_single_eui_f)


        d_bldg_summary = OrderedDict({
            "Building ID": v_single_ids,
            "Building Name": v_single_names,
            "Building Address": v_single_address,
            "Building Area": v_single_area,
            "Building Annual Electricity Consumption (kWh)": v_single_annual_consumption_e,
            "Building Annual Fossil Fuel Consumption (kWh)": v_single_annual_consumption_f,
            "Building Annual Electricity Cost": v_single_annual_cost_e,
            "Building Annual Fossil Fuel Cost": v_single_annual_cost_f,
            "Building Annual Electricity EUI (kWh/m2)": v_single_eui_e,
            "Building Annual Fossil Fuel EUI (kWh/m2)": v_single_eui_f,
            "Building Annual Energy Cost Savings": v_single_cost_savings,
            "Building Annual Energy Saving (%)": v_single_cost_savings_pct,
            "Building Annual Fossil Fuel EUI (kWh/m2)": v_single_eui_f,
            "Detail Report": v_rpt_path
        })

        self.df_bldg_summary = pd.DataFrame(d_bldg_summary)

        # Explore whether this support JS to enable the sorting function
        self.html_table_bldg_summary = self.df_bldg_summary.to_html(
            classes = 'w3-table w3-bordered w3-border tablesorter" id="myTable"',
            index=False
            )

        if save_portfolio_results:
            s_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            output_path = s_path + '/outputs/'
            self.df_bldg_summary.to_csv(output_path + 'portfolio_results.csv', index=False)

        return


if __name__ == "__main__":
    # Example of how to generate benchmark stats from the portfolio spreadsheet
    p = Portfolio('Test')
    # file = 'C:/Users/Han/Dropbox (Energy Technologies)/Projects/CERC-BEE  Benchmarking Tool/Demonstration/2018-11-05/tool/data/portfolio_JCI_tuning.xlsx'
    file = 'C:/Users/Han/Documents/GitHub/CERC/CERC-BEE-Benchmarking-Tool/data/portfolio.xlsx'
    p.read_raw_data_from_xlsx(file)
    dict_utility_e = p.get_portfolio_raw_data_by_spaceType_and_utilityType('Hotel_酒店', 1)
    dict_utility_f = p.get_portfolio_raw_data_by_spaceType_and_utilityType('Hotel_酒店', 2)

    df_models_e = p.generate_building_models(dict_utility_e)
    df_models_f = p.generate_building_models(dict_utility_f)

    df_bench_coeffs_e = p.generate_benchmark_stats(df_models_e)
    df_bench_coeffs_f = p.generate_benchmark_stats(df_models_f)

    print(df_bench_coeffs_e)
    print(df_bench_coeffs_f)

    import datetime
    df_models_e.to_csv('C:/Users/Han/Documents/GitHub/CERC/CERC-BEE-Benchmarking-Tool/data/' + datetime.datetime.today().strftime('%Y-%m-%d') + 'models_e.csv')
    df_models_f.to_csv('C:/Users/Han/Documents/GitHub/CERC/CERC-BEE-Benchmarking-Tool/data/' + datetime.datetime.today().strftime('%Y-%m-%d') + 'models_f.csv')
    df_bench_coeffs_e.to_csv('C:/Users/Han/Documents/GitHub/CERC/CERC-BEE-Benchmarking-Tool/data/' + datetime.datetime.today().strftime('%Y-%m-%d') + 'bench_stats_e.csv')
    df_bench_coeffs_f.to_csv('C:/Users/Han/Documents/GitHub/CERC/CERC-BEE-Benchmarking-Tool/data/' + datetime.datetime.today().strftime('%Y-%m-%d') + 'bench_stats_f.csv')
'''

Energy Efficiency Targeting Tool Copyright (c) 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Intellectual Property Office at  IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department of Energy and the U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit other to do so. 

'''


import model
import benchmark
import constants
import assessment

import pandas as pd
import numpy as np
import geocoder
import copy


class Building:
    def __init__(self, bldg_id, bldg_name, bldg_address, bldg_type, bldg_area, currency='US Dollar', saving_target=2):
        self.bldg_id = bldg_id
        self.bldg_name = bldg_name
        self.bldg_address = bldg_address
        self.bldg_type = bldg_type
        self.bldg_area = round(bldg_area, 1)
        self.currency = currency
        self.geocode_address()

        self.saving_target = saving_target
        if(saving_target==1):
            self.saving_target_str = 'Conservative'
        elif(saving_target==2):
            self.saving_target_str = 'Nominal'
        else:
            self.saving_target_str = 'Aggressive'

    def geocode_address(self):
        # Note: google API might not be accessible in China
        # Change the geocoder to Baidu or other Chinese search engine for Chinese tool
        try:
            # Try different geocoders: Google -> ArcGIS -> Bing -> Baidu
            self.geo_coder = geocoder.google(self.bldg_address)
            if (self.geo_coder.latlng is None):
                self.geo_coder = geocoder.arcgis(self.bldg_address)
            if (self.geo_coder.latlng is None):
                self.geo_coder = geocoder.bing(self.bldg_address)
            if (self.geo_coder.latlng is None):
                self.geo_coder = geocoder.baidu(self.bldg_address)
        except:
            raise ("Try another geocoder provider")

        self.coord = self.geo_coder.latlng
        self.latitude, self.longitude = self.coord
        self.geo_address = self.geo_coder.address

    def add_utility(self, utility_e=None, utility_f=None):
        if (utility_e is not None):
            self.utility_electricity = copy.deepcopy(utility_e)
            if (hasattr(self.utility_electricity, "df_raw_data")):
                self.utility_electricity.process()
        if (utility_f is not None):
            self.utility_fossil_fuel = copy.deepcopy(utility_f)
            if (hasattr(self.utility_fossil_fuel, "df_raw_data")):
                self.utility_fossil_fuel.process()

    def add_weather(self, cached=True, weather_e=None, weather_f=None):
        # cached: True ~ pre-downloaded weather dat, False ~ download the weather on the go.
        if (weather_e is not None and hasattr(self.utility_electricity, "df_raw_data")):
            self.weather_electricity = copy.deepcopy(weather_e)
            self.weather_electricity.process(self.utility_electricity.df_periods)
            if cached:
                self.weather_electricity.use_downloaded_weather()
            else:
                self.weather_electricity.download_weather_NOAA()
        if (weather_f is not None and hasattr(self.utility_fossil_fuel, "df_raw_data")):
            self.weather_fossil_fuel = copy.deepcopy(weather_f)
            self.weather_fossil_fuel.process(self.utility_fossil_fuel.df_periods)
            if cached:
                self.weather_fossil_fuel.use_downloaded_weather()
            else:
                self.weather_fossil_fuel.download_weather_NOAA()

    def pre_process(self):
        # Calculate energy, cost, and EUI
        if (hasattr(self, "utility_electricity") and hasattr(self.utility_electricity, "daily_kWh")):
            self.recent_annual_electricity_kWh = self.utility_electricity.recent_annual_consumption
            if self.utility_electricity.recent_annual_cost > 0:
                self.recent_annual_electricity_cost = int(self.utility_electricity.recent_annual_cost)
            else:
                self.recent_annual_electricity_cost = int(self.recent_annual_electricity_kWh * constants.Constants.electricity_unit_price)
            self.recent_annual_electricity_EUI = round(self.recent_annual_electricity_kWh /self.bldg_area, 1)
            self.eui_daily_electricity = self.utility_electricity.daily_kWh / self.bldg_area
            self.eui_daily_all_periods_electricity = self.utility_electricity.daily_kWh_all_periods / self.bldg_area
            self.annual_eui_electricity = round(
                self.eui_daily_all_periods_electricity * constants.Constants.days_in_year, 2)


        if (hasattr(self, "utility_fossil_fuel") and hasattr(self.utility_fossil_fuel, "daily_kWh")):
            self.recent_annual_fossil_fuel_kWh = self.utility_fossil_fuel.recent_annual_consumption
            if self.utility_fossil_fuel.recent_annual_cost > 0:
                self.recent_annual_fossil_fuel_cost = int(self.utility_fossil_fuel.recent_annual_cost)
            else:
                self.recent_annual_fossil_fuel_cost = int(self.recent_annual_fossil_fuel_kWh * constants.Constants.fossil_fuel_unit_price)
            self.recent_annual_fossil_fuel_EUI = round(self.recent_annual_fossil_fuel_kWh /self.bldg_area, 1)
            self.eui_daily_fossil_fuel = self.utility_fossil_fuel.daily_kWh / self.bldg_area
            self.eui_daily_all_periods_fossil_fuel = self.utility_fossil_fuel.daily_kWh_all_periods / self.bldg_area
            self.annual_eui_fossil_fuel = round(
                self.eui_daily_all_periods_fossil_fuel * constants.Constants.days_in_year, 2)

    def fit_inverse_model(self):

        # Pre-processing
        self.pre_process()
        has_fit_e = has_fit_f = False
        # Fit change-point model for electricity consumption
        print('Fitting electricity model...')
        if (hasattr(self, "weather_electricity")):
            self.im_electricity = model.InverseModel(self.weather_electricity.v_T_C,
                                                     self.eui_daily_electricity,
                                                     'Electricity')
            has_fit_e = self.im_electricity.fit_model()
            if (has_fit_e):
                self.im_electricity.plot_IM(self)
        # Fit change-point model for fossil fuel consumption
        print('Fitting fossil fuel model...')
        if (hasattr(self, "weather_fossil_fuel")):
            self.im_fossil_fuel = model.InverseModel(self.weather_fossil_fuel.v_T_C,
                                                     self.eui_daily_fossil_fuel,
                                                     'Fossil Fuel')
            has_fit_f = self.im_fossil_fuel.fit_model()
            if (has_fit_f): self.im_fossil_fuel.plot_IM(self)
        return (has_fit_e or has_fit_f)

    def benchmark(self, use_default=True, df_benchmark_stats_electricity=None,
                  df_benchmark_stats_fossil_fuel=None):
        """
        This function add Benchmark instances for the current Building instance
        :return:
        """
        print("Start benchamrking")
        if use_default:
            df_sample_bench_stats_e = constants.Constants.df_sample_benchmark_stats_e
            df_sample_bench_stats_f = constants.Constants.df_sample_benchmark_stats_f
        else:
            df_sample_bench_stats_e = df_benchmark_stats_electricity
            df_sample_bench_stats_f = df_benchmark_stats_fossil_fuel

        if (hasattr(self, "im_electricity") and hasattr(self.im_electricity, "coeffs")):
            # Electricity
            self.benchmark_HSL_e = benchmark.Benchmark('beta_hdd',
                                                       self.im_electricity.coeffs['hsl'],
                                                       df_bench_stats=df_sample_bench_stats_e,
                                                       valid=self.im_electricity.coeff_validation['hsl'])
            self.benchmark_HCP_e = benchmark.Benchmark('beta_beth',
                                                       self.im_electricity.coeffs['hcp'],
                                                       df_bench_stats=df_sample_bench_stats_e,
                                                       valid=self.im_electricity.coeff_validation['hcp'])
            self.benchmark_BASE_e = benchmark.Benchmark('beta_base',
                                                        self.im_electricity.coeffs['base'],
                                                        df_bench_stats=df_sample_bench_stats_e,
                                                       valid=self.im_electricity.coeff_validation['base'])
            self.benchmark_CCP_e = benchmark.Benchmark('beta_betc',
                                                       self.im_electricity.coeffs['ccp'],
                                                       df_bench_stats=df_sample_bench_stats_e,
                                                       valid=self.im_electricity.coeff_validation['ccp'])
            self.benchmark_CSL_e = benchmark.Benchmark('beta_cdd',
                                                       self.im_electricity.coeffs['csl'],
                                                       df_bench_stats=df_sample_bench_stats_e,
                                                       valid=self.im_electricity.coeff_validation['csl'])
            self.benchmark_HSL_e.benchmark(plot=False)
            self.benchmark_HCP_e.benchmark(plot=False)
            self.benchmark_BASE_e.benchmark(plot=False)
            self.benchmark_CCP_e.benchmark(plot=False)
            self.benchmark_CSL_e.benchmark(plot=False)
        else:
            self.benchmark_HSL_e = None
            self.benchmark_HCP_e = None
            self.benchmark_BASE_e = None
            self.benchmark_CCP_e = None
            self.benchmark_CSL_e = None
        if (hasattr(self, "im_fossil_fuel") and hasattr(self.im_fossil_fuel, "coeffs")):
            # Need to add default fossil fuel in the constants module !!!
            # Default benchmark stats will be used is no specific benchmark stats are provided
            # Fossil fuel
            self.benchmark_HSL_f = benchmark.Benchmark('beta_hdd',
                                                       self.im_fossil_fuel.coeffs['hsl'],
                                                       df_bench_stats=df_sample_bench_stats_f,
                                                       valid=self.im_fossil_fuel.coeff_validation['hsl'])
            self.benchmark_HCP_f = benchmark.Benchmark('beta_beth',
                                                       self.im_fossil_fuel.coeffs['hcp'],
                                                       df_bench_stats=df_sample_bench_stats_f,
                                                       valid=self.im_fossil_fuel.coeff_validation['hcp'])
            self.benchmark_BASE_f = benchmark.Benchmark('beta_base',
                                                        self.im_fossil_fuel.coeffs['base'],
                                                        df_bench_stats=df_sample_bench_stats_f,
                                                       valid=self.im_fossil_fuel.coeff_validation['base'])
            self.benchmark_CCP_f = benchmark.Benchmark('beta_betc',
                                                       self.im_fossil_fuel.coeffs['ccp'],
                                                       df_bench_stats=df_sample_bench_stats_f,
                                                       valid=self.im_fossil_fuel.coeff_validation['ccp'])
            self.benchmark_CSL_f = benchmark.Benchmark('beta_cdd',
                                                       self.im_fossil_fuel.coeffs['csl'],
                                                       df_bench_stats=df_sample_bench_stats_f,
                                                       valid=self.im_fossil_fuel.coeff_validation['csl'])
            self.benchmark_HSL_f.benchmark(plot=False)
            self.benchmark_HCP_f.benchmark(plot=False)
            self.benchmark_BASE_f.benchmark(plot=False)
            self.benchmark_CCP_f.benchmark(plot=False)
            self.benchmark_CSL_f.benchmark(plot=False)
        else:
            self.benchmark_HSL_f = None
            self.benchmark_HCP_f = None
            self.benchmark_BASE_f = None
            self.benchmark_CCP_f = None
            self.benchmark_CSL_f = None

        # Plot benchmark html sections
        self.benchmarking_bar_hsl_e_html = benchmark.Benchmark.generate_benchmark_bar_html(self.benchmark_HSL_e)
        self.benchmarking_bar_hcp_e_html = benchmark.Benchmark.generate_benchmark_bar_html(self.benchmark_HCP_e)
        self.benchmarking_bar_base_e_html = benchmark.Benchmark.generate_benchmark_bar_html(self.benchmark_BASE_e)
        self.benchmarking_bar_ccp_e_html = benchmark.Benchmark.generate_benchmark_bar_html(self.benchmark_CCP_e)
        self.benchmarking_bar_csl_e_html = benchmark.Benchmark.generate_benchmark_bar_html(self.benchmark_CSL_e)

        self.benchmarking_bar_hsl_f_html = benchmark.Benchmark.generate_benchmark_bar_html(self.benchmark_HSL_f)
        self.benchmarking_bar_hcp_f_html = benchmark.Benchmark.generate_benchmark_bar_html(self.benchmark_HCP_f)
        self.benchmarking_bar_base_f_html = benchmark.Benchmark.generate_benchmark_bar_html(self.benchmark_BASE_f)
        self.benchmarking_bar_ccp_f_html = benchmark.Benchmark.generate_benchmark_bar_html(self.benchmark_CCP_f)
        self.benchmarking_bar_csl_f_html = benchmark.Benchmark.generate_benchmark_bar_html(self.benchmark_CSL_f)

    def ee_assess(self, use_default=True, df_benchmark_stats_electricity=None,
                  df_benchmark_stats_fossil_fuel=None):
        # Current building model coefficients
        if (hasattr(self, "im_electricity") and hasattr(self.im_electricity, "coeffs")):
            building_coeffs_e = [
                self.im_electricity.coeffs['base'],
                self.im_electricity.coeffs['csl'],
                self.im_electricity.coeffs['ccp'],
                self.im_electricity.coeffs['hsl'],
                self.im_electricity.coeffs['hcp']
            ]
        else:
            building_coeffs_e = None

        if (hasattr(self, "im_fossil_fuel") and hasattr(self.im_fossil_fuel, "coeffs")):
            building_coeffs_f = [
                self.im_fossil_fuel.coeffs['base'],
                self.im_fossil_fuel.coeffs['csl'],
                self.im_fossil_fuel.coeffs['ccp'],
                self.im_fossil_fuel.coeffs['hsl'],
                self.im_fossil_fuel.coeffs['hcp']
            ]
        else:
            building_coeffs_f = None

        if (use_default):
            # Use default benchmarking stats
            df_assessment_e = copy.deepcopy(constants.Constants.df_sample_benchmark_stats_e)
            df_assessment_f = copy.deepcopy(constants.Constants.df_sample_benchmark_stats_f)
        else:
            df_assessment_e = copy.deepcopy(df_benchmark_stats_electricity)
            df_assessment_f = copy.deepcopy(df_benchmark_stats_fossil_fuel)

        df_assessment_e["site_coefficients"] = building_coeffs_e
        df_assessment_f["site_coefficients"] = building_coeffs_f

        # Assess energy efficient measures
        if (not pd.isna(df_assessment_e['site_coefficients']).all()):
            # Assess only if there is an electricity change-point model
            FIM_analysis_e = assessment.LEAN_FIMs(df_assessment_e, 1)  # (electricity = 1, fossil fuel = 2)
            FIM_analysis_e.set_targets(self.saving_target)  # conservative = 1, nominal = 2, aggressive = 3
            self.FIM_table_e = FIM_analysis_e.FIM_recommendations(save_file=False)
            self.coeff_out_e = FIM_analysis_e.savings_coefficients(save_file=False)
            # Save the suggested new model coefficients
            df_new_coeffs_e = FIM_analysis_e.savings_coefficients()['savings_coefficients']
            self.base_new_e = df_new_coeffs_e['beta_base']
            self.hsl_new_e = -df_new_coeffs_e['beta_hdd']
            self.hcp_new_e = df_new_coeffs_e['beta_beth']
            self.csl_new_e = df_new_coeffs_e['beta_cdd']
            self.ccp_new_e = df_new_coeffs_e['beta_betc']
            self.p_new_e = self.hcp_new_e, self.ccp_new_e, self.base_new_e, self.hsl_new_e, self.csl_new_e

            # print(self.p_new_e)

            ls_p = FIM_analysis_e.benchmark_medians.tolist()
            self.p_typical_e = ls_p[4], ls_p[2], ls_p[0], -ls_p[3], ls_p[1]

        if (not pd.isna(df_assessment_f['site_coefficients']).all()):
            # Assess only if there is a fossil fuel change-point model
            FIM_analysis_f = assessment.LEAN_FIMs(df_assessment_f, 2)  # (electricity = 1, fossil fuel = 2)
            FIM_analysis_f.set_targets(self.saving_target)  # conservative = 1, nominal = 2, aggressive = 3
            self.FIM_table_f = FIM_analysis_f.FIM_recommendations(save_file=False)
            self.coeff_out_f = FIM_analysis_f.savings_coefficients(save_file=False)
            df_new_coeffs_f = FIM_analysis_f.savings_coefficients()['savings_coefficients']
            self.base_new_f = df_new_coeffs_f['beta_base']
            self.hsl_new_f = -df_new_coeffs_f['beta_hdd']
            self.hcp_new_f = df_new_coeffs_f['beta_beth']
            self.csl_new_f = df_new_coeffs_f['beta_cdd']
            self.ccp_new_f = df_new_coeffs_f['beta_betc']
            self.p_new_f = self.hcp_new_f, self.ccp_new_f, self.base_new_f, self.hsl_new_f, self.csl_new_f
            ls_p = FIM_analysis_f.benchmark_medians.tolist()
            self.p_typical_f = ls_p[4], ls_p[2], ls_p[0], -ls_p[3], ls_p[1]

        # Get final fim list
        if (hasattr(self, 'FIM_table_e') and not hasattr(self, 'FIM_table_f')):
            df_FIM = self.FIM_table_e
            df_FIM = df_FIM[(df_FIM['FIM Recommendations'] == 'X')]
        elif (not hasattr(self, 'FIM_table_e') and hasattr(self, 'FIM_table_f')):
            df_FIM = self.FIM_table_f
            df_FIM = df_FIM[(df_FIM['FIM Recommendations'] == 'X')]
        elif (hasattr(self, 'FIM_table_e') and hasattr(self, 'FIM_table_f')):
            df_FIM = pd.concat([self.FIM_table_e, self.FIM_table_f], axis=1)
            df_FIM.columns = ['FIM Electricity', 'FIM Fossil Fuel']
            df_FIM = df_FIM[(df_FIM['FIM Electricity'] == 'X') | (df_FIM['FIM Fossil Fuel'] == 'X')]
        self.FIM_list = list(df_FIM.index)

    def calculate_savings(self):
        self.total_energy_consumption_old = 0
        if (not hasattr(self, "p_new_e")):
            print("No saving model found for electricity consumption!")
        else:
            # Calculate electricity savings (all and most recent year)
            self.v_old_daily_eui_all_e = model.InverseModel.piecewise_linear(self.weather_electricity.v_T_C, *self.im_electricity.model_p)
            self.v_new_daily_eui_all_e = model.InverseModel.piecewise_linear(self.weather_electricity.v_T_C, *self.p_new_e)
            self.v_old_consumption_all_e = np.round(self.bldg_area * np.multiply(self.v_old_daily_eui_all_e, self.utility_electricity.days), 1)
            self.v_new_consumption_all_e = np.round(self.bldg_area * np.multiply(self.v_new_daily_eui_all_e, self.utility_electricity.days), 1)
            self.v_old_consumption_last_year_e = self.v_old_consumption_all_e[-12:]
            self.v_new_consumption_last_year_e = self.v_new_consumption_all_e[-12:]
            self.old_consumption_last_year_e = np.sum(self.v_old_consumption_last_year_e)
            self.new_consumption_last_year_e = np.sum(self.v_new_consumption_last_year_e)
            self.total_energy_savings_last_year_e = self.old_consumption_last_year_e - self.new_consumption_last_year_e
            self.total_energy_savings_pct_last_year_e = np.round(self.total_energy_savings_last_year_e / self.old_consumption_last_year_e * 100, 2)
            # Calculate cost savings
            if (not hasattr(self.utility_electricity, 'utility_unit_price')):
                self.utility_electricity.utility_unit_price = constants.Constants.electricity_unit_price
                print('Warning: No electricity cost data provided, using default value!')
            self.total_cost_savings_e = round(self.utility_electricity.utility_unit_price * self.total_energy_savings_last_year_e, 1)
            self.total_energy_consumption_old += self.old_consumption_last_year_e

        if (not hasattr(self, "p_new_f")):
            print("No saving model found for fossil fuel consumption!")
        else:
            # Calculate fossil_fuel savings (all and most recent year)
            self.v_old_daily_eui_all_f = model.InverseModel.piecewise_linear(self.weather_fossil_fuel.v_T_C, *self.im_fossil_fuel.model_p)
            self.v_new_daily_eui_all_f = model.InverseModel.piecewise_linear(self.weather_fossil_fuel.v_T_C, *self.p_new_f)
            self.v_old_consumption_all_f = np.round(self.bldg_area * np.multiply(self.v_old_daily_eui_all_f, self.utility_fossil_fuel.days), 1)
            self.v_new_consumption_all_f = np.round(self.bldg_area * np.multiply(self.v_new_daily_eui_all_f, self.utility_fossil_fuel.days), 1)
            self.v_old_consumption_last_year_f = self.v_old_consumption_all_f[-12:]
            self.v_new_consumption_last_year_f = self.v_new_consumption_all_f[-12:]
            self.old_consumption_last_year_f = np.sum(self.v_old_consumption_last_year_f)
            self.new_consumption_last_year_f = np.sum(self.v_new_consumption_last_year_f)
            self.total_energy_savings_last_year_f = self.old_consumption_last_year_f - self.new_consumption_last_year_f
            self.total_energy_savings_pct_last_year_f = np.round(self.total_energy_savings_last_year_f / self.old_consumption_last_year_f * 100, 2)
            # Calculate cost savings
            if (not hasattr(self.utility_fossil_fuel, 'utility_unit_price')):
                self.utility_fossil_fuel.utility_unit_price = constants.Constants.fossil_fuel_unit_price
                print('Warning: No fossil_fuel cost data provided, using default value!')
            self.total_cost_savings_f = round(self.utility_fossil_fuel.utility_unit_price * self.total_energy_savings_last_year_f, 1)
            self.total_energy_consumption_old += self.old_consumption_last_year_f


        # Get combined total savings
        self.total_energy_savings = 0
        self.total_cost_savings = 0
        if (hasattr(self, 'total_energy_savings_last_year_e')):
            self.total_energy_savings += self.total_energy_savings_last_year_e
            self.total_cost_savings += self.total_cost_savings_e
        if (hasattr(self, 'total_energy_savings_last_year_f')):
            self.total_energy_savings += self.total_energy_savings_last_year_f
            self.total_cost_savings += self.total_cost_savings_f
        self.total_energy_savings_pct = np.round(self.total_energy_savings / self.total_energy_consumption_old * 100, 1)
        self.total_cost_savings = np.round(self.total_cost_savings, 0)

    def assemble_saving_dataframe(self):
        # Create a dataframe of savings per billing period for plotting
        if (hasattr(self, "v_new_consumption_all_e")):
            d_savings_e = {'Bill Start Dates': self.weather_electricity.v_start_dates,
                           'Bill End Dates': self.weather_electricity.v_end_dates,
                           'Original Consumption': self.utility_electricity.df_raw_data['kWh'],
                           'Estimated Consumption with Improvements': self.v_new_consumption_all_e
                           }
            df_savings_e = pd.DataFrame(d_savings_e)
            self.df_savings_e = df_savings_e.sort_values(by=['Bill End Dates'])

        if (hasattr(self, "v_new_consumption_all_f")):
            d_savings_f = {'Bill Start Dates': self.weather_fossil_fuel.v_start_dates,
                           'Bill End Dates': self.weather_fossil_fuel.v_end_dates,
                           'Original Consumption': self.utility_fossil_fuel.df_raw_data['kWh'],
                           'Estimated Consumption with Improvements': self.v_new_consumption_all_f
                           }
            df_savings_f = pd.DataFrame(d_savings_f)
            self.df_savings_f = df_savings_f.sort_values(by=['Bill End Dates'])

    def plot_savings(self):
        self.assemble_saving_dataframe()
        if (hasattr(self, "df_savings_e")):
            self.energy_savings_fig_e = self.plot_helper(self.df_savings_e, 'Electricity')
        if (hasattr(self, "df_savings_f")):
            self.energy_savings_fig_f = self.plot_helper(self.df_savings_f, 'Fossil Fuel')

    @staticmethod
    def plot_helper(df_savings, utility_type):
        # Prepare
        df_savings['Time'] = pd.to_datetime(df_savings['Bill End Dates'])
        df_savings['Time'] = df_savings['Time'].dt.strftime('%Y-%m')
        canvas_type = 'consumption_e' if utility_type == 'Electricity' else 'consumption_f'

        v_time = list(df_savings['Time'])
        v_old_consumption = list(df_savings['Original Consumption'])
        v_new_consumption = list(df_savings['Estimated Consumption with Improvements'])

        # Write the html
        consumption_line_chart_html = '''
            <script>
              var options = {
                legend: {
                    position: "bottom"
                    },
                title: {
                  display: true,
                  text: "''' + utility_type + ''' Consumption"
                },
                scales: {
                  xAxes: [{
                     ticks: {
                        maxRotation: 0,
                        autoSkip: 0,
                        callback(value) {
                        var rem = parseInt(value.substring(5,7))%3;
                        if (rem == 0){
                        return value;
                        } else {
                        return ;
                        }
                      }
                    }    
                  }
                  ],
                  yAxes: [{
                    scaleLabel:{
                      display : true,
                      labelString: "''' + utility_type + ''' Consumption (MWh)",
                    },
                    ticks: {
                      beginAtZero: true,
                      callback: function (value) {
                        return (value/1000.).toLocaleString()
                      },
                    }
                  }
                  ]
                },
              }
              var myChart = new Chart(document.getElementById("''' + canvas_type + '''"), {{
                type: 'line',
                data: {{
                  labels: {},
                  datasets: [{{
                    data: {},
                    label: "Original Consumption",
                    borderColor: "rgba(255,192,0,1)",
                    backgroundColor: "rgba(255,192,0,1)",
                    fill: false,
                    pointRadius: 0,
                  }}, {{
                    data: {},
                    label: "Improved Consumption",
                    borderColor: "rgba(0,176,80,1)",
                    backgroundColor: "rgba(0,176,80,1)",
                    fill: false,
                    pointRadius: 0,
                  }},
                  ]
                }},
                options: options
              }});
            </script>
        '''.format(v_time,
                   v_old_consumption,
                   v_new_consumption)

        return (consumption_line_chart_html)

    @staticmethod
    def disaggregate_consumption(v_T, v_days, model_p, area):
        # Get model coefficients
        hcp, ccp, base, hsl, csl = model_p
        # Mask the temperature and number of days vectors
        v_T_heating = v_T[v_T < hcp] if (not np.isnan(hcp)) else [-1]
        v_T_cooling = v_T[v_T > ccp] if (not np.isnan(ccp)) else [-1]
        v_days_heating = v_days[v_T < hcp] if (not np.isnan(hcp)) else [-1]
        v_days_cooling = v_days[v_T > ccp] if (not np.isnan(ccp)) else [-1]
        # Calculate the disaggregated energy consumption
        v_base_consumption = base * v_days * area

        if(len(v_T_heating) > 1):
            v_heating_consumption = (model.InverseModel.piecewise_linear(v_T_heating,
                                                                         *model_p) - base) * v_days_heating * area
        else:
            v_heating_consumption = [0]
        if(len(v_T_cooling) > 1):
            v_cooling_consumption = (model.InverseModel.piecewise_linear(v_T_cooling,
                                                                         *model_p) - base) * v_days_cooling * area
        else:
            v_cooling_consumption = [0]
        return sum(v_base_consumption), sum(v_heating_consumption), sum(v_cooling_consumption)

    def disaggregate_consumption_wrapper(self):
        # All the consumption terms are in kWh in this function
        # Consumption (kWh)
        self.base_old = 0
        self.heating_old = 0
        self.cooling_old = 0
        self.base_typical = 0
        self.heating_typical = 0
        self.cooling_typical = 0
        self.base_new = 0
        self.heating_new = 0
        self.cooling_new = 0

        # Cost
        self.base_old_cost = 0
        self.heating_old_cost = 0
        self.cooling_old_cost = 0
        self.base_typical_cost = 0
        self.heating_typical_cost = 0
        self.cooling_typical_cost = 0
        self.base_new_cost = 0
        self.heating_new_cost = 0
        self.cooling_new_cost = 0

        # Annualize the consumption (How?)
        # Calculate the diaggregated consumption
        if (hasattr(self, "v_new_consumption_last_year_e")):
            unit_price_e = self.utility_electricity.utility_unit_price
            base_old_e, heating_old_e, cooling_old_e = self.disaggregate_consumption(
                self.weather_electricity.v_T_C[-12:],
                self.utility_electricity.days[-12:],
                self.im_electricity.model_p,
                self.bldg_area
            )
            base_typical_e, heating_typical_e, cooling_typical_e = self.disaggregate_consumption(
                self.weather_electricity.v_T_C[-12:],
                self.utility_electricity.days[-12:],
                self.p_typical_e,
                self.bldg_area
            )
            base_new_e, heating_new_e, cooling_new_e = self.disaggregate_consumption(
                self.weather_electricity.v_T_C[-12:],
                self.utility_electricity.days[-12:],
                self.p_new_e,
                self.bldg_area
            )

            self.base_old += base_old_e
            self.base_typical += base_typical_e
            self.base_new += base_new_e
            self.heating_old += heating_old_e
            self.heating_typical += heating_typical_e
            self.heating_new += heating_new_e
            self.cooling_old += cooling_old_e
            self.cooling_typical += cooling_typical_e
            self.cooling_new += cooling_new_e

            self.base_old_cost += base_old_e * unit_price_e
            self.base_typical_cost += base_typical_e * unit_price_e
            self.base_new_cost += base_new_e * unit_price_e
            self.heating_old_cost += heating_old_e * unit_price_e
            self.heating_typical_cost += heating_typical_e * unit_price_e
            self.heating_new_cost += heating_new_e * unit_price_e
            self.cooling_old_cost += cooling_old_e * unit_price_e
            self.cooling_typical_cost += cooling_typical_e * unit_price_e
            self.cooling_new_cost += cooling_new_e * unit_price_e


        if (hasattr(self, "v_new_consumption_last_year_f")):
            unit_price_f = self.utility_fossil_fuel.utility_unit_price
            base_old_f, heating_old_f, cooling_old_f = self.disaggregate_consumption(
                self.weather_fossil_fuel.v_T_C[-12:],
                self.utility_fossil_fuel.days[-12:],
                self.im_fossil_fuel.model_p,
                self.bldg_area
            )

            base_typical_f, heating_typical_f, cooling_typical_f = self.disaggregate_consumption(
                self.weather_fossil_fuel.v_T_C[-12:],
                self.utility_fossil_fuel.days[-12:],
                self.p_typical_f,
                self.bldg_area
            )

            base_new_f, heating_new_f, cooling_new_f = self.disaggregate_consumption(
                self.weather_fossil_fuel.v_T_C[-12:],
                self.utility_fossil_fuel.days[-12:],
                self.p_new_f,
                self.bldg_area
            )
            self.base_old += base_old_f
            self.base_typical += base_typical_f
            self.base_new += base_new_f
            self.heating_old += heating_old_f
            self.heating_typical += heating_typical_f
            self.heating_new += heating_new_f
            self.cooling_old += cooling_old_f
            self.cooling_typical += cooling_typical_f
            self.cooling_new += cooling_new_f

            self.base_old_cost += base_old_f * unit_price_f
            self.base_typical_cost += base_typical_f * unit_price_f
            self.base_new_cost += base_new_f * unit_price_f
            self.heating_old_cost += heating_old_f * unit_price_f
            self.heating_typical_cost += heating_typical_f * unit_price_f
            self.heating_new_cost += heating_new_f * unit_price_f
            self.cooling_old_cost += cooling_old_f * unit_price_f
            self.cooling_typical_cost += cooling_typical_f * unit_price_f
            self.cooling_new_cost += cooling_new_f * unit_price_f
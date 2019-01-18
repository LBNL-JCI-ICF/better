'''

Energy Efficiency Targeting Tool Copyright (c) 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Intellectual Property Office at  IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department of Energy and the U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit other to do so. 

'''

import utility
import weather
import building
import portfolio
import report

import os

def run_single(
    bldg_id = 1, 
    saving_target = 2, 
    space_type='Office',
    cached_weather=True, 
    write_fim=True, 
    write_model=True, 
    return_data=False,
    use_default_benchmark_data=True,
    df_user_bench_stats_e=None,
    df_user_bench_stats_f=None
    ):
    # Set paths
    s_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    data_path = s_path + '/Data/'
    report_path = s_path + '/outputs/'

    # Create an outputs directoty if there isn't one.
    if not os.path.exists(report_path): os.makedirs(report_path)

    # Initialize a portfolio instance
    p = portfolio.Portfolio('Test')
    # p.read_raw_data_from_xlsx(data_path + 'portfolio.xlsx')
    p.read_raw_data_from_xlsx(data_path + 'portfolio.xlsx')

    # Get building data from the portfolio
    building_id = bldg_id
    building_info = p.get_building_info_by_id(building_id)
    if(building_info == None):
        return False, None
    else:
        # Initialize a building instance
        building_test = building.Building(building_id, *building_info, saving_target)
        # Get utility data from portfolio
        df_raw_electricity = p.get_utility_by_building_id_and_energy_type(building_ID=building_id, energy_type=1)
        df_raw_fossil_fuel = p.get_utility_by_building_id_and_energy_type(building_ID=building_id, energy_type=2)
        df_raw_utility_e = df_raw_electricity
        df_raw_utility_f = df_raw_fossil_fuel
        utility_test_e = utility.Utility('electricity', df_raw_utility_e)
        utility_test_f = utility.Utility('fossil fuel', df_raw_utility_f)
        building_test.add_utility(utility_test_e, utility_test_f)
        weather_test_e = weather.Weather(building_test.coord)
        weather_test_f = weather.Weather(building_test.coord)
        building_test.add_weather(cached_weather, weather_test_e, weather_test_f)
    
        # Fit inverse model and benchmark
        has_fit = building_test.fit_inverse_model()
        # Continue only if there is at least one change-point model fit.
        if has_fit:
            if (use_default_benchmark_data):
                building_test.benchmark()
                building_test.ee_assess()
            else:
                # Note: the benchmark data sets are generated from the portfolio spreadsheet.
                # 1 ~ electricity; 2 ~ fossil fuel
                dict_raw_electricity = p.get_portfolio_raw_data_by_spaceType_and_utilityType(space_type, utility_type=1)
                dict_raw_fossil_fuel = p.get_portfolio_raw_data_by_spaceType_and_utilityType(space_type, utility_type=2)
    
                # Generate the benchmark stats from the user provided data in the portfolio spreadsheet
                if df_user_bench_stats_e is None:
                    df_user_bench_stats_e = p.generate_benchmark_stats_wrapper(dict_raw_electricity, cached_weather)
                if df_user_bench_stats_f is None:
                    df_user_bench_stats_f = p.generate_benchmark_stats_wrapper(dict_raw_fossil_fuel, cached_weather)
    
                building_test.benchmark(use_default=False,
                                        df_benchmark_stats_electricity=df_user_bench_stats_e,
                                        df_benchmark_stats_fossil_fuel=df_user_bench_stats_f)
                building_test.ee_assess(use_default=False,
                                        df_benchmark_stats_electricity=df_user_bench_stats_e,
                                        df_benchmark_stats_fossil_fuel=df_user_bench_stats_f)
    
            building_test.calculate_savings()
            building_test.plot_savings()
            building_test.disaggregate_consumption_wrapper()
    
            # Output to files
            # Save FIM to csv
            if (hasattr(building_test, 'FIM_table_e')):
                if write_model: building_test.coeff_out_e.to_csv(report_path + 'bldg_' + str(building_test.bldg_id) + "_Electricity Coeffs_out.csv")
                if write_fim: building_test.FIM_table_e.to_csv(report_path + 'bldg_' + str(building_test.bldg_id) + "_Electricity FIM_recommendations.csv")
            if (hasattr(building_test, 'FIM_table_f')):
                if write_model: building_test.coeff_out_f.to_csv(report_path + 'bldg_' + str(building_test.bldg_id) + "_Fossil Fuel Coeffs_out.csv")
                if write_fim: building_test.FIM_table_f.to_csv(report_path + 'bldg_' + str(building_test.bldg_id) + "_Fossil Fuel FIM_recommendations.csv")
    
            # Generate static HTML report
            report_building = report.Report(building = building_test)
            report_building.generate_building_report_beta(report_path)
            return True, building_test
        else:
            print("No meaningful change-point model was found for the current building.")
            return False, None


def summary_html(report_path, start_id, end_id):
    report_file = report_path + '/summary_report.html'
    with open(report_file, 'w', encoding="utf-8") as report_html:
        report_html.write('<!DOCTYPE html>\n')
        report_html.write('<html>\n')
        report_html.write('<body>\n')
        for i in range(start_id, end_id+1):
            report_html.write('    <p><a href="./' + str(i) + '_Beijing_Hotel A' + str(i) + '_report.html">Building ' + str(i) + ' report</a></p>\n')
        report_html.write('</body>\n')
        report_html.write('</html>\n')

def run_batch(
    start_id, 
    end_id, 
    space_type='Office',
    saving_target=2, 
    cached_weather=True, 
    batch_report=False,
    use_default_benchmark_data=True
    ):
    
    # Conditionally generate the benchmark stats for the porfolio
    if use_default_benchmark_data:
        df_user_bench_stats_e, df_user_bench_stats_f = None, None
    else:
        # Initialize a portfolio instance
        s_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        data_path = s_path + '/Data/'
        p = portfolio.Portfolio('Test')
        p.read_raw_data_from_xlsx(data_path + 'portfolio.xlsx')

        # 1 ~ electricity; 2 ~ fossil fuel
        dict_raw_electricity = p.get_portfolio_raw_data_by_spaceType_and_utilityType(space_type, utility_type=1)
        dict_raw_fossil_fuel = p.get_portfolio_raw_data_by_spaceType_and_utilityType(space_type, utility_type=2)
        df_user_bench_stats_e = p.generate_benchmark_stats_wrapper(dict_raw_electricity, cached_weather)
        df_user_bench_stats_f = p.generate_benchmark_stats_wrapper(dict_raw_fossil_fuel, cached_weather)
        
    v_single_buildings = []
    v_single_building_reports = []
    for i in range(start_id, end_id+1):
        print('--------------------------------------------------')
        print('Analyzing building ' + str(i))
        single_building = run_single(
            bldg_id=i, 
            saving_target=saving_target, 
            cached_weather=cached_weather,
            use_default_benchmark_data=use_default_benchmark_data, 
            df_user_bench_stats_e=df_user_bench_stats_e,
            df_user_bench_stats_f=df_user_bench_stats_f
            )[1]
        v_single_buildings.append(single_building)

    if batch_report:
        report_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/outputs/'
        portfolio_out = portfolio.Portfolio('Sample Portfolio')
        portfolio_out.prepare_portfolio_report_data(v_single_buildings, report_path)
        report_portfolio = report.Report(portfolio = portfolio_out)
        report_portfolio.generate_portfolio_report(report_path)


def main():
    # Saving target: 1 ~ conservative, 2 ~ nominal, 3 ~ aggressive
    # Change the building id and saving target for the building you want to analyze
    # run_single(bldg_id = 11, saving_target=2, cached_weather=True)
    # run_single(bldg_id=18, saving_target=3, cached_weather=True)
    # run_single(bldg_id=10, saving_target=2, cached_weather=False)

    # Uncomment the line below [delete the '#' before run_batch(...)] to run the analysis for buildings between start_id and end_id
    run_batch(start_id = 1, end_id = 3, saving_target=2, cached_weather=False, batch_report=True)

if __name__ == "__main__":
    main()
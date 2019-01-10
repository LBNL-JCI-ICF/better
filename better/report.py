'''

Energy Efficiency Targeting Tool Copyright (c) 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Intellectual Property Office at  IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department of Energy and the U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit other to do so. 

'''

import datetime
import numpy as np
from .constants import *

class Report:

    def __init__(self, building=None, portfolio=None):
        self.logo()
        if building != None:
            self.building = building
            if (building.currency == 'Chinese Yuan 人民币'):
                self.currency_str = '¥'
            elif (building.currency == 'US Dollar 美元'):
                self.currency_str = '$'
            self.charts_js()
        if portfolio != None:
            self.portfolio = portfolio

    @staticmethod
    def format_number(number):
        str_number = ''
        try:
            str_number = '{:,}'.format(number)
        except:
            str_number = str(number)
        return str_number

    @staticmethod
    def html_basic():
        html_text =  '''
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
            <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Raleway">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.4.0/Chart.min.js"></script>
            <script type="text/javascript" src="https://code.jquery.com/jquery-3.3.1.js"></script>
            <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.0/js/jquery.tablesorter.js"></script>
            <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/plotly.js/1.42.5/plotly.js"></script>
            <style>
            body,
            h1,
            h2,
            h3,
            h4,
            h5,
            h6 {
                font-family: "Helvetica", sans-serif
                }
            .td_border {
                border: solid 0px grey;
                }
            .w3-table td {
                padding: 0px;
                }
            .number {
                position: relative;
                font: bold italic 45px/1.5 Helvetica, Verdana, sans-serif;
                color: green;
                margin: 10px;
                text-align: left;
                }
            .benchmark_bar {
                height: 38px;
                background: linear-gradient(to right, #ff0000 0%, #ffff00 50%, #00ff00 100%);
                }
            .vertical_line {
                height: 38px;
                width: 3px;
                background: #000;
                position: relative;
                }
            </style>
        '''
        return html_text

    def navigation_bar(self):
        html_text = ''
        # Navigation bar
        html_text += '<nav class="w3-sidebar w3-collapse w3-white w3-animate-left" style="z-index:3;width:270px;" id="mySidebar"><br>'
        html_text += '    <div class="w3-container">'
        html_text += '        <a href="#" onclick="w3_close()" class="w3-hide-large w3-right w3-jumbo w3-padding w3-hover-grey" title="close menu">'
        html_text += '            <i class="fa fa-remove"></i>'
        html_text += '        </a>'
        html_text += self.lbl_logo
        html_text += self.icf_logo
        html_text += self.jci_logo
        html_text += '        <br><br>'
        html_text += '        <h4><b>Energy Efficiency Targeting Tool</b></h4>'
        html_text += '        <p class="w3-text-grey">' + datetime.datetime.now().strftime("%Y-%m-%d  %H:%M") + '</p>'
        html_text += '    </div>'
        html_text += '    <div class="w3-bar-block">'
        html_text += '        <a href="#overview" onclick="w3_close()" class="w3-bar-item w3-button w3-padding"><i class="fa fa-th-large fa-fw w3-margin-right"></i>Overview</a> '
        html_text += '        <a href="#benchmark" onclick="w3_close()" class="w3-bar-item w3-button w3-padding"><i class="fa fa-group fa-fw w3-margin-right"></i>Benchmark</a> '
        html_text += '        <a href="#EE" onclick="w3_close()" class="w3-bar-item w3-button w3-padding"><i class="fa fa-calculator fa-fw w3-margin-right"></i>Energy Efficiency Analysis</a>'
        html_text += '        <a href="#IMT" onclick="w3_close()" class="w3-bar-item w3-button w3-padding"><i class="fa fa-key fa-fw w3-margin-right"></i>Performance Key</a>'
        html_text += '        <a href="#About" onclick="w3_close()" class="w3-bar-item w3-button w3-padding"><i class="fa fa-info fa-fw w3-margin-right"></i>About the Tool</a>'
        html_text += '    </div>'
        html_text += '</nav>'

        # Overlay effect when opening sidebar on small screens
        html_text += '<div class="w3-overlay w3-hide-large w3-animate-opacity" onclick="w3_close()" style="cursor:pointer" title="close side menu" id="myOverlay"></div>'
        html_text += '<!-- !PAGE CONTENT! -->'
        html_text += '<div class="w3-main" style="margin-left:300px; margin-right:20px">'
        return html_text

    def generate_building_report_beta(self, report_path):
        report_file = report_path + str(self.building.bldg_id) + '_' + self.building.bldg_address + '_' + self.building.bldg_name + '_report.html'
        report_file = report_file.replace(' ', '_')
        print(report_file)
        with open(report_file, 'w', encoding="utf-8") as report_html:
            report_html.write('<!DOCTYPE html>')
            report_html.write('<html>')
            report_html.write('<title>Energy Efficiency Targeting Tool Building Report</title>')

            # Add basic stuff including css and scripts
            report_html.write(self.html_basic())

            report_html.write('<body class="w3-light-grey w3-content" style="max-width:1500px">')
            report_html.write('<!-- Sidebar/menu -->')

             # Navigation bar
            report_html.write(self.navigation_bar())

            # Building Overview Card
            report_html.write('  <div class="w3-container w3-padding-large w3-white">')
            report_html.write('    <h2 id="overview"><b>' + self.building.bldg_name.upper() + '</b></h2>')
            report_html.write('    <hr class="w3-opacity">')

            report_html.write('<div class="w3-container w3-margin-bottom w3-padding-small">')
            report_html.write('    <table class="w3-table w3-bordered w3-border" style="width:95% border: solid 1 px blue">')
            report_html.write('  <tr>')
            report_html.write('    <td class="td_border" colspan="3"><b>Building Type</b></td>')
            report_html.write('    <td class="td_border" colspan="3">' + self.building.bldg_type + '</td>')
            report_html.write('    <td class="td_border" colspan="3"><b>Builidng Location</b></td>')
            report_html.write('    <td class="td_border" colspan="3">' + self.building.bldg_address + '</td>')
            report_html.write('  </tr>')
            report_html.write('  <tr>')
            report_html.write('    <td class="td_border" colspan="3"><b>Gross Floor Area (m<sup>2</sup>)</b></td>')
            report_html.write('    <td class="td_border" colspan="9">' + '{:,}'.format(self.building.bldg_area) + '</td>')
            report_html.write('  </tr>')
            report_html.write('  </table>')
            report_html.write('  <br>')
            report_html.write('    <table class="w3-table w3-bordered w3-border" style="width:95% border: solid 1 px blue">')
            report_html.write('  <tr>')
            report_html.write('    <td class="td_border" colspan="4"></td>')
            report_html.write('    <td class="td_border" colspan="4"><b>Electricity</b></td>')
            report_html.write('    <td class="td_border" colspan="4"><b>Fossil Fuel</b></td>')
            report_html.write('  </tr>')
            report_html.write('  <tr>')
            report_html.write('    <td class="td_border" colspan="4"><b>Annual Consumption (kWh)</b></td>')
            if(hasattr(self.building, 'recent_annual_electricity_kWh')):
                report_html.write('    <td class="td_border" colspan="4">' + '{:,}'.format(self.building.recent_annual_electricity_kWh) + '</td>')
            else:
                report_html.write('    <td class="td_border" colspan="4">No electricity data</td>')
          #  report_html.write('    <td class="td_border" colspan="4"><b>Annual Fossil Fuel Consumption (kWh)</b></td>')
            if(hasattr(self.building, 'recent_annual_fossil_fuel_kWh')):
                report_html.write('    <td class="td_border" colspan="4">' + '{:,}'.format(self.building.recent_annual_fossil_fuel_kWh) + '</td>')
            else:
                report_html.write('    <td class="td_border" colspan="4">No fossil fuel data</td>')
            report_html.write('  </tr>')
            report_html.write('  <tr>')
            report_html.write('    <td class="td_border" colspan="4"><b>Annual Cost (' + self.currency_str + ')</b></td>')
            if(hasattr(self.building, 'recent_annual_electricity_cost')):
                report_html.write('    <td class="td_border"  colspan="4">' + '{:,}'.format(self.building.recent_annual_electricity_cost) + '</td>')
            else:
                report_html.write('    <td class="td_border"  colspan="4">No electricity data</td>')
          #  report_html.write('    <td class="td_border" colspan="4"><b>Annual  Cost (' + self.currency_str + ')</b></td>')
            if(hasattr(self.building, 'recent_annual_fossil_fuel_cost')):
                report_html.write('    <td class="td_border"  colspan="4">' + '{:,}'.format(self.building.recent_annual_fossil_fuel_cost) + '</td>')
            else:
                report_html.write('    <td class="td_border"  colspan="4">No fossil fuel data</td>')
            report_html.write('  </tr>')
            report_html.write('  <tr>')
            report_html.write('    <td class="td_border" colspan="4"><b>Annual Site EUI (kWh/m<sup>2</sup>)</b></td>')
            if(hasattr(self.building, 'recent_annual_electricity_EUI')):
                report_html.write('    <td class="td_border" colspan="4">' + '{:,}'.format(self.building.recent_annual_electricity_EUI) + '</td>')
            else:
                report_html.write('    <td class="td_border" colspan="4">No electricity data</td>')
          #  report_html.write('    <td class="td_border" colspan="4"><b>Annual Site EUI (kWh/m<sup>2</sup>)</b></td>')
            if(hasattr(self.building,'recent_annual_fossil_fuel_EUI')):
                report_html.write('    <td class="td_border" colspan="4">' + '{:,}'.format(self.building.recent_annual_fossil_fuel_EUI) + '</td>')
            else:
                report_html.write('    <td class="td_border" colspan="4">No fossil fuel data</td>')
            report_html.write('  </tr>')
            report_html.write('    </table>')
            report_html.write('<p style="margin:0px;">&nbsp;&nbsp;<i>Note: The annual results are from the most recent 12 months\' input.</i></p>')
            report_html.write('</div>')
            report_html.write('</div>')


            ### Saving Potentials Card
            report_html.write('<br>')
            report_html.write('  <div class="w3-container w3-padding-large w3-white">')
            report_html.write('    <h2 id="about"><b>Saving Potentials</b></h2>')
            report_html.write('    <hr class="w3-opacity">')

            report_html.write('<div class="w3-container w3-margin-bottom w3-col m12 w3-padding-small">')
            report_html.write('<div class="w3-container ">')
            # Savings plots start
            # Savings plot row 1 -- saving numbers and target
            report_html.write('<div class="w3-cell-row">')
            # Col 1 -- Saving numbers
            report_html.write('<div class="w3-container w3-cell w3-hover-indigo w3-mobile">')
            report_html.write('<p class="w3-xlarge">    Target Selection: ' + self.building.saving_target_str + '</p>')
            report_html.write('<p class="w3-xlarge">    Potential Cost Savings: </p><p class="number">' + self.currency_str + " {:,}".format(
                int(self.building.total_cost_savings)) + '</p>')
            report_html.write('<p class="w3-xlarge">    Potential Percent Savings: </p><p class = "number">' + "{:,}".format(
                self.building.total_energy_savings_pct) + '%</p>')
            report_html.write('</div>')
            # Col 2 -- EE recommendations
            report_html.write('<div class="w3-container w3-hover-indigo w3-cell w3-mobile">')
            report_html.write('<h5><b>Energy Efficiency Recommendations</b></h5>')
            report_html.write('<ul>')
            for i in range(len(self.building.FIM_list)):
                report_html.write('<li>' + self.building.FIM_list[i] + '</li>')
            report_html.write('</ul>')
            report_html.write(
                '<a href="#EE" onclick="w3_close()" class="w3-bar-item w3-button w3-padding"><i class="fa fa-th-large fa-info w3-margin-right"></i>Details</a> ')
            report_html.write('</div>')
            report_html.write('</div><hr>')
            # Savings plot row 2 -- stacked bar chart and pie chart
            report_html.write('''
                  <div class="w3-row">
                      <div class="w3-half">
                      <p  class="w3-center"> <b> Utility Cost Breakdown (Thousands'''+ self.currency_str +''') </b> </p>
                          <canvas id="disag" style="height:500px"></canvas>
                      </div>
                      <div  class="w3-half">
                      <p  class="w3-center"><b> Utility Cost Savings ('''+ self.currency_str +''') </b></p>
                          <canvas id="saving_pie_chart" style="height:500px"></canvas>
                      </div>
                  </div>''')
            report_html.write(self.saving_bar_str)
            report_html.write(self.saving_pie_str)
            report_html.write('<div class="w3-container w3-content">')
            report_html.write('<hr><button class="w3-button w3-border w3-hover-grey" onclick="showTrends()">Show/Hide original and predicted consumption with upgrade</button>')
            report_html.write('</div>')
            # Savings plot row 3 -- hidden saving trend charts
            report_html.write('<div class="w3-cell-row" id="trend_plot" style = "display:none">')
            #report_html.write('<div class="w3-container w3-cell w3-mobile">')
            report_html.write('''
                <div id="trend_plot" class = "w3-row-padding">
                      <div class ="w3-half">
                            <canvas id="consumption_e"></canvas>
                      </div>
                      <div class="w3-half">
                            <canvas id="consumption_f"></canvas>
                      </div>
                </div>''')
            if(hasattr(self.building, 'energy_savings_fig_e')):
                report_html.write(self.building.energy_savings_fig_e)
            else:
                report_html.write('<p>No electricity data</p>')
            if(hasattr(self.building, 'energy_savings_fig_f')):
                report_html.write(self.building.energy_savings_fig_f)
            else:
                report_html.write('<p>No fossil fuel data</p>')
            report_html.write('</div>')
            report_html.write('</div>')
            # Savings plots end
            report_html.write('</div>')
            # EE recommendations brief
            report_html.write('<div class="w3-container w3-margin-bottom w3-padding-small">')
            report_html.write('</div>')
            report_html.write('</div>')
            report_html.write('<br>')


            ### Weather Sensitivity and Benchmarks Card
            report_html.write('  <div class="w3-container w3-padding-large w3-white" id="about">')
            report_html.write('    <h2 id="benchmark"><b>Weather Sensitivity and Benchmarks</b></h2>')
            report_html.write('    <hr class="w3-opacity">')
            report_html.write(
                "Daily electricity and fossil fuel  use per floor area is plotted below against monthly average outdoor air temperature. When energy use goes up at low temperatures on the left side of the graph, it represents heating energy. When energy use goes up at high temperatures on the right side of the graph, it represents cooling energy. The flat part of the graph shows the buidling's base load.")
            report_html.write('    <hr>')

            # Electricity model and benchmarking
            report_html.write('<div class="w3-row">')
            if(hasattr(self.building,'im_electricity') and hasattr(self.building.im_electricity, 'model_description_html')):
                report_html.write(self.building.im_electricity.model_description_html)
            report_html.write('</div>')
            report_html.write('<div class="w3-row">')
            report_html.write('  <div class="w3-half w3-container w3-margin-bottom w3-col m5 w3-padding-small">')
            report_html.write('    <div class="w3-container ">')
            report_html.write('      <p><b>Electricity Change-point Model</b></p>')
            if (hasattr(self.building, 'im_electricity') and hasattr(self.building.im_electricity, 'model_description_html')):
                # report_html.write(self.building.im_electricity.fig_html)
                report_html.write('<div class="graph_container"> ')
                report_html.write('<canvas id="e_model" style="height:240px;"></canvas>')
                report_html.write('</div>')
                report_html.write(self.building.im_electricity.model_chart_html)

            else:
                report_html.write(
                    '<p>No electricity consumption data is provided or no significant change-point model for electricity was found.</p>')
            report_html.write('    </div>')
            report_html.write('  </div>')
            report_html.write('<div class="w3-half w3-container w3-margin-bottom w3-col m7 w3-padding-small">')
            #report_html.write('<div class="w3-container ">')
            report_html.write('<p><b>Electricity Consumption Benchmarking</b></p>')
            report_html.write(self.building.benchmarking_bar_base_e_html)
            report_html.write(self.building.benchmarking_bar_hsl_e_html)
            report_html.write(self.building.benchmarking_bar_hcp_e_html)
            report_html.write(self.building.benchmarking_bar_csl_e_html)
            report_html.write(self.building.benchmarking_bar_ccp_e_html)
            report_html.write('<p><i>Note: % indicate the percentage of buildings your building is superior to.</i></p>')
            report_html.write(
                 '<a href="#IMT" onclick="w3_close()" class="w3-bar-item w3-button w3-padding"><i class="fa fa-th-large fa-info w3-margin-right"></i>Details</a> ')
            report_html.write('</div>')
            report_html.write('</div>')
            # -->Electricity model and benchmarking end

            report_html.write('<hr>')
            # Fossil fuel model and benchmarking
            report_html.write('<div class="w3-row">')
            if (hasattr(self.building, 'im_fossil_fuel') and hasattr(self.building.im_fossil_fuel, 'model_description_html')):
                report_html.write(self.building.im_fossil_fuel.model_description_html)
            report_html.write('</div>')
            report_html.write('<div class="w3-row">')
            report_html.write('  <div class="w3-half w3-container w3-margin-bottom w3-col m5 w3-padding-small">')
            report_html.write('    <div class="w3-container">')
            report_html.write('      <p><b>Fossil Fuel Change-point Model</b></p>')
            if (hasattr(self.building, 'im_fossil_fuel') and hasattr(self.building.im_fossil_fuel, 'model_description_html')):
                #report_html.write(self.building.im_fossil_fuel.fig_html)
                report_html.write('<div class="graph_container"> ')
                report_html.write('<canvas id="f_model" style="height:240px;"></canvas>')
                report_html.write('</div>')
                report_html.write(self.building.im_fossil_fuel.model_chart_html)

            else:
                report_html.write(
                    '<p>No fossil fuel consumption data is provided or no significant change-point model for fossil fuel was found.</p>')
            report_html.write('    </div>')
            report_html.write('  </div>    ')
            report_html.write('<div class="w3-half w3-container w3-margin-bottom w3-col m7 w3-padding-small">')
            report_html.write('<div class="w3-container">')
            report_html.write('<p><b>Fossil Fuel Consumption Benchmarking</b></p>')
            report_html.write(self.building.benchmarking_bar_base_f_html)
            report_html.write(self.building.benchmarking_bar_hsl_f_html)
            report_html.write(self.building.benchmarking_bar_hcp_f_html)
            report_html.write(self.building.benchmarking_bar_csl_f_html)
            report_html.write(self.building.benchmarking_bar_ccp_f_html)
            report_html.write('<p><i>Note: % indicate the percentage of buildings your building is superior to.</i></p>')
            report_html.write(
                 '<a href="#IMT" onclick="w3_close()" class="w3-bar-item w3-button w3-padding"><i class="fa fa-th-large fa-info w3-margin-right"></i>Details</a> ')
            report_html.write('</div>')
            report_html.write('</div>')
            report_html.write('</div>')
            # -->Fossil fuel model and benchmarking end

            report_html.write('</div>')
            report_html.write('  <br>')

            # Detail EE analysis
            report_html.write('  <div class="w3-container w3-padding-large w3-white">')
            report_html.write('    <h2 id="EE"><b>Energy Efficiency Recommendation Details</b></h2>')
            report_html.write('    <p>More details on each energy efficiency opportunity identified </p>')
            FIM_des = {
                "Reduce Equipment Schedules": "Your building equipment load is higher than typical. Equipment and systems within any building should operate using a schedule. Check equipment schedule and if equipment is operational during low occupancy times or during reduced building use. Setup a notification to identify when schedules are overridden and are not returned to normal.",
                "Reduce Lighting Load": "Your building lighting load is higher than typical. Lighting load is an ample portion of any building energy consumption. Lighting efficiency and controls have big impact on lighting system performance. Consider upgrading bulbs and fixtures to improve efficiency and check existing (or upgrade to) controls that dim and turn off the lights appropriately. Take advantage of natural daylighting whenever possible. Lights near existing window or skylights can be controlled to dim or turn off for maximum daylight utilization. Renovations to the building envelope and internal space configurations are good opportunity to check lighting system performance. ",
                "Reduce Plug Loads": " Your building plug load is higher than typical. Anything that is plugged into standard electric receptacles or outlets fall under plug load. Personal computers, monitors, printers, coffeemakers, other office/lab/lighting equipment are examples of plug loads. Consider upgrading to more efficient models and operate on a schedule where possible.",
                "Increase Cooling System Efficiency": "Your building cooling load is higher than similar buildings for similar weather conditions. HVAC system performance has big impact on building energy consumption. Check your cooling system, all related equipment and controls to improve system efficiency. Upgrading your system to a more efficient model, will reduce your system energy consumption.",
                "Decrease Heating Setpoints": "Your building heating setpoint is higher than typical buildings. Check the occupied and unoccupied heating setpoint during the heating season. Heating system and auxiliaries’ energy consumption will be reduced by decreasing the heating setpoint.",
                "Decrease Ventilation": "Correct percentage of fresh air into the building is necessary to provide comfortable and safe conditions for building occupants. Reducing the amount of fresh air will reduce the energy used to condition and distribute it. Make sure to understand and follow all related building codes.",
                "Decrease Infiltration": "Infiltration is the uncontrolled outside air that is brought into a building. It adds to the overall building cooling and heating loads. Infiltration is reduced with caulking, weather stripping, and upgrades in envelope components (e.g. windows, doors, air intakes and exhausts).",
                "Increase Heating System Efficiency": "Your building heating load is higher than similar buildings for similar weather conditions. HVAC system performance has big impact on building energy consumption. Check the heating system, related equipment and controls for efficient operations. Upgrading your system to a more efficient model, will reduce your system energy consumption.",
                "Add Wall/Ceiling Insulation": "Heating and cooling loads are reduced by insulating the building walls, ceilings, and foundations. Check current insulation levels and assess opportunities of adding more insulation.",
                "Check Fossil Baseload": "Your building thermal load is higher than typical. Check building thermal baseload (minimum continuous usage) for the building. Poor operating schedules, simultaneous heating and cooling, and faulty heating equipment result in higher baseload.",
                "Upgrade Windows": "Windows have big impact on heating and cooling loads. Poor window insulation is like low insulation wall. Check current windows for U-value.",
                "Eliminate Electric Heating": "Your building electric heating load is higher than typical. Electric heating is expensive and increases heating system energy consumption. Check electric heating system schedules and controls. ",
                "Increase Cooling Setpoints" : "Your building starts cooling at lower temperature than typical. Check the occupied and unoccupied cooling setpoint during the cooling season. Cooling system and auxiliaries’ energy consumption will be reduced by increasing the cooling setpoint ",
                "Add/Fix Economizers":"Utilizing outside air that is cooler and/or drier than indoor air in an economizer can significantly reduce the energy used to cool the building. Check existing economizers, if any, for efficient operations."

            }
            for i in range(len(self.building.FIM_list)):
                report_html.write('<h4>' + self.building.FIM_list[i] + '</h4>')
                report_html.write('<p>' + FIM_des[self.building.FIM_list[i]] + '</p>')

            report_html.write('<p><i>Note: Special thanks to Johnson Controls (JCI) technical team for their valuable technical support and for their algorithm in identifying Energy Efficiency Recommendations.</i></p>')
            report_html.write('    <hr class="w3-opacity">')
            report_html.write('  </div>')
            report_html.write('  <br>')

            report_html.write('  <div class="w3-container w3-padding-large w3-white">')
            report_html.write('    <h2 id="IMT"><b>Understand the Model</b></h2>')
            report_html.write("""
                <h4>Baseload</h4>
                <p>Energy consumption of all non-weather-related equipment like computers and lighting. The lower the baseload, the less the energy consumed in plugs and permanently plugged equipment.</p>

                <h4>Cooling Sensitivity </h4>
                <p>Cooling system energy consumption for each degree increase in outdoor temperature. Low cooling sensitivity results in less energy-consuming cooling system.</p>

                <h4>Cooling change-point</h4>
                <p>The temperature at which cooling system starts. Below the cooling change point, the cooling system is not operational.</p>

                <h4>Heating Sensitivity</h4>
                <p>Heating system consumption of energy for each degree decrease in outdoor temperature. Low heating sensitivity results in less energy-consuming heating system.</p>

                <h4>Heating change-point</h4>
                <p>The temperature at which heating system starts. Above the heating change point, the cooling system is not operational.</p>
                           """)
            report_html.write('    <hr class="w3-opacity">')
            report_html.write('  </div>')
            report_html.write('  <br>')

            # Tool description
            report_html.write('  <div class="w3-container w3-padding-large w3-white">')
            report_html.write('    <h2 id="About"><b>About the Tool</b></h2>')
            report_html.write("  <p><b>What is the Energy Efficiency Targeting Tool?</b></p>")
            report_html.write(
                "  <p>The Energy Efficiency Targeting Tool helps building owners and managers quickly assess potential opportunities for energy savings, to inform decisions on where to target energy efficiency efforts. The tool can identify low and no-cost opportunities that can be implemented immediately, as well as retrofit opportunities that can be investigated further through more detailed audits or studies.</p>")
            report_html.write(
                "  <p>The tool uses regresion techniques to analyze a building's monthly energy data and weather, in order to determine how much energy is used for heating, cooling, and baseload (lighting, plug loads, etc.). The performance of the building is then benchmarked against similar building. In addition to telling you whether a building's energy consumption is higher or lower than peers, it goes a step further to tell you why that is the case. If a building's energy use is high compared to peers, for example, it can tell you it is because the heating system is performing poorly, while the cooling system and baseload equipment are typical compared to peers. With this information, a building owner can adjust heating setpoints, add insulation, or perform an energy audit that focuses on heating equipment.</p>")

            report_html.write('    <hr class="w3-opacity">')
            report_html.write('  </div>')
            report_html.write('  <br>')

            report_html.write('  <!-- Footer -->')
            report_html.write('  <footer class="w3-container w3-padding-32 w3-white">')
            report_html.write('  <div class="w3-row-padding">')
            report_html.write('    <div class="w3-half">')
            report_html.write('      <h3>Partners</h3>')
            # report_html.write('      <p>Place holder.</p>')
            report_html.write(self.lbl_logo)
            report_html.write(self.icf_logo)
            report_html.write(self.jci_logo)
            report_html.write('    </div>')
            report_html.write('    <div class="w3-half">')
            report_html.write('      <h3>Links</h3>')
            report_html.write('      <ul class="w3-ul w3-hoverable">')
            report_html.write('        <li class="w3-padding-16">')
            report_html.write('          <span class="w3-large"><a href="https://github.com/LBNL-CERC-BEE/CERC-BEE-Virtual-Energy-Efficiency-Targeting-Tool">GitHub Repository</a></span><br>')
            report_html.write('        </li>')
            report_html.write('      </ul>')
            report_html.write('    </div>')
            report_html.write('  </div>')
            report_html.write('  </footer>')
            report_html.write('  <div class="w3-black w3-center w3-padding-24"></div>')
            report_html.write('</div>')
            report_html.write('<script>')
            report_html.write('function w3_open() {')
            report_html.write('    document.getElementById("mySidebar").style.display = "block";')
            report_html.write('    document.getElementById("myOverlay").style.display = "block";')
            report_html.write('}')
            report_html.write('function w3_close() {')
            report_html.write('    document.getElementById("mySidebar").style.display = "none";')
            report_html.write('    document.getElementById("myOverlay").style.display = "none";')
            report_html.write('}')

            # Show/hide trends
            report_html.write('function showTrends() {')
            report_html.write('    var x = document.getElementById("trend_plot");')
            report_html.write('    if (x.style.display === "none") {')
            report_html.write('        x.style.display = "block";')
            report_html.write('    } else {')
            report_html.write('        x.style.display = "none";')
            report_html.write('    }')
            report_html.write('}')

            report_html.write('</script>')
            report_html.write('</body>')
            report_html.write('</html>')
        return(report_file)

    def logo(self):
        self.cerc_logo = '<a href="https://cercbee.lbl.gov/"><img src="https://cercbee.lbl.gov/sites/default/files/styles/max_image/public/images/cerc_logo.jpg?itok=HE_BbWn3" style="height:220px;"></a>'
        self.lbl_logo = '<a href="https://www.lbl.gov/"><img src="https://creative.lbl.gov/wp-content/uploads/sites/23/2015/05/Berkeley_Lab_Logo_Large.png" style="height:100px;"></a>'
        self.icf_logo = '<a href="https://www.icf.com/"><img src="https://upload.wikimedia.org/wikipedia/commons/2/29/ICF_International_logo.png" style="height:100px;"></a>'
        self.jci_logo = '<a href="https://www.johnsoncontrols.com/"><img src="https://upload.wikimedia.org/wikipedia/en/thumb/0/0f/Johnson_Controls.svg/250px-Johnson_Controls.svg.png" style="height:100px;"></a>'


    def charts_js(self):
        # Horizontal bar chart
        self.saving_bar_str = '''
            <script>
                var barOptions_stacked = {
                    responsive: true,
                    legend: {
                    position: "bottom"
                    },

                    tooltips: {
                        enabled: true,
                        callbacks: {
                            label: function(tooltipItem, data) {
                                return Math.round(tooltipItem.xLabel).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")+" '''+ self.currency_str +'''"
                            },
                        }
                    },
                    hover :{
                        animationDuration:0
                    },
                    scales: {
                        xAxes: [{
                            ticks: {
                                callback: function (value) {
                                    return (value/1000.).toLocaleString()+" "
                                },
                                beginAtZero:true,
                                fontFamily: "sans-serif",
                                fontSize:16
                            },
                            scaleLabel:{
                                display:false
                            },
                            gridLines: {},
                            stacked: true
                        }],
                        yAxes: [{
                            gridLines: {
                                display:false,
                                color: "#fff",
                                zeroLineColor: "#fff",
                                zeroLineWidth: 1
                            },
                            ticks: {
                                fontFamily: "sans-serif",
                                fontSize:16
                            },
                            stacked: true
                        }],
                        legend:{
                            display:true
                        },
                        animation: {},
                        pointLabelFontFamily : "Quadon Extra Bold",
                        scaleFontFamily : "Quadon Extra Bold",
                    }}
                var ctx = document.getElementById("disag");
                var myChart = new Chart(ctx, {
                    type: 'horizontalBar',
                    data: {
                        labels: ["Your Building", "Typical Building", "Goal"],
                        datasets: [
                            {
                                label: "Cooling",
                                data: ['''+str(self.building.cooling_old_cost)+''', '''+str(self.building.cooling_typical_cost)+''', '''+str(self.building.cooling_new_cost)+'''],
                                backgroundColor: "rgba(31,78,121,1)",
                                hoverBackgroundColor: "rgba(21,68,111,1)"
                            },
                            {
                                label: "Baseload",
                                data: ['''+str(self.building.base_old_cost)+''', '''+str(self.building.base_typical_cost)+''', '''+str(self.building.base_new_cost)+'''],
                                backgroundColor: "rgba(127,127,127,1)",
                                hoverBackgroundColor: "rgba(117,117,117,1)"
                            },
                            {
                                label: "Heating",
                                data: ['''+str(self.building.heating_old_cost)+''', '''+str(self.building.heating_typical_cost)+''', '''+str(self.building.heating_new_cost)+'''],
                                backgroundColor: "rgba(192,0,0,1)",
                                hoverBackgroundColor: "rgba(182,0,0,1)"
                            }
                        ]
                    },
                    options: barOptions_stacked,
                });
            </script>
        '''

        self.saving_pie_str = '''
            <script>
                var ctx = document.getElementById("saving_pie_chart");
                var myChart = new Chart(ctx, {
                    type: "doughnut",
                    data: {
                      labels: ["Cooling", "Baseload", "Heating"],
                      datasets: [
                      {
                          label: "Utility Cost Savings ('''+ self.currency_str +''')",
                          backgroundColor: ["rgba(31,78,121,1)", "rgba(127,127,127,1)", "rgba(192,0,0,1)"],
                          data: ['''+str(self.building.cooling_old_cost - self.building.cooling_new_cost)+''',
                                 '''+str(self.building.base_old_cost - self.building.base_new_cost)+''',
                                 '''+str(self.building.heating_old_cost - self.building.heating_new_cost)+''']
                      }
                      ]
                  },
                  options: {
                      legend: {
                         position: "bottom"
                          },

                    tooltips: {
                      callbacks: {
                        label: function(tooltipItem, data) {
                            var dataset = data.datasets[tooltipItem.datasetIndex];
                            var meta = dataset._meta[Object.keys(dataset._meta)[0]];
                            var total = meta.total;
                            var currentValue = Math.round(data.datasets[0].data[tooltipItem.index]).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")+' '''+ self.currency_str +'''';
                            var percentage = parseFloat((dataset.data[tooltipItem.index]/total*100).toFixed(1));
                            return currentValue + ' (' + percentage + '%)';
                        },
                    },
                    responsive: true,
                    enabled: true
                },

            }
            });
            </script>
        '''

        # print(self.saving_pie_str)


    @staticmethod
    def add_3d_scatter_trace(name, v_x, v_y, v_z, info, v_s, c_str):
        import math
    
        print(v_x)
        print(v_y)

        # Sanitize data
        v_x = ['null' if isinstance(x, str) else x for x in v_x]
        v_y = ['null' if isinstance(x, str) else x for x in v_y]
        v_z = ['null' if isinstance(x, str) else x for x in v_z]
        v_s = ['null' if isinstance(x, str) else x for x in v_s]
    
        trace_str = ''
        trace_str = '''
            {{
                "name": "Building in {}",
                "type": "scatter3d", 
                "x": {}, 
                "y": {}, 
                "z": {}, 
                "mode": "markers", 
                "text": "{}",
                "marker": {{
                    "autocolorscale": true, 
                    "sizeref": 0.8, 
                    "size": {}, 
                    "color": "{}", 
                    "line": {{
                        "color": "rgba(186, 63, 63, 0.9)", 
                        "width": 0.5 
                    }}, 
                    "opacity": 0.9 
                }}
            }}
        '''.format(name, list(v_x), list(v_y), list(v_z), info, list(v_s), c_str)
        trace_str += ','
        return (trace_str)


    @staticmethod
    def add_2d_scatter_trace(name, v_x, v_y, v_info, v_s, c_str):
        import math

        # Sanitize data
        v_x = ['null' if isinstance(x, str) else x for x in v_x]
        v_y = ['null' if isinstance(x, str) else x for x in v_y]
        v_s = ['null' if isinstance(x, str) else x for x in v_s]

        # Scale the bubble size
        v_s = [(x + 20)/1.5 for x in v_s]
    
        trace_str = ''
        trace_str = '''
            {{
                "type": "scatter",
                "name": "Building in {}",
                "x": {}, 
                "y": {}, 
                "mode": "markers", 
                "text": "{}",
                "marker": {{
                    "autocolorscale": true, 
                    "sizeref": 0.8, 
                    "size": {}, 
                    "color": "{}", 
                    "line": {{
                        "width": 2 
                    }}, 
                    "opacity": 0.9 
                }}
            }}
        '''.format(name, list(v_x), list(v_y), v_info, list(v_s), c_str)
        trace_str += ','
        return (trace_str)


    @staticmethod
    def add_2d_scatter_plot(df_summary):
        div_id = str(datetime.datetime.now())

        print(div_id)
        locations = df_summary['Building Address'].unique()
        scatter_html = ''
        scatter_html += '''
            <div id="'''+div_id+'''" style="height: 100%; width: 100%;" class="plotly-graph-div"></div>
            <script type="text/javascript">
            window.PLOTLYENV = window.PLOTLYENV || {};
            window.PLOTLYENV.BASE_URL = "https://plot.ly";
            Plotly.newPlot("'''+div_id+'''", ['''
        v_rgb_str = np.random.choice(Constants.rgb_color_strs, replace=False)
        for i, location in enumerate(locations):
            df_temp = df_summary.loc[df_summary['Building Address']==location]
            v_x = df_temp['Building Annual Electricity EUI (kWh/m2)']
            v_y = df_temp['Building Annual Fossil Fuel EUI (kWh/m2)']
            v_z = df_temp['Building Annual Energy Cost Savings']
            v_s = df_temp['Building Annual Energy Saving (%)']
            v_info = 'Description'

            c_str = v_rgb_str[i]
            # scatter_html +=  '\n' + self.add_3d_scatter_trace(location, v_x, v_y, v_z, info, v_s, c_str)
            scatter_html +=  '\n' + Report.add_2d_scatter_trace(location, v_x, v_y, v_info, v_s, c_str)
        scatter_html += '''
            ],
            {
              "title": "Building Saving Opportunities",
              "hovermode": "closest",
              "height": 1000,
              "xaxis": { "title": "Building Annual Electricity EUI (kWh/m2)", "ticklen": 5, "gridwidth": 2 },
              "yaxis": { "title": "Building Annual Fossil Fuel EUI (kWh/m2)", "ticklen": 5, "gridwidth": 2 },
              "legend": { "x": 0, "y": 1, "orientation": "h" },
              "showlegend": true
            },
            {
              "showLink": true,
              "linkText": "Export to plot.ly"
            }
            )
    
            </script>
            <script type="text/javascript">
            window.addEventListener("resize", function() { Plotly.Plots.resize(document.getElementById("'''+div_id+'''")); });
            </script>
        '''
    
        return (scatter_html)


    def generate_portfolio_report(self, report_path):
        report_file = report_path + str(self.portfolio.name) + '_report.html'
        with open(report_file, 'w', encoding="utf-8") as report_html:
            report_html.write('<!DOCTYPE html>')
            report_html.write('<html>')
            report_html.write('<title>Energy Efficiency Targeting Tool Building Report</title>')
            report_html.write(self.html_basic())

            report_html.write('<body class="w3-light-grey w3-content" style="max-width:1500px">')

            # Navigation bar
            report_html.write(self.navigation_bar())

            # Portfolio overview card
            report_html.write('''
            <div class="w3-container w3-padding-large w3-white"> <h2 id="overview"><b>Portfolio Summary</b></h2>
                <hr class="w3-opacity">
                <div class="w3-container w3-margin-bottom w3-padding-small">
                    <table class="w3-table w3-bordered w3-border">
                        <tr>
                            <td width="50%" class="td_border" colspan="3"><b>Portfolio Name</b></td>
                            <td width="50%" class="td_border" colspan="3">''' + self.portfolio.name + '''</td>
                        </tr>
                        <tr>
                            <td width="50%" class="td_border" colspan="3"><b>Number of Buildings</b></td>
                            <td width="50%" class="td_border" colspan="3">''' + '{:,}'.format(self.portfolio.n_buildings) + '''</td>
                        </tr>
                        <tr>
                            <td width="50%" class="td_border" colspan="3"><b>Total Building Area (m<sup>2</sup>)</b></td>
                            <td width="50%" class="td_border" colspan="3">''' + '{:,}'.format(self.portfolio.total_area) + '''</td>
                        </tr>
                        <tr>
                            <td width="50%" class="td_border" colspan="3"><b>Total Building Area (m<sup>2</sup>)</b></td>
                            <td width="50%" class="td_border" colspan="3">''' + '{:,}'.format(self.portfolio.total_area) + '''</td>
                        </tr>
                    </table> <br>
                    <table class="w3-table w3-bordered w3-border" style="width:95% border: solid 1 px blue">
                        <tr>
                            <td width="50%" class="td_border" colspan="4"></td>
                            <td width="25%" class="td_border" colspan="4"><b>Electricity</b></td>
                            <td width="25%" class="td_border" colspan="4"><b>Fossil Fuel</b></td>
                        </tr>
                        <tr>
                            <td width="50%" class="td_border" colspan="4"><b>Portfolio Annual Consumption (kWh)</b></td>
                            <td width="25%" class="td_border" colspan="4">''' + '{:,}'.format(self.portfolio.total_annual_consumption_e) + '''</td>
                            <td width="25%" class="td_border" colspan="4">''' + '{:,}'.format(self.portfolio.total_annual_consumption_f) + '''</td>
                        </tr>
                        <tr>
                            <td width="50%" class="td_border" colspan="4"><b>Portfolio Annual Cost (¥)</b></td>
                            <td width="25%" class="td_border" colspan="4">''' + '{:,}'.format(self.portfolio.total_annual_cost_e) + '''</td>
                            <td width="25%" class="td_border" colspan="4">''' + '{:,}'.format(self.portfolio.total_annual_cost_f) + '''</td>
                        </tr>
                        <tr>
                            <td width="50%" class="td_border" colspan="4"><b>Portfolio Average Annual Site EUI (kWh/m<sup>2</sup>)</b></td>
                            <td width="25%" class="td_border" colspan="4">''' + '{:,}'.format(self.portfolio.portfolio_eui_e) + '''</td>
                            <td width="25%" class="td_border" colspan="4">''' + '{:,}'.format(self.portfolio.portfolio_eui_f) + '''</td>
                        </tr>
                    </table>
                    <p style="margin:0px;">&nbsp;&nbsp;<i>Note: The annual results are from the most recent 12 months' input.</i></p>
                </div>
            </div><br>
            ''')


            # Portfolio summary charts card


            scatter_html = self.add_2d_scatter_plot(self.portfolio.df_bldg_summary)

            report_html.write('''
            <div class="w3-container w3-padding-large w3-white"> <h2 id="about"><b>Benchmarking</b></h2>
                <hr class="w3-opacity">
                <div class="w3-container w3-margin-bottom w3-col m12 w3-padding-small">
                    <div class="w3-container ">

                        ''' + 'Coming soon' + '''
                        ''' + scatter_html + '''
                    </div>
                </div>
                <div class="w3-container w3-margin-bottom w3-padding-small"></div>
            </div><br>
            ''')


            # Building details table card
            tbstr = ''
            tbstr += '<table border="1" class="dataframe w3-table w3-bordered w3-border tablesorter" id="myTable"">\n'
            tbstr += '    <thead>\n'
            tbstr += '      <tr style=" text-align: right;">\n'
            for col_name in self.portfolio.df_bldg_summary.columns:
                if col_name != 'Detail Report': tbstr += '          <th>' + col_name + '</th>\n'
            tbstr += '      </tr>\n'
            tbstr += '    </thead>\n'
            tbstr += '    <tbody>\n'
            for n in range(0, len(self.portfolio.df_bldg_summary.axes[0])):
                tbstr += '        <tr>\n'
                tbstr += '            <td><a href=' + report_path + str(self.portfolio.df_bldg_summary['Detail Report'][n]) + '>' + str(self.portfolio.df_bldg_summary['Building ID'][n]) + '</a></td>\n'
                tbstr += '            <td>' + self.portfolio.df_bldg_summary['Building Name'][n] + '</td>\n'
                tbstr += '            <td>' + self.portfolio.df_bldg_summary['Building Address'][n] + '</td>\n'
                tbstr += '            <td>' + self.format_number(self.portfolio.df_bldg_summary['Building Area'][n]) + '</td>\n'
                tbstr += '            <td>' + self.format_number(self.portfolio.df_bldg_summary['Building Annual Electricity Consumption (kWh)'][n]) + '</td>\n'
                tbstr += '            <td>' + self.format_number(self.portfolio.df_bldg_summary['Building Annual Fossil Fuel Consumption (kWh)'][n]) + '</td>\n'
                tbstr += '            <td>' + self.format_number(self.portfolio.df_bldg_summary['Building Annual Electricity Cost'][n]) + '</td>\n'
                tbstr += '            <td>' + self.format_number(self.portfolio.df_bldg_summary['Building Annual Fossil Fuel Cost'][n]) + '</td>\n'
                tbstr += '            <td>' + self.format_number(self.portfolio.df_bldg_summary['Building Annual Electricity EUI (kWh/m2)'][n]) + '</td>\n'
                tbstr += '            <td>' + self.format_number(self.portfolio.df_bldg_summary['Building Annual Fossil Fuel EUI (kWh/m2)'][n]) + '</td>\n'
                tbstr += '            <td>' + self.format_number(self.portfolio.df_bldg_summary['Building Annual Energy Cost Savings'][n]) + '</td>\n'
                tbstr += '            <td>' + self.format_number(self.portfolio.df_bldg_summary['Building Annual Energy Saving (%)'][n]) + '</td>\n'
                tbstr += '        </tr>\n'
            tbstr += '    </tbody>\n'
            tbstr += '</table>\n'
            report_html.write('''
            <div class="w3-container w3-padding-large w3-white"> <h2 id="about"><b>Building Details</b></h2>
                <hr class="w3-opacity">
                <div class="w3-container w3-margin-bottom w3-col m12 w3-padding-small">
                    <div class="w3-container ">

                        ''' + tbstr + '''
                    </div>
                </div>
                <div class="w3-container w3-margin-bottom w3-padding-small"></div>
            </div><br>
            ''')


            report_html.write('</body>')

            report_html.write('''
            <script type="text/javascript">
                $(function() {
                    $("#myTable").tablesorter();
                });
            </script>
            ''')

            report_html.write('</html>')




        return
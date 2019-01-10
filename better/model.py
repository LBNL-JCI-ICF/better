'''

Energy Efficiency Targeting Tool Copyright (c) 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Intellectual Property Office at  IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department of Energy and the U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit other to do so. 

'''

from scipy import optimize, stats
import numpy as np

from .constants import *


class InverseModel:
    def __init__(self, temperature, eui, energy_type='Energy type unknown', significance_threshold=0.1):

        if (np.size(eui) != np.size(temperature)):
            print("Please make sure eui and temperature arrays have the same length")
        else:
            self.temperature = temperature
            self.eui = eui
            self.energy_type = energy_type
            self.hcp_bound_percentile = 45
            self.ccp_bound_percentile = 55
            percentiles = self.hcp_bound_percentile, self.ccp_bound_percentile
            self.hcp, self.ccp = np.percentile(self.temperature,
                                               percentiles)  # Set initial boundaries for change-point models
            self.hcp_min = self.hcp  # Heating change-point minimum
            self.hcp_max = self.ccp  # Heating change-point maximum
            self.ccp_min = self.hcp  # Cooling change-point minimum
            self.ccp_max = self.ccp  # Cooling change-point minimum
            self.base_min = 0  # Baseload minimum
            self.base_max = np.inf  # Baseload maximum
            self.hsl_min = -np.inf  # Heating slope minimum
            self.hsl_max = 0  # Heating slope maximum
            self.csl_min = 0  # Cooling slope minimum
            self.csl_max = np.inf  # Cooling slope maximum
            self.significance_threshold = significance_threshold
            self.hsl_insignificant = False  # assume significant heating slope
            self.csl_insignificant = False  # assume significant cooling slope
            self.best_model = None

    @staticmethod
    def piecewise_linear(x, hcp, ccp, base, hsl, csl):
        #  k1  \              / k2
        #       \            /
        # y0     \__________/
        #        cpL      cpR

        # Handle 3P models when use this function to predict.
        if np.isnan(hcp) and np.isnan(hsl):
            hcp = ccp
            hsl = 0
        if np.isnan(csl) and np.isnan(csl):
            ccp = hcp
            csl = 0

        conds = [x < hcp, (x >= hcp) & (x <= ccp), x > ccp]

        funcs = [lambda x: hsl * x + base - hsl * hcp,
                 lambda x: base,
                 lambda x: csl * x + base - csl * ccp]

        return np.piecewise(x, conds, funcs)

    def rmse(self):
        yp = self.piecewise_linear(self.temperature, *self.p)
        y = self.eui
        return np.sqrt(np.mean([(i - j) ** 2 for i, j in zip(y, yp)]))

    def R_Squared(self, adjusted_r2_calc=False):
        x = self.temperature
        y = self.eui
        residuals = y - self.piecewise_linear(x, *self.p)
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        rsquared = 1 - (ss_res / ss_tot)
        r2_result = rsquared
        n = len(self.eui)
        numP = len(np.nonzero(self.p))
        # If we need to calculate adjusted r-squared
        if (adjusted_r2_calc and n - numP - 1 != 0):
            r2_result = 1 - (1 - rsquared) * (n - 1) / (n - numP - 1)

        self.r2 = r2_result
        return (r2_result)

    def fit(self):
        try:
            self.p, self.e = optimize.curve_fit(
                self.piecewise_linear,
                self.temperature,
                self.eui,
                bounds=([self.hcp_min, self.ccp_min, self.base_min, self.hsl_min, self.csl_min],
                        [self.hcp_max, self.ccp_max, self.base_max, self.hsl_max, self.csl_max]
                        )
            )
            # Model coefficients
            self.hcp, self.ccp, self.base, self.hsl, self.csl = self.p

            # Get p-value from t-stes for the model coefficients
            n = len(self.temperature)
            self.p_base = stats.t.sf(self.base / np.sqrt(np.diag(self.e)[2] / n), df=n - 2)
            self.p_hsl = stats.t.cdf(self.hsl / np.sqrt(np.diag(self.e)[3] / n), df=n - 2)
            self.p_csl = stats.t.sf(self.csl / np.sqrt(np.diag(self.e)[4] / n), df=n - 2)
            # self.p_hcp = stats.t.cdf(abs(self.hcp - self.hcp_min) / np.sqrt(np.diag(self.e)[0]/n), df = n-2)
            # self.p_ccp = stats.t.cdf(abs(self.ccp - self.ccp_max) / np.sqrt(np.diag(self.e)[1]/n), df = n-2)
        except:
            self.has_fit = False


    def optimize_cp_limit(self, point):
        # Finds the optimum range for heating and cooling change-points bounds
        if point == "R":
            percentiles = [[i, i + 5] for i in np.arange(30, 90, 5)]
        else:
            percentiles = [[i, i + 5] for i in np.arange(10, 70, 5)]

        var = []
        # print('optimize cp limits')
        for per in percentiles:
            cp_limit_min, cp_limit_max = np.percentile(self.temperature, per)
            # print('Percentile = {}, search range: {:04.2f} - {:04.2f}, rmse = {:04.3f}'.format( per, cp_limit_min, cp_limit_max, self.rmse()))

            if point == "L":
                self.hcp_min = cp_limit_min  # Heating change-point minimum
                self.hcp_max = cp_limit_max  # Heating change-point maximum
            elif point == "R":
                self.ccp_min = cp_limit_min  # Cooling change-point minimum
                self.ccp_max = cp_limit_max  # Cooling change-point maximum

            self.fit()
            # print(self.p)
            r2 = self.R_Squared()
            # print('P value: base= {:04.3f}, left= {:04.3f}, right= {:04.3f}, R2 = {:04.2f} '.format(self.p_base, self.p_hsl, self.p_csl, r2 ))
            var.append(r2)

        optimum_limits = percentiles[var.index(max(var))]
        cp_limit_min, cp_limit_max = np.percentile(self.temperature, optimum_limits)
        if point == "L":
            self.hcp_min = cp_limit_min  # Heating change-point minimum
            self.hcp_max = cp_limit_max  # Heating change-point maximum
        elif point == "R":
            self.ccp_min = cp_limit_min  # Cooling change-point minimum
            self.ccp_max = cp_limit_max  # Cooling change-point maximum

        self.fit()
        return optimum_limits

    def fit_model(self, has_fit=False, threshold=0.1):
        ### Handle outliers (TBD)

        ### Fit change-point model
        self.fit()  # Initial guess
        self.p_init = self.p


        # self.optimize_slopes()
        # self.optimize_cp_limit("L")
        # self.optimize_cp_limit("R")
        # self.optimize_slopes()
        # self.inverse_cp()
        # self.model_type()  # Get model type
        # has_fit = True
        # self.has_fit = has_fit
        # # Save final model coefficients
        # return (has_fit)

        if (self.R_Squared() < threshold):
            print('No fit found')
            # Cannot accept model immediately. No meaningful correlation found.
            return (has_fit)
        else:
            self.optimize_slopes()
            self.optimize_cp_limit("L")
            self.optimize_cp_limit("R")
            self.optimize_slopes()
            self.inverse_cp()
            self.model_type()  # Get model type
            has_fit = True
            self.has_fit = has_fit
            # Save final model coefficients
            return (has_fit)

    def optimize_slopes(self):
        import math
        if (not (self.significant(self.p_hsl)) or math.isnan(self.p_hsl)):
            # print("--->Left slope is not significant! - P=",self.p_hsl)
            self.hsl_min = -10 ** -3
            self.hsl_insignificant = True

        if (not (self.significant(self.p_csl)) or math.isnan(self.p_csl)):
            # print("--->Right slope is not significant!- P=",self.p_csl)
            self.csl_max = 10 ** -3
            self.csl_insignificant = True

        self.fit()

        if self.hsl_insignificant:
            self.hcp = self.ccp
            self.hsl = 0

        if self.csl_insignificant:
            self.ccp = self.hcp
            self.csl = 0

        if self.hsl_insignificant and self.csl_insignificant:
            self.hcp = self.ccp = 0
            self.hsl = self.csl = 0

    def inverse_cp(self):
        if self.hcp > self.ccp and not self.csl_insignificant and not self.hsl_insignificant:
            cp = (self.hsl * self.hcp - self.csl * self.ccp) / (self.hsl - self.csl)
            self.hcp = self.ccp = cp

    def significant(self, x, threshold=0.05):
        sig = True if x < threshold else False
        return sig

    def model_type(self):
        # This function clean up the model parameters and assign model type string
        self.cp_txt = []
        self.R_Squared()
        if (self.hcp is None):
            self.model_type_str = 'No fit'
            self.has_fit = False
            self.coeff_validation = {'base': False, 'csl': False, 'ccp': False, 'hsl': False, 'hcp': False}
        elif (self.hcp == self.ccp and self.hsl == 0):
            self.model_type_str = "3P Cooling"
            self.cp_txt = "(" + str(round(self.ccp, 1)) + ", " + str(round(self.base, 1)) + ")"
            self.hcp = self.ccp
            self.hsl = 0
            # self.hsl, self.hcp = np.nan, np.nan

            self.coeff_validation = {'base': True, 'csl': True, 'ccp': True, 'hsl': False, 'hcp': False}
        elif (self.hcp == self.ccp and self.csl == 0):
            self.model_type_str = "3P Heating"
            self.cp_txt = "(" + str(round(self.hcp, 1)) + ", " + str(round(self.base, 1)) + ")"
            self.ccp = self.hcp
            self.csl = 0
            # self.csl, self.ccp = np.nan, np.nan

            self.coeff_validation = {'base': True, 'csl': False, 'ccp': False, 'hsl': True, 'hcp': True}
        elif (self.hcp == self.ccp and self.csl != 0 and self.hsl != 0):
            self.model_type_str = "4P"
            self.cp_txt = "(" + str(round(self.hcp, 1)) + ", " + str(round(self.base, 1)) + ")"
            self.coeff_validation = {'base': True, 'csl': True, 'ccp': True, 'hsl': True, 'hcp': True}
        elif (self.hcp != self.ccp and self.csl != 0 and self.hsl != 0):
            self.model_type_str = "5P"
            self.cp_txt.append("(" + str(round(self.hcp, 1)) + ", " + str(round(self.base, 1)) + ")")
            self.cp_txt.append("(" + str(round(self.ccp, 1)) + ", " + str(round(self.base, 1)) + ")")
            self.coeff_validation = {'base': True, 'csl': True, 'ccp': True, 'hsl': True, 'hcp': True}
        # Finally assign the model coefficients
        self.coeffs = {'base': self.base, 'csl': self.csl, 'ccp': self.ccp, 'hsl': abs(self.hsl), 'hcp': self.hcp}
        self.model_p = np.array([self.hcp, self.ccp, self.base, self.hsl, self.csl])
        

    def model_lines(self,mts,x,y):
        if mts == "3P Cooling":
            return """{
                    label: 'Cooling',
                    data:""" + str([{"x:{:.2f}".format(x[i]),"y:{:.2f}".format(y[i])} for i in range(2,4) ]).replace("'","") + """,
                    showLine: true,
                    lineTension: 1,
                    pointRadius: 1,
                    fill: false,
                    borderColor: 'rgba(31,78,121,1)',
                    backgroundColor: 'rgba(31,78,121,1)' 
                    },
                  {
                    label: 'Baseload',
                    data:""" + str([{"x:{:.2f}".format(x[i]),"y:{:.2f}".format(y[i])} for i in range(0,2) ]).replace("'","") + """,
                    showLine: true,
                    lineTension: 0,
                    pointRadius: 0,
                    fill: false,
                    borderColor: 'rgba(127, 127, 127, 1)',
                    backgroundColor: 'rgba(127, 127, 127, 1)'
                    }"""
        elif mts == "3P Heating":
            return """{
                    label: 'Heating',
                    data:""" + str([{"x:{:.2f}".format(x[i]),"y:{:.2f}".format(y[i])} for i in range(0,2) ]).replace("'","") + """,
                    showLine: true,
                    lineTension: 0,
                    pointRadius: 0,
                    fill: false,
                    borderColor: 'rgba(192,0,0,1)',
                    backgroundColor: 'rgba(192,0,0,1)'
                    },
                  {
                    label: 'Baseload',
                    data:""" + str([{"x:{:.2f}".format(x[i]),"y:{:.2f}".format(y[i])} for i in range(2,4) ]).replace("'","") + """,
                    showLine: true,
                    lineTension: 0,
                    pointRadius: 0,
                    fill: false,
                    borderColor: 'rgba(127, 127, 127, 1)',
                    backgroundColor: 'rgba(127, 127, 127, 1)'
                    }"""
        else :
            return """{
                    label: 'Heating',
                    data:""" + str([{"x:{:.2f}".format(x[i]),"y:{:.2f}".format(y[i])} for i in range(0,2) ]).replace("'","") + """,
                    showLine: true,
                    lineTension: 0,
                    pointRadius: 0,
                    fill: false,
                    borderColor: 'rgba(192,0,0,1)',
                    backgroundColor: 'rgba(192,0,0,1)'
                    },
                  {
                    label: 'Cooling',
                    data:""" + str([{"x:{:.2f}".format(x[i]),"y:{:.2f}".format(y[i])} for i in range(2,4) ]).replace("'","") + """,
                    showLine: true,
                    lineTension: 1,
                    pointRadius: 0,
                    fill: false,
                    borderColor: 'rgba(31,78,121,1)',
                    backgroundColor: 'rgba(31,78,121,1)'
                    },
                  {
                    label: 'Baseload',
                    data:""" + str([{"x:{:.2f}".format(x[i]),"y:{:.2f}".format(y[i])} for i in range(1,3) ]).replace("'","") + """,
                    showLine: true,
                    lineTension: 0,
                    pointRadius: 0,
                    fill: false,
                    borderColor: 'rgba(127, 127, 127, 1)',
                    backgroundColor: 'rgba(127, 127, 127, 1)'
                    }"""
                      

    def plot_IM(self, building):
        self.describe_model_html(building)
        x = [min(self.temperature) - 1, self.hcp, self.ccp, max(self.temperature) + 1]
        y = self.piecewise_linear([min(self.temperature) - 1, self.hcp, self.ccp, max(self.temperature) + 1], *self.p)

        model_type = '"e_model"' if self.energy_type == 'Electricity' else '"f_model"'

        self.model_chart_html = """
            <script>
            var ctx = document.getElementById(""" + model_type + """);
            var myChart = new Chart(ctx, {
              type: 'scatter',
              data: {
                datasets: [
                    
                  {
                    label: 'Data',
                    data: """ + str([{"x:{:.2f}".format(self.temperature[i]),"y:{:.2f}".format(np.array(self.eui)[i])} for i in range(0,len(self.temperature)) ]).replace("'","") +""",
                    showLine: false,
                    fill: false,
                    borderColor: 'rgba(0,0,0,1)',
                    backgroundColor: 'rgba(0,0,0,1)'
                    },""" + self.model_lines(self.model_type_str,x,y) + """ ]
              },
              options: {
          		 maintainAspectRatio: false,
              legend: {
                    position: "bottom"
                    },
              scales: {
                    xAxes: [{
                    ticks: {
                      beginAtZero:true
                    },
                    scaleLabel:{
                            display : true,
                            labelString: "Outside Air Temperature (°C)",
                            },
                    }],
                    yAxes: [{
                    ticks: {
                      beginAtZero:true
                    },
                    scaleLabel:{
                            display : true,
                            labelString: "Energy Intensity (kWh/m²-day)",
                            },
                    }]
                },

                tooltips: {
                  mode: 'index',
                  intersect: false,
                },
                hover: {
                  mode: 'nearest',
                  intersect: true
                },
              }
            });
            </script>"""

    def describe_model_html(self, building):
        model_description_html = ""
        if (self.has_fit):
            model_description_html += '<p>'
            model_description_html += '<b>' + self.energy_type + ':</b> '
            model_description_html += 'Your consistent baseload is ' + str(round(self.base, 1)) + ' kWh/(m<sup>2</sup>*day), or ' + str(round(self.base * 1 * Constants.days_in_year, 1)) + ' kWh/(m<sup>2</sup>*yr) <b>[Baseload]:</b>. '
            if(self.model_type_str != '3P Heating'):
                model_description_html += 'The building is in cooling mode when the outside air temperature is above ' + str(round(self.ccp, 1)) + ' &#176;C <b>[Cooling Change Point]</b>. '
                model_description_html += 'During cooling, the building daily energy consumption increases by ' + str(round(building.bldg_area * self.csl, 1)) + ' kWh/day for each 1 degree increase in outside air temperature <b>[Cooling Sensitivity]</b>. '
            if(self.model_type_str != '3P Cooling'):
                model_description_html += 'The building is in heating mode when the outside air temperature is below ' + str(round(self.hcp, 1)) + ' &#176;C <b>[Heating Start Point]</b>. '
                model_description_html += 'During heating, the building daily energy consumption increases by ' + str(round(abs(building.bldg_area * self.hsl), 1)) + ' kWh/day for each 1 degree decrease in outside air temperature <b>[Heating Sensitivity]</b>.'
            model_description_html += '</p>'
        else:
            model_description_html = ''
        self.model_description_html = model_description_html

    def print_IM(self):
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("Final Model:")
        print("    Model Type: " + self.model_type_str)
        print("    Base load: %s" % self.base)
        print("    Heating slope: %s" % self.hsl)
        print("    Heating change-point: %s" % self.hcp)
        print("    Cooling slope: %s" % self.csl)
        print("    Cooling change-point: %s" % self.ccp)
        print("    R-sqaured: %s" % self.R_Squared())
        print(
            '    P value: base= {:04.3f}, left= {:04.3f}, right= {:04.3f}'.format(self.p_base, self.p_hsl, self.p_csl))
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

'''

Energy Efficiency Targeting Tool Copyright (c) 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Intellectual Property Office at  IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department of Energy and the U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit other to do so. 

'''

import pandas as pd
import numpy as np
import copy

from better import constants


# Modified by Han Li on 2018-7-31 for the open source tool
class LEAN_FIMs:
    def __init__(self, df_assessment, utility_type):
        self.df_assessment = copy.deepcopy(df_assessment)
        self.utility_type = utility_type
        self.utility_type_str = 'Electricity' if (utility_type == 1) else 'Fossil Fuel'
        self.base = self.df_assessment.site_coefficients.beta_base
        self.cdd = self.df_assessment.site_coefficients.beta_cdd
        self.betc = self.df_assessment.site_coefficients.beta_betc
        self.hdd = self.df_assessment.site_coefficients.beta_hdd
        self.beth = self.df_assessment.site_coefficients.beta_beth

        # Adapt the model coefficients to the LEAN_FIMs module
        if self.betc == self.beth:
            if self.cdd == 0:
                self.betc, self.cdd  = np.nan, np.nan
            if self.hdd == 0:
                self.beth, self.hdd = np.nan, np.nan

        self.benchmark_medians = self.df_assessment.beta_median
        self.benchmark_stdevs = self.df_assessment.beta_standard_deviation
        self.site_coeffs = [self.base, self.cdd, self.betc, self.hdd, self.beth]

    # self.utility_type: electricity = 1, fossil fuel = 2
    # target_level: conservative = 1, nominal = 2, aggressive = 3
    def set_targets(self, target_level):

        self.n = len(self.site_coeffs)
        self.targets = np.zeros(self.n)

        # print(self.n)
        print('---------------------------------------------------------------')
        print(self.utility_type_str)
        print('Site Coefficients:')
        print(self.site_coeffs)

        if target_level == 1:
            for i in range(0, self.n):
                beta_name = self.df_assessment.index[i]
                if np.isnan(self.site_coeffs[i]):
                    self.targets[i] = np.nan
                elif beta_name == 'beta_betc':
                    self.targets[i] = max(self.benchmark_medians[i] - self.benchmark_stdevs[i], self.site_coeffs[i])
                else:
                    self.targets[i] = min(self.benchmark_medians[i] + self.benchmark_stdevs[i], self.site_coeffs[i])

        elif target_level == 2:
            for i in range(0, self.n):
                beta_name = self.df_assessment.index[i]
                if np.isnan(self.site_coeffs[i]):
                    self.targets[i] = np.nan
                else:
                    if beta_name == 'beta_betc':
                        self.targets[i] = max(self.benchmark_medians[i], self.site_coeffs[i])
                    else:
                        self.targets[i] = min(self.benchmark_medians[i], self.site_coeffs[i])

        elif target_level == 3:
            for i in range(0, self.n):
                beta_name = self.df_assessment.index[i]
                if np.isnan(self.site_coeffs[i]):
                    self.targets[i] = np.nan
                else:
                    if beta_name == 'beta_betc':
                        self.targets[i] = max(self.benchmark_medians[i] + (0.5 * self.benchmark_stdevs[i]), self.site_coeffs[i])
                    else:
                        self.targets[i] = min(self.benchmark_medians[i] - (0.5 * self.benchmark_stdevs[i]), self.site_coeffs[i])

        self.base_targ = self.targets[0]
        self.cdd_targ = self.targets[1]
        self.betc_targ = self.targets[2]
        self.hdd_targ = self.targets[3]
        self.beth_targ = self.targets[4]

        print('Target Coefficients:')
        print(self.targets)
        print('---------------------------------------------------------------')

    def FIM_recommendations(self, save_file=True):
        column = ['FIM Recommendations']
        rows = ['Increase Cooling Setpoints', 'Decrease Heating Setpoints',
                'Reduce Equipment Schedules', 'Decrease Ventilation',
                'Eliminate Electric Heating', 'Decrease Infiltration',
                'Reduce Lighting Load', 'Reduce Plug Loads', 'Add/Fix Economizers',
                'Increase Cooling System Efficiency',
                'Increase Heating System Efficiency', 'Add Wall/Ceiling Insulation',
                'Upgrade Windows', 'Check Fossil Baseload']
        self.FIM_table = pd.DataFrame(index=rows, columns=column)

        ovrd_thres = 1
        ovrd_val = 0.001

        # Increase Cooling Setpoint (indicated by low betc)
        setpoint_recommendation = False  # used for scheduling measure
        if ovrd_thres:
            threshold = ovrd_val
        else:
            threshold = 0.2
        if (self.betc_targ - self.betc) >= (threshold * self.betc_targ):
            self.FIM_table.loc['Increase Cooling Setpoints'] = 'X'
            setpoint_recommendation = True

        # Decrease Heating Setpoint (indicated by high beth)
        if ovrd_thres:
            threshold = ovrd_val
        else:
            threshold = 0.2
        if (self.beth - self.beth_targ) >= (threshold * self.beth_targ):
            self.FIM_table.loc['Decrease Heating Setpoints'] = 'X'
            setpoint_recommendation = True

        # Tighten Schedules (indicated by high electric baseload)
        """
        9/20/13 - Added logic to also recommend schedules if recommending
        increasing cooling setpoints or decreasing heating setpoints. A
        building's break-even temperature are affected by the average building
        temperatures (i.e., occupied & unoccupied). That means that adjusting
        schedules for switching between an occupied and unoccupied setpoint
        will also change the average building temperatures.
        """
        if ovrd_thres:
            threshold = ovrd_val
        else:
            threshold = 0.001

        if self.utility_type == 1 and self.base > 0 and (self.base - self.base_targ) >= (threshold * self.base_targ):
            self.FIM_table.loc['Reduce Equipment Schedules'] = 'X'
        elif setpoint_recommendation:
            self.FIM_table.loc['Reduce Equipment Schedules'] = 'X'

        # Decrease Ventilation (indicated by two of the following three: high cdd, high hdd, high beth)
        count = 0
        if ovrd_thres:
            threshold = ovrd_val
        else:
            threshold = 0.1
        if self.cdd > 0 and (self.cdd - self.cdd_targ) >= (threshold * self.cdd_targ):
            count = count + 1
        if self.hdd > 0 and (self.hdd - self.hdd_targ) >= (threshold * self.hdd_targ):
            count = count + 1
        if ovrd_thres:
            threshold = ovrd_val
        else:
            threshold = 0.2
        if (self.beth - self.beth_targ) >= (threshold * self.beth_targ):
            count = count + 1
        if count >= 2:
            self.FIM_table.loc['Decrease Ventilation'] = 'X'

        # Eliminate Any Electric Heating
        """
        Before 9/20/2013, electric heating indicated by electric fuel and HDD>0.
        Added threshold to improve diagnostic and reduce mis-diagnosis of electric
        heating. It appears that both electric and fossil heating has beta_hdd's
        around 0.04 kWh/m2 while electric beta_hdd's without electric heating
        are around 0.004 kWh/m2.
        """
        electric_htg_threshold = 0.01
        if self.utility_type == 1 and self.hdd > electric_htg_threshold:
            self.FIM_table.loc['Eliminate Electric Heating'] = 'X'

        # Decrease Infiltration (indicated by two of the following three: high cdd, high hdd, high beth)
        count = 0
        if ovrd_thres:
            threshold = ovrd_val
        else:
            threshold = 0.1
        if self.cdd > 0 and (self.cdd - self.cdd_targ) >= (threshold * self.cdd_targ):
            count = count + 1
        if self.hdd > 0 and (self.hdd - self.hdd_targ) >= (threshold * self.hdd_targ):
            count = count + 1
        if ovrd_thres:
            threshold = ovrd_val
        else:
            threshold = 0.2
        if (self.beth - self.beth_targ) >= (threshold * self.beth_targ):
            count = count + 1
        if count >= 2:
            self.FIM_table.loc['Decrease Infiltration'] = 'X'

        # Reduce Lighting Load (indicated by high baseload)
        if ovrd_thres:
            threshold = ovrd_val
        else:
            threshold = 0.001
        if self.utility_type == 1 and self.base > 0 and (self.base - self.base_targ) >= (threshold * self.base_targ):
            self.FIM_table.loc['Reduce Lighting Load'] = 'X'

        # Reduce Plug Load (indicated by high baseload)
        if ovrd_thres:
            threshold = ovrd_val
        else:
            threshold = 0.001
        if self.utility_type == 1 and self.base > 0 and (self.base - self.base_targ) >= (threshold * self.base_targ):
            self.FIM_table.loc['Reduce Plug Loads'] = 'X'

        # Add/Fix Economizers (indicated by low betc)
        if ovrd_thres:
            threshold = ovrd_val
        else:
            threshold = 0.2
        if (self.betc_targ - self.betc) >= (threshold * self.betc_targ):
            self.FIM_table.loc['Add/Fix Economizers'] = 'X'

        # Increase Cooling Efficiency (indicated by high cdd)
        if ovrd_thres:
            threshold = ovrd_val
        else:
            threshold = 0.1
        if self.cdd > 0 and (self.cdd - self.cdd_targ) >= (threshold * self.cdd_targ):
            self.FIM_table.loc['Increase Cooling System Efficiency'] = 'X'

        # Increase Heating Efficiency (indicated by high hdd)
        if ovrd_thres:
            threshold = ovrd_val
        else:
            threshold = 0.1
        if self.hdd > 0 and (self.hdd - self.hdd_targ) >= (threshold * self.hdd_targ):
            self.FIM_table.loc['Increase Heating System Efficiency'] = 'X'

        # Add Wall/Ceiling Insulation (indicated by two of the following three: high cdd, high hdd, high beth)
        count = 0
        if ovrd_thres:
            threshold = ovrd_val
        else:
            threshold = 0.1
        if self.cdd > 0 and (self.cdd - self.cdd_targ) >= (threshold * self.cdd_targ):
            count = count + 1
        if self.hdd > 0 and (self.hdd - self.hdd_targ) >= (threshold * self.hdd_targ):
            count = count + 1
        if ovrd_thres:
            threshold = ovrd_val
        else:
            threshold = 0.2
        if (self.beth - self.beth_targ) >= (threshold * self.beth_targ):
            count = count + 1
        if count >= 2:
            self.FIM_table.loc['Add Wall/Ceiling Insulation'] = 'X'

        # Upgrade Windows (indicated by all of the following: high cdd, low betc, high hdd)
        count = 0
        if ovrd_thres:
            threshold = ovrd_val
        else:
            threshold = 0.1
        if self.cdd > 0 and (self.cdd - self.cdd_targ) >= (threshold * self.cdd_targ):
            count = count + 1
        if self.hdd > 0 and (self.hdd - self.hdd_targ) >= (threshold * self.hdd_targ):
            count = count + 1
        if ovrd_thres:
            threshold = ovrd_val
        else:
            threshold = 0.2
        if (self.betc_targ - self.betc) >= (threshold * self.betc_targ):
            count = count + 1
        if count == 3:
            self.FIM_table.loc['Upgrade Windows'] = 'X'

        # Check Excessive Fossil Fuel Baseload
        if ovrd_thres:
            threshold = ovrd_val
        else:
            threshold = 0.001
        if self.utility_type == 2 and self.base > 0 and (self.base - self.base_targ) >= (threshold * self.base_targ):
            self.FIM_table.loc['Check Fossil Baseload'] = 'X'
        # if(save_file): self.FIM_table.to_csv(self.utility_type_str + " FIM_recommendations.csv")
        return self.FIM_table

    def savings_coefficients(self, save_file=True):
        columns = ['coefficients', 'original_coefficients', 'savings_coefficients']
        rows = ['beta_base', 'beta_cdd', 'beta_betc', 'beta_hdd', 'beta_beth']
        self.coeff_out = pd.DataFrame(columns=columns)
        for i in range(0, len(rows)):
            self.coeff_out.loc[i, columns[0]] = rows[i]
            self.coeff_out.loc[i, columns[1]] = self.site_coeffs[i]
            if(self.site_coeffs[i] > self.targets[i]):
                if(i==2):
                    self.coeff_out.loc[i, columns[2]] = self.site_coeffs[i]
                else:
                    self.coeff_out.loc[i, columns[2]] = self.targets[i]
            else:
                if(i==2):
                    self.coeff_out.loc[i, columns[2]] = self.targets[i]
                else:
                    self.coeff_out.loc[i, columns[2]] = self.site_coeffs[i]
        self.coeff_out = self.coeff_out.set_index(columns[0])
        # if(save_file): self.coeff_out.to_csv(self.utility_type_str + " Coeffs_out.csv")
        return self.coeff_out

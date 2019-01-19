'''
Energy Efficiency Targeting Tool Copyright (c) 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.
If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Intellectual Property Office at  IPO@lbl.gov.
NOTICE.  This Software was developed under funding from the U.S. Department of Energy and the U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit other to do so.
'''

from demo import *
# Notes:
    # Saving target: 1 ~ conservative, 2 ~ nominal, 3 ~ aggressive
    # Change the building id and saving target for the building you want to analyze
#run_single(bldg_id=16, saving_target=2, cached_weather=False)
    # Uncomment the line below [delete the '#' before run_batch(...)] to run the analysis for buildings between start_id and end_id
run_batch(start_id = 1, end_id = 2, saving_target=2, cached_weather=False, batch_report=True, use_default_benchmark_data=True)
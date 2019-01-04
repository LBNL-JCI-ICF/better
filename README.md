# Copyright

Energy Efficiency Targeting Tool Copyright (c) 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Intellectual Property Office at  IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department of Energy and the U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit other to do so. 


# Energy Efficiency Targeting Tool
The lack of public-access, data-driven tools requiring minimal inputs and short run time to benchmark against peers, quantify energy-/cost-savings, and recommend EE improvements is one of the main barriers to capturing untapped EE opportunities in the United States and globally. To fill the gap, and simultaneously address the need for automated, cost-effective, and standardized EE assessment of large volumes of buildings in U.S. state and municipal benchmarking and disclosure programs, an automated, open-source, virtual building EE targeting tool is being developed by Lawrence Berkeley National Laboratory (LBNL), Johnson Controls and ICF International (ICF). 

The tool requires very simple building data inputs; minimum manual work; and provides fast, “no-cost/no-touch” building EE upgrade targeting (equipment and operations) with an acceptable accuracy. It implements the ASHRAE Inverse Modeling Toolkit (IMT) to find piece-wise linear regression models between building energy consumption (electricity and fossil fuel) and outdoor air temperature. The model coefficients of each individual building are then benchmarked against the coefficients of buildings in the same space type category. Johnson Controls’ LEAN Energy Analysis is used to identify the EE measures for the building. Finally, the potential energy and cost savings are estimated with the EE measures.

The tool is being developed under the U.S. Department of Energy (DOE) U.S.-China Clean Energy Research Center Building Energy Efficiency (CERC-BEE) program.

## Getting Started
The EE Targeting Tool is developed using Python 3.6

### Software Prerequisites
Python 3.6.x - We recommend using Anaconda distribution which bundles most of the required packages. If you'd rather not install Anaconda, you can download Python 3.6 from [here](https://www.python.org/downloads/release/python-360/).

### Data Prerequisites
The EE Targeting Tool source code posted here can provide analysis on a building-by-building basis for any building type in any geographic location as long as the data prerequisites are met for either Option A: Portfolio User or Option B: Single Chinese Hotel User.

#### Option A: Portfolio User Data Requirements

The following data must be input into the Portfolio Data Input Template for at least 30 buildings of an identical type (e.g., hotel, commercial office, residential, data center):
1.	Building Location (zip code)
2.	Gross Floor Area (exclude parking)
3.	Building Primary/Secondary Space Use Type
4.	Calendar Information (required for buildings with unique occupancy patterns that vary on a monthly time scale (e.g., K-12 and higher education))
5.	Monthly Utility Bill Consumption and Cost Data (by fuel type)
    *	Electricity and fossil fuel (if any) consumption and cost 
    *	Minimum of 1 year is required (2-5 years of data is desirable)
    *	For each consumption point, start and end dates (“bill dates”) are required
    *	Consumption units are required (e.g., kWh, therms, etc.)
    *	Cost units are required (e.g., US Dollars)

#### Option B: Single Chinese Hotel User Data Requirements
The following data must be input into the Chinese Hotel Data Input Template for a single Chinese hotel:
1.	Gross Floor Area (exclude parking)
2.	Building Primary/Secondary Space Use Type
3.	Monthly Utility Bill Consumption and Cost Data (by fuel type)
    *	Electricity and fossil fuel (if any) consumption and cost 
    *	Minimum of 1 year is required (2-5 years of data is desirable)
    *	For each consumption point, start and end dates (“bill dates”) are required
    *	Consumption units are required (e.g., kWh, therms, etc.)
    *	Cost units are required (e.g., US Dollars)



### Installation
1. Download and install [Python >=3.5](https://www.python.org/downloads/) 
2. Download the source code:
   * Clone using git
      ```
      git clone https://github.com/LBNL-CERC-BEE/CERC-BEE-Virtual-Energy-Efficiency-Targeting-Tool.git
      ```
   * Clone or download using the browser
     
     <img src="https://developer.servicenow.com/app_store_learnv2_automatingapps_jakarta_app-store_AutomatingAppLogic_AppProperties_Images_Props_CopyForkRepoURL.png" alt text="Clone or Download" width ="250" height ="100" style = "clip: rect(0px,50px,100px,50px)">

3. Install dependencies

## How to Use
1. After downloading/cloning the package, enter building information and utility data in the data/portfolio.xlsx and save the file
2. Set the analysis mode in the ee_targeting/demo.py file, and save it.
  1). Single building: set the target building id.
  2). Portfolio: set the start and end building id.
  3). Set the saving target level.
3. Run the analysis by running the demo.py script. Example:
```
$ python demo.py
```

## Input Data Format
An .XLSX spreadsheet is used in the demonstration. Users can find the example data specification in the portfolio.xlsx file


## Weather Data
Depending on building locations, the tool will decide either to download weather data from NOAA website or use already downloaded weather data. Users can choose wether to download weather data from NOAA, examples are in the demo.py.

## Results
The analysis results can be found in the /outputs folder. As a demonstration, there are two types of output reports - one for single builiding and the other for portfolio. The reports are in static HTML format in the current version.

# Building Efficiency Targeting Tool for Energy Retrofits (BETTER)

## Latest Releases
Download latest release [here](https://github.com/LBNL-JCI-ICF/better/releases/).

## Background
The lack of public-access, data-driven tools requiring minimal inputs and short run time to benchmark against peers, quantify energy/cost savings, and recommend energy efficiency (EE) improvements is one of the main barriers to capturing untapped EE opportunities in the United States and globally. To fill the gap, and simultaneously address the need for automated, cost-effective, and standardized EE assessment of large volumes of buildings in U.S. state and municipal benchmarking and disclosure programs, an automated, open-source, virtual building EE targeting tool is being developed by Lawrence Berkeley National Laboratory (LBNL), Johnson Controls (JCI), and ICF.

The tool requires very simple building data inputs; minimum manual work; and provides fast, “no-cost/no-touch” building EE upgrade targeting (equipment and operations) with an acceptable accuracy. It implements the ASHRAE Inverse Modeling Toolkit (IMT) to find piece-wise linear regression models between building energy consumption (electricity and fossil fuel) and outdoor air temperature. The model coefficients of each individual building are then benchmarked against the coefficients of buildings in the same space type category. Johnson Controls’ LEAN Energy Analysis is used to identify the EE measures for the building. Finally, the potential energy and cost savings are estimated with the EE measures.

The tool is being developed under Cooperative Research and Development Agreement (CRADA) No. FP00007338 between the Regents of the University of California Ernest Orlando Lawrence Berkeley National Laboratory under its U.S. Department of Energy (DOE) Contract No. DE-AC02-05CH11231 and Johnson Controls, Inc., with support from ICF.

## Getting Started


### Software Prerequisites
BETTER is developed using Python 3.6. We recommend using Anaconda to manage Python environments. If you'd rather not install Anaconda, you can download Python 3.6 from [here](https://www.python.org/downloads/).

### Data Requirements

The BETTER source code posted here can provide analysis on a building-by-building and portfolio basis as long as the following data points for at least 30 buildings of an identical type are provided:
1. Building Location (City, State)
2. Gross Floor Area in m<sup>2</sup> (exclude parking)
3. Building Primary/Secondary Space Use Type
4. Monthly Utility Bill Consumption and Cost Data (by fuel type)<br/>
   - Electricity and fossil fuel (if any) consumption and cost<br/>
   - Minimum of 1 year is required (2-5 years of data is desirable)<br/>
   - For each consumption point, start and end dates (“bill dates”) are required<br/>
   - Consumption units are required (e.g., kWh, therms, etc.)<br/>
   - Cost units are required (e.g., US Dollars)<br/>
<br/>

#### Input Data Format
Please note that this tool was initially developed for an international market and therefore the current alpha version uses metric/SI units (such as square meters instead of square feet for building area) for some inputs and outputs. Later releases will focus on the US market and will use imperial units (e.g., square feet).

Sample data for 10 buildings are included in `./data/portfolio.xlsx`. Metadata for each building to be analyzed should be entered in the “Metadata” tab, one row per building. Utility data for all fuel types should be entered on the “Utility” tab. Be sure to double check that the building ID, fuel type, and units are accurate for each utility bill entry, and be sure to save the file as `portfolio.xlsx`. Overwrite the file to suit your needs.

#### Benchmark Statistics
A sample benchmark statistic is provided in `./better/constants.py`. The team is working to create a database of U.S. buildings to allow the benchmarking and analysis of individual buildings.

#### Weather Data
Weather data is downloaded from the [NOAA website](https://governmentshutdown.noaa.gov/?page=gsod.html) for the building location. To use previously downloaded weather data at later runs set `cached_weather` to `False` in `run.py`.

### Installation
1. Download and install [Python >=3.6](https://www.python.org/downloads/)
2. Download the source code from the [latest release](https://github.com/LBNL-JCI-ICF/better/releases/)
3. Extract and navigate to the downloaded release 
3. Install dependencies by running `python setup.py install`

<i>Note: The current release is an alpha version. The tool will be packaged and setup files will be provided in future releases.</i> 

## How to Use
The focus of the development is the building energy benchmarking and EE targeting analytical core but not the user interface. To demonstrate the data input/output and the use of the tool.

### Demo
1. From your cmd or terminal, change your working directory to `./better`
2. Run `python demo.py`. It will run the sample of 10 buildings provided in `./data/portfolio.xslx`
3. Output is stored in `./outputs`

### Run Single Building
1. Change building information and utility data in the `./data/portfolio.xlsx` and save the file
2. Open `./better/run.py` file using a text editor and
   - For a single building: uncomment `run_single()`, set the target building id<br/>
   - For a portfolio: uncomment `run_batch()`, set the start and end building id<br/>
   - Set the saving target level.
3. Run the analysis by running the `python run.py` from your cmd or terminal

## Interpreting Results
The analysis results are in the `./outputs` folder. Single building reports and Portfolio reports.

## Copyright

Energy Efficiency Targeting Tool Copyright (c) 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Intellectual Property Office at  IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department of Energy and the U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit other to do so. 

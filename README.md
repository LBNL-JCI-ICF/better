# Building Efficiency Targeting Tool for Energy Retrofits (BETTER)
The lack of public-access, data-driven tools requiring minimal inputs and short run time to benchmark against peers, quantify energy-/cost-savings, and recommend energy efficiency (EE) improvements is one of the main barriers to capturing untapped EE opportunities in the United States and globally. To fill the gap, and simultaneously address the need for automated, cost-effective, and standardized EE assessment of large volumes of buildings in U.S. state and municipal benchmarking and disclosure programs, an automated, open-source, virtual building EE targeting tool is being developed by Lawrence Berkeley National Laboratory (LBNL), Johnson Controls, and ICF International (ICF).

The tool requires very simple building data inputs; minimum manual work; and provides fast, “no-cost/no-touch” building EE upgrade targeting (equipment and operations) with an acceptable accuracy. It implements the ASHRAE Inverse Modeling Toolkit (IMT) to find piece-wise linear regression models between building energy consumption (electricity and fossil fuel) and outdoor air temperature. The model coefficients of each individual building are then benchmarked against the coefficients of buildings in the same space type category. Johnson Controls’ LEAN Energy Analysis is used to identify the EE measures for the building. Finally, the potential energy and cost savings are estimated with the EE measures.

The tool is being developed under Cooperative Research and Development Agreement (CRADA) No. FP00007338 between the Regents of the University of California Ernest Orlando Lawrence Berkeley National Laboratory under its U.S. Department of Energy (DOE) Contract No. DE-AC02-05CH11231 and Johnson Controls, Inc., with support from ICF International.


## Getting Started
The Virtual Building EE Targeting Tool is developed using Python 3.6

### Software Prerequisites
Python 3.6.x - We recommend using Anaconda to manage Python environments. If you'd rather not install Anaconda, you can download Python 3.6 from [here](https://www.python.org/downloads/).

### Data Prerequisites

The Virtual Building EE Targeting Tool source code posted here can provide analysis on a building-by-building and portfolio basis for any building type in any geographic location as long as the following data points for at least 30 buildings of an identical type are provided:
1. Building Location (zip code)
2. Gross Floor Area (exclude parking)
3. Building Primary/Secondary Space Use Type
4. Calendar Information (required for buildings with unique occupancy patterns that vary on a monthly time scale (e.g., K-12 and higher education))
5. Monthly Utility Bill Consumption and Cost Data (by fuel type)<br/>
  1). Electricity and fossil fuel (if any) consumption and cost<br/>
  2). Minimum of 1 year is required (2-5 years of data is desirable)<br/>
  3). For each consumption point, start and end dates (“bill dates”) are required<br/>
  4). Consumption units are required (e.g., kWh, therms, etc.)<br/>
  5). Cost units are required (e.g., US Dollars)<br/>
<br/>
The team is working to create a database of U.S. buildings to allow the benchmarking and analysis of individual buildings.

### Installation
1. Download and install [Python >=3.6](https://www.python.org/downloads/).
2. Download the source code from the [latest release](https://github.com/LBNL-CERC-BEE/CERC-BEE-Virtual-Energy-Efficiency-Targeting-Tool/releases).
3. Install dependencies with by exectuting the install_dependencies.py script in the source code folder. We recommend using pip 9.0.1 when installing the dependencies.

Note: The current release is an alpha version. The tool will be packaged and setup files will be provided in future releases. 

## How to Use
The focus of the development is the building energy benchmarking and EE targeting analytical core but not the user interface. To demonstrate the data input/output and the use of the tool, a demonstration is provided. Below is a brief guidance of the demo:

1. After downloading the source file, enter building information and utility data in the data/portfolio.xlsx and save the file
2. Set the analysis mode in the ee_targeting/demo.py file, and save it.<br/>
  1). Single building: set the target building id.<br/>
  2). Portfolio: set the start and end building id.<br/>
  3). Set the saving target level.
3. Run the analysis by running the demo.py script. Example:
```
$ python demo.py
```

## Input Data Format
An .XLSX spreadsheet is used in the demonstration. Users can find the example data specification in the portfolio.xlsx file. Users can input the required building data using the .XLSX spreadsheet, or any other format that the tool can read (e.g., CSV file).


## Weather Data
Users can decide either to download weather data from the NOAA website or use already downloaded weather data. By default, the tool download the historical weather data from NOAA.

## Results
The analysis results can be found in the /outputs folder. As a demonstration, there are two types of output reports - one for a single building and the other for a portfolio. The reports are in static HTML format in the current version.

# Copyright

Energy Efficiency Targeting Tool Copyright (c) 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Intellectual Property Office at  IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department of Energy and the U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit other to do so. 

## How to Use
The focus of the development is the building energy benchmarking and energy efficiency targeting analytical core but not the user interface. To demondatrate the data input/output and the use of the tool, a demo.py script is provided. Below is a brief guidance of the demo: 
1. Install python and pip from [here](https://www.python.org/downloads/)
2. Download the [latest release](https://github.com/LBNL-JCI-ICF/better/releases).
3. Open a `cmd` or a `Terminal` window and run 
 ```pip install .```
 4. Make sure `better` is installed by running `better --help`
 5. Run example `better single ` # TODO: create an example
 6. Run your analysis
 
    ##Examples
    Single building: ``` better single --building-id 1 --savings-target 2 --no-cached-weather --portfolio-file PATH/TO/portfolio.xlsx --output-path PATH/TO/output/ ```
    
    Portfolio: ```better portfolio --building-id 2 --to 10 --no-cached-weather --portfolio-file PATH/TO/portfolio.xlsx --output-path PATH/TO/output/```
    *you can use "=" or space e.g --building-id 1 or --building-id=1*
'''

Energy Efficiency Targeting Tool Copyright (c) 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Intellectual Property Office at  IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department of Energy and the U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit other to do so.

'''

from .demo import *
import click

@click.command()
@click.argument('type')
@click.option('--building-id', default=18, required=True, type=int, help="building id as in portfolio.xslx")
@click.option('--to', 'to', type=int, help="range of building to include")
@click.option('--savings-target', default = 2, required=True, type=int, show_default=True, help= "use 1 for conservative, 2 for nominal or 3 for aggressive")
@click.option('--cached-weather/--no-cached-weather', default=True, help="Use cached weather files or not")
@click.option('--portfolio-file', required=True, type=click.Path('rb'), help="file directory e.g.: c:\portfolio.xslx")
@click.option('--output-path', envvar='PATHS', required=True, type=click.Path(), help="output directory e.g.:c:\output\\")

def cli(type, building_id, to, savings_target, cached_weather, portfolio_file, output_path):
    """Run single building or portfolio analysis

Example usage:

    - Use better for a single building:

        $ better single --building-id 1 --savings-target 2 --no-cached-weather --portfolio-file PATH/TO/portfolio.xlsx --output-path PATH/TO/output/

    - Use better for a portfolio of buildings with the default savings target

        $ better portfolio --building-id 2 --to 10 --no-cached-weather --portfolio-file PATH/TO/portfolio.xlsx --output-path PATH/TO/output/
"""
    if type == "single":
        run_single(bldg_id= building_id, saving_target=savings_target, cached_weather=cached_weather, portfolio_path=portfolio_file, report_path=output_path)
    elif type == "portfolio":
        run_batch(start_id=building_id, end_id=to, saving_target=savings_target, cached_weather=cached_weather, batch_report=True, portfolio_path=portfolio_file, report_path=output_path)


# if __name__ == '__main__':
#     cli()
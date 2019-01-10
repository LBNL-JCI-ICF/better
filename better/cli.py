'''

Energy Efficiency Targeting Tool Copyright (c) 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Intellectual Property Office at  IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department of Energy and the U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit other to do so.

'''

from .demo import *
import click
# def run_single(
#     use_default_benchmark_data=True,
#     bldg_id = 1,
#     saving_target = 2,
#     space_type='Hotel_酒店',
#     cached_weather=True,
#     write_fim=True,
#     write_model=True,
#     return_data=False
#     ):
#     print("HOLA")
#
#     def run_batch(
#             start_id,
#             end_id,
#             saving_target=2,
#             cached_weather=True,
#             batch_report=False
#     ):
#
#         print("HOLA2")


@click.command()
@click.argument('type')
@click.option('--building-id', default=18, required=True, type=int, show_default=True, help="sdf")
@click.option('--savings-target', default = 2, required=True, type=int, show_default=True)
@click.option('--cached-weather/--no-cached-weather', default=True)
@click.option('--portfolio-file', required=True, type=click.Path('rb'))
@click.option('--output-path', envvar='PATHS', required=True, type=click.Path())

def cli(type, building_id, savings_target, cached_weather, portfolio_file, output_path):
    """choose between single and portfolio types"""
    if type == "single":
        run_single(bldg_id= building_id, saving_target= savings_target, cached_weather=cached_weather, portfolio_path=portfolio_file, report_path=output_path)
    elif type == "portfolio":
        run_batch(start_id=1, end_id=36, saving_target=2, cached_weather=cached_weather, batch_report=True)


# if __name__ == '__main__':
#     cli()
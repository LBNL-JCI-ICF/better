'''

Energy Efficiency Targeting Tool Copyright (c) 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Intellectual Property Office at  IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department of Energy and the U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit other to do so. 

'''

import pandas as pd
import numpy as np


class Constants:
    # Unit conversions
    M3_to_kWh = 8.816  # m3 of Natural gas
    MWH_to_kWh = 1000
    MJ_to_kWh = 1000 / 3600
    GJ_to_kWh = 1000000 / 3600
    Btu_to_kWh = 0.000293071
    MMBtu_to_kWh = 293.071
    Therms_to_kWh = 29.307
    Decatherms_to_kWh = 293.071

    # Default fuel price
    electricity_unit_price = 0.93  # RMB/kWh
    fossil_fuel_unit_price = 0.32  # RMB/kWh

    # Constants
    earth_radius = 6371  # Radius of earth in kilometers. Use 3959 for miles
    days_in_year = 365
    rgb_color_strs = [
        "rgb(255, 87, 51)",
        "rgb(41, 128, 185)",
        "rgb(34, 153, 84)",
        "rgb(44, 62, 80)",
        "rgb(118, 68, 138)",
        "rgb(241, 196, 15)",
        "rgb(218, 247, 166)",
        "rgb(241, 15, 203)",
        "rgb(5, 249, 71)",
        "rgb(13, 13, 13)",
        "rgb(0, 0, 0)"
    ]

    # Default NOAA weather station lists
    # Weather station in the US
    d_us_weather_station = {
        'station_ID': [	"702700-00489",	"703656-99999",	"703891-99999",	"720168-99999",	"720171-99999",	"720329-99999",	"720331-99999",	"720394-00428",	"720406-00135",	"720417-99999",	"720425-99999",	"720446-99999",	"720449-99999",	"720451-99999",	"720452-99999",	"720464-99999",	"720465-99999",	"720468-00466",	"720472-99999",	"720475-99999",	"720477-99999",	"720478-99999",	"720481-99999",	"720482-99999",	"720483-99999",	"720484-99999",	"720487-99999",	"720488-99999",	"720491-00150",	"720507-99999",	"720508-99999",	"720516-99999",	"720517-24165",	"720518-00449",	"720519-99999",	"720521-00475",	"720522-00443",	"720534-00161",	"720536-99999",	"720551-99999",	"720553-99999",	"720558-03977",	"720561-00467",	"720567-24180",	"720572-99999",	"720575-00173",	"720581-00178",	"720609-00201",	"720644-00226",	"720681-99999",	"720684-99999",	"720709-99999",	"720769-00275",	"720777-99999",	"720779-00461",	"720835-99999",	"720895-99999",	"720897-99999",	"720902-00298",	"720903-00441",	"720907-99999",	"720977-99999",	"720978-99999",	"720984-99999",	"720994-99999",	"721001-99999",	"721002-99999",	"721009-99999",	"721011-99999",	"721048-00471",	"722219-99999",	"722221-00444",	"722266-99999",	"722355-93999",	"722592-99999",	"722781-99999",	"723249-00463",	"723271-99999",	"723897-99999",	"724733-23170",	"725023-00474",	"999999-00262",	"999999-00343",	"999999-00370",	"999999-00421",	"999999-00423",	"999999-00425",	"999999-00440",	"999999-00447",	"999999-00458",	"999999-00477",	"999999-00480",	"999999-00481",	"999999-00484",	"999999-25382",	"999999-26564",	"999999-26565",	"999999-54856",	"999999-56401",	"999999-96405",	"999999-96406",	"999999-96407",	"999999-96408",	"999999-96409",	"A00015-53129",	"A00016-03036",	"A00018-23162",	"A00028-04116",	"A00029-63820",	"A05735-00209",	"A06773-00334",	"A06800-00120",	"A06854-00115",	"A06884-00416",	"A07049-00320",	"A07053-00346",	"A07056-00464",	"A07086-00468",	"A07141-00327",	"A07354-00132",	"A07355-00241",	"A07357-00182",	"A07359-00240",	"A51255-00445",	"A51256-00451"	]
 ,
        'station_name': [	"BRYANT ARMY AIRFIELD HELIPORT",	"QUINHAGAK AIRPORT",	"ELIM AIRPORT",	"COVINGTON MUNI",	"WILLIAM L WHITEHURST FLD",	"CABLE",	"KENNETT MEM",	"DEXTER B FLORENCE MEMORIAL FIELD AIRPORT",	"GNOSS FIELD AIRPORT",	"JOHNSON (STANTON CO MUNI)",	"HUGOTON MUNI",	"SAMUELS FLD / BARDSTOWN",	"ASHLAND RGNL",	"ADDINGTON FLD",	"FLEMING/MASON AIRPORT",	"PIKE CO HATCHER FLD",	"WILLIAMSBURG (WHITLEY CO ARPT)",	"ST LANDRY PARISH AIRPORT AHART FIELD",	"STEVEN A BEAN MUNI",	"NORTHWEST MISSOURI RGNL",	"FLOYD W JONES LEBANON",	"LAWRENCE SMITH MEM",	"MALDEN MUNI",	"OMAR N BRADLEY",	"MARSHALL MEM MUNI",	"MEXICO MEM",	"WARSAW MUNI",	"SIKESTON MEM MUNI",	"GWINNER ROGER MELROE FIELD AIRPORT",	"BESSEMER AIPORT",	"MERKEL FLD SYLACAUGA MUNI",	"AFTON MUNI",	"KEMMERER MUNICIPAL AIRPORT",	"FORT BRIDGER AIRPORT",	"POWELL MUNI",	"SHIVELY FIELD AIRPORT",	"DUBOIS MUNICIPAL AIRPORT",	"ERIE MUNICIPAL AIRPORT",	"GRANBY GRAND CO",	"MINDEN TAHOE AIRPORT",	"PORT AUTH DOWNTN MANHATTAN WALL ST HEL",	"ELK CITY MUNICIPAL AP",	"WILLIAM R POUGE MUNICIPAL AIRPORT",	"BRIGHAM CITY AIRPORT",	"BOLINDER FIELD TOOELE VALLEY",	"INDIANAPOLIS EXECUTIVE AIRPORT",	"LINDEN AIRPORT",	"LOWCOUNTRY REGIONAL AIRPORT",	"BUCKEYE MUNICIPAL AIRPORT",	"CALAVERAS CO MAURY RASMUSSEN FLD",	"PHIFER AFLD",	"PUTNAM COUNTY AIRPORT",	"GEORGE M BRYAN AIRPORT",	"LAWRENCEVILLE BRUNSWICK MUNI",	"MEXIA LIMESTONE COUNTY AIRPORT",	"MADELINE ISLAND",	"GLEN ULLIN REGIONAL",	"MONROE WALTON CO",	"DUPONT LAPEER AIRPORT",	"DAVIESS COUNTY AIRPORT",	"CAMPBELL CO",	"ALPHA (BURNS)",	"BRAVO (PINE BLUFFS)",	"GOLF (SIDNEY)",	"ALPHA (RAYNESFORD)",	"GOLF (SIMMS)",	"HOTEL (FAIRFIELD)",	"OSCAR (ROY)",	"ALPHA (BALFOUR)",	"PRESIDIO LELY INTERNATIONAL AIRPORT",	"SHELL AHP",	"DIXON AIRPORT",	"CRAIG FLD",	"VICKSBURG MUNICIPAL AIRPORT",	"ANCHORAGE(WFO)",	"HENRY CO",	"MAURY COUNTY AIRPORT",	"JOHN C TUNE",	"FRESNO CHANDLER EXECUTIVE",	"HANKSVILLE",	"CLEVELAND MUNICIPAL AIRPORT",	"MUSTANG ISLAND A85A",	"ST MARYS HOSPITAL",	"PINEY ISLAND",	"MADISONVILLE MUNICIPAL AIRPORT",	"DE QUINCY INDUSTRIAL AIRPARK",	"MIDDLEBURY STATE AIRPORT",	"CULLMAN REGIONAL AIRPORT FOLSOM FIELD",	"ATHENS MUNICIPAL AIRPORT",	"CLERMONT COUNTY AIRPORT",	"ROGER M DREYER MEMORIAL AIRPORT",	"EAGLE RANGE WSO",	"GRANITE PEAK FILLMORE ARPT",	"HULETT MUNICIPAL AIRPORT",	"YAKUTAT 3 SSE",	"IVOTUK 1 NNE",	"DEADHORSE 3 S",	"WOOSTER 3 SSE",	"GLENNALLEN 64 N",	"CORDOVA 14 ESE",	"RUBY 44 ESE",	"SELAWIK 28 E",	"DENALI 27 N",	"TOOLIK LAKE 5 ENE",	"COLORADO CITY MUNI AIRPORT",	"BLANDING MUNICIPAL AIRPORT",	"DELTA MUNICIPAL AIRPORT",	"SALT LAKE CITY MUNI 2 ARPT",	"EVERETT-STEWART AIRPORT",	"BOWIE MUNICIPAL AIRPORT",	"TUCKER GUTHRIE MEMORIAL AIRPORT",	"TAZEWELL COUNTY AIRPORT",	"BIG BEAR CITY AIRPORT",	"LURAY CAVERNS AIRPORT",	"PETALUMA MUNICIPAL AIRPORT",	"TRINITY CENTER AIRPORT",	"J DOUGLAS BAKE MEMORIAL AIRPORT",	"CARL R KELLER FIELD AIRPORT",	"COOPERSTOWN MUNICIPAL AIRPORT",	"WAUTOMA MUNICIPAL AIRPORT",	"VIROQUA MUNICIPAL AIRPORT",	"ELBOW LAKE MUNICIPAL PRIDE OF THE PRAIRIE AIRPORT",	"IONIA COUNTY AIRPORT",	"DEMOPOLIS MUNICIPAL AIRPORT",	"BRANSON WEST MUNICIPAL EMERSON FIELD AIRPORT"	]
 ,
        'latitude': [	61.266,	59.75,	64.617,	35.583,	35.214,	34.112,	36.226,	34.1,	38.15,	37.583,	37.163,	37.814,	38.555,	37.686,	38.542,	37.562,	36.8,	30.558,	44.992,	40.353,	37.648,	38.611,	36.601,	39.464,	39.096,	39.158,	38.347,	36.899,	46.217,	33.313,	33.172,	42.711,	41.824,	41.393,	44.867,	41.444,	43.548,	40.017,	40.09,	39,	40.701,	35.433,	36.175,	41.552,	40.612,	40.031,	40.617,	32.917,	33.417,	38.146,	42.05,	41.036,	33.433,	36.773,	31.641,	46.789,	46.813,	33.782,	43.067,	38.7,	36.335,	41.333,	41.517,	41.217,	47.283,	47.333,	47.7,	47.333,	47.967,	29.634,	31.363,	41.037,	32.344,	32.233,	61.15,	36.338,	35.554,	36.182,	36.732,	38.417,	33.861,	27.733,	44.017,	35.02,	37.35,	30.441,	43.985,	34.269,	32.164,	39.078,	29.529,	41.05,	38.958,	44.663,	59.509,	68.485,	70.162,	40.764,	63.03,	60.473,	64.502,	66.562,	63.452,	68.648,	36.96,	37.583,	39.383,	40.619,	36.38,	33.6,	36.859,	37.067,	34.264,	38.667,	38.25,	40.983,	44.874,	41.516,	47.423,	44.033,	43.579,	45.986,	42.938,	32.464,	36.699	]
 ,
        'longitude': [	-149.653,	-161.833,	-162.267,	-89.587,	-89.043,	-117.688,	-90.037,	-93.066,	-122.55,	-101.733,	-101.371,	-85.5,	-82.738,	-85.925,	-83.743,	-82.566,	-84.2,	-92.099,	-70.665,	-94.915,	-92.652,	-94.342,	-89.992,	-92.427,	-93.203,	-91.818,	-93.345,	-89.562,	-97.633,	-86.926,	-86.306,	-110.942,	-110.557,	-110.406,	-108.793,	-106.828,	-109.69,	-105.05,	-105.917,	-119.751,	-74.009,	-99.4,	-96.152,	-112.062,	-112.351,	-86.251,	-74.25,	-80.633,	-112.683,	-120.648,	-104.933,	-83.982,	-88.849,	-77.794,	-96.514,	-90.759,	-101.86,	-83.693,	-83.267,	-87.13,	-84.162,	-104.267,	-104,	-103.1,	-110.8,	-112.1,	-111.95,	-108.933,	-100.581,	-104.361,	-85.849,	-107.493,	-86.988,	-90.933,	-149.983,	-88.383,	-87.179,	-86.887,	-119.82,	-110.7,	-90.758,	-96.183,	-92.483,	-76.46,	-87.4,	-93.474,	-73.095,	-85.858,	-95.828,	-84.21,	-97.464,	-113.06,	-112.363,	-104.568,	-139.685,	-155.751,	-148.464,	-81.91,	-145.5,	-145.354,	-154.13,	-159.004,	-150.875,	-149.399,	-113.014,	-109.483,	-112.517,	-111.993,	-88.985,	-97.783,	-83.358,	-81.8,	-116.854,	-78.501,	-122.6,	-122.694,	-87.91,	-82.869,	-98.106,	-89.3,	-90.913,	-95.992,	-85.061,	-87.954,	-93.402	]

        }

    df_us_weather_station = pd.DataFrame(d_us_weather_station)


    # # Sample benchmarking statistics (for demonstration purposes only)
    ## Electricity
        # From simulation
    d_sample_benchmark_stats_e = {'beta_median': [0.356550675, 0.0115249, 14.99895357, 0.013061297, 14.37165836],
                                   'beta_standard_deviation': [0.023339094, 0.005313114, 4.323367826, 0.005181999, 4.838926188],
                                  }
    ## Fossil fuel
    # From simulation
    d_sample_benchmark_stats_f = {'beta_median': [0.107, 0, 4.493517689, 0.072, 12.4],
                                  'beta_standard_deviation': [0.0125, 0, 0.34410526, 0.0386, 5.7],
                                   }

    df_sample_benchmark_stats_e = pd.DataFrame(data=d_sample_benchmark_stats_e,
                                               index=["beta_base", "beta_cdd", "beta_betc", "beta_hdd", "beta_beth"])
    df_sample_benchmark_stats_f = pd.DataFrame(data=d_sample_benchmark_stats_f,
                                               index=["beta_base", "beta_cdd", "beta_betc", "beta_hdd", "beta_beth"])

    df_sample_benchmark_stats_e.index.name = "coefficient"
    df_sample_benchmark_stats_f.index.name = "coefficient"

    def read_bench_stats(self, file_name, utility_type):
        # utility_type: 1 ~ electricity, 2 ~ fossil fuel
        df_bench_stats = pd.read_csv(file_name)
        if (utility_type == 1):
            df_sample_benchmark_stats_e = df_bench_stats
            df_sample_benchmark_stats_e.index.name = "coefficient"
        else:
            df_sample_benchmark_stats_f = df_bench_stats
            df_sample_benchmark_stats_f.index.name = "coefficient"

from read_log_files import FileReader
import json
from statistics import StatsCalculator
from Plots.Plotting import DataPlotter
import numpy as np
import matplotlib.pyplot as plt
import sys
import argparse
from fft_calculator import FFTCalculator

def print_dictionary(inp_dict):
    """
        This function prints the dictionary in a readable format
        :param inp_dict: Dictionary to be printed
        :return: None
    """

    formatted_dict = json.dumps(inp_dict, default=str, indent=4)
    print(formatted_dict)

def normalize_frequencies(error_position_frequency):
    max_freq = max(error_position_frequency.values())
    min_freq = min(error_position_frequency.values())

    for position, freq in error_position_frequency.items():
        norm_freq = ((freq - min_freq)/ (max_freq - min_freq)) * 100
        error_position_frequency[position] = norm_freq

    return error_position_frequency


def plot_average_bit_errors(physical_layer, bv_mode):
    if bv_mode:
        # path = f'/home/burhanuddin/Desktop/osf/logparser/Dcube_Logs/Templab/Neg8dBm/Same_Temperature/CSVFiles/{physical_layer}/With_BV'
        path = f'/home/burhanuddin/Desktop/osf/logparser/Dcube_Logs/Nodes100to119/Neg16dBm/CSVFiles/{physical_layer}/With_BV'
    else:
        # path = f'/home/burhanuddin/Desktop/osf/logparser/Dcube_Logs/Templab/Neg8dBm/Same_Temperature/CSVFiles/{physical_layer}/No_BV'
        path = f'/home/burhanuddin/Desktop/osf/logparser/Dcube_Logs/Nodes100to119/Neg16dBm/CSVFiles/{physical_layer}/No_BV'
    reader = FileReader(path)
    print(path)
    csv_files = reader.get_csv_file_paths(path)
    # bv_csv_files, no_bv_csv_files = reader.get_dcube_raw_csv_files(str(122), str(126), str(124))
    # print_dictionary(bv_csv_files)
    # print(len(bv_csv_files))
    # sys.exit()
    plotter = DataPlotter(path, path+'/CSVFiles', 255, bv_mode)
    fft_calc = FFTCalculator(path, physical_layer, bv_mode)
    calc = StatsCalculator(path, path+'/CSVFiles', True, False)
    calc.file_paths = csv_files
    if bv_mode:
        calc.calc_error_corrected_error_positions()
    else:
        calc.calc_error_positions()
    # s_freq, powr, cutoff_freq = fft_calc.fft_calculator(calc.get_error_positions_dictionary())
    # print_dictionary(calc.get_error_positions_dictionary()) 
    # print_dictionary(calc.get_corrected_error_positions_dictionary())
    err_dict = calc.get_error_positions_dictionary()
    # err_dict = normalize_frequencies(err_dict)
    # print(len(err_dict))000
    # print_dictionary(err_dict)
    # sys.exit()
    plotter.plot_error_positions(err_dict, 'Bit Index vs No. of Errors')
    # plotter.plot_fft(s_freq, powr, cutoff_freq)
    # plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--phy', type=str, help= 'Physical_layer for which calculation needs to be done', required=True)
    parser.add_argument('--bv', type=int, help= 'Bit Voting mode', required=True)
    args = parser.parse_args()
    if args.bv == 1:
        bv_m = True
    else:
        bv_m = False
    plot_average_bit_errors(args.phy, bv_m)
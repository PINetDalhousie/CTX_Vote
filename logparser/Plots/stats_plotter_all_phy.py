import math
import matplotlib.pyplot as plt
import sys
import pandas as pd
import json
from Plotting import DataPlotter
import numpy as np
import datetime
import argparse
import os
sys.path.append('../')
from read_log_files import FileReader

# import read_log_files
# sys.remove('../logparser')


def make_box_plot() -> None:
    """
        This function creates box plots for each physical layer.
        The plot is drawn for PRR values for each physical layer for the cases when BV is used and when BV is not used.
        The values are divided into 5 categories based on the packet size.
        :return: None
    """

    pkt_size_prr_vals_dict = {16:{
        '1M':{'BV':[91.33,39.74,20.77,90.41,41.84],
              'NO_BV':[86.44,85.9,7.96,85.11,14.56]},
        '2M':{'BV':[53.25,35.61,19.24,95.34,54.54],
              'NO_BV':[12.92,60.29,74.85,16.58,47.38],},
        '125K':{'BV':[71.35,67.79,54.05,83.33,71.89],
                'NO_BV':[73.51,92.30,67.7,76.31,63.1]},
        '500K':{'BV':[82.03,84.79,68.57,93.22,68.85],
                'NO_BV':[93.15,57.94,88.05,83.57,56.99]},
        'IEEE':{'BV':[69.94,100,89.2,81.08,67.36],
                'NO_BV':[73.36,80.11,69.51,72.92,79.16]}, 
    },
                              32:{
                                '1M':{'BV':[83.33,89.85,81.7,50.7,77.7],
                                      'NO_BV':[81.39,79.76,81.43,77.38,52.19]},
                                '2M':{'BV':[65.11,60.69,40.92,64.86,40.9],
                                      'NO_BV':[51.74,28.95,50,38.86,55.02]},
                                '125K':{'BV':[75.12,69.35,60.65,56.57,50],
                                        'NO_BV':[65.64,59.53,49.75,66.52,58.48]},
                                '500K':{'BV':[42.91,87.58,83.73,41.47,80.12],
                                        'NO_BV':[75.72,82.91,81.5,85.79,45.96]},
                                'IEEE':{'BV':[73.51,77.43,55.94,74.85,50.23],
                                          'NO_BV':[76.68,87.01,64.28,85.23,72.34]},
                                
                              },
                              64:{
                                '1M':{'BV':[71.28,70.98,66.81,69.13,67.06],
                                      'NO_BV':[57.39,45.55,74.40,71.83,64.13]},
                                '2M':{'BV':[37.03,30,27.62,73.48,22.97],
                                      'NO_BV':[33.46,4.65,48.7,2.97,28.85]},
                                '125K':{'BV':[40.75,45.93,42.36,38.98,71.6],
                                        'NO_BV':[33,51.4,41.84,40.64,40.4]},
                                '500K':{'BV':[59.56,72.25,71.3,60.38,75.65],
                                        'NO_BV':[73.18,59.92,51.39,67.77,56.95]},
                                'IEEE':{'BV':[44.48,64.34,59.06,68.68,60.89],
                                          'NO_BV':[50.89,55.41,42.47,70.61,46.64]},
                              },
                              125:{
                                '1M':{'BV':[58.76,60.09,54.14,60.91,47.88],
                                      'NO_BV':[50.44,46.88,44.67,55.17,46]},
                                '2M':{'BV':[26.55,15.98,30.79,15.5,32.58],
                                      'NO_BV':[27.4,2.9,35.94,5.86,15.2]},
                                '125K':{'BV':[18.55,28.44,15.38,45.11,21.23],
                                        'NO_BV':[14.21,49.35,9.61,22.58,16.9]},
                                '500K':{'BV':[43.16,45.74,40.25,57.48,49.49],
                                        'NO_BV':[41.53,56.83,43.94,50.86,50.42]},
                                'IEEE':{'BV':[23.62,34.71,43.63,42.7,32.58],
                                          'NO_BV':[25.5,37.14,30.31,34.07,22.01]},
                              },
                              255:{
                                '1M':{'BV':[47.36,38.65,32.69,52.87,25.4],
                                      'NO_BV':[34.72,29.81,45.28,38.7,19.43]},
                                '2M':{'BV':[27.51,36.25,27.62,15.87,14.99],
                                      'NO_BV':[24.92,2.73,16.26,33.33,36.23]},
                                '125K':{'BV':[8.87,16.63,11.71,36.9,15.08],
                                        'NO_BV':[3.86,13.51,1.86,3.83,4.07]},
                                '500K':{'BV':[34.81,37.37,25.41,41.69,25.25],
                                        'NO_BV':[30,11.32,24.81,26.54,19.67]},
                              }}
    packet_sizes = list(pkt_size_prr_vals_dict.keys())
    prr_values = {}

    for pkt_size, pkt_size_data in pkt_size_prr_vals_dict.items():
        for phy_layer, prr_data in pkt_size_data.items():
            for modulation, values in prr_data.items():
                key = (pkt_size, phy_layer, modulation)
                prr_values[key] = values
    # print(prr_values)
    # Create box plots for each packet size
    for pkt_size in packet_sizes:
        fig, ax = plt.subplots()
        ax.boxplot([prr_values[(pkt_size, phy_layer, 'BV')] for phy_layer in pkt_size_prr_vals_dict[pkt_size].keys()],
                labels=list(pkt_size_prr_vals_dict[pkt_size].keys()))
        
        ax.set_title(f'Box Plot for Packet Size {pkt_size}')
        ax.set_xlabel('Physical Layer')
        ax.set_ylabel('PRR Values (%)')
        
        plt.savefig(f'./Boxplots/box_plot_{pkt_size}.png')
    
    for pkt_size, pkt_size_data in pkt_size_prr_vals_dict.items():
        print(f"Packet Siself.bf_v_stats_phywise['BV'][stat_name_t]ze: {pkt_size}")
        for phy_layer, prr_data in pkt_size_data.items():
            bv_average = sum(prr_data['BV']) / len(prr_data['BV'])
            nobv_average = sum(prr_data['NO_BV']) / len(prr_data['NO_BV'])
            print(f"Physical Layer: {phy_layer}")
            print(f"Average BV: {bv_average:.2f}")
            print(f"Average NO_BV: {nobv_average:.2f}")
        print()


class StatsPlotter:

	def __init__(self) -> None:
		self.bf_v_stat = {'PHY_BLE_1M':{
		}, 'PHY_BLE_2M':{
		}, 'PHY_BLE_125K':{
		}, 'PHY_BLE_500K':{
		}}

		self.bf_v_stats_phywise = {
			'No_BV':{
			'Beating_Frequency':[]},
			'BV':{      
			'Beating_Frequency':[]}
		}
		

	def reset_phy_wise_dict(self):
		"""
			This function resets the dictionary for each physical layer
			:param inp_dict: Dictionary to be reset
			:return: None
		"""
		self.bf_v_stats_phywise = {
			'No_BV':{
			'Beating_Frequency':[]},
			'BV':{      
			'Beating_Frequency':[]}
		}

	def print_dictionary(self, inp_dict):
		"""
				This funcself.bf_v_stats_phywise['BV'][stat_name_t]tion prints the dictionary in a readable format
				:param inp_dict: Dictionary to be printed
				:return: None
		"""

		formatted_dict = json.dumps(inp_dict, default=str, indent=4)
		print(formatted_dict)

	def barplot_avg_stats_vs_phys(self, power, stat_name, src, fwd, dst):
		"""
			This function plots a bar plot for average stat value when BV is enabled as compared to when BV is disabled.
			:param power: Power used for the experiment
			:param stat_name: Name of the statistic that we want to plot against beating frequency
			:param src: Source node id
			:param fwd: Forwarder node id
			:param dst: Destination node id
			:return: None
		"""
		path = f'/home/burhanuddin/Desktop/osf/logparser/Dcube_Logs/Nodes100to119/{power}/Bit_Voting'
		reader_bv = FileReader(path)
		reader_no_bv = FileReader(path)
		# csv_files_dict_bv = reader_bv.get_dcube_csv_files_pair(True, str(src), str(fwd), str(dst))
		# csv_files_dict_no_bv = reader_no_bv.get_dcube_csv_files_pair(False, str(src), str(fwd), str(dst))
		csv_files_dict_bv = reader_bv.get_dcube_stat_csv_files(True)
		csv_files_dict_no_bv = reader_no_bv.get_dcube_stat_csv_files(False)
		stat_name_t = stat_name

		if stat_name == 'PER':
			stat_name = 'PRR'
		plotter = DataPlotter(path, 'PHY_BLE_2M', 64, False)
		for (phy_bv, phy_stat_bv_csv_files),(phy_no_bv, phy_stat_no_bv_csv_files) in zip(csv_files_dict_bv.items(), csv_files_dict_no_bv.items()):
			print(f"--------------- PHY: {phy_bv} {phy_no_bv}-----------------------")
			# sys.exit(1)
			self.reset_phy_wise_dict()
			aux_bv_stat = []
			aux_no_bv_stat = []
			aux_bv_bf = []
			aux_no_bv_bf = []
			for (csv_file_bv, csv_file_no_bv) in zip(phy_stat_bv_csv_files, phy_stat_no_bv_csv_files):
				print(f"Reading file {csv_file_bv}")
				print(f"Reading file {csv_file_no_bv}")
				data_bv = pd.read_csv(csv_file_bv)
				data_no_bv = pd.read_csv(csv_file_no_bv)
				if not data_bv.empty and not data_no_bv.empty:
					if stat_name_t == 'PER':
						aux_bv_stat.append(100 - data_bv[stat_name].values[0])
						aux_no_bv_stat.append(100 - data_no_bv[stat_name].values[0])
					else:
						aux_bv_stat.append(data_bv[stat_name].values[0])
						aux_no_bv_stat.append(data_no_bv[stat_name].values[0])
					aux_bv_bf.append(0 if math.isnan(data_bv['Beating_Frequency'].values[0]) else data_bv['Beating_Frequency'].values[0])
					aux_no_bv_bf.append(0 if math.isnan(data_no_bv['Beating_Frequency'].values[0]) else data_no_bv['Beating_Frequency'].values[0])
				print('--------------------------------------------------------')
			print("BV_stat: ",aux_bv_stat)
			print("No_BV_stat: ", aux_no_bv_stat)
			print("BV_bf", aux_bv_bf)
			print("No_BV_bf", aux_no_bv_bf)
			self.bf_v_stats_phywise['BV'][stat_name_t] = np.average(aux_bv_stat)
			self.bf_v_stats_phywise['BV']['Beating_Frequency'] = np.average(aux_bv_bf)
			self.bf_v_stats_phywise['No_BV'][stat_name_t] = np.average(aux_no_bv_stat)
			self.bf_v_stats_phywise['No_BV']['Beating_Frequency'] = np.average(aux_no_bv_bf)
			self.print_dictionary(self.bf_v_stats_phywise) 
			self.bf_v_stat[phy_bv] = self.bf_v_stats_phywise

			print('\n ---------------------- Complete Dictionary ----------------------------------- \n')
			self.print_dictionary(self.bf_v_stat)       
			print('\n --------------------------------------------------------- \n')
		x_l = 'Physical Layer (PHY)'
		y_l = stat_name + " (%)"
		plot_title = f'Physical_Layer vs {stat_name}'
		# plotter.plot_beating_v_prr_pdr_all_phy(self.bf_v_stat, x_l, y_l, plot_title, stat_name)
		plotter.bar_plot_all_stats_phy(self.bf_v_stat, x_l, y_l, plot_title, stat_name_t)
		# plotter.bar_plot_with_error_bars_phy(self.bf_v_stat, x_l, y_l, plot_title, 'Beating_Frequency')
		# plt.show()
		print('Saving plot to location: ', f'/home/burhanuddin/Desktop/Diagrams/PDFs/{stat_name_t}_vs_phy_{power}.pdf')
		plt.savefig(f'/home/burhanuddin/Desktop/Diagrams/PDFs/{stat_name_t}_vs_phy_{power}.pdf', format='pdf', bbox_inches='tight')
	
	def plot_average_corrections_v_bf_all_phys(self, power, pair_wise=False, src=None, fwd=None, dst=None):	
		"""
			This function plots the average corrections vs beating frequency for all physical layers
			:param pair_wise: Boolean value to indicate if the plotting is to be done for a specific node pair
			:param src: Source node id
			:param fwd: Forwarder node id
			:param dst: Destination node id
			:return: None
		"""
		
		path = f'/home/burhanuddin/Desktop/osf/logparser/Dcube_Logs/Templab/{power}'
		reader = FileReader(path)

		average_corrections = {'PHY_BLE_2M': 0, 'PHY_BLE_1M': 0, 'PHY_BLE_500K': 0, 'PHY_BLE_125K': 0}
		average_beating_frequency = {'PHY_BLE_2M': 0, 'PHY_BLE_1M': 0, 'PHY_BLE_500K': 0, 'PHY_BLE_125K': 0}

		csv_files_dict_bv = reader.get_dcube_csv_files_pair(True, str(src), str(fwd), str(dst))
		plotter = DataPlotter(path, 'PHY_BLE_2M', 64, False)
		for phy, phy_stat_csv_files in csv_files_dict_bv.items():
			print(f"--------------- PHY: {phy} -----------------------")
			self.bf_v_stat[phy]['Corrections'] = []
			for csv_file in phy_stat_csv_files:
					print(f"Reading file {csv_file}")
					data = pd.read_csv(csv_file)
					if not data.empty:
							self.bf_v_stat[phy]['Corrections'].append(data['Total_Corrections'].values[0])
							self.bf_v_stat[phy]['Beating Frequency'].append(data['Beating_Frequency'].values[0])
			average_corrections[phy] = np.average(self.bf_v_stat[phy]['Corrections'])
			average_beating_frequency[phy] = np.average(self.bf_v_stat[phy]['Beating Frequency'])
		
		print('------------------ Original Dictionary----------------------')
		self.print_dictionary(self.bf_v_stat)
		print('--------------- Average Correctoins -----------------------')
		self.print_dictionary(average_corrections)
		print('--------------- Average Beating Frequency -----------------------')
		self.print_dictionary(average_beating_frequency)
		markers = {'PHY_BLE_1M':'o', 'PHY_BLE_2M':'s', 'PHY_BLE_125K':'D', 'PHY_BLE_500K':'^'}
		plt.scatter(average_beating_frequency.values(), average_corrections.values(), marker='o')

		for label, x, y in zip(average_beating_frequency.keys(), average_beating_frequency.values(), average_corrections.values()):
				plt.annotate(label, xy=(x, y), xytext=(-20, 20), textcoords='offset points', ha='right', va='bottom',
										bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
										arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

		# plt.scatter(average_corrections.keys(), average_corrections.values(), marker='x')
		plt.xlabel('Average Beating Frequency')
		plt.ylabel('Average Corrections')
		plt.title('Average Corrections vs Average Beating Frequency')
		plt.show()

if __name__ == '__main__':
	arg_parser = argparse.ArgumentParser()
	arg_parser.add_argument('-bv', '--bit_voting', type=int, help='Whether Bit Voting error correction scheme is enabled or not', required=False)
	arg_parser.add_argument('-pw', '--pairwise', type=int, help='Whether the plotting should be done pairwise or not', required=False)
	arg_parser.add_argument('-stat', '--stat_name', type=str, help='Name of the statistic that we want to plot', required=True)
	arg_parser.add_argument('-phy', '--physical_layer', type=str, help='Physical layer for which the plot is to be drawn', required=False)
	arg_parser.add_argument('-temp', '--temperature', type=str, help='Temperature for which the plot is to be drawn', required=False)
	args = arg_parser.parse_args()
	# print(args.bit_voting)
	stat_plotter = StatsPlotter()

	if args.bit_voting == 1:
		bv = True
	else:
		bv = False
	
	if args.pairwise == 1:
		pair_wise = True
	else:
		pair_wise = False
	
	stat_plotter.barplot_avg_stats_vs_phys('Neg40dBm', args.stat_name, 122, 126, 124)
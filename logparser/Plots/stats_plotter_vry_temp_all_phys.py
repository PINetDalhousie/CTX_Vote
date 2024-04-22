from typing import Any
import matplotlib.pyplot as plt

import pandas as pd
import json
from Plotting import DataPlotter
import numpy as np
import datetime
import argparse
import sys
sys.path.append('../')
from read_log_files import FileReader

class StatsPlotter:

	def __init__(self) -> None:
		self.bf_v_stat = {'PHY_BLE_2M':{
			'Beating Frequency':[]
		}, 'PHY_BLE_1M':{
			'Beating Frequency':[]
		}, 'PHY_BLE_500K':{
			'Beating Frequency':[]
		}, 'PHY_BLE_125K':{
			'Beating Frequency':[]
		}}

		self.bf_v_stats_phywise = {
			'No_BV':{
			'Beating Frequency':[]},
			'BV':{      
			'Beating Frequency':[]}
		}
		
		self.temperature_v_stats = {'PHY_BLE_2M':{
		'temperature_stat':{}
		}, 'PHY_BLE_1M':{
		'temperature_stat':{}
		}, 'PHY_BLE_500K':{
		'temperature_stat':{}
		}, 'PHY_BLE_125K':{
		'temperature_stat':{}
		}}

		self.temperature_v_stats_phywise = {
			'No_BV':{
			'temperature_stat':{}},
			'BV':{      
			'temperature_stat':{}}
		}

		self.phy_wise_stats = {
			'BV':{},
			'No_BV':{}
		}

		

	def print_dictionary(self, inp_dict):
		"""
				This function prints the dictionary in a readable format
				:param inp_dict: Dictionary to be printed
				:return: None
		"""

		formatted_dict = json.dumps(inp_dict, default=str, indent=4)
		print(formatted_dict)
    
	def plot_avg_prr_v_temperature_all_phys(self, heating_node, bv_mode, src, fwd, dst, stat_name):
		"""
			This function plots the PDR/PRR vs temperature for all physical layers.
			Here the Average PRR for each temperature is considered
			:param heating_node: Node which is being heated
			:param bv_mode: Mode of bit voting
			:param src: Source node id
			:param fwd: Forwarder node id
			:param dst: Destination node id
			:param stat_name: Name of the statistic that we want to plot against temperature
			:return: None
		"""

		path = '/home/burhanuddin/Desktop/osf/logparser/Dcube_Logs/Templab'
		if heating_node == 'fwd':
			path = path + '/Neg8dBm/Increasing_Temperature/Heating_Forwarder'
		elif heating_node == 'src':
			path = path + '/Neg8dBm/Increasing_Temperature/Heating_Source/Heating_Source_inc_10'

		reader = FileReader(path)

		x_label = 'Temperature (C)'
		y_label = stat_name + ' (%)'
		plot_title = f'{stat_name} vs Temperature'

		csv_files_dict = reader.get_dcube_csv_files_pair_temperature(bv_mode, str(src), str(fwd), str(dst))
		plotter = DataPlotter(path, 'PHY_BLE_2M', 64, False)

		for phy, phy_stat_temp_csv_files in csv_files_dict.items():
			print(f"--------------- PHY: {phy} -----------------------")
			auxiliary_prr = []
			for temperature, csv_files in phy_stat_temp_csv_files.items():
				print(f"--------------- Temperature: {temperature} -----------------------")
				for csv_file in csv_files:
					print(f"Reading file {csv_file}\n")
					data = pd.read_csv(csv_file)
					if not data.empty:
							auxiliary_prr.append(data[stat_name].values[0])
				temperature = int(temperature[:-1])
				if temperature not in self.temperature_v_stats[phy]['temperature_stat']:
					self.temperature_v_stats[phy]['temperature_stat'][temperature] = np.average(auxiliary_prr)
				else:
					self.temperature_v_stats[phy]['temperature_stat'][temperature] = np.average(auxiliary_prr)
				auxiliary_prr = []
		self.print_dictionary(self.temperature_v_stats)
		plotter.plot_prr_v_temperature_all_phy(self.temperature_v_stats, bv_mode, x_label, y_label, plot_title)
		
		plt.show()

	def plot_avg_prr_v_bf_temperature_all_phys(self, heating_node, src, fwd, dst, temperature, stat_name):
		"""
			This function plots the PRR/PDR vs Beating Frequency for all physical layers for a specific temperature.
			Here the Average PRR/PDR for each temperature is considered
			:param heating_node: Node which is being heated
			:param src: Source node id
			:param fwd: Forwarder node id
			:param dst: Destination node id
			:param temperature: Temperature for which the plot is to be drawn
			:param stat_name: Name of the statistic that we want to plot against temperature
			:return: None
		"""

		path = '/home/burhanuddin/Desktop/osf/logparser/Dcube_Logs/Templab'
		if heating_node == 'fwd':
			path = path + '/Neg8dBm/Increasing_Temperature/Heating_Forwarder'
		elif heating_node == 'src':
			path = path + '/Neg8dBm/Increasing_Temperature/Heating_Source/Heating_Source_inc_10'

		reader = FileReader(path)
		temperature_stats = {'PHY_BLE_2M':{
			'BV':{
				'BF':[],
			},
			'No_BV':{
				'BF':[],
			}

		}, 'PHY_BLE_1M':{
			'BV':{
				'BF':[],
			},
			'No_BV':{
				'BF':[],
			}

		}, 'PHY_BLE_500K':{
			'BV':{
				'BF':[],
			},
			'No_BV':{
				'BF':[],
			}
		}, 'PHY_BLE_125K':{
			'BV':{
				'BF':[],
			},
			'No_BV':{
				'BF':[],
			}
		}}
		csv_files_dict_bv = reader.get_dcube_csv_files_pair_temperature(True, str(src), str(fwd), str(dst))
		reader_2 = FileReader(path)
		csv_files_dict_no_bv = reader_2.get_dcube_csv_files_pair_temperature(False, str(src), str(fwd), str(dst))
		stat_name_t = None
		if stat_name == 'PER':
			stat_name = 'PRR'
			stat_name_t = 'PER'
		plotter = DataPlotter(path, 'PHY_BLE_2M', 64, False)

		#BV
		print('--------------BV------------------')
		for (phy, phy_stat_bv_csv_files),(phy_no_bv, phy_stat_no_bv_csv_files) in zip(csv_files_dict_bv.items(), csv_files_dict_no_bv.items()):
			print(f"--------------- PHY: {phy} {phy_no_bv}-----------------------")
			auxiliary_stat_bv = []
			auxiliary_bf_bv = []
			auxiliary_stat_no_bv = []
			auxiliary_bf_no_bv = []
			print(f"--------------- Temperature: {temperature} -----------------------")
			for (csv_file_bv, csv_file_no_bv) in zip(phy_stat_bv_csv_files[temperature], phy_stat_no_bv_csv_files[temperature]):
				print(f"Reading file {csv_file_bv}\n")
				print(f"Reading file {csv_file_no_bv}\n")
				data_bv = pd.read_csv(csv_file_bv)
				data_no_bv = pd.read_csv(csv_file_no_bv)
				if not data_bv.empty:
						if stat_name_t is not None and stat_name_t == 'PER':
							auxiliary_stat_bv.append(100 - data_bv[stat_name].values[0])
						else:
							auxiliary_stat_bv.append(data_bv[stat_name].values[0])
						auxiliary_bf_bv.append(data_bv['Beating_Frequency'].values[0])
				if not data_no_bv.empty:
						if stat_name_t is not None and stat_name_t == 'PER':
							auxiliary_stat_no_bv.append(100 - data_no_bv[stat_name].values[0])
						else:
							auxiliary_stat_no_bv.append(data_no_bv[stat_name].values[0])
						auxiliary_bf_no_bv.append(data_no_bv['Beating_Frequency'].values[0])
			print('---------BV---------\n')
			print(auxiliary_stat_bv)
			print(auxiliary_bf_bv)
			print('---------NO BV---------\n')
			print(auxiliary_stat_no_bv)
			print(auxiliary_bf_no_bv)
			if stat_name not in temperature_stats[phy]['BV']:
				temperature_stats[phy]['BV'][stat_name] = np.average(auxiliary_stat_bv)
				temperature_stats[phy]['BV']['BF'] = np.average(auxiliary_bf_bv)
			if stat_name not in temperature_stats[phy]['No_BV']:
				temperature_stats[phy]['No_BV'][stat_name] = np.average(auxiliary_stat_no_bv)
				temperature_stats[phy]['No_BV']['BF'] = np.average(auxiliary_bf_no_bv)
			auxiliary_stat_bv = []
			auxiliary_bf_bv = []
			auxiliary_stat_no_bv = []
			auxiliary_bf_no_bv = []
		self.print_dictionary(temperature_stats)
		xlabel = 'Beating Frequency (Hz)'
		if stat_name_t is not None and stat_name_t == 'PER':
			ylabel = 'PER (%)'
			plot_title = f'PER vs Beating Frequency for {temperature}'
			fig_name = f'plot_PER_vs_BF_{temperature}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.png'
		else:
			ylabel = f'{stat_name} (%)'
			plot_title = f'{stat_name} vs Beating Frequency for {temperature}'
			fig_name = f'plot_{stat_name}_vs_BF_{temperature}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.png'
		fig_save_path = '/home/burhanuddin/Desktop/osf/logparser/Graphs/Increasing_Temperature/All_phys_graphs'+'/'+fig_name
		plotter.plot_prr_v_temperature_phy(temperature_stats, xlabel,ylabel,plot_title, stat_name)
		
		# plt.savefig(fig_save_path)
		plt.show()

	def plot_avg_bf_v_temperature_all_phys(self, heating_node, bv_mode, src, fwd, dst, physical_layer=None):
		"""
			This function plots the Beating Frequency vs temperature for all physical layers.
			:param heating_node: Node which is being heated
			:param bv_mode: Mode of bit voting
			:param src: Source node id
			:param fwd: Forwarder node id
			:param dst: Destination node id
			:return: None
		"""

		path = '/home/burhanuddin/Desktop/osf/logparser/Dcube_Logs/Templab'
		if heating_node == 'fwd':
			path = path + '/Neg8dBm/Increasing_Temperature/Heating_Forwarder'
		elif heating_node == 'src':
			path = path + '/Neg8dBm/Increasing_Temperature/Heating_Source/Heating_Source_inc_10'

		reader = FileReader(path)
		temperature_bf_stats = {'PHY_BLE_2M':{
			'temperature_bf':{}
		}, 'PHY_BLE_1M':{
			'temperature_bf':{}
		}, 'PHY_BLE_500K':{
			'temperature_bf':{}
		}, 'PHY_BLE_125K':{
			'temperature_bf':{}
		}}

		csv_files_dict = reader.get_dcube_csv_files_pair_temperature(bv_mode, str(src), str(fwd), str(dst))
		plotter = DataPlotter(path, 'PHY_BLE_2M', 64, False)

		for phy, phy_stat_temp_csv_files in csv_files_dict.items():
			print(f"--------------- PHY: {phy} -----------------------")
			auxiliary_bf = []
			for temperature, csv_files in phy_stat_temp_csv_files.items():
				print(f"--------------- Temperature: {temperature} -----------------------")
				for csv_file in csv_files:
					print(f"Reading file {csv_file}\n")
					data = pd.read_csv(csv_file)
					if not data.empty:
							auxiliary_bf.append(data['Beating_Frequency'].values[0])
				temperature = int(temperature[:-1])
				if temperature not in temperature_bf_stats[phy]['temperature_bf']:
					temperature_bf_stats[phy]['temperature_bf'][temperature] = np.average(auxiliary_bf)
				else:
					temperature_bf_stats[phy]['temperature_bf'][temperature] = np.average(auxiliary_bf)
				auxiliary_bf = []

		self.print_dictionary(temperature_bf_stats)
		# plotter.plot_bf_v_temperature_all_phy(temperature_bf_stats, bv_mode)
		if physical_layer is not None:
			plotter.plot_bf_v_temperature_all_phy(temperature_bf_stats[physical_layer], bv_mode, physical_layer)
			fig_save_path = '/home/burhanuddin/Desktop/osf/logparser/Graphs/Increasing_Temperature/'+physical_layer+'/'+'BF_vs_Temp/'+f'plot_BF_vs_{bv_mode}_Temp_{physical_layer}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.png'
			plt.savefig(fig_save_path)
		plt.show()
	
	def plot_average_corrections_vs_temperature(self, heating_node, bv_mode, src, fwd, dst, physical_layer=None):
		"""
			This function plots the average corrections vs temperature for all or specific physical layer.
			:param heating_node: Node which is being heated
			:param bv_mode: Mode of bit voting
			:param src: Source node id
			:param fwd: Forwarder node id
			:param dst: Destination node id
			:param physical_layer: Physical layer used for the experiment
			:return: None
		"""
		path = '/home/burhanuddin/Desktop/osf/logparser/Dcube_Logs/Templab'
		if heating_node == 'fwd':
			path = path + '/Neg8dBm/Increasing_Temperature/Heating_Forwarder'
		elif heating_node == 'src':
			path = path + '/Neg8dBm/Increasing_Temperature/Heating_Source/Heating_Source_inc_10'

		corrections_temperature_stats = {'PHY_BLE_2M':{
			'temperature_corrections':{}
		}, 'PHY_BLE_1M':{
			'temperature_corrections':{}
		}, 'PHY_BLE_500K':{
			'temperature_corrections':{}
		}, 'PHY_BLE_125K':{
			'temperature_corrections':{}
		}}

		reader = FileReader(path)
		csv_files_dict = reader.get_dcube_csv_files_pair_temperature(bv_mode, str(src), str(fwd), str(dst))
		plotter = DataPlotter(path, 'PHY_BLE_2M', 64, False)

		for phy, phy_stat_temp_csv_files in csv_files_dict.items():
			print(f"--------------- PHY: {phy} -----------------------")
			auxiliary_corrections = []
			for temperature, csv_files in phy_stat_temp_csv_files.items():
				print(f"--------------- Temperature: {temperature} -----------------------")
				for csv_file in csv_files:
					print(f"Reading file {csv_file}\n")
					data = pd.read_csv(csv_file)
					if not data.empty:
							auxiliary_corrections.append(data['Total_Corrections'].values[0])
				temperature = int(temperature[:-1])
				print('Corrections: ', auxiliary_corrections)
				if temperature not in corrections_temperature_stats[phy]['temperature_corrections']:
					print('average: ', np.average(auxiliary_corrections))
					corrections_temperature_stats[phy]['temperature_corrections'][temperature] = np.average(auxiliary_corrections)

				auxiliary_corrections = []

		self.print_dictionary(corrections_temperature_stats)
		plotter.plot_corrections_v_temperature_all_phy(corrections_temperature_stats, bv_mode)

		plt.show()


	def plot_avg_bf_per_across_temp_all_phys(self, heating_node, bv_mode, src, fwd, dst, physical_layer=None):
		path = '/home/burhanuddin/Desktop/osf/logparser/Dcube_Logs/Templab'
		if heating_node == 'fwd':
			path = path + '/Neg8dBm/Increasing_Temperature/Heating_Forwarder'
		elif heating_node == 'src':
			path = path + '/Neg8dBm/Increasing_Temperature/Heating_Source/Heating_Source_inc_10'

		corrections_temperature_stats = {'PHY_BLE_2M':{
		}, 'PHY_BLE_1M':{
		}, 'PHY_BLE_500K':{
		}, 'PHY_BLE_125K':{
		}}

		reader = FileReader(path)
		csv_files_dict = reader.get_dcube_csv_files_pair_temperature(bv_mode, str(src), str(fwd), str(dst))		
		self.print_dictionary(csv_files_dict)
		plotter = DataPlotter(path, 'PHY_BLE_2M', 64, False)
		for phy, phy_stat_temp_csv_files in csv_files_dict.items():
			print(f"--------------- PHY: {phy} -----------------------")
			auxiliary_stat = []
			auxiliary_bf = []
			for temperature, csv_files in phy_stat_temp_csv_files.items():
				print(f"--------------- Temperature: {temperature} -----------------------")
				for csv_file in csv_files:
					print(f"Reading file {csv_file}\n")
					data = pd.read_csv(csv_file)
					if not data.empty:
						auxiliary_stat.append((100 - data['PRR'].values[0]))
						auxiliary_bf.append(data['Beating_Frequency'].values[0])
				temperature = int(temperature[:-1])
				print('PER: ', auxiliary_stat)
				if 'PER' not in corrections_temperature_stats[phy]:
					corrections_temperature_stats[phy]['PER'] = []
					corrections_temperature_stats[phy]['BF'] = []
					corrections_temperature_stats[phy]['PER'].append(np.average(auxiliary_stat))
					corrections_temperature_stats[phy]['BF'].append(np.average(auxiliary_bf))
				else:
					corrections_temperature_stats[phy]['PER'].append(np.average(auxiliary_stat))
					corrections_temperature_stats[phy]['BF'].append(np.average(auxiliary_bf))


			auxiliary_stat = []
			auxiliary_bf = []
		self.print_dictionary(corrections_temperature_stats)
		xlabel='Beating Frequency (Hz)'
		ylabel='PER (%)'
		plot_title = f'PER vs Beating Frequency'
		if bv_mode:
			mode = 'BV'
		else:
			mode = 'No_BV'
		plotter.plot_beating_v_per_phy(corrections_temperature_stats, mode,xlabel, ylabel, plot_title)
		plt.show()

if __name__ == '__main__':
	arg_parser = argparse.ArgumentParser()
	arg_parser.add_argument('-bv', '--bit_voting', type=int, help='Whether Bit Voting error correction scheme is enabled or not', required=True)
	arg_parser.add_argument('-pw', '--pairwise', type=int, help='Whether the plotting should be done pairwise or not', required=True)
	arg_parser.add_argument('-stat', '--stat_name', type=str, help='Name of the statistic that we want to plot', required=True)
	arg_parser.add_argument('-phy', '--physical_layer', type=str, help='Physical layer for which the plot is to be drawn', required=False)
	arg_parser.add_argument('-temp', '--temperature', type=str, help='Temperature for which the plot is to be drawn', required=True)
	args = arg_parser.parse_args()
	print(args.bit_voting)
	stat_plotter = StatsPlotter()

	if args.bit_voting == 1:
		bv = True
	else:
		bv = False
	
	if args.pairwise == 1:
		pair_wise = True
	else:
		pair_wise = False

	# stat_plotter.plot_average_bit_errors()
	stat_plotter.plot_avg_prr_v_bf_temperature_all_phys('src',str(122), str(126), str(124), args.temperature, args.stat_name)
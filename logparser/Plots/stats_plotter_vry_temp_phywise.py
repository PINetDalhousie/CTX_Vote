from typing import Any
import matplotlib.pyplot as plt
from read_log_files import FileReader
import pandas as pd
import json
from logparser.Plots.Plotting import DataPlotter
import numpy as np
import datetime
import argparse
import sys

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

	#Complete this function
	def plot_avg_prr_v_temperature_one_phy(self, heating_node, src, fwd, dst, stat_name, physical_layer):
		"""
			This function plots the PDR/PRR/PER vs temperature for a specific physical layer.
			Here the Average PRR/PDR for each temperature is considered
			:param heating_node: Node which is being heated
			:param bv_mode: Mode of bit voting
			:param src: Source node id
			:param fwd: Forwarder node id
			:param dst: Destination node id
			:param stat_name: Name of the statistic that we want to plot against temperature
			:param physical_layer: Physical layer for which the plot is to be drawn
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
		stat_name_t = None
		if stat_name == 'PER':
			stat_name = 'PRR'
			stat_name_t = 'PER'			

		csv_files_dict_bv = reader.get_dcube_csv_files_pair_temperature(True, str(src), str(fwd), str(dst))
		reader = FileReader(path)
		csv_files_dict_no_bv = reader.get_dcube_csv_files_pair_temperature(False, str(src), str(fwd), str(dst))
		plotter = DataPlotter(path, 'PHY_BLE_2M', 64, False)
		sorted_bv_files = dict(sorted(csv_files_dict_bv[physical_layer].items()))
		sorted_no_bv_files = dict(sorted(csv_files_dict_no_bv[physical_layer].items()))
		for (temperature_bv, csv_temp_files_bv), (temperature_no_bv, csv_temp_files_no_bv) in zip(sorted_bv_files.items(), sorted_no_bv_files.items()):
			auxiliary_prr_bv = []
			auxiliary_prr_no_bv = []
			print(f"--------------- Temperature: {temperature_bv }{temperature_no_bv} -----------------------")
			
			for (csv_file_bv, csv_file_no_bv) in zip(csv_temp_files_bv, csv_temp_files_no_bv):
				print(f"Reading file {csv_file_bv}\n")
				print(f"Reading file {csv_file_no_bv}\n")
				data_bv = pd.read_csv(csv_file_bv)
				data_no_bv = pd.read_csv(csv_file_no_bv)
				if not data_bv.empty:
						auxiliary_prr_bv.append(data_bv[stat_name].values[0])
				if not data_no_bv.empty:
						auxiliary_prr_no_bv.append(data_no_bv[stat_name].values[0])

			temperature = int(temperature_no_bv[:-1])
			if temperature not in self.temperature_v_stats_phywise['BV']['temperature_stat']:
				self.temperature_v_stats_phywise['BV']['temperature_stat'][temperature] = np.average(auxiliary_prr_bv)
				if stat_name_t is not None and stat_name_t == 'PER':
					self.temperature_v_stats_phywise['BV']['temperature_stat'][temperature] = 100 - np.average(auxiliary_prr_bv)
			
			if temperature not in self.temperature_v_stats_phywise['No_BV']['temperature_stat']:
				self.temperature_v_stats_phywise['No_BV']['temperature_stat'][temperature] = np.average(auxiliary_prr_no_bv)
				if stat_name_t is not None and stat_name_t == 'PER':
					self.temperature_v_stats_phywise['No_BV']['temperature_stat'][temperature] = 100 - np.average(auxiliary_prr_no_bv)
			print('BV: ', auxiliary_prr_bv)
			print('No BV: ', auxiliary_prr_no_bv)
			auxiliary_prr_bv = []
			auxiliary_prr_no_bv = []
		self.print_dictionary(self.temperature_v_stats_phywise)
		plotter.plot_prr_v_temperature_one_phy(self.temperature_v_stats_phywise, x_label, y_label, plot_title, physical_layer)
		if stat_name_t is not None and stat_name_t == 'PER':
			stat_name = 'PER'
		fig_save_path = '/home/burhanuddin/Desktop/osf/logparser/Graphs/Increasing_Temperature/'+physical_layer+'/'+stat_name+'_vs_Temp/'+f'plot_{stat_name}_vs_Temp_{physical_layer}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.png'
		# plt.savefig(fig_save_path)
		# plt.show()

	
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

	def plot_average_corrections_vs_bf_one_phy(self, heating_node, src, fwd, dst, physical_layer):
		"""
			This function plots the average corrections vs Beating Frequency for a specific physical layer for all temperatures.
			:param heating_node: Node which is being heated
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

		reader = FileReader(path)
		csv_files_dict = reader.get_dcube_csv_files_pair_temperature(True, str(src), str(fwd), str(dst))
		plotter = DataPlotter(path, physical_layer, 255, False)
		csv_files_tempwise = csv_files_dict[physical_layer]
		auxiliary_corrections = []
		auxiliary_bf = []
		print(f"--------------- PHY: {physical_layer} -----------------------")
		for temperature, csv_files in csv_files_tempwise.items():
			auxiliary_corrections = []
			auxiliary_bf = []
			print(f"--------------- Temperature: {temperature} -----------------------")
			for csv_file in csv_files:
				print(f"Reading file {csv_file}\n")
				data = pd.read_csv(csv_file)
				if not data.empty:
					auxiliary_corrections.append(data['Total_Corrections'].values[0])
					auxiliary_bf.append(data['Beating_Frequency'].values[0])
			temp = int(temperature[:-1])
			print('Corrections: ', auxiliary_corrections)
			print('Beating Frequency: ', auxiliary_bf)
			if  'Corrections' not in self.phy_wise_stats['BV']:
				print('average: ', np.average(auxiliary_corrections))
				self.phy_wise_stats['BV']['Corrections'] = []
				self.phy_wise_stats['BV']['BF'] = []
				self.phy_wise_stats['BV']['Corrections'].append(np.average(auxiliary_corrections))
				self.phy_wise_stats['BV']['BF'].append(np.average(auxiliary_bf))
			else:
				self.phy_wise_stats['BV']['Corrections'].append(np.average(auxiliary_corrections))
				self.phy_wise_stats['BV']['BF'].append(np.average(auxiliary_bf))
			auxiliary_corrections = []
			auxiliary_bf = []

		self.print_dictionary(self.phy_wise_stats)
		plotter.plot_beating_v_per_phy(self.phy_wise_stats, 'BV', 'Beating Frequency (Hz)', 'Average Corrections', 'Average Corrections vs Beating Frequency', 'Corrections', physical_layer, True)

		plt.show()

	def plot_average_stat_vs_bf_one_phy_all_temp(self, heating_node, src, fwd, dst, physical_layer, stat_name):
		"""
			This function plots the average PRR/PDR/PER vs Beating Frequency for a specific physical layer from the temperature data.
			All the temperature values are chained together and not bifurcated according to temperature.
			:param heating_node: Node which is being heated
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

		reader = FileReader(path)
		csv_files_dict_bv = reader.get_dcube_csv_files_pair_temperature(True, str(src), str(fwd), str(dst))
		reader_2 = FileReader(path)
		csv_files_dict_no_bv = reader_2.get_dcube_csv_files_pair_temperature(False, str(src), str(fwd), str(dst))
		stat_name_t = None
		if stat_name == 'PER':
			stat_name = 'PRR'
			stat_name_t = 'PER'
		plotter = DataPlotter(path, 'PHY_BLE_2M', 64, False)
		csv_files_tempwise_bv = dict(sorted(csv_files_dict_bv[physical_layer].items()))
		csv_files_tempwise_no_bv = dict(sorted(csv_files_dict_no_bv[physical_layer].items()))
		self.print_dictionary(csv_files_tempwise_bv)
		self.print_dictionary(csv_files_tempwise_no_bv)
		# sys.exit(1)
		#BV
		print('--------------BV------------------')
		for (temperature_bv, phy_stat_bv_csv_files),(temperature_no_bv, phy_stat_no_bv_csv_files) in zip(csv_files_tempwise_bv.items(), csv_files_tempwise_no_bv.items()):
			print(f"--------------- Temperature: {temperature_bv }{temperature_no_bv} -----------------------")
			auxiliary_stat_bv = []
			auxiliary_bf_bv = []
			auxiliary_stat_no_bv = []
			auxiliary_bf_no_bv = []
			# sys.exit(1)
			for (csv_file_bv, csv_file_no_bv) in zip(phy_stat_bv_csv_files, phy_stat_no_bv_csv_files):
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
			if stat_name not in self.phy_wise_stats['BV']:
				self.phy_wise_stats['BV'][stat_name] = []
				self.phy_wise_stats['BV']['BF'] = []
				self.phy_wise_stats['BV'][stat_name].append(np.average(auxiliary_stat_bv))
				self.phy_wise_stats['BV']['BF'].append(np.average(auxiliary_bf_bv))
			else:
				self.phy_wise_stats['BV'][stat_name].append(np.average(auxiliary_stat_bv))
				self.phy_wise_stats['BV']['BF'].append(np.average(auxiliary_bf_bv))

			if stat_name not in self.phy_wise_stats['No_BV']:
				self.phy_wise_stats['No_BV'][stat_name] = []
				self.phy_wise_stats['No_BV']['BF'] = []
				self.phy_wise_stats['No_BV'][stat_name].append(np.average(auxiliary_stat_no_bv))
				self.phy_wise_stats['No_BV']['BF'].append(np.average(auxiliary_bf_no_bv))
			else:
				self.phy_wise_stats['No_BV'][stat_name].append(np.average(auxiliary_stat_no_bv))
				self.phy_wise_stats['No_BV']['BF'].append(np.average(auxiliary_bf_no_bv))
			auxiliary_stat_bv = []
			auxiliary_bf_bv = []
			auxiliary_stat_no_bv = []
			auxiliary_bf_no_bv = []
		self.print_dictionary(self.phy_wise_stats)
		xlabel = 'Beating Frequency (Hz)'
		if stat_name_t is not None and stat_name_t == 'PER':
			ylabel = 'PER (%)'
			plot_title = f'PER vs Beating Frequency'
			fig_name = f'plot_PER_vs_BF_all_temp_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.png'
		else:
			ylabel = f'{stat_name} (%)'
			plot_title = f'{stat_name} vs Beating Frequency'
			fig_name = f'plot_{stat_name}_vs_BF_all_temp_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.png'
		fig_save_path = '/home/burhanuddin/Desktop/osf/logparser/Graphs/Increasing_Temperature/All_phys_graphs'+'/'+fig_name
		plotter.plot_beating_v_per_phy(self.phy_wise_stats, 'BV', 'Beating Frequency (Hz)', 'PDR', 'PDR vs Beating Frequency', 'PDR', physical_layer, True)
		
		# plt.savefig(fig_save_path)
		plt.show()


	def plot_avg_bf_per_across_temp_one_phy(self, heating_node, src, fwd, dst, physical_layer, stat_name):
		"""
			This function plots the beating frequency vs PER/PRR/PDR for a specific physical layer, with temperature data
			:param heating_node: Node which is being heated
			:param src: Source node id
			:param fwd: Forwarder node id
			:param dst: Destination node id
			:param physical_layer: Physical layer for which the plot is to be drawn
			:param stat_name: Name of the statistic that we want to plot against temperature
			:return: None
		"""
		path = '/home/burhanuddin/Desktop/osf/logparser/Dcube_Logs/Templab'
		if heating_node == 'fwd':
			path = path + '/Neg8dBm/Increasing_Temperature/Heating_Forwarder'
		elif heating_node == 'src':
			path = path + '/Neg8dBm/Increasing_Temperature/Heating_Source/Heating_Source_inc_10'

		reader = FileReader(path)
		temperature_stats = {
			'BV':{
				'BF':[],
			},
			'No_BV':{
				'BF':[],
			}
		}
		csv_files_dict_bv = reader.get_dcube_csv_files_pair_temperature(True, str(src), str(fwd), str(dst))
		reader_2 = FileReader(path)
		csv_files_dict_no_bv = reader_2.get_dcube_csv_files_pair_temperature(False, str(src), str(fwd), str(dst))
		stat_name_t = stat_name
		if stat_name == 'PER':
			stat_name = 'PRR'
			stat_name_t = 'PER'
		plotter = DataPlotter(path, 'PHY_BLE_2M', 64, False)

		#BV
		print('--------------BV------------------')
		print(f"--------------- PHY: {physical_layer} -----------------------")
		physical_layer_dict_bv = dict(sorted(csv_files_dict_bv[physical_layer].items()))
		physical_layer_dict_no_bv = dict(sorted(csv_files_dict_no_bv[physical_layer].items()))
		for (temperature_bv, csv_files_bv), (temperature_no_bv, csv_files_no_bv) in zip(physical_layer_dict_bv.items(), physical_layer_dict_no_bv.items()):
			auxiliary_stat_bv = []
			auxiliary_bf_bv = []
			auxiliary_stat_no_bv = []
			auxiliary_bf_no_bv = []
			print(f'--------------- BV: {temperature_bv} No_BV:{temperature_no_bv}-----------------------')
			for (csv_file_bv, csv_file_no_bv) in zip(csv_files_bv, csv_files_no_bv):
				print(f"Reading file {csv_file_bv}\n")
				print(f"Reading file {csv_file_no_bv}\n")
				data_bv = pd.read_csv(csv_file_bv)
				data_no_bv = pd.read_csv(csv_file_no_bv)
				if not data_bv.empty:
						if stat_name_t and stat_name_t == 'PER':
							auxiliary_stat_bv.append(100 - data_bv[stat_name].values[0])
						else:
							auxiliary_stat_bv.append(data_bv[stat_name].values[0])
						auxiliary_bf_bv.append(data_bv['Beating_Frequency'].values[0])
				if not data_no_bv.empty:
						if stat_name_t and stat_name_t == 'PER':
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
			if stat_name_t not in temperature_stats['BV']:
				temperature_stats['BV'][stat_name_t] = []
				temperature_stats['BV']['BF'] = []
				temperature_stats['BV'][stat_name_t].append(np.average(auxiliary_stat_bv))
				temperature_stats['BV']['BF'] .append(np.average(auxiliary_bf_bv))
			else:
				temperature_stats['BV'][stat_name_t].append(np.average(auxiliary_stat_bv))
				temperature_stats['BV']['BF'] .append(np.average(auxiliary_bf_bv))
			if stat_name_t not in temperature_stats['No_BV']:
				temperature_stats['No_BV'][stat_name_t] = []
				temperature_stats['No_BV']['BF'] = []
				temperature_stats['No_BV'][stat_name_t].append(np.average(auxiliary_stat_no_bv))
				temperature_stats['No_BV']['BF'].append(np.average(auxiliary_bf_no_bv))
			else:
				temperature_stats['No_BV'][stat_name_t].append(np.average(auxiliary_stat_no_bv))
				temperature_stats['No_BV']['BF'] .append(np.average(auxiliary_bf_no_bv))
			auxiliary_stat_bv = []
			auxiliary_bf_bv = []
			auxiliary_stat_no_bv = []
			auxiliary_bf_no_bv = []
		self.print_dictionary(temperature_stats)
		xlabel = 'Beating Frequency (Hz)'
		ylabel = stat_name_t+' (%)'
		plot_title = f'{stat_name_t} vs Beating Frequency'

		plotter.plot_beating_v_per_phy(temperature_stats, True,xlabel,ylabel,plot_title, stat_name_t,physical_layer, True,)
		
		plt.show()

if __name__ == '__main__':
	arg_parser = argparse.ArgumentParser()
	arg_parser.add_argument('-bv', '--bit_voting', type=int, help='Whether Bit Voting error correction scheme is enabled or not', required=True)
	arg_parser.add_argument('-pw', '--pairwise', type=int, help='Whether the plotting should be done pairwise or not', required=True)
	arg_parser.add_argument('-stat', '--stat_name', type=str, help='Name of the statistic that we want to plot', required=True)
	arg_parser.add_argument('-phy', '--physical_layer', type=str, help='Physical layer for which the plot is to be drawn', required=True)
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

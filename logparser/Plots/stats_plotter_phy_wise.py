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

	def plot_beating_vs_prr_pdr_all_phys(self, power, bv, stat_name, pair_wise=False, src=None, fwd=None, dst=None):
		"""
			This function plots the beating frequency vs PRR for all physical layers for a single mode of bit voting
			:param power: Power used for the experiment
			:param stat_name: Name of the statistic that we want to plot against beating frequency
			:param bv: Boolean value to indicate if bit voting was used or not
			:param pair_wise: Boolean value to indicate if the plotting is to be done for a specific node pair
			:param src: Source node id
			:param fwd: Forwarder node id
			:param dst: Destination node id
			:return: None
		"""
		path = f'/home/burhanuddin/Desktop/osf/logparser/Dcube_Logs/Templab/{power}'
		reader = FileReader(path)
		if not pair_wise:
			csv_files_dict = reader.get_dcube_stat_csv_files(bv)
		else:
			csv_files_dict = reader.get_dcube_csv_files_pair(bv, str(src), str(fwd), str(dst))

		plotter = DataPlotter(path, 'PHY_BLE_2M', 64, False)
		for phy, phy_stat_csv_files in csv_files_dict.items():
			print(f"--------------- PHY: {phy} -----------------------")
			self.bf_v_stat[phy][stat_name] = []
			for csv_file in phy_stat_csv_files:
				print(f"Reading file {csv_file}")
				data = pd.read_csv(csv_file)
				if not data.empty:
					self.bf_v_stat[phy][stat_name].append(data[stat_name].values[0])
					self.bf_v_stat[phy]['Beating Frequency'].append(data['Beating_Frequency'].values[0])
				print('--------------------------------------------------------')

		print('\n ---------------------- Complete Dictionary ----------------------------------- \n')
		self.print_dictionary(self.bf_v_stat)       
		print('\n --------------------------------------------------------- \n')
		if bv:
			bv_mode = 'with_bv'
		else:
			bv_mode = 'no_bv'
		
		x_l = 'Beating Frequency (Hz)'
		y_l = stat_name + " (%)"
		plot_title = f'Beating Frequency vs {stat_name}'
		plotter.plot_beating_v_prr_pdr_all_phy(self.bf_v_stat, bv_mode, x_l, y_l, plot_title, stat_name)
		plt.show()
	
	def plot_beating_v_prr_pdr_phywise(self, power, physical_layer, stat_name):
		"""
			This function plots the beating frequency vs PRR/PDR for a specific physical layer.
			:param power: Power used for the experiment
			:param physical_layer: Physical layer used for the experiment
			:param stat_name: Name of the statistic that we want to plot against beating frequency
			:return: None
		"""
		path = f'/home/burhanuddin/Desktop/osf/logparser/Dcube_Logs/Templab/{power}/Same_Temperature'
		# path = '/home/burhanuddin/Desktop/osf/logparser/Dcube_Logs/Templab/Neg8dBm/Increasing_Temperature/Heating_Source/Heating_Source_inc_10/'
		reader = FileReader(path)


		csv_files_dict_bv = reader.get_dcube_csv_files_pair(True, str(122), str(126), str(124))
		reader_2 = FileReader(path)
		csv_files_dict_no_bv = reader_2.get_dcube_csv_files_pair(False, str(122), str(126), str(124))
		x_l = 'Beating Frequency (Hz)'
		y_l = stat_name + ' (%)'
		plot_title = f'Beating Frequency vs {stat_name}'
		self.bf_v_stats_phywise['BV'][stat_name] = []
		self.bf_v_stats_phywise['No_BV'][stat_name] = []
		print(f'-------------------------- {stat_name} ----------------------------')
		plotter = DataPlotter(path, 'PHY_BLE_2M', 64, False)
		for (csv_file_bv, csv_file_no_bv) in zip(csv_files_dict_bv[physical_layer], csv_files_dict_no_bv[physical_layer]):
			print('\n--------------------------------------------------------\n')
			print(f"Reading file {csv_file_bv}")
			print(f"Reading file {csv_file_no_bv}")
			data_bv = pd.read_csv(csv_file_bv)
			data_no_bv = pd.read_csv(csv_file_no_bv)
			if not data_bv.empty:
				self.bf_v_stats_phywise['BV'][stat_name].append(data_bv[stat_name].values[0])
				self.bf_v_stats_phywise['BV']['Beating Frequency'].append(data_bv['Beating_Frequency'].values[0])
			if not data_no_bv.empty:
				self.bf_v_stats_phywise['No_BV'][stat_name].append(data_no_bv[stat_name].values[0])
				self.bf_v_stats_phywise['No_BV']['Beating Frequency'].append(data_no_bv['Beating_Frequency'].values[0])
		
		plotter.plot_beating_v_prr_pdr_phy(self.bf_v_stats_phywise['BV'], physical_layer, 'BV', x_l, y_l, plot_title, stat_name)
		print(f"Standard Deviation {stat_name} BV: {str(np.std(self.bf_v_stats_phywise['BV'][stat_name]))}")
		print(f"Average {stat_name} BV {str(np.average(self.bf_v_stats_phywise['BV'][stat_name]))}")
		print('Standard Deviation BF BV: ', str(np.std(self.bf_v_stats_phywise['BV']['Beating Frequency'])))
		print('Average BF BV', str(np.average(self.bf_v_stats_phywise['BV']['Beating Frequency'])))

		plotter.plot_beating_v_prr_pdr_phy(self.bf_v_stats_phywise['No_BV'], physical_layer, 'No BV', x_l, y_l, plot_title, stat_name)
		print(f"Standard Deviation {stat_name} No_BV: {str(np.std(self.bf_v_stats_phywise['No_BV'][stat_name]))}")
		print(f"Average {stat_name} No_BV {str(np.average(self.bf_v_stats_phywise['No_BV'][stat_name]))}")
		print('Standard Deviation BF No_BV: ', str(np.std(self.bf_v_stats_phywise['No_BV']['Beating Frequency'])))
		print('Average BF No_BV:', str(np.average(self.bf_v_stats_phywise['No_BV']['Beating Frequency'])))
		print('--------------------------------------------------------')
		
		if stat_name == 'PRR':
			plt.savefig(f'./Graphs/Same_Temperature/Beating_vs_PRR_graphs_S=122_F=126_D=124/prr_vs_bf_{physical_layer}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.png')
		elif stat_name == 'PDR':
			plt.savefig(f'./Graphs/Same_Temperature/Beating_vs_PDR_graphs_S=122_F=126_D=124/pdr_vs_bf_{physical_layer}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.png')

		# plt.savefig(f'./Graphs/Beating_vs_PRR_graphs_S=122_F=126_D=124/beating_vs_prr_{physical_layer}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.png')
	
	#Check the plotting function of this function
	def plot_beating_freq_vs_corrections_phywise(self, power, physical_layer):
		"""
			This function plots the beating frequency vs total corrections for a specific physical layer.
			:param power: Power used for the experiment
			:param physical_layer: Physical layer used for the experiment
			:return: None
		"""

		path = f'/home/burhanuddin/Desktop/osf/logparser/Dcube_Logs/Templab/{power}'
		reader = FileReader(path)

		csv_files_dict_bv = reader.get_dcube_csv_files_pair(True, str(122), str(126), str(124))
		plotter = DataPlotter(path, 'PHY_BLE_2M', 64, False)
		self.bf_v_stats_phywise['BV']['Corrections'] = []
		for csv_file in csv_files_dict_bv[physical_layer]:
			print(f"Reading file {csv_file}")
			data = pd.read_csv(csv_file)
			if not data.empty:
					self.bf_v_stat['Corrections'].append(data['Total_Corrections'].values[0])
					self.bf_v_stat['Beating Frequency'].append(data['Beating_Frequency'].values[0])
		self.print_dictionary(self.bf_v_stat)
		plotter.plot_beating_v_total_corrections(self.bf_v_stats_phywise, physical_layer, 'BV')
		plt.savefig(f'./Boxplots/beating_vs_correctoins_{physical_layer}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.png')

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
		
		plt.savefig(fig_save_path)
		# plt.show()

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

	def plot_average_corrections_vs_bf_one_phy(self, heating_node, src, fwd, dst, physical_layer):
		"""
			This function plots the average corrections vs Beating Frequency for a specific physical layer.
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

	def plot_average_stat_vs_bf_one_phy(self, heating_node, src, fwd, dst, physical_layer, stat_name):
		"""
			This function plots the average PRR/PDR/PER vs Beating Frequency for a specific physical layer.
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

		#BV
		print('--------------BV------------------')
		for (temperature_bv, phy_stat_bv_csv_files),(temperature_no_bv, phy_stat_no_bv_csv_files) in zip(csv_files_tempwise_bv.items(), csv_files_tempwise_no_bv.items()):
			print(f"--------------- Temperature: {temperature_bv }{temperature_no_bv} -----------------------")
			auxiliary_stat_bv = []
			auxiliary_bf_bv = []
			auxiliary_stat_no_bv = []
			auxiliary_bf_no_bv = []
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

	#Uncomment the function calls to plot the desired graphs

	#Plot beating vs PRR/PDR for all physical layers
	# stat_plotter.plot_beating_vs_prr_pdr_all_phys('Neg8dBm', bv, 'PDR', pair_wise, 122, 126, 124)
	# stat_plotter.plot_beating_vs_prr_pdr_all_phys('Neg8dBm', bv, 'PDR', pair_wise, 122, 126, 124)
	# plt.show()

	#Plot beating vs PDR/PRR for a specific physical layer
	# stat_plotter.plot_beating_v_prr_pdr_phywise('Neg8dBm', 'PHY_BLE_1M', 'PRR')

	#plotting average corrections vs beating frequency
	# stat_plotter.plot_average_corrections_v_bf('Neg8dBm', True, 122, 126, 124)
    
	#Plot beating vs total corrections for a specific physical layer
	# stat_plotter.plot_beating_freq_vs_corrections('Neg8dBm', 'PHY_BLE_500K')

	#Plot PRR/PDR vs temperature for all physical layers
	# stat_plotter.plot_avg_prr_v_temperature_all_phys('src', bv, 122, 126, 124, 'PRR')
	# stat_plotter.plot_avg_prr_v_temperature_one_phy('src', 122, 126, 124, args.stat_name, args.physical_layer)

	# #Plot Temperature vs Beating Frequency for all physical layers
	# stat_plotter.plot_avg_bf_v_temperature_all_phys('src', bv, 122, 126, 124, args.physical_layer)

	#Plot average corrections vs temperature for all physical layers
	# stat_plotter.plot_average_corrections_vs_temperature('src', bv, 122, 126, 124)
	# stat_plotter.plot_average_corrections_vs_bf_one_phy('src', 122, 126, 124, args.physical_layer)
	# stat_plotter.plot_average_stat_vs_bf_one_phy('src', 122, 126, 124, args.physical_layer, args.stat_name)


	#Plot PRR/PDR vs temperature for all physical layers for a specific temperature
	# stat_plotter.plot_avg_prr_v_bf_temperature_all_phys('src', 122, 126, 124, args.temperature, args.stat_name)

	#Plot BF vs PER for all physical layer(s)
	# stat_plotter.plot_avg_bf_per_across_temp_all_phys('src',bv, 122, 126, 124, 'PHY_BLE_1M')

	#Plot BF vs PER/PRR/PDR for a specific physical layer with temperature data
	# stat_plotter.plot_avg_bf_per_across_temp_one_phy('src', 122, 126, 124, args.physical_layer, args.stat_name)

	stat_plotter.plot_average_bit_errors()
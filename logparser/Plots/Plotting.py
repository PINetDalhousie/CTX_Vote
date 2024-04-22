import matplotlib.pyplot as plt
import pandas as pd
import datetime
import seaborn as sns
import os
import sys
sys.path.append('../')
from read_log_files import FileReader
import datetime
import numpy as np
from scipy.stats import t, sem
import math
import json
class DataPlotter:
    """ 
    This class plots different properties of data from the CSV files
    """
    def __init__(self, main_dp, dp, pkt_len, bv) -> None:
        self.error_positions = {}
        self.corrected_error_positions = {}
        self.phys_lyr = ''
        self.fr = FileReader(dp)
        self.logs_dir = main_dp
        self.file_paths = []
        # Colour-blind cycle by thriveth: https://gist.github.com/thriveth
        self.CB_color_cycle = ['#377eb8', '#ff7f00', '#4daf4a',
                                '#f781bf', '#a65628', '#984ea3',
                                '#999999', '#e41a1c', '#dede00']

        self.isbv = bv
        if self.isbv:
            self.pkt_len = pkt_len
        else:
            self.pkt_len = pkt_len
    
    def print_dictionary(self, inp_dict):
        """
                This funcself.bf_v_stats_phywise['BV'][stat_name_t]tion prints the dictionary in a readable format
                :param inp_dict: Dictionary to be printed
                :return: None
        """

        formatted_dict = json.dumps(inp_dict, default=str, indent=4)
        print(formatted_dict)
    
    def get_all_file_paths(self) -> None:
        """
        This function gets the file paths dictionary from the FileReader class
        :return: None
        """
        self.file_paths = self.fr.get_csv_file_paths()
    
    def set_physical_layer(self, pl) -> None:
        """
        This function sets the physical layer for which data plotting is being carried out
        :return: None
        """
        self.phys_lyr = pl
    
    def get_error_positions(self) -> None:
        """
        This function calculates the frequency of errors at each bit position from the CSV files.
        The error positions are stored in a dictionary with the error position as the key 
        and the frequency of error at that bit as the value
        :return: None
        """
        # Read the data from the csv file
        for filename in self.file_paths:
            data = pd.read_csv(filename)
            # Extract the error positions
            for (err_poses, ok, rnd) in zip(data["ERRORS"], data["BV_SUCCESS_FLAG"], data["ROUND"]):
                indices = err_poses.strip("\{\}").split(";")
                if len(indices) > 0:
                    for index in indices:
                        pair = index.split(":")
                        if len(pair) > 1:
                            i = int(pair[0])

                            # stop in case of errors
                            try:
                                freq = int(pair[1])
                            except:
                                print("err in rnd ", rnd, " index ", i)
                                exit()

                            if(i > 2040 or freq > 6):
                                print("err in rnd ", rnd, " index ", i)
                                # exit()
                                continue

                            if i not in self.error_positions:
                                self.error_positions[i] = freq
                            else:
                                self.error_positions[i] += freq

                            if ok == 1 and i not in self.corrected_error_positions:
                                self.corrected_error_positions[i] = freq
                            elif ok == 1 and i in self.corrected_error_positions:
                                self.corrected_error_positions[i] += freq
    
    def get_error_positions_no_bv(self) -> None:
        """
        This function calculates the error positions from the CSV files.
        The error positions are stored in a dictionary with the error position as the key 
        and the frequency of error at that bit as the value
        :return: None
        """
        # Read the data from the csv file
        for filename in self.file_paths:
            data = pd.read_csv(filename)
            # Extract the error positions
            for (err_poses, rnd) in zip(data["ERRS"], data["ROUND"]):
                indices = err_poses.strip("\{\}").split(";")
                if len(indices) > 0:
                    for index in indices:
                        pair = index.split(":")
                        if len(pair) > 1:
                            i = int(pair[0])

                            # stop in case of errors
                            try:
                                freq = int(pair[1])
                            except:
                                print("err in rnd ", rnd, " index ", i)
                                exit()

                            if(i > 2040 or freq > 6):
                                print("err in rnd ", rnd, " index ", i)
                                # exit()
                                continue

                            if i not in self.error_positions:
                                self.error_positions[i] = freq
                            else:
                                self.error_positions[i] += freq

    def plot_error_positions(self, error_positions, plot_title, temperature=None, corrected_error_positions=None) -> None:
        """
        This function plots the error positions from the CSV files.
        :param error_positions: Dictionary of error positions and their frequencies
        :param plot_title: Title of the plot
        :param temperature: Temperature at which the data was collected
        :param corrected_error_positions: Dictionary of corrected error positions and their frequencies
        :return: None
        """

        # Sort the data dictionary by key
        sorted_data = dict(sorted(error_positions.items()))
        if temperature:
            name_of_fig = self.logs_dir+"/Graphs/"+self.phys_lyr + "_error_positions_"+datetime.datetime.now().strftime("%Y%m%d_%H%M")+"_"+temperature+".pdf"
        else:
            name_of_fig = self.logs_dir+"/Graphs/"+self.phys_lyr + "_error_positions_"+datetime.datetime.now().strftime("%Y%m%d_%H%M")+".pdf"

        # Set up the figure and axes
        fig, ax = plt.subplots(figsize=(3, 3))
        # Create the bar plot
        if len(sorted_data) > 0:
            bit_indices = list(sorted_data.keys())
            bit_errors = list(sorted_data.values())
            print('Bit Errors: ',len(bit_errors))
            
            df = pd.DataFrame({'Bit Index':bit_indices, 'Bit Errors':bit_errors})
            sns.set_context("poster", font_scale=7, rc={"lines.linewidth": 2})
            

            
            plot = sns.barplot(df,x='Bit Index',y='Bit Errors', color="#00008B", label="Errors", ax=ax)

            # Set labels and title
            plot.set_xlabel('Bit Index in Packet', weight='bold', fontdict={'size':12})
            plot.set_ylabel('Absolute Errors', weight='bold', fontdict={'size':12})

            # Remove spines
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            # # Adjust x-axis tick labels rotation
            if 'BLE' in self.phys_lyr:
                
                plot.set_xticks(np.arange(0, 1501, 500))
                plot.set_xticklabels([str(v) for v in np.arange(0, 1501, 500)],weight='bold', fontsize=12)
            else:
                plot.set_xticks([0, 500, 1000])
                plot.set_xticklabels([0, 500, 1000], weight='bold', fontsize=12)
            # val = plt.locator_params(axis='x', nbins=4) # set number of ticks on x-axis
            
            plt.yticks(fontweight='bold', fontsize=12)
            plt.xticks(fontweight='bold', fontsize=12)

            # Display the plot
            # plt.show()
            # plt.tight_layout()
            plt.savefig(name_of_fig, format='pdf' ,bbox_inches='tight') #
            print('Saved plot to ', name_of_fig)
        else:
            
            print("No errors found")

    def plot_fft(self, sample_freq, power, cutoff_freq, temperature=None) -> None:
        """
        This function plots the FFT of the error positions from the CSV files.
        :param sample_freq: Sample frequency
        :param power: Power
        :param cutoff_freq: Cutoff frequency
        :return: None
        """

        # Plot the original signal and FFT result
        sns.set_context("poster", font_scale=4, rc={"lines.linewidth": 1})
        if len(sample_freq) > 0 and len(power) > 0:
            plt.figure(figsize=(3, 3))

            plt.plot(sample_freq, power, label='FFT')
            plt.xlabel("Frequency (Hz)", weight='bold', fontsize=7) 
            plt.xticks(fontsize=7, weight='bold')
            plt.ylabel("Amplitude", weight='bold', fontsize=7)
            plt.yticks(fontsize=7, weight='bold')
            plt.xlim(1, cutoff_freq)

            # plt.tight_layout()
            if not os.path.exists(self.logs_dir+"/Graphs/"):
                os.makedirs(self.logs_dir+"/Graphs/")
            
            if temperature:
                name_of_the_plot = self.logs_dir+"/Graphs/"+f'/fft_{self.phys_lyr}_'+datetime.datetime.now().strftime("%Y%m%d_%H%M")+"_"+temperature+".png"
            else:
                name_of_the_plot = self.logs_dir+"/Graphs/"+f'/fft_{self.phys_lyr}_'+datetime.datetime.now().strftime("%Y%m%d_%H%M")+".pdf"
            print('Saving FFT Figure as: ',name_of_the_plot)
            plt.savefig(name_of_the_plot, format='pdf', bbox_inches='tight')
            # plt.show()
        else:
            print('No FFT data to plot')
    
    
    def plot_beating_v_prr_pdr_all_phy(self, inp_dict, x_label, y_label, plt_title, stat_name) -> None:
        """
            This function plots the beating frequency vs PRR for all PHY layers
            :param inp_dict: Dictionary of beating frequency and PRR for all physical layers
            :param x_label: X-axis label
            :param y_label: Y-axis label
            :param plt_title: Plot title
            :param stat_name: Name of the statistic that we want to plot against beating frequency
            :return: None
        """
        
        # Iterate through the dictionary and plot each line
        beating_frequency=[]
        stat_vals_each=[]
        markers = {'PHY_BLE_1M':'o', 'PHY_BLE_2M':'s', 'PHY_BLE_125K':'D', 'PHY_BLE_500K':'^'}

        for phy, phy_stats in inp_dict.items():
            print('------------------ PHY: ',phy,'--------------------')
            plt.scatter(phy_stats['BV']['Beating_Frequency'],phy_stats['BV'][stat_name],  label=phy+" "+'BV', marker=markers[phy])
            plt.scatter(phy_stats['No_BV']['Beating_Frequency'],phy_stats['No_BV'][stat_name], label=phy+" "+'No_BV', marker=markers[phy])
            beating_frequency = []
            stat_vals_each = []

        # Set labels and title
        plt.yticks(np.arange(0,101,5))
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(plt_title)

        # Add a legend
        plt.legend()

        # Show the plot
        # plt.show()
    
    def bar_plot_all_stats_phy(self, inp_dict, x_label, y_label, plt_title, stat_name) -> None:
        """
            This function plots a bar plot the PDR for all PHY layers
            :param inp_dict: Dictionary of beating frequency and PRR for all physical layers
            :param x_label: X-axis label
            :param y_label: Y-axis label
            :param plt_title: Plot title
            :param stat_name: Name of the statistic that we want to plot against beating frequency
            :return: None
        """
        
        # Iterate through the dictionary and plot each line
        stat_vals_each_bv=[]
        stat_vals_each_no_bv=[]
        markers = {'1M':'s','2M':'o',  '125K':'^', '500K':'D', 'IEEE':'x'}
        width = 0.35
        for phy, phy_stats in inp_dict.items():
            print('------------------ PHY: ',phy,'--------------------')
            
            stat_vals_each_bv.append(phy_stats['BV'][stat_name] if not math.isnan(phy_stats['BV'][stat_name]) else 0)
            stat_vals_each_no_bv.append(phy_stats['No_BV'][stat_name] if not math.isnan(phy_stats['No_BV'][stat_name]) else 0)
        print('BV: ',stat_vals_each_bv)
        print('No BV: ',stat_vals_each_no_bv)
        x = np.arange(len(list(markers.keys())))
        fig, ax = plt.subplots(figsize=(2, 2))
        sns.set_context("poster", font_scale=4, rc={"lines.linewidth": 2})
        ax.bar(x - width/2, stat_vals_each_bv, width, label='BV')
        ax.bar(x + width/2, stat_vals_each_no_bv, width, label='No BV')
        ax.set_ylabel(y_label, weight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(list(markers.keys()), weight='bold')
        if stat_name == 'Beating_Frequency':
            ax.set_yticks(np.arange(0,21001,1000))    
        else:
            ax.set_yticks(np.arange(0,101,25))
            ax.set_yticklabels(np.arange(0,101,25), weight='bold')
            ax.tick_params(axis='y', labelsize=7)
            ax.tick_params(axis='x', labelsize=7)
        ax.legend(prop={'weight':'bold','size':5}, loc='lower right')
    
    def bar_plot_with_error_bars_phy(self, inp_dict, x_label, y_label, plt_title, stat_name) -> None:
        """
            This function plots a bar plot the PDR for all PHY layers
            :param inp_dict: Dictionary of beating frequency and PRR for all physical layers
            :param x_label: X-axis label
            :param y_label: Y-axis label
            :param plt_title: Plot title
            :param stat_name: Name of the statistic that we want to plot against beating frequency
            :return: None
        """
        
        # Iterate through the dictionary and plot each line
        beating_frequency=[]
        stat_vals_each_bv=[]
        stat_vals_each_no_bv=[]
        markers = {'PHY_BLE_2M':'s','PHY_BLE_1M':'o',  'PHY_BLE_500K':'^', 'PHY_BLE_125K':'D', 'PHY_IEEE':'x'}
        width = 0.35
        for phy, phy_stats in inp_dict.items():
            print('------------------ PHY: ',phy,'--------------------')
            
            stat_vals_each_bv.append(phy_stats['BV'][stat_name])
            stat_vals_each_no_bv.append(phy_stats['No_BV'][stat_name])
        print('BV: ',stat_vals_each_bv)
        print('No BV: ',stat_vals_each_no_bv)

        x = np.arange(len(list(markers.keys())))
        fig, ax = plt.subplots()
        # Calculate confidence intervals
        conf_interval_bv = [
        t.interval(0.95, len(stat_vals_each_bv)-1, loc=np.mean(stat_vals_each_bv), scale=sem(stat_vals_each_bv) )
        ]
        conf_interval_no_bv = [
        t.interval(0.95, len(stat_vals_each_no_bv)-1, loc=np.mean(stat_vals_each_no_bv), scale=sem(stat_vals_each_no_bv)) 
        ]

        # Extract lower and upper bounds of the confidence intervals
        lower_bound_no_bv, upper_bound_no_bv = zip(*conf_interval_no_bv)
        lower_bound_bv, upper_bound_bv = zip(*conf_interval_bv)

        mean_bv = np.mean(stat_vals_each_bv)
        mean_no_bv = np.mean(stat_vals_each_no_bv)
        ax.bar(x - width/2, stat_vals_each_bv, width, label='BV', yerr=[(upper - lower) / 2 for lower, upper in zip(lower_bound_bv, upper_bound_bv)])
        ax.bar(x + width/2, stat_vals_each_no_bv, width, label='No BV', yerr=[(upper - lower) / 2 for lower, upper in zip(lower_bound_no_bv, upper_bound_no_bv)])
        ax.set_ylabel(y_label)
        ax.set_title(plt_title)
        ax.set_xticks(x)
        ax.set_xticklabels(list(markers.keys()), rotation=35)
        if stat_name == 'Beating_Frequency':
            ax.set_yticks(np.arange(0,5001,500))    
        else:
            ax.set_yticks(np.arange(0,101,5))
        ax.legend()
        

        
    def plot_beating_v_prr_pdr_phy(self, inp_dict, phy, bv_mode, x_label, y_label, plt_title, stat_name) -> None:
        """
            This function plots the beating frequency vs PRR for a given PHY layer
            :param inp_dict: Dictionary of beating frequency and PRR
            :param phy: Physical Layer used
            :param bv_mode: Bit voting mode
            :param x_label: X-axis label
            :param y_label: Y-axis label
            :param plt_title: Plot title
            :param stat_name: Name of the statistic that we want to plot against beating frequency
            :return: None
        """

        # Iterate through the dictionary and plot each line
        beating_frequency=[]
        stat_vals_each=[]
        markers = {'PHY_BLE_1M':'o', 'PHY_BLE_2M':'s', 'PHY_BLE_125K':'D', 'PHY_BLE_500K':'^'}

        for key, val in inp_dict.items():
            if len(val) > 0:
                if key == 'Beating Frequency':
                    beating_frequency = val
                if key == stat_name:
                    stat_vals_each = val
        print('BF: ',beating_frequency)
        print(stat_name,': ',stat_vals_each)
        plt.scatter(beating_frequency, stat_vals_each, label=phy+" "+bv_mode, marker=markers[phy])

        # Set labels and title
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(plt_title)

        # Add a legend
        plt.legend()

        # Show the plot
        # plt.show()

    def plot_beating_v_total_corrections_phy(self, inp_dict, phy, bv_mode)-> None:
        """
            This function plots the beating frequency vs total corrections for a given PHY layer
            :param inp_dict: Dictionary of beating frequency and total corrections
            :param phy: Physical Layer used
            :param bv_mode: Bit voting mode
            :return: None
        """

        # Iterate through the dictionary and plot each line
        beating_frequency=[]
        corrections=[]
        markers = {'PHY_BLE_1M':'o', 'PHY_BLE_2M':'s', 'PHY_BLE_125K':'D', 'PHY_BLE_500K':'^'}

        for key, val in inp_dict.items():
            if len(val) > 0:
                if key == 'Beating Frequency':
                    beating_frequency = val
                if key == 'Corrections':
                    corrections = val
        print('BF: ',beating_frequency)
        print('Corrections: ',corrections)
        plt.scatter(beating_frequency, corrections, label=phy+bv_mode, marker=markers[phy])

        # Set labels and title
        plt.xlabel('Beating Frequency')
        plt.ylabel('Corrections')
        plt.title('Corrections vs Beating Frequency')

        # Add a legend
        plt.legend()
    
    def plot_prr_v_temperature_all_phy(self, inp_dict, bv_mode, xlabel, ylabel, plot_title) -> None:
        """
            This function plots the PRR vs Temperature for all PHY layers
            :param inp_dict: Dictionary of beating frequency and PRR for all physical layers
            :param bv_mode: Bit voting mode
            :param xlabel: X-axis label
            :param ylabel: Y-axis label
            :param plot_title: Plot title
            :return: None
        """
        
        # Iterate through the dictionary and plot each line

        markers = {'PHY_BLE_1M':'o', 'PHY_BLE_2M':'s', 'PHY_BLE_125K':'D', 'PHY_BLE_500K':'^'}

        if bv_mode:
            bv_mode = 'BV'
        else:
            bv_mode = 'No BV'

        for phy, phy_stats in inp_dict.items():
            print('------------------ PHY: ',phy,'--------------------')
            sorted_t = sorted(phy_stats['temperature_stat'].items())
            phy_stats = dict(sorted_t) 
            print('Sorted PHY Stats: ',phy_stats)
            plt.scatter(list(phy_stats.keys()), list(phy_stats.values()), label=phy+" "+bv_mode, marker=markers[phy])

        # Set labels and title
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(plot_title)

        # Add a legend
        plt.legend()

        # Show the plot
        # plt.show()

    def plot_prr_v_temperature_one_phy(self, inp_dict, xlabel, ylabel, plot_title, physical_layer) -> None:
        """
            This function plots the PRR/PDR vs Temperature for one specific PHY layer
            :param inp_dict: Dictionary of beating frequency and PRR for all physical layers
            :param xlabel: X-axis label
            :param ylabel: Y-axis label
            :param plot_title: Plot title
            :param physical_layer: Physical layer
            :return: None
        """
        
        # Iterate through the dictionary and plot each line

        markers = {'PHY_BLE_1M':'o', 'PHY_BLE_2M':'s', 'PHY_BLE_125K':'D', 'PHY_BLE_500K':'^'}

        sorted_bv_stats = dict(sorted(inp_dict['BV']['temperature_stat'].items()))
        print('Sorted PHY Stats BV: ',sorted_bv_stats)
        sorted_no_bv_stats = dict(sorted(inp_dict['No_BV']['temperature_stat'].items()))
        print('Sorted PHY Stats No_BV: ',sorted_no_bv_stats)
        print('------------------ PHY: ',physical_layer,'--------------------')
        plt.scatter(list(sorted_bv_stats.keys()), list(sorted_bv_stats.values()), label=physical_layer+" BV", marker=markers[physical_layer]) 
        plt.scatter(list(sorted_no_bv_stats.keys()), list(sorted_no_bv_stats.values()), label=physical_layer+" "+"No_BV", marker=markers[physical_layer])

        # Set labels and title
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(plot_title)

        # Add a legend
        plt.legend()

        # Show the plot
        # plt.show()

    def plot_bf_v_temperature_all_phy(self, inp_dict, bv_mode, physical_layer=None) -> None:
        """
            This function plots the beating frequency vs temperature for all PHY layers
            :param inp_dict: Dictionary of beating frequency and PRR for all physical layers
            :param bv_mode: Bit voting mode
            :return: None
        """
        
        # Iterate through the dictionary and plot each line

        markers = {'PHY_BLE_1M':'o', 'PHY_BLE_2M':'s', 'PHY_BLE_125K':'D', 'PHY_BLE_500K':'^'}

        if bv_mode:
            bv_mode = 'BV'
        else:
            bv_mode = 'No BV'

        if not physical_layer:
            for phy, phy_stats in inp_dict.items():
                print('------------------ PHY: ',phy,'--------------------')
                sorted_t = sorted(phy_stats['temperature_bf'].items())
                phy_stats = dict(sorted_t) 
                print('Sorted PHY Stats: ',phy_stats)
                plt.scatter(list(phy_stats.keys()), list(phy_stats.values()), label=phy+" "+bv_mode, marker=markers[phy])
        else:
            sorted_t = sorted(inp_dict['temperature_bf'].items())
            phy_stats = dict(sorted_t) 
            print('Sorted PHY Stats: ',phy_stats)
            plt.scatter(list(phy_stats.keys()), list(phy_stats.values()), label=physical_layer+" "+bv_mode, marker=markers[physical_layer])
        # Set labels and title
        plt.yticks(np.arange(0,10001,500))
        plt.xlabel('Temperature')
        plt.ylabel('Beating Frequency')
        plt.title('Temperature vs Beating Frequency')

        # Add a legend
        plt.legend()

        # Show the plot
        # plt.show()
    
    def plot_corrections_v_temperature_all_phy(self, inp_dict, bv_mode) -> None:
        """
            This function plots the beating frequency vs temperature for all PHY layers
            :param inp_dict: Dictionary of beating frequency and PRR for all physical layers
            :param bv_mode: Bit voting mode
            :return: None
        """
        
        # Iterate through the dictionary and plot each line

        markers = {'PHY_BLE_1M':'o', 'PHY_BLE_2M':'s', 'PHY_BLE_125K':'D', 'PHY_BLE_500K':'^'}

        if bv_mode:
            bv_mode = 'BV'
        else:
            bv_mode = 'No BV'

        for phy, phy_stats in inp_dict.items():
            print('------------------ PHY: ',phy,'--------------------')
            sorted_t = sorted(phy_stats['temperature_corrections'].items())
            phy_stats = dict(sorted_t) 
            print('Sorted PHY Stats: ',phy_stats)
            plt.scatter(list(phy_stats.keys()), list(phy_stats.values()), label=phy+" "+bv_mode, marker=markers[phy])

        # Set labels and title
        plt.xlabel('Temperature')
        plt.ylabel('Corrections')
        plt.title('Temperature vs Corrections')

        # Add a legend
        plt.legend()

        # Show the plot
        # plt.show()

    def plot_prr_v_temperature_phy(self, inp_dict, x_label, y_label, plt_title, stat_name) -> None:
        """
            This function plots the PRR/PDR vs Beating frequency for all PHY layers for a specific temperature
            :param inp_dict: Dictionary of beating frequency and PRR for all physical layers
            :param bv_mode: Bit voting mode
            :param x_label: X-axis label
            :param y_label: Y-axis label
            :param plt_title: Plot title
            :return: None
        """
        
        # Iterate through the dictionary and plot each line

        stat_vals_each_bv=[]
        stat_vals_each_no_bv=[]
        markers = {'PHY_BLE_2M':'s','PHY_BLE_1M':'o',  'PHY_BLE_500K':'^', 'PHY_BLE_125K':'D'}
        width = 0.35
        for phy, phy_stats in inp_dict.items():
            print('------------------ PHY: ',phy,'--------------------')
            
            stat_vals_each_bv.append(phy_stats['BV'][stat_name])
            stat_vals_each_no_bv.append(phy_stats['No_BV'][stat_name])
        print('BV: ',stat_vals_each_bv)
        print('No BV: ',stat_vals_each_no_bv)
        x = np.arange(len(list(markers.keys())))
        fig, ax = plt.subplots()
        ax.bar(x - width/2, stat_vals_each_bv, width, label='BV')
        ax.bar(x + width/2, stat_vals_each_no_bv, width, label='No BV')
        ax.set_ylabel(y_label)
        ax.set_title(plt_title)
        ax.set_xticks(x)
        ax.set_xticklabels(list(markers.keys()), rotation=35)
        if stat_name == 'Beating_Frequency':
            ax.set_yticks(np.arange(0,21001,1000))    
        else:
            ax.set_yticks(np.arange(0,101,5))
        ax.legend()
    
    def plot_beating_v_per_phy(self, inp_dict, bv_mode, x_label, y_label, plt_title, stat_name,physical_layer=None, s=False, ) -> None:
        """
            This function plots the PER vs Beating frequency for all PHY layers for a specific temperature
            :param inp_dict: Dictionary of beating frequency and PRR for all physical layers
            :param bv_mode: Bit voting mode
            :param x_label: X-axis label
            :param y_label: Y-axis label
            :param plt_title: Plot title
            :param stat_name: Name of the statistic that we want to plot against beating frequency
            :param physical_layer: Physical layer
            :param s: A bool that says that dictionary has data for a single physical layer only
            :return: None
        """
        
        # Iterate through the dictionary and plot each line

        markers = {'PHY_BLE_1M':'o', 'PHY_BLE_2M':'s', 'PHY_BLE_125K':'D', 'PHY_BLE_500K':'^'}
        # plt.figure(figsize=(5, 5))
        if not s:
            if not physical_layer:
                for phy, phy_stats in inp_dict.items():
                    print('------------------ PHY: ',phy,'--------------------')
                    plt.scatter(phy_stats['BF'], phy_stats[stat_name], label=phy+" "+bv_mode, marker=markers[phy])
            else:
                plt.scatter(inp_dict[physical_layer]['BF'], inp_dict[physical_layer][stat_name], label=physical_layer+" "+bv_mode, marker=markers[physical_layer])
        else:
            if inp_dict['BV']:
                plt.scatter(inp_dict['BV']['BF'], inp_dict['BV'][stat_name], label=physical_layer+" "+'BV', marker=markers[physical_layer])
            if inp_dict['No_BV']:
                plt.scatter(inp_dict['No_BV']['BF'], inp_dict['No_BV'][stat_name], label=physical_layer+" "+'No_BV', marker=markers[physical_layer])

        # Set labels and title
        plt.xticks(np.arange(0,5001,500))
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(plt_title)

        # Add a legend
        plt.legend()

        # Show the plot
        # plt.show()
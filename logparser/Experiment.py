"""
This script helps to run the experiment for the given physical layer and payload length on your local machine.
It compiles the contiki application, flashes it to the JLink device, runs picocom to get the logs from the JLink device,
parses the logs, calculates the required statistics and plots the data.

The script can be run using the following example command:
python3 Experiment.py -pldlen 50 -s 1 -d 2 -f 3 -p 0dBm -bv 1 -phy PHY_BLE_2M -dur 1

The arguments are as follows:
-pldlen: Payload length in bytes
-s: Source node ID
-d: Destination node ID
-f: Forwarder node ID
-p: Transmit Power level of the nodes
-bv: Enable Bit voting the error correction mechanism
-phy: Physical layer to be used for the experiment
-dur: Duration in minutes the experiment should run

Author: Burhanuddin Rangwala
"""

import datetime
import subprocess
from add_timestamp import AddTS
import os
from Plots.Plotting import DataPlotter
from gather_data import Parser
import argparse
import sys
from make_experiment_structure import ExperimentStructure
from statistics import StatsCalculator
from fft_calculator import FFTCalculator
import re
import json

class Experiment:
    def __init__(self, pl, pd_len,source, destination, forwarder, power, dur) -> None:
        self.physical_layer = pl #Name of the physical layer used for the experiment
        self.packet_length = pd_len #Length of the payload used for the experiment
        self.dst_port = '' #Serial port of the JLink device (Destination)
        self.src = source #Source node ID
        self.dst = destination #Destination node ID
        self.fwd = forwarder
        self.picocom_output_file = '' #Path of the picocom output file
        self.power = power #Power of the JLink device
        self.logs_dir = '' #Path of the logs directory
        self.is_bv = False #Boolean variable to check if the experiment has bit voting enabled or not 
        self.src_port = '' #Serial port of the JLink device (Source)
        self.errs_collection = {}
        self.exp_dur = dur
    
    def print_dictionary(self, inp_dict):
        """
                This funcself.bf_v_stats_phywise['BV'][stat_name_t]tion prints the dictionary in a readable format
                :param inp_dict: Dictionary to be printed
                :return: None
        """

        formatted_dict = json.dumps(inp_dict, default=str, indent=4)
        print(formatted_dict)

    def get_destination_port(self):
        """
        This function gets the serial destination port of the JLink device
        :return: True if the destination port is found, False otherwise
        """

        JLink_devices_id = {1:'683040797',2:'683292912',3:'683141591'}
        nrf_command = 'nrfjprog --com' 
        nrf_process_output = subprocess.run(nrf_command, capture_output=True, shell=True, text=True)

        if nrf_process_output.returncode == 0:
            print('Got the Destination port....')
            print(nrf_process_output.stdout)  
            for coms in nrf_process_output.stdout.splitlines():
                coms = coms.split()
                if coms[0] == JLink_devices_id[self.dst]:
                    self.dst_port = coms[1]
                    print('The Destination port is: ', self.dst_port)
                if coms[0] == JLink_devices_id[self.src]:
                    self.src_port = coms[1]
                    print('The Source port is: ', self.src_port)
        else:
            print('Failed to get device ports....')
            print(f'Command: {nrf_process_output.args}')
            print(nrf_process_output.stderr)
        
        return False

    def set_logs_dir(self):
        """
        This function sets the logs directory for the experiment from the experiment file structure
        :return: None
        """
        exp_struct = ExperimentStructure()
        exp_struct.make_experiment_structure()
        self.logs_dir = exp_struct.get_physical_layer_directory(self.physical_layer)

    def set_picocom_output_file_path(self):
        """
        This function sets the picocom output file path for the experiment which contains the logs from the JLink device
        :return: None
        """
        if self.is_bv:
            self.picocom_output_file = f'{self.logs_dir}/dst_log_{self.physical_layer}.log'
        else:
            self.picocom_output_file = f'{self.logs_dir}/dst_log_{self.physical_layer}_no_bv.log'
        if os.path.exists(self.picocom_output_file):
            os.remove(self.picocom_output_file)
    
    
    def compile_experiment(self):
        """
        This function compiles the experiment using make command which compiles the contiki application 
        and flashes it to the JLink device
        :return: True if the compilation is successful, False otherwise
        """

        directory = '/home/burhanuddin/Desktop/osf/examples/osf'
        
        make_command = f'make clean TARGET=nrf52840 && make -j16 node.upload-all TARGET=nrf52840 BOARD=dk DEPLOYMENT=nulltb TESTBED=nulltb SRC={self.src} FWD={self.fwd} DST={self.dst} PERIOD=1000 CHN=0 LOGGING=1 GPIO=1 LEDS=1 NTX=6 NSLOTS=6 PWR={self.power} PROTO=OSF_PROTO_BCAST PHY={self.physical_layer} BV={1 if self.is_bv == True else 0} LENGTH={self.packet_length}'
        print('Compiling experiment...')
        print(make_command)

        make_process_output = subprocess.run(make_command, capture_output=True, cwd=directory, shell=True, text=True)

        if make_process_output.returncode == 0:
            print('Compilation done...')    
            return True
        else:
            print('Failed to compile experiment...')
            print(f'Command: {make_process_output.args}')
            print(make_process_output.stderr)
            return False

    def run_picocom(self):
        # source_command = f'picocom -fh -b 115200 --imap lfcrlf {self.src_port}'
        # print('--------- The source picocom command is: ', source_command,'---------')
        destination_command = f'picocom -fh -b 115200 --imap lfcrlf {self.dst_port}'
        print('--------- The destination picocom command is: ', destination_command,'---------')
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        # source_process = subprocess.Popen(source_command.split(), stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        destination_process = subprocess.Popen(destination_command.split(), stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        timestamp = AddTS(self.exp_dur, self.logs_dir)
        log_folder = timestamp.create_log_folder()
        self.picocom_output_file = log_folder+'/output_log'+datetime.datetime.now().strftime('%Y%m%d%H%M%S')+'.txt'
        output_file = open(self.picocom_output_file, "a")
        packet_number = 0
        stop_value = 20
        # Read the output from both destination process

        while not timestamp.is_next_window():            
            try:
                # Read and process the output from the destination process
                destination_output = destination_process.stdout.readline().decode().strip()
                destination_output = ansi_escape.sub('', destination_output)
                if destination_output:
                    # Timestamp the destination output
                        to_be_written = '['+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+']'+" "+ destination_output
                        # print('-----------------------------')
                        print(to_be_written)
                        print('-----------------------------')
                        output_file.write(to_be_written + '\n')
                        output_file.flush()
            except UnicodeDecodeError:
                pass
            except TypeError:
                pass
        output_file.close()
        # destination_process.terminate()
        return log_folder
    
    def make_csvs(self, logs_dir):
        """
        This function makes the CSVs from the logs
        :param logs_dir: Directory containing the logs
        :return: Name of the CSV file where the parsed data is written
        """

        print('Making CSVs...')
        parser = Parser(logs_dir, self.is_bv)
        csv_file_name = parser.execute_csv_generation()
        
        return csv_file_name

    def plot_data(self, logs_dir):
        """
        This function plots the data from the CSVs and calculates required metrics
        :param logs_dir: Directory containing the logs
        :return: None
        """

        print('Plotting data...')
        plotter = DataPlotter(self.logs_dir,logs_dir, (self.packet_length+9), self.is_bv)
        plotter.set_physical_layer(self.physical_layer)
        plotter.get_all_file_paths()
        plotter.plot_error_positions(self.errs_collection, 'Beating Graph')
        # plotter.plot_fft(self.smp_freq, self.pwr, self.cutoff_freq)

    def get_statistics(self, logs_dir, csv_file_path):
        """
        This function calculates the required statistics from
        the logs
        :return: None
        """
        
        print('Calculating statistics...')
        print(self.logs_dir)
        stats = StatsCalculator(self.logs_dir,logs_dir, self.is_bv, False)
        stats.calc_rx_prr()
        stats.calc_rx_pdr()
        if self.is_bv:
            print('---------Bit Voting Effectiveness---------\n')
            stats.calc_bit_voting_effectiveness()
            stats.calc_error_corrected_error_positions()
        else:
            stats.calc_error_positions()
        stats.write_stats(self.physical_layer)
        fft_calculator = FFTCalculator(self.logs_dir, self.physical_layer, self.is_bv)
        self.smp_freq, self.pwr, self.cutoff_freq = fft_calculator.fft_calculator(stats.get_error_positions_dictionary())
        self.errs_collection = stats.get_error_positions_dictionary()

def main():
    """
    This is the main function which runs the experiment
    :return: None
    """

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-pldlen', '--payload_length', type=int, help='Payload length in bytes', required=True)
    arg_parser.add_argument('-s', '--src', type=int, help='Source node ID', required=True)
    arg_parser.add_argument('-d', '--dst', type=int, help='Destination node ID', required=True)
    arg_parser.add_argument('-f', '--fwd', type=int, help='Forwarder node ID', required=True)
    arg_parser.add_argument('-p', '--power', type=str, help='Transmit Power level of the nodes', required=True)
    arg_parser.add_argument('-bv', '--bitvoting', type=int, help='Enable Bit voting the error correction mechanism', required=True)
    arg_parser.add_argument('-phy', '--physical_layer', type=str, help='Enable Bit voting the error correction mechanism', required=True)
    arg_parser.add_argument('-dur', '--duration', type=int, help='Duration in minutes the experiment should run', required=True)
    args = arg_parser.parse_args()

    all_arguments_provided = all(getattr(args, arg) is not None for arg in vars(args))

    if not(all_arguments_provided):
        print('Please provide all the required arguments...')
        arg_parser.print_help()
        sys.exit(1)

    #for phy in ['PHY_BLE_2M','PHY_BLE_1M', 'PHY_BLE_125K', 'PHY_BLE_500K','PHY_IEEE']: Can be uncommented to run the experiment for all the physical layers
    phy = args.physical_layer # to comment this out if the above for loop is used.
    if phy:
        print(f'Running experiment for {phy}....')
        if args.payload_length > 116 and phy == 'PHY_IEEE':
            print('Payload length cannot be greater than 116 for IEEE 802.15.4')
            sys.exit(1)
        exp = Experiment(args.physical_layer,  args.payload_length, args.src, args.dst, args.fwd, args.power, args.duration)
        if args.bitvoting == 1:
            exp.is_bv = True
        exp.set_logs_dir()
        exp.logs_dir = args.main_directory
        exp.get_destination_port()
        exp.compile_experiment()
        txt_log_dir = exp.run_picocom()
        csv_fl_nm = exp.make_csvs(txt_log_dir)
        exp.get_statistics(txt_log_dir, csv_fl_nm)
        exp.plot_data(txt_log_dir)
        print('Experiment done...')
    sys.exit(0)

if __name__ == '__main__':
    main()
        

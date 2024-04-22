Experiment Details

This experiment was conducted to encounter beating and to check the effectiveness of Bit-voting error correction scheme in correcting burst errors occurring due to this beating. The nodes used here are random 3 node combination of templab nodes with the temperature fixed at 30C.

Experiment Parameters:
Transmission Power: Neg8dBm
Packet length: 255 bytes for BLE5 and 125 bytes for IEEE
Topology: 3 Nodes, 2 nodes as transmitters(1 as source or initiator of the flood and 1 as forwarder) and 1 nodes as receiver.

Results:
The results of the beating pattern plots cannot be trusted as there is an error in calculating expected packet because of the period selected for OSF working caused the calculated packet ID to go out of sync. But I guess the results regarding PDR, PER and PRR can be trusted.

Different node combinations demonstrated different beating patterns for different physical layers in which bit voting got chance to correct errors and sometimes bit-voting was not required. Also, there were cases where the nodes were not able to sync for certain physical layers (We are not considering such cases for the calculation of PDRs).

//ToDO: 
//Write why we are changing temperatures and what is the advantage of that.
//Wrtie conclusions from the graphs that we have.

Experiment Details

This experiment was conducted to encounter beating and to check the effectiveness of Bit-voting error correction scheme in correcting burst errors occurring due to this beating. The node IDs  used here are 122 as source, 126 as forwarder and 124. The reason for doing multiple runs on this combination is because it showed promising beating and it also showed corrections done by bit-voting scheme. Other combinations tried showed less beating and all the receptions were received correctly during the round and thus bit voting was not required at that point. 
As we know that temperature has its effect on the crystal oscillator due to which the carrier frequency of the device also varies and thus, the CFO between the transmitting devices also vary which will give rise to different beating frequencies, which will create different burst errors which might come in handy to study how bit voting performs in this scenarios.

Experiment Parameters:
Transmission Power: Neg8dBm
Packet length: 255 bytes for BLE5 and 125 bytes for IEEE
Topology: 3 Nodes, 2 nodes as transmitters(1 as source or initiator of the flood and 1 as forwarder) and 1 nodes as receiver.
Temperature: Temperature for the source is varied from 30 to 70C with 10 degree increase every 10 minutes.

Results:
Different beating patterns can be seen at each temperature. 
For 1M and 2M it is generally following narrow beating but the size of the envelope varies with the temperature which suggests that the RFO is varying which inturn is affecting the beating envelope.
For 125K and 500K similar behaviour is seen but they experience a bit of a wider beating than uncoded PHYs.

PDR evaluations for different temperatures.
30C and 40C:
125K shows the maximum performance increase at this temperature which is around 30.5%, 2M shows 7-8% increase, 1M shows 5% increase. For uncoded PHYs this is a case of narrow beating but I think that due to faster transmission rates it is able to escape the beating most of the time which should not be the case since it should suffer because of the narrow beating. and 125K should not suffer this much since it is a coded PHY and it should survive narrow beating because of FEC and Manchester Mapping. Least suffering is seen by 500K

At 60C and 70C it seems that 2Ms faster transmission rate is resulting in a bit of a wide beating as there is not much difference in its PDRs irrespective of bit voting is enabled or not. 125K is the most suffering PHY across all the temperatures. 1M shows almost 5% or more increase in PDR across temperatures.

All in all with BV employed it offers performance no matter the minimality of it but it does offer performance increase which proves that it is beneficial to have such error correction scheme along with FEC and other packet-level error correction mechanisms.

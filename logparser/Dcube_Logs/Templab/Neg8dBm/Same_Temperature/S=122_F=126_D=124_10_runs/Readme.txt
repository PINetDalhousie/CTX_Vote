Experiment Details

This experiment was conducted to encounter beating and to check the effectiveness of Bit-voting error correction scheme in correcting burst errors occurring due to this beating. The node IDs  used here are 122 as source, 126 as forwarder and 124 with the temperature fixed at 30C. The reason for doing multiple runs on this combination is because it showed promising beating and it also showed corrections done by bit-voting scheme. Other combinations tried showed less beating and all the receptions were received correctly during the round and thus bit voting was not required at that point.

Experiment Parameters:
Transmission Power: Neg8dBm
Packet length: 255 bytes for BLE5 and 125 bytes for IEEE
Topology: 3 Nodes, 2 nodes as transmitters(1 as source or initiator of the flood and 1 as forwarder) and 1 nodes as receiver.

Results:
The beating patterns in this experimentation clearly show the type of beating encountered by the node combinations at the receiver meaning wide or narrow.

From the graph of PHYSICAL LAYER VS AVERAGE PDR  we can see that bit voting does help in increasing PDR (Packet Delivery Ratio) of the physical layers and for this node combination the most increase in the PDR can be seen for PHY_BLE_125K with almost 30.5% increase. 1M and 2M showed approximately 3-4% increase in PDR when bit voting is enabled. For this pair it seems that PHY_BLE_500K doesn't need bit-voting as the FEC employed by it is good enough. 

From the ABSOULTE ERRORS VS BIT POSITION graphs we can see that the CFO between 122 and 126 is high as for all the physical layers it is seen that the beating is narrow especially for 1M and 2M it can be seen that way. For 1M and 2M there aren't much corrections which is a bit confusing as the beating is narrow and they should suffer more.

One possible reason for this behaviour to be seen is maybe the beating is narrow but because of faster transmission rates they can fit in a transmission which is received correctly at the destination.
PHY_BLE_125K suffers more which should not be the case as the beating experienced is narrow and coded PHYs are known to perform better in case of narrow beating???
However this is only the case for 125K, 500K seems to be performing good even without bit voting since the beating type is narrow and thus its FEC is helping in getting correct receptions.

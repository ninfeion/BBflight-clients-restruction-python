# BBflight-clients-restruction-python

WARNING：
  16MHz CRYTAL IS CONFIlCT WITH USB VIRTUAL COM!!!
# The Serial Error isn't cue of 16MHz. The Result Is That The Radio's Usb FIFO Overflow.
 So I Add A txEnabledMonitor Value Which If RxTimer Can Not Receive Affective Data Will Turn
 To False And Stop TxTimer Transmitting.
 ATTENTION: "txEnabledMonitor" set to True when initializing so that when open serial port it
 will trigger the affective data transmitting at first time.And then it just like chain
 reaction,the SLAVE will be triggered to transmit respond data.
 In addition, if "txEnabledMonitor" set to False when initializing, txTimer be disabled,and SLAVE
 can not receive the first command to trigger itself radio system. In this result, SLAVE can
 not clear the NRF TX FIFO, it should herit the last respond data to trigger PC clients transmitting.
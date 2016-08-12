BBflight-clients-restruction-python
===================================

USB BUG
----------------------------------
###WARNING：
16MHz CRYTAL IS CONFIlCT WITH USB VIRTUAL COM!!!<br>
The Serial Error isn't cue of 16MHz. The Result Is That The Radio's Usb FIFO Overflow.<br>
So I Add A txEnabledMonitor Value Which If RxTimer Can Not Receive Affective Data Will Turn<br>
To False And Stop TxTimer Transmitting.<br>
    
ATTENTION: "txEnabledMonitor" set to True when initializing so that when open serial port it<br>
will trigger the affective data transmitting at first time.And then it just like chain<br>
reaction,the SLAVE will be triggered to transmit respond data.<br>
In addition, if "txEnabledMonitor" set to False when initializing, txTimer be disabled,and SLAVE<br>
can not receive the first command to trigger itself radio system. In this result, SLAVE can<br>
not clear the NRF TX FIFO, it should herit the last respond data to trigger PC clients transmitting.<br>
 
2016/8/12  
---------------------------------
Today I released the client v0.01 which is packed by pyinstaller. At first, I must raise that if<br> 
the python install dir and the target script dir path name including blank space " ", the processing<br>
of pyinstaller will fail. In order to finish the packing, we should use double quote to include the<br>
dir path name which involve blank space in cmd environment. For instantce, we used to pyinstaller us<br>
script in cmd: `C:\Users\N> pyinstaller <target py file>` ,but it must fail if the pyinstaller dir path<br> 
name involve blank space and the way is like the: `C:\Users\N> "C:\Extra Software\python351\python.exe"`<br>
`"C:\Extra Software\python351\Scripts\pyinstaller-script.py" "C:\target.py"`.<br>
By the way, this version is incompleted and lacks of: address matching, more stable and flexible command<br> 
transmitting and receiving mechanism, air connection protecting, etc. Unfortunately, I must handle other<br>
problem first. Good luck to myself.<br>
BBflight-clients-restruction-python
===================================

USB BUG
----------------------------------
#WARNING：
    16MHz CRYTAL IS CONFIlCT WITH USB VIRTUAL COM!!!
    The Serial Error isn't cue of 16MHz. The Result Is That The Radio's Usb FIFO Overflow.
    So I Add A txEnabledMonitor Value Which If RxTimer Can Not Receive Affective Data Will Turn
    To False And Stop TxTimer Transmitting.
    
    ATTENTION: "txEnabledMonitor" set to True when initializing so that when open serial port it
    will trigger the affective data transmitting at first time.And then it just like chain 
    reaction,the SLAVE will be triggered to transmit respond data.
    In addition, if "txEnabledMonitor" set to False when initializing, txTimer be disabled,and SLAVE  
    can not receive the first command to trigger itself radio system. In this result, SLAVE can  
    not clear the NRF TX FIFO, it should herit the last respond data to trigger PC clients transmitting.  
 
2016/8/12  
---------------------------------
    Today I released the client v0.01 which is packed by pyinstaller. At first, I must raise that if 
    the python install dir and the target script dir path name including blank space " ", the processing 
    of pyinstaller will fail. In order to finish the packing, we should use double quote to include the 
    dir path name which involve blank space in cmd environment. For instantce, we used to pyinstaller us
    script in cmd: `C:\Users\N> pyinstaller <target py file>` ,but it must fail if the pyinstaller dir path
    name involve blank space and the way is like the: `C:\Users\N> "C:\Extra Software\python351\python.exe"` 
    `"C:\Extra Software\python351\Scripts\pyinstaller-script.py" "C:\target.py"`.
    By the way, this version is incompleted and lacks of: address matching, more stable and flexible command
    transmitting and receiving mechanism, air connection protecting, etc. Unfortunately, I must handle other
    problem first. Good luck to myself.

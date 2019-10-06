import ParseFunctions as pf
import TCP_com as tp  #in-built 5s delay in all of them
import AllModules as am

################################### Important #########################################
######## This parameter defines at what time it is safe to start a new run ############
######## It should be about 30 seconds before the arrival time of each spill ##########
######## Since spills come every minute, this is defined as a number of seconds #######
######## after the start of each clock minute (only meaningful modulo 60 seconds) #####
################ Periodically make sure this value makes sense. #######################
#######################################################################################

StartSeconds = 9
StopSeconds = 40
NumSpillsPerRun = 2


#################################Parsing arguments######################################                                                                                                                               

parser = argparse.ArgumentParser(description='Information for running the AutoPilot program. 
/n /n General Instructions: If using OTSDAQ make sure the start and stop seconds in the beginning of the program are hard coded correctly. /n Make sure to add sensor and configuration after each controlled access and pass it as an argument to this script. /n
/n /n TekScope Specific Instructions: /n Make sure you hard code the dpo_fastframe path. /n If using the OTSDAQ with TekScope make sure the Use_otsdaq boolean is True in dpo_fastframe script. /n Make Sure you pass all four Scope trigger and channel settings. 
/n /n Other Digitizer Specific Instructions: /n If not running the TekScope make sure that the run file name in TCP_com is correct.') 
parser.add_argument('-rtm', '--RunTableMode', type=int, default = 0, help='Give 1 if you are using the run table', required=False)                                       
parser.add_argument('-ac', '--AlreadyConfigured', type=int, default = 0, help='Give 1 if the OTSDAQ is already configured', required=False)   
parser.add_argument('-de', '--Debug', type=int, default = 0, required=False)                                                                                                        
parser.add_argument('-io', '--IsOTSDAQ', type=int, default=0, help = 'Give 1 if using OTSDAQ',required=False)        
parser.add_argument('-it', '--IsTelescope', type=int,default=0, help = 'Give 1 if using the telescope',required=False)                                                              
parser.add_argument('-di', '--Digitizer', type=str,default= 'TekScope', help = 'Give VME or DT5742 or TekScope', required =False)        
parser.add_argument('-se', '--Sensor', type=int, help = 'Make sure to add the sensor record in the run table. Give sensor S/N from the run table',required=False) 
parser.add_argument('-conf', '--Configuration', type=int, help = 'Make sure to add the configuration in the run table. Give COnfiguration S/N from the run table',required=False)  
parser.add_argument('-sac', '--StopAndContinue', type=int, default = 0, help = 'This bool should be 1 if the OTSDAQ is already in the running state and you want to stop and it and continue running it.',required=False)                                        

######################### Only care about this if using TekScope #########################
parser.add_argument('-tl', '--TriggerLevel', type=float,default= -0.01, help = 'Trigger level in volts', required =False)        
parser.add_argument('-tc', '--TriggerChannel', type=str, deafult= 'CH4', help = 'Channel to trigger on',required=False) 
parser.add_argument('-ne', '--NumEvents', type=int,default=50000, help = 'Number of events',required=False)  
parser.add_argument('-tne', '--TotalNumEvents', type=int,default=50000, help = 'Total number of events',required=False)  
                
args = parser.parse_args()                                                                                                                                                                
RunTableMode = args.RunTableMode        
AlreadyConfigured = args.AlreadyConfigured        
Debug = args.Debug                                                                                                                                                                    
IsOTS = args.IsOTSDAQ                                                                                                                                                      
IsTelescope = args.IsTelescope                                                                                                                                
Digitizer = args.Digitizer                                                                                                                                      
Sensor = args.Sensor                                                                                                                                                   
Configuration = args.Configuration        
StopAndContinue = args.StopAndContinue
TriggerLevel = args.TriggerLevel
TriggerChannel = args.TriggerChannel
NumEvents = args.NumEvents
TotalNumEvents = args.TotalNumEvents



########################### Only when Run table is used ############################

if RunTableMode:

        if IsTelescope: 
                Tracking = 'Not started'
        else:
                Tracking = 'N/A'
        if Digitizer == 'TekScope': 
                IsScope = True
                Conversion = 'Not started'
                StartScopeCMD = "python %s --trig=%f --trigCh=%s --numFrames=%i --totalNumber=%i" % (am.DPOFastFramePath, TriggerLevel, TriggerChannel, NumEvents, TotalNumEvents) 
        else: 
                Conversion = 'N/A'                

        TimingDAQ = 'Not started'
        TimingDAQNoTracks = 'Not started'

    # Get Sensor ID and Configuration ID list  
    
    if pf.QueryGreenSignal(True):  
        SensorID = pf.GetFieldIDOtherTable('Sensor', 'Configuration number', str(Sensor), False)                                                                                                                            
        ConfigID = pf.GetFieldIDOtherTable('Config', 'Configuration number', str(Configuration), False)  

    if not SensorID or not ConfigID:
            raise Exception('\n The sensor and configuration you passed as argument are not in the table!!!!!!!!!!!!!!!!!!!! \n')
            ##### Exit the program ######


#################### CONFIGURING AND INITIALIZING THE OTSDAQ ######################

if not Debug and not AlreadyConfigured and UseOTS: 
	print 'INTITIALIZING THE OTS-DAQ'
	init_ots()
if not Debug and not AlreadyConfigured and UseOTS: 
	print 'CONFIGURING THE OTS-DAQ'
	config_ots()
	time.sleep(25)



while True:

        if not IsScope and UseOTS and StopAndContinue:                                                                                                                                

                ############### Wait until stop time ##################                                                                                                                  
                am.wait_until(StopSeconds)                                                                                                                                               
                print "Stopping run at %s" % (am.datetime.now().time())                                                                                                                      
                if not debug: stop_ots(False)                                                                                                                                             
                StopAndContinue = False                                                                                                                                                 
                time.sleep(20)  
                                                                                                                                                          
        elif not StopAndContinue:

                ############ Wait for safe time to start run ##########
                am.wait_until(StartSeconds)        
                
                if not Debug and IsScope: 
                        
                        # In case of the scope, running the dpo_fastframe script which will take care of the otsdaq.
                        os.system(StartScopeCMD)
                        time.sleep(1) 

                elif not Debug and not IsScope:

                        ################### Starting the run ###################
                        StartTime = str(am.datetime.now())
                        print "Starting run at %s" % (StartTime)

                        RunNumber = tp.start_ots(False)

                        time.sleep(60*(NumSpillsPerRun-1))  

                        am.wait_until(StopSeconds)   
                        StopTime = str(am.datetime.now())

                        print "Stopping run at %s" % (StopTime)                                                                                                
                        if not debug: tp.stop_ots(False)                                                                                                                                             

                        if RunTableMode:

                                Duration = StopTime - StartTime

                                if pf.QueryGreenSignal(True): pf.NewRunRecord(RunNumber, StartTime, Duration, Digitizer, Tracking, Conversion, TimingDAQ, TimingDAQNoTracks, SensorID, ConfigID, False)
                                
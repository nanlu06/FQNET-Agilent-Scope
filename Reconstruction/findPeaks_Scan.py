import struct  #struct unpack result - tuple
import numpy as np
import matplotlib.pyplot as plt
import time
import optparse
import argparse
import os
import time, datetime
import math
from ROOT import TFile, TTree

parser = argparse.ArgumentParser(description='Creating a root file from Binary format')

parser.add_argument('--Scan', metavar='Scan', type=str, help='Scan Number to process',required=True)
args = parser.parse_args()
scan = args.Scan

RawDataPath = '/home/sxie/KeySightScope/KeySightScopeMount/'
RawDataLocalCopyPath = '/home/sxie/KeySightScope/RawData/'
OutputFilePath = '/home/sxie/KeySightScope/Peaks/'
TimeFile = '/home/sxie/ETL_Agilent_MSO-X-92004A/Acquisition/TimestampFile.txt'
RootFilePath = '/home/sxie/KeySightScope/PeaksRootFiles/'
VoltageFilePath = '/home/mhussain/InterFerDAQ/VoltageScanDataRegistry/'

Debug=False

def keysight_get_points(filepath_in):
    my_file = open(filepath_in, 'rb')
    b_cookie = my_file.read(2) #char
    b_version = my_file.read(2) #char
    b_size = struct.unpack('i', my_file.read(4)) #int32 - i
    b_nwaveforms = struct.unpack('i', my_file.read(4)) #int32 - i ## number of events (or segments)
    b_header = struct.unpack('i', my_file.read(4)) #int32 - i
    remaining = b_header[0] - 4
    # print " remaining = ", remaining
    b_wavetype = struct.unpack('i', my_file.read(4)) #int32 - i
    # print "b_wavetype = ", b_wavetype
    remaining = remaining - 4
    b_wavebuffers = struct.unpack('i', my_file.read(4)) #int32 - i
    # print " b_wavebuffers = ", (b_wavebuffers[0])
    remaining = remaining - 4
    b_points = struct.unpack('i', my_file.read(4)) #int32 - i
    # my_file.close()
    return b_points


def fast_Keysight_bin(filepath_in, index_in,n_points):
    global x_axis, y_axis, remaining
    x_axis = []
    y_axis = []

    # read from file
    my_index = index_in
    # start = time.time()
    my_file = open(filepath_in, 'rb')

    b_cookie = my_file.read(2) #char
    b_version = my_file.read(2) #char
    b_size = struct.unpack('i', my_file.read(4)) #int32 - i
    b_nwaveforms = struct.unpack('i', my_file.read(4)) #int32 - i ## number of events (or segments)
    # end = time.time()

    if my_index <= b_nwaveforms[0]:
        my_index = my_index
    else:
        my_index = 1
    counter = 0

    nBytesPerEvent = 140+12+(4*n_points)
    # print nBytesPerEvent
    # nBytesPerEvent = 16152 ##-- 140+12+16000
    my_file.seek( (nBytesPerEvent)*(my_index-1) ,1)
    b_header = struct.unpack('i', my_file.read(4)) #int32 - i
    # if b_header[0]!=140:
    #     print "bad event, skipping"
    #     x_axis = np.linspace(0, 1000, n_points)
    #     y_axis = np.linspace(0, 1000, n_points)
    #     return [x_axis,y_axis]
    #print " b_header = ", (b_header)
    remaining = b_header[0] - 4
    #print " remaining = ", remaining
    b_wavetype = struct.unpack('i', my_file.read(4)) #int32 - i
    #print "b_wavetype = ", b_wavetype
    remaining = remaining - 4
    b_wavebuffers = struct.unpack('i', my_file.read(4)) #int32 - i
    #print " b_wavebuffers = ", (b_wavebuffers[0])
    remaining = remaining - 4
    b_points = struct.unpack('i', my_file.read(4)) #int32 - i
    #print " b_point =", (b_points)
    remaining = remaining - 4
    b_count = struct.unpack('i', my_file.read(4)) #int32 - i
    remaining = remaining - 4
    b_x_disp_range = struct.unpack('f', my_file.read(4)) #float32 - f
    remaining = remaining - 4
    b_x_disp_orig = struct.unpack('d', my_file.read(8)) #double - d
    remaining = remaining - 8
    b_x_inc = struct.unpack('d', my_file.read(8)) #double - d
    remaining = remaining - 8
    b_x_orig = struct.unpack('d', my_file.read(8)) #double - d
    remaining = remaining - 8
    b_x_units = struct.unpack('i', my_file.read(4)) #int32 - i
    remaining = remaining - 4
    b_y_units = struct.unpack('i', my_file.read(4)) #int32 - i
    remaining = remaining - 4
    b_date =  my_file.read(16)
    remaining = remaining - 16
    b_time =  my_file.read(16)
    remaining = remaining - 16
    b_frame =  my_file.read(24)
    remaining = remaining - 24
    b_wave_string =  my_file.read(16)
    remaining = remaining - 16
    b_time_tag = struct.unpack('d', my_file.read(8)) #double - d
    remaining = remaining - 8
    b_segment_index = struct.unpack('I', my_file.read(4)) #unsigned int - I
    remaining = remaining - 4
    # print " remaining is now = ", remaining

   # print " x origin = ", b_x_orig[0]
   # print " x inc = ", b_x_inc[0]
   # print b_points[0]

    x_axis = b_x_orig[0] + b_x_inc[0] * np.linspace(0, b_points[0]-1, b_points[0])
 
   # j loop on buffers - only returns the last buffer
    for j in range(0,b_wavebuffers[0]):
        counter += 1
        #header size - int 32
        b_header = struct.unpack('i' , my_file.read(4)) #int32 - i
       # print 'buffer header size: ' ,( str(b_header[0]))
        remaining = b_header[0] - 4
        #buffer type - int16
        b_buffer_type = struct.unpack('h' , my_file.read(2)) #int16 - h
        # print 'buffer type: ' ,( str(b_buffer_type[0]))
        remaining = remaining - 2
        #bytes per point - int16
        b_bytes_per_point = struct.unpack('h' , my_file.read(2)) #int16 - h
        #print 'bytes per point: ' ,( str(b_bytes_per_point[0]) )
        remaining = remaining - 2
        #buffer size - int32
        b_buffer_size = struct.unpack('i' , my_file.read(4)) #int32 - i
        #print 'buffer size: ' ,( str(b_buffer_size[0]) )
        remaining = remaining - 4
        # create y axis for voltage vector
        # currently ONLY standard voltage -  float32 - Buffer Type 1 / 2 / 3
        # print  " buffer size = ", (b_buffer_size[0])
        b_y_data = my_file.read(b_buffer_size[0])
        y_axis = struct.unpack("<"+str(b_points[0])+"f", b_y_data)
    return_array = [x_axis,y_axis]
    # print " counter = ", (counter)
    # print len(return_array[0])
    # print (return_array[1])
    # my_file.close()
    return return_array, b_nwaveforms, b_points


#### Copy files locally, and if successful, move them to "to_delete" directory

#print "Copying files locally."
#rawFiles = RawDataPath + 'Wavenewscope_CH*_'+run+'.bin'
#os.system('rsync -z -v %s %s && mv %s %s' % (rawFiles,RawDataLocalCopyPath,rawFiles,RawDataPath+"/to_delete/"))
#print "Starting conversion."
## read the input files
#print "file1"
#inputFile1 = RawDataLocalCopyPath + 'Wavenewscope_CH1_'+run+'.bin'
#print "file2"
#inputFile2 = RawDataLocalCopyPath + 'Wavenewscope_CH2_'+run+'.bin'
#print "file3"
#inputFile3 = RawDataLocalCopyPath + 'Wavenewscope_CH3_'+run+'.bin'
#inputFile4 = RawDataLocalCopyPath + 'Wavenewscope_CH4_'+run+'.bin'

# Voltage file
voltageFile = '%sscan%s.txt' % (VoltageFilePath, scan)
f_voltage = open(voltageFile, 'r')
runs = []
voltages = []
temperatures = []
for line in f_voltage:
	datan = line.split()
	runs.append(int(float(datan[0])))
	voltages.append(float(datan[1]))
	temperatures.append(float(datan[2]))

baseline = []
baseline_error = []
timestamps = []
#t = datetime.datetime(2019, 6, 30, 0, 0)
mean_list1 = []
error_list1 = []
mean_list2 = []
error_list2 = []
mean_list3 = []
error_list3 = []


for run_ind in range(len(runs)):
	run = runs[run_ind]
	voltage = voltages[run_ind]
	temperature = temperatures[run_ind]
	# Run files
	inputFileName1 = "Wavenewscope_CH1_" + str(run) + ".bin"
	inputFileName2 = "Wavenewscope_CH2_" + str(run) + ".bin"
	inputFile1 = os.path.join(RawDataPath, inputFileName1)
	inputFile2 = os.path.join(RawDataPath, inputFileName2)
	n_points = keysight_get_points(inputFile1)[0]
	#n_points2 = keysight_get_points(inputFile2)[0] 
	input1 = fast_Keysight_bin(inputFile1, 1, n_points) ## to get the number of segments/events and points

	n_events = list (input1[1])[0] ## number of events/segments
	n_points = list(input1[2])[0] ## number of points acquired for each event/segment
	print "n_events = ", n_events
	print "n_points = ", n_points
	print(list(input1[0][1]))
	
	# Output file
	outputFileName = "peaks_" + str(run) + ".txt"
	outputFile = os.path.join(OutputFilePath, outputFileName);
	f_open = open(outputFile, "w+") # create and write to file

	# Print Timestamp
	f_time = open(TimeFile, "r")
	for line in f_time:
		values = line.split()
		if int(values[0]) == int(run):
			f_open.write(values[1] + " " + values[2] + " ")
			f_open.write(values[3]+"\n")
			#timestamps.append(float(values[3]) - time.mktime(t.timetuple()))
			timestamps.append(float(values[3]))
			break;
	# Print Voltage
	f_open.write(str(voltage) + ' V\n')
	# Print Temperature
	f_open.write(str(temperature) + ' degree Celsius\n')

	# Find three peaks and their mean and RMS deviation
	wave_cp = np.zeros(n_points)
	# lists of tuples to store peak data
	first_list = []
	second_list = []
	third_list = []
#	baseline_list = []
	count = 0
	count2 = 0
	for i in range(n_events):
		inputloop = fast_Keysight_bin(inputFile1, i+1, n_points) ## to get the number of segments/events and points
		inputloop2 = fast_Keysight_bin(inputFile2, i+1, n_points)
		base = list(inputloop2[0][1])
		wave = list(inputloop[0][1]) # y axis

		# Subtract background noise 0.16 mV
		for a in range(len(wave)):
			wave[a] -= 0.16 * 10**(-3)

		# Approximate number of points in 2 ns
		timeArray = list(inputloop[0][0])#x_axis
		twoNS_counts = 0
		for k in range(len(timeArray)):
			twoNS_counts += 1
			if timeArray[k] - 2 * 10**(-9) >= timeArray[0]:
				break
		#print("2ns counts: " + str(twoNS_counts))

		f_open.write("Event %d\nindex number peaks[mV]\n" % (i))

		largest = 0
		largest_index = 0
		
		# Find Baseline, first 300 points
#		sum_base = 0
#		for k in range(300):
#			sum_base += base[k] / 300.0
#		baseline_list.append(sum_base * 10**3)
		
		for a in range(len(wave)):
			wave_cp[a] = wave[a]

		# Find largest peak
		for j in range(n_points):
			if j >= len(wave):
				break
			if wave[j] <= largest and wave[j+1] >= wave[j] and wave[j-1] >= wave[j]:
				largest = wave[j]
				largest_index = j
		first_list.append((largest_index, largest))		
		f_open.write("%d %5.2f\n" % (largest_index, largest * 10**3))
	
		# Find second largest peak
		second_index = 0
		# Set all values of the largest peak to 10, start from peak and approach left and right
		m = largest_index
		while (m < len(wave_cp) and wave_cp[m] < largest * 10**(-2)):
			wave_cp[m] = 10
			m += 1
		m = largest_index - 1
		while (m >= 0 and wave_cp[m] < largest * 10**(-2)):
			wave_cp[m] = 10
			m -= 1
		sum_near = 0
		sum_min = 0
		for p in range(largest_index - int(1.5 * twoNS_counts), largest_index + int(2.5 * twoNS_counts)):
			sum_near = wave_cp[p-2] + wave_cp[p-1] + wave_cp[p] + wave_cp[p+1] + wave_cp[p+2]
			if sum_min > sum_near and wave_cp[p] <= wave_cp[p+1] and wave_cp[p] <= wave_cp[p-1]:
				sum_min = sum_near
	
		for j in range(largest_index - int(1.5 * twoNS_counts), largest_index + int(2.5 * twoNS_counts)):
			sum_near = wave_cp[j-2] + wave_cp[j-1] + wave_cp[j] + wave_cp[j+1] + wave_cp[j+2]
			if wave_cp[j] <= wave_cp[j-1] and wave_cp[j] <= wave_cp[j+1] and sum_min >= sum_near:
				second_index = j
				count2 += 1
				second_peak = wave[j]
				
		f_open.write("%d %5.2f\n" % (second_index, second_peak * 10**3))
		second_list.append((second_index, second_peak))  

		# Find third biggest peak
		# Set the values of the second peak to 10
		n = second_index
		while (n < len(wave_cp) and wave_cp[n] < second_peak * 10**(-2)):
			wave_cp[n] = 10
			n += 1
		n = second_index - 1
		while (n >= 0 and wave_cp[n] < second_peak * 10**(-2)):
			wave_cp[n] = 10
			n -= 1
		third_index = 0
		third_peak = 0
		sum_min1 = 0
		sum_near3 = 0
		check_third_peak = True
		
		# approximate position of smallest peak
		approxi = 0
		difference = abs(second_index - largest_index)
		if abs(difference - twoNS_counts) < 10: # smallest peak is third peak
			approxi = max(second_index, largest_index) + twoNS_counts
		elif abs(difference - 2 * twoNS_counts) < 10: # smallest peak is second peak
			approxi = max(second_index, largest_index) - twoNS_counts
		
		for j in range(approxi - int(0.3 * twoNS_counts), approxi + int(0.3 * twoNS_counts)):
			sum_near3 = wave_cp[j-1] + wave_cp[j] + wave_cp[j+1]
			if sum_min1 > sum_near3 and wave_cp[j] <= wave_cp[j+1] and wave_cp[j] <= wave_cp[j-1] and wave_cp[j-1] < 0 and wave_cp[j+1] < 0:
				sum_min1 = sum_near3

		for j in range(approxi - int(0.3 * twoNS_counts), approxi + int(0.3 * twoNS_counts)):
			if wave_cp[j] <= wave_cp[j-1] and wave_cp[j] <= wave_cp[j+1] and sum_min1 >= wave_cp[j]+wave_cp[j+1] + wave_cp[j-1]:
				third_peak = wave[j]
				third_index = j
				check_third_peak = False
		f_open.write("%d %5.2f\n" % (third_index, third_peak * 10**3))	
		# Check if third peak is detected
		if check_third_peak:
			#print("Third peak undetected Event: " + str(i))
			f_open.write("Third peak undetected\n")
			third_index = approxi
			count += 1
		third_list.append((third_index, third_peak))
		# Check for third peak value
		#if abs(third_peak * 10**3 + 15) > 20:
		#	print("Third peak value Event: " + str(i) + " " + str(third_peak*10**3))
			
	print("Undetected peak3 count: " + str(count))
	print("Number of peak2: " + str(count2))

	peak1Array = []
	peak2Array = []
	peak3Array = []
	# Differentiate first, second and third peaks
	# The first peak has the smallest index, the third peak has the largest
	for i in range(n_events):
		min_index = min(first_list[i][0], second_list[i][0], third_list[i][0])
		max_index = max(first_list[i][0], second_list[i][0], third_list[i][0])
		if first_list[i][1] != 0:
			if first_list[i][0] == min_index:
				peak1Array.append(abs(first_list[i][1] * 10**3))
			elif first_list[i][0] == max_index:
				peak3Array.append(abs(first_list[i][1] * 10**3))
			else:
				peak2Array.append(abs(first_list[i][1] * 10**3))

		if second_list[i][1] != 0:
			if second_list[i][0] == min_index:
				peak1Array.append(abs(second_list[i][1] * 10**3))
			elif second_list[i][0] == max_index:
				peak3Array.append(abs(second_list[i][1] * 10**3))
			else:
				peak2Array.append(abs(second_list[i][1] * 10**3))
	
		if third_list[i][1] != 0:
			if third_list[i][0] == min_index:
				peak1Array.append(abs(third_list[i][1] * 10**3))
			elif third_list[i][0] == max_index:
				peak3Array.append(abs(third_list[i][1] * 10**3))
			else:
				peak2Array.append(abs(third_list[i][1] * 10**3))


	# Take the mean values
#	baseline_mean = np.mean(baseline_list)
#	if baseline_mean > 0:
#		print("Run number: " + str(runs[run_ind]))
#		print(baseline_mean)
#		print(baseline_list)



	peak1_mean = np.mean(peak1Array)
	peak2_mean = np.mean(peak2Array)
	peak3_mean = np.mean(peak3Array)
	mean_list1.append(peak1_mean)
	mean_list2.append(peak2_mean)
	mean_list3.append(peak3_mean)
#	baseline.append(baseline_mean)
	print("peak1: " + str(peak1_mean))
	print("peak2: " + str(peak2_mean))
	print("peak3: " + str(peak3_mean))
#	print("baseline: " + str(baseline_mean))
	# Take RMS deviation
#	std_baseline = np.std(baseline_list) / math.sqrt(len(baseline_list)) 
	std1 = np.std(peak1Array) / math.sqrt(len(peak1Array))
	std2 = np.std(peak2Array) / math.sqrt(len(peak2Array))
	std3 = np.std(peak3Array) / math.sqrt(len(peak3Array))
	error_list1.append(std1)
	error_list2.append(std2)
	error_list3.append(std3)
#	baseline_error.append(std_baseline)
	print("std1: " + str(std1))
	print("std2: " + str(std2))
	print("std3: " + str(std3))
	f_open.close()

	#print(str(len(peak3Array)))
# Create root file
rootFile = '%speaks_scan_%s.root' % (RootFilePath, scan)
f_root = TFile(rootFile, "RECREATE")
treeName = 'data'
tree = TTree(treeName, treeName)
n_run = len(runs)
run_array = np.zeros(len(runs), dtype=np.dtype('u4'))
timestamp_array = np.zeros(len(runs), dtype=np.float32)
voltage_array = np.zeros(len(runs), dtype=np.float32)
temperature_array = np.zeros(len(runs), dtype=np.float32)
#baseline_array = np.zeros(len(runs), dtype=np.float32)
#baseline_error_array = np.zeros(len(runs), dtype=np.float32)
mean1_array = np.zeros(len(runs), dtype=np.float32)
mean2_array = np.zeros(len(runs), dtype=np.float32)
mean3_array = np.zeros(len(runs), dtype=np.float32)
std1_array = np.zeros(len(runs), dtype=np.float32)
std2_array = np.zeros(len(runs), dtype=np.float32)
std3_array = np.zeros(len(runs), dtype=np.float32)
voltage_sq = np.zero(len(runs), dtype=np.float32)

tree.Branch('run_number', run_array, 'run_number['+str(n_run)+']/i') # unsigned integer
tree.Branch('timestamp', timestamp_array, 'timestamp['+str(n_run)+']/F')
#tree.Branch('baseline', baseline_array, 'baseline['+str(n_run)+']/F')
#tree.Branch('baseline_error', baseline_error_array, 'baseline_error['+str(n_run)+']/F')
tree.Branch('voltage', voltage_array, 'voltage['+str(n_run)+']/F')
tree.Branch('voltage_square', voltage_sq, 'voltage_square['+str(n_run)+']/F') 
tree.Branch('temperature', temperature_array, 'temperature['+str(n_run)+']/F')
tree.Branch('peak1_mean', mean1_array, 'peak1_mean['+str(n_run)+']/F')
tree.Branch('peak2_mean', mean2_array, 'peak2_mean['+str(n_run)+']/F')
tree.Branch('peak3_mean', mean3_array, 'peak3_mean['+str(n_run)+']/F')
tree.Branch('peak1_error', std1_array, 'peak1_error['+str(n_run)+']/F')
tree.Branch('peak2_error', std2_array, 'peak2_error['+str(n_run)+']/F')
tree.Branch('peak3_error', std3_array, 'peak3_error['+str(n_run)+']/F')

for a in range(len(runs)):
	run_array[a] = runs[a]
	timestamp_array[a] = timestamps[a]
	voltage_array[a] = voltages[a]
	temperature_array[a] = temperatures[a]
	#baseline_array[a] = baseline[a]
	#baseline_error_array[a] = baseline_error[a]
	mean1_array[a] = mean_list1[a]
	std1_array[a] = error_list1[a]
	mean2_array[a] = mean_list2[a]
	std2_array[a] = error_list2[a]
	mean3_array[a] = mean_list3[a]
	std3_array[a] = error_list3[a]
	voltage_sq[a] = voltages[a]**2
tree.Fill()
f_root.cd()
tree.Write()
f_root.Close()

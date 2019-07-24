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

parser.add_argument('--Run', metavar='Run', type=int, help='Run Number to process', required=True)
parser.add_argument('--Event', metavar='Event', type=int, help='Event Number to process', required=True)
args = parser.parse_args()
run = args.Run
event = args.Event

RawDataPath = '/home/sxie/KeySightScope/KeySightScopeMount/'
RawDataLocalCopyPath = '/home/sxie/KeySightScope/RawData/'
OutputFilePath = '/home/sxie/KeySightScope/Peaks/'
TimeFile = '/home/sxie/ETL_Agilent_MSO-X-92004A/Acquisition/TimestampFile.txt'
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

# Run files
inputFileName1 = "Wavenewscope_CH1_" + str(run) + ".bin"
inputFile1 = os.path.join(RawDataPath, inputFileName1)
n_points = keysight_get_points(inputFile1)[0]

input1 = fast_Keysight_bin(inputFile1, 1, n_points) ## to get the number of segments/events and points

n_events = list (input1[1])[0] ## number of events/segments
n_points = list(input1[2])[0] ## number of points acquired for each event/segment
print "n_events = ", n_events
print "n_points = ", n_points
#	print(list(input1[0][1]))
inputloop = fast_Keysight_bin(inputFile1, event+1, n_points) ## to get the number of segments/events and points
wave = list(inputloop[0][1]) # y axis

for a in range(len(wave)):
	wave[a] *= 10**3


timeArray = list(inputloop[0][0])#x_axis
plt.plot(timeArray[:300], wave[:300])
plt.show()

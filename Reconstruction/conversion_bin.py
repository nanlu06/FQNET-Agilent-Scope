import struct  #struct unpack result - tuple
import numpy as np
import matplotlib.pyplot as plt

def import_Keysight_bin(filepath_in, index_in):
    # read from file
    my_index = index_in
    my_file = open(filepath_in, 'rb')
    b_cookie = my_file.read(2) #char
    b_version = my_file.read(2) #char
    b_size = struct.unpack('i', my_file.read(4)) #int32 - i
    b_nwaveforms = struct.unpack('i', my_file.read(4)) #int32 - i
    # check to make sure index is < b_waveforms, if not return 1st waveform
    if my_index <= b_nwaveforms[0]:
        my_index = my_index
    else:
        my_index = 1

    for i in range(0,b_nwaveforms[0]):
            b_header = struct.unpack('i', my_file.read(4)) #int32 - i
            remaining = b_header[0] - 4
            b_wavetype = struct.unpack('i', my_file.read(4)) #int32 - i
            remaining = remaining - 4
            b_wavebuffers = struct.unpack('i', my_file.read(4)) #int32 - i
            remaining = remaining - 4
            b_points = struct.unpack('i', my_file.read(4)) #int32 - i
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

            if i == my_index-1:
                # create x axis array

                #x_axis = x_orig + x_inc * array

                x_axis = b_x_orig[0] + b_x_inc[0] * np.linspace(0, b_points[0]-1, b_points[0])
           # j loop on buffers - only returns the last buffer

            for j in range(0,b_wavebuffers[0]):
                #header size - int 32
                b_header = struct.unpack('i' , my_file.read(4)) #int32 - i
                # print 'buffer header size: ' + str(b_header[0])
                remaining = b_header[0] - 4
                #buffer type - int16
                b_buffer_type = struct.unpack('h' , my_file.read(2)) #int16 - h
                # print 'buffer type: ' + str(b_buffer_type[0])
                remaining = remaining - 2
                #bytes per point - int16
                b_bytes_per_point = struct.unpack('h' , my_file.read(2)) #int16 - h
                # print 'bytes per point: ' + str(b_bytes_per_point[0])
                remaining = remaining - 2
                #buffer size - int32
                b_buffer_size = struct.unpack('i' , my_file.read(4)) #int32 - i
                # print 'buffer size: ' + str(b_buffer_size[0])
                remaining = remaining - 4
                # print 'remaining header: ' + str(remaining)
                # create y axis for voltage vector
                # currently ONLY standard voltage -  float32 - Buffer Type 1 / 2 / 3
                b_y_data = my_file.read(b_buffer_size[0])
                if i == my_index-1:
                    y_axis = struct.unpack("<"+str(b_points[0])+"f", b_y_data)
    my_file.close()
    return_array = [x_axis,y_axis]

    return return_array

## read the input files
inputFile1 = '/Users/tanviwamorka/Desktop/Wavenewscope_CH3_Apr2_87.bin'
inputFile2 = '/Users/tanviwamorka/Desktop/Wavenewscope_CH3_Apr2_87.bin'
inputFile3 = '/Users/tanviwamorka/Desktop/Wavenewscope_CH3_Apr2_87.bin'
inputFile4 = '/Users/tanviwamorka/Desktop/Wavenewscope_CH3_Apr2_87.bin'

index = 4

input1 = import_Keysight_bin(inputFile1,index)
input2 = import_Keysight_bin(inputFile2,index)
input3 = import_Keysight_bin(inputFile3,index)
input4 = import_Keysight_bin(inputFile4,index)

x_axis = input1[0]
y_axis_CH1 = input1[1]
y_axis_CH2 = input2[1]
y_axis_CH3 = input3[1]
y_axis_CH4 = input4[1]

n_events = len(x_axis)
print (len(x_axis))
# plt.plot(x_axis, y_axis)
# plt.show()

## prepare the output files
outputFile = 'output.root'
outRoot = ROOT.TFile(outputFile, "RECREATE")
outTree = ROOT.TTree("reco","reco")

i_evt = np.zeros(1,dtype=np.dtype("u4"))
channel = np.zeros([4,32005],dtype=np.float32)
time = np.zeros([1,32005],dtype=np.float32)

outTree.Branch('i_evt',i_evt,'i_evt/i')
outTree.Branch( 'channel', channel, 'channel[4][32005]/F' )
outTree.Branch( 'time', time, 'time[1][32005]/F')

time = x_axis
for event in range(n_events):
    i_evt[0] = event
    channel[0] = y_axis_CH1[event]
    channel[1] = y_axis_CH2[event]
    channel[2] = y_axis_CH3[event]
    channel[3] = y_axis_CH4[event]

    outTree.Fill()

outRoot.cd()
outTree.Write()
outRoot.Close()

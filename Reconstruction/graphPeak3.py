import datetime
import time
import numpy as np
import argparse
import os
from ROOT import TFile, TTree, TGraphErrors, TCanvas
from ROOT import*
import math
# command line input format example: input scan24 and scan25: --Scan 24 --Scan 25
parser = argparse.ArgumentParser(description='Read peaks and plot peak versus time and voltage')
parser.add_argument('--Scan', metavar='Scan', action='append', type=str, help='Scan numbers', required=True)
args = parser.parse_args()
scan = args.Scan
InputPath = '/home/sxie/KeySightScope/PeaksRootFiles/'
OutputPath = '/home/sxie/KeySightScope/Peak3/'
#VoltageFilePath = '/home/mhussain/InterFerDAQ/VoltageScanDataRegistry/'
#PDFFilePath = '/home/sxie/KeySightScope/Plots_PDFs/scan%s/' % (scan)

timestamps = []
peak3 = []
error3 = []

for a in range(len(scan)):
#	voltageFile = '%sscan%s.txt' % (VoltageFilePath, scan[a])
#	f_voltage = open(voltageFile, 'r')
	n_points = 0
#	for line in f_voltage:
#		n_points += 1


	InputFile = '%speaks_scan_%s.root' % (InputPath, scan[a])
	f = TFile.Open(InputFile, "READ")
	tr = f.Get("data")
#	print('n_points: ' + str(n_points))
	for evt in tr:
		print('time: ' + str(len(evt.timestamp)))
		print('peak3: ' + str(len(evt.peak3_mean)))
		print('error3: ' + str(len(evt.peak3_error)))
		for i in range(len(evt.timestamp)):
			if i % 2 == 0:
				timestamps.append(evt.timestamp[i])
				peak3.append(evt.peak3_mean[i])
				error3.append(evt.peak3_error[i])
		
print(timestamps)
# Time plots
# Find smallest value in timestamps
#for i in range(len(timestamps)):
#	print(str(i) + ': ' + str(timestamps[i] - timestamps[0]))
#time_min = timestamps[0]
#for i in range(n_points):
#	if time_min > timestamps[i]:
#		time_min = timestamps[i]
#		min_index = i
temperature = np.zeros(len(timestamps), dtype=np.float32)
temperature_error = np.zeros(len(timestamps), dtype=np.float32)
timestamps_array = np.zeros(len(timestamps), dtype=np.float32)
time_error = np.zeros(len(timestamps), dtype=np.float32)
peak3_array = np.zeros(len(timestamps), dtype=np.float32)
error3_array = np.zeros(len(timestamps), dtype=np.float32)
for i in range(len(timestamps)):
	timestamps_array[i] = timestamps[i]
	peak3_array[i] = peak3[i]
	error3_array[i] = error3[i] 
scan_nums = ''
for i in range(len(scan)):
	scan_nums += '_%s' % (scan[i])


time_pdf = '%sscan%s_peak3_time.pdf' % (OutputPath, scan_nums)

# Draw graphs
c1 = TCanvas("c1", "Peak VS Time", 200, 10, 700, 500)
graph1 = TGraphErrors(len(timestamps), timestamps_array, peak3_array, time_error, error3_array)
graph1.SetTitle("peak 3 over time")
graph1.GetXaxis().SetTitle("Datetime")
graph1.GetYaxis().SetTitle("Peaks Amp (mV)")
print("Bin Number: " + str(graph1.GetXaxis().GetNbins()))
for i in range(len(timestamps_array)):
	binx = graph1.GetXaxis().FindBin(timestamps_array[i])
	graph1.GetXaxis().SetBinLabel(binx, time.ctime(timestamps_array[i]))
graph1.Draw()
c1.Update()
c1.Print(time_pdf)


c1.Clear()
temp_pdf = '%sscan%s_peak3_temperature.pdf' % (OutputPath, scan_nums)
graph2 = TGraphErrors(len(timestamps), timestamps_array, peak3_array, time_error, error3_array)
graph2.SetTitle("Peak3 Temperature")
graph2.GetXaxis().SetTitle("Temperature (degree Celsius)")
graph2.GetYaxis().SetTitle("Peaks Amp (mV)")
for i in range(len(timestamps_array)):
	binx1 = graph2.GetXaxis().FindBin(timestamps_array[i])	
	if timestamps_array[i] < time.mktime(datetime.datetime(2019, 7, 5, 14, 0).timetuple()):
		graph2.GetXaxis().SetBinLabel(binx1, "26.6")
	elif timestamps_array[i] < time.mktime(datetime.datetime(2019, 7, 5, 15, 50).timetuple()) and timestamps_array[i] >= time.mktime(datetime.datetime(2019, 7, 5, 14, 0).timetuple()):
		graph2.GetXaxis().SetBinLabel(binx1, "26.7")
	elif timestamps_array[i] >= time.mktime(datetime.datetime(2019, 7, 5, 15, 50).timetuple()) and timestamps_array[i] < time.mktime(datetime.datetime(2019, 7, 5, 15, 57).timetuple()):
		graph2.GetXaxis().SetBinLabel(binx1, "26.8")
	elif timestamps_array[i] >= time.mktime(datetime.datetime(2019, 7, 5, 15, 57).timetuple()) and timestamps_array[i] < time.mktime(datetime.datetime(2019, 7, 5, 16, 5).timetuple()):
		graph2.GetXaxis().SetBinLabel(binx1, "26.9")
	elif timestamps_array[i] >= time.mktime(datetime.datetime(2019, 7, 5, 16, 5).timetuple()) and timestamps_array[i] < time.mktime(datetime.datetime(2019, 7, 5, 16, 30).timetuple()):
		graph2.GetXaxis().SetBinLabel(binx1, "27.0")
	elif timestamps_array[i] >= time.mktime(datetime.datetime(2019, 7, 5, 16, 30).timetuple()):
		graph2.GetXaxis().SetBinLabel(binx1, "27.1")


graph2.Draw()
c1.Update()
c1.Print(temp_pdf)


# Save graphs to file
outputFile = '%speak3_time_plot%s.root' % (OutputPath, scan_nums)
f1 = TFile(outputFile, "RECREATE")
graph1.Write()
graph2.Write()
f1.Close()


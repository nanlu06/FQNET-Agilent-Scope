import numpy as np
import argparse
import os
from ROOT import TFile, TTree, TGraphErrors, TCanvas
from ROOT import*

parser = argparse.ArgumentParser(description='Read peaks and plot peak versus time')
parser.add_argument('--Start', metavar='Start', type=int, help='Start run number', required=True)
parser.add_argument('--End', metavar='End', type=int, help='End run number', required=True)
args = parser.parse_args()
start = args.Start
end = args.End
n_points = end + 1 - start
timestamps = np.zeros(n_points, dtype=np.float32)
time_error = np.zeros(n_points, dtype=np.float32)
peak1_array = np.zeros(n_points, dtype=np.float32)
error1_array = np.zeros(n_points, dtype=np.float32)
peak2_array = np.zeros(n_points, dtype=np.float32)
error2_array = np.zeros(n_points, dtype=np.float32)
peak3_array = np.zeros(n_points, dtype=np.float32)
error3_array = np.zeros(n_points, dtype=np.float32)
InputPath = '/home/sxie/KeySightScope/PeaksRootFiles/'
OutputPath = '/home/sxie/KeySightScope/Plots/'
for i in range(n_points):
	InputFile = '%speaks_run_%s.root' % (InputPath, str(i + start))
	f = TFile.Open(InputFile, "READ")
	tr = f.Get("data")
	print(str(tr.GetEntries()))
	for evt in tr:
		#evt = tr.GetEntry(0)
		timestamps[i] = evt.timestamp
		peak1_array[i] = evt.peak1_mean
		peak2_array[i] = evt.peak2_mean
		peak3_array[i] = evt.peak3_mean
		error1_array[i] = evt.peak1_error
		error2_array[i] = evt.peak2_error
		error3_array[i] = evt.peak3_error

# Find smallest value in timestamps
time_min = timestamps[0]
for i in range(n_points):
	if time_min > timestamps[i]:
		time_min = timestamps[i]
timestamps = timestamps - time_min 

# Draw graphs
c1 = TCanvas("c1", "Peak VS Time", 200, 10, 700, 500)
graph1 = TGraphErrors(n_points, timestamps, peak1_array,time_error, error1_array)
graph1.GetYaxis().SetRange(0, 600)
graph1.SetTitle("peak 1")
graph1.GetXaxis().SetTitle("Time (sec)")
graph1.GetYaxis().SetTitle("Peaks Amp (mV)")
#graph1.SetMarkerStyle(20)
graph1.Draw()

graph2 = TGraphErrors(n_points, timestamps, peak2_array, time_error, error2_array)
graph2.SetTitle("peak 2")
graph2.GetXaxis().SetTitle("Time (sec)")
graph2.GetYaxis().SetTitle("Peaks Amp (mV)")
graph2.Draw()

graph3 = TGraphErrors(n_points, timestamps, peak3_array, time_error, error3_array)
graph3.SetTitle("peak 3")
graph3.GetXaxis().SetTitle("Time (sec)")
graph3.GetYaxis().SetTitle("Peaks Amp (mV)")
graph3.Draw()

c1.Update()

# Save graphs to file
outputFile = '%speaks_plot.root' % (OutputPath)
f1 = TFile(outputFile, "RECREATE")
graph1.Write()
graph2.Write()
graph3.Write()

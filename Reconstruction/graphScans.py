import numpy as np
import argparse
import os
from ROOT import TFile, TTree, TGraphErrors, TCanvas
from ROOT import*
import math

parser = argparse.ArgumentParser(description='Read peaks and plot peak versus time and voltage')
parser.add_argument('--Scan', metavar='Scan', type=str, help='Scan number', required=True)
args = parser.parse_args()
scan = args.Scan
InputPath = '/home/sxie/KeySightScope/PeaksRootFiles/'
OutputPath = '/home/sxie/KeySightScope/Plots/'
VoltageFilePath = '/home/mhussain/InterFerDAQ/VoltageScanDataRegistry/'
PDFFilePath = '/home/sxie/KeySightScope/Plots_PDFs/scan%s/' % (scan)
voltageFile = '%sscan%s.txt' % (VoltageFilePath, scan)
f_voltage = open(voltageFile, 'r')
n_points = 0
for line in f_voltage:
	n_points += 1

timestamps = np.zeros(n_points, dtype=np.float32)
voltages = np.zeros(n_points, dtype=np.float32)
voltage_error = np.zeros(n_points, dtype=np.float32)
time_error = np.zeros(n_points, dtype=np.float32)
temperatures = np.zeros(n_points, dtype=np.float32)
temperature_error = np.zeros(n_points, dtype=np.float32)
peak1_array = np.zeros(n_points, dtype=np.float32)
error1_array = np.zeros(n_points, dtype=np.float32)
peak2_array = np.zeros(n_points, dtype=np.float32)
error2_array = np.zeros(n_points, dtype=np.float32)
peak3_array = np.zeros(n_points, dtype=np.float32)
error3_array = np.zeros(n_points, dtype=np.float32)
#baselines = np.zeros(n_points, dtype=np.float32)
#base_error = np.zeros(n_points, dtype=np.float32)
voltage_sq = np.zeros(n_points, dtype=np.float32)


InputFile = '%speaks_scan_%s.root' % (InputPath, scan)
f = TFile.Open(InputFile, "READ")
tr = f.Get("data")
print(str(tr.GetEntries()))
for evt in tr:
	timestamps = evt.timestamp
	voltages = evt.voltage
	temperatures = evt.temperature
#	baselines = evt.baseline
#	base_error = evt.baseline_error
	peak1_array = evt.peak1_mean
	peak2_array = evt.peak2_mean
	peak3_array = evt.peak3_mean
	error1_array = evt.peak1_error
	error2_array = evt.peak2_error
	error3_array = evt.peak3_error
	voltage_sq = evt.voltage_square

print(n_points)
#print(len(baselines))
#for a in range(n_points):
#	print('baseline'+str(baselines[a]))
#	print('baseline error' + str(base_error[a]))



time_min = timestamps[0]
for i in range(n_points):
	if time_min > timestamps[i]:
		time_min = timestamps[i]
for i in range(n_points):
	timestamps[i] -= time_min 


# Baseline plots
#base_temp_pdf = '%sscan%s_baseline_temperature.pdf' % (PDFFilePath, scan)
#base_time_pdf = '%sscan%s_baseline_time.pdf' % (PDFFilePath, scan)
# Baseline ratio
#base_peak1 ='%sscan%s_baseline_peak1_ratio.pdf' % (PDFFilePath, scan)
#base_peak2 ='%sscan%s_baseline_peak2_ratio.pdf' % (PDFFilePath, scan)
#bp1_ratio = np.zeros(n_points, dtype=np.float32)
#bp2_ratio = np.zeros(n_points, dtype=np.float32)
#for a in range(n_points):
#	bp1_ratio[a] = -peak1_array[a] / baselines[a]
#	bp2_ratio[a] = -peak2_array[a] / baselines[a]

# Draw graphs
#c6 = TCanvas("c6", "Baseline", 200, 10, 700, 500)
#base = TGraphErrors(n_points, temperatures, baselines, temperature_error, base_error)
#base.SetTitle("Baseline VS Temperature")
#base.GetXaxis().SetTitle("Temperature (degree Celsius)")
#base.GetYaxis().SetTitle("Baseline (mV)")
#base.Draw()
#c6.Update()
#c6.Print(base_temp_pdf) # save to pdf

#c6.Clear()
#base1 = TGraphErrors(n_points, timestamps, baselines, time_error, base_error)
#base1.SetTitle("Baseline VS Time")
#base1.GetXaxis().SetTitle("Time (sec)")
#base1.GetYaxis().SetTitle("Baseline (mV)")
#base1.Draw()
#c6.Update()
#c6.Print(base_time_pdf) # save to pdf

#c6.Clear()
#base2 = TGraph(n_points, timestamps, bp1_ratio)
#base2.SetTitle("Baseline_Peak1_Ratio VS Time")
#base2.GetXaxis().SetTitle("Time (sec)")
#base2.GetYaxis().SetTitle("Ratio")
#base2.Draw()
#c6.Update()
#c6.Print(base_peak1) # save to pdf

#c6.Clear()
#base3 = TGraphErrors(n_points, timestamps, bp2_ratio)
#base3.SetTitle("Baseline_Peak2_ratio VS Time")
#base3.GetXaxis().SetTitle("Time (sec)")
#base3.GetYaxis().SetTitle("Ratio")
#base3.Draw()
#c6.Update()
#c6.Print(base_peak2) # save to pdf

# Save graph to file
#OutputFilebase = '%sbaseline_temperature_time_plot_%s.root' % (OutputPath, scan)
#f6 = TFile(OutputFilebase, "RECREATE")
#base.Write()
#base1.Write()
#base2.Write()
#base3.Write()
#f6.Close()


# Visibility plots versus voltage
vis_pdf = '%sscan%s_visibility_voltage.pdf' % (PDFFilePath, scan)
visibility  = np.zeros(n_points, dtype=np.float32)
#visibility_error = np.zeros(n_points, dtype=np.float32)
for a in range(n_points):
	visibility[a] = peak2_array[a] / (math.sqrt(peak1_array[a]) + math.sqrt(peak3_array[a]))**2
# Draw graphs
c3 = TCanvas("c3", "Visibility VS Voltage", 200, 10, 700, 500)
vis = TGraph(n_points, voltage_sq, visibility)
vis.SetTitle("Visibility")
vis.GetXaxis().SetTitle("Voltage^2 (V^2)")
vis.GetYaxis().SetTitle("Visibility")
vis.Draw()
c3.Update()
c3.Print(vis_pdf) # save to pdf
# Save graph to file
OutputFilevis = '%svisibility_voltage_plot_%s.root' % (OutputPath, scan)
f3 = TFile(OutputFilevis, "RECREATE")
vis.Write()
f3.Close()

# Voltage plots 
# Draw graphs
voltage_pdf1 = '%sscan%s_peak1_voltage.pdf' % (PDFFilePath, scan)
voltage_pdf2 = '%sscan%s_peak2_voltage.pdf' % (PDFFilePath, scan)
voltage_pdf3 = '%sscan%s_peak3_voltage.pdf' % (PDFFilePath, scan)
c2 = TCanvas("c2", "Peak VS Voltage", 200, 10, 700, 500)
graph1v = TGraphErrors(n_points, voltage_sq, peak1_array, voltage_error, error1_array)
graph1v.SetTitle("peak 1")
graph1v.GetXaxis().SetTitle("Voltage^2 (V^2)")
graph1v.GetYaxis().SetTitle("Peaks Amp (mV)")
graph1v.Draw()
c2.Update()
c2.Print(voltage_pdf1)

c2.Clear()
graph2v = TGraphErrors(n_points, voltage_sq, peak2_array, voltage_error, error2_array)
graph2v.SetTitle("peak 2")
graph2v.GetXaxis().SetTitle("Voltage^2 (V^2)")
graph2v.GetYaxis().SetTitle("Peaks Amp (mV)")
graph2v.Draw()
c2.Update()
c2.Print(voltage_pdf2)

c2.Clear()
graph3v = TGraphErrors(n_points, voltage_sq, peak3_array, voltage_error, error3_array)
graph3v.SetTitle("peak 3")
graph3v.GetXaxis().SetTitle("Voltage^2 (V^2)")
graph3v.GetYaxis().SetTitle("Peaks Amp (mV)")
graph3v.Draw()
c2.Update()
c2.Print(voltage_pdf3)

# Save graphs to file
outputFilev = '%speaks_voltage_plot_%s.root' % (OutputPath, scan)
f2 = TFile(outputFilev, "RECREATE")
graph1v.Write()
graph2v.Write()
graph3v.Write()
f2.Close()

# Temperature plots
# Draw graphs
temperature_pdf1 = '%sscan%s_peak1_temperature.pdf' % (PDFFilePath, scan)
temperature_pdf22 = '%sscan%s_peak2_temperature.pdf' % (PDFFilePath, scan)
temperature_pdf3 = '%sscan%s_peak3_temperature.pdf' % (PDFFilePath, scan)
temperature_time = '%sscan%s_time_temperature.pdf' % (PDFFilePath, scan)
c5 = TCanvas("c5", "Temperature", 200, 10, 700, 500)
grapht = TGraphErrors(n_points, temperatures, peak1_array, temperature_error, error1_array)
grapht.SetTitle("peak 1")
grapht.GetXaxis().SetTitle("Temperature (degree Celsius)")
grapht.GetYaxis().SetTitle("Peaks Amp (mV)")
grapht.Draw()
c5.Update()
c5.Print(temperature_pdf1)

c5.Clear()
graph2t = TGraphErrors(n_points, temperatures, peak2_array, temperature_error, error2_array)
graph2t.SetTitle("peak 2")
graph2t.GetXaxis().SetTitle("Temperature (degree Celsius)")
graph2t.GetYaxis().SetTitle("Peaks Amp (mV)")
graph2t.Draw()
c5.Update()
c5.Print(temperature_pdf22)

c5.Clear()
graph3t = TGraphErrors(n_points, temperatures, peak3_array, temperature_error, error3_array)
graph3t.SetTitle("peak 3")
graph3t.GetXaxis().SetTitle("Temperature (degree Celsius)")
graph3t.GetYaxis().SetTitle("Peaks Amp (mV)")
graph3t.Draw()
c5.Update()
c5.Print(temperature_pdf3)

c5.Clear()
graph4t = TGraph(n_points, timestamps, temperatures)
graph4t.SetTitle("Temperature VS Time")
graph4t.GetXaxis().SetTitle("Time (sec)")
graph4t.GetYaxis().SetTitle("Temperature (degree Celsius)")
graph4t.Draw()
c5.Update()
c5.Print(temperature_time)

c5.Clear()
graph5t = TGraph(n_points, temperatures, visibility)
graph5t.SetTitle("Temperature VS Time")
graph5t.GetXaxis().SetTitle("Temperature (degree Celsius)")
graph5t.GetYaxis().SetTitle("Visibility")
graph5t.Draw()
tempvis = '%sscan%s_visbility_temperature.pdf' % (PDFFilePath, scan) 
c5.Update()
c5.Print(tempvis)

# Save graphs to file
outputFiletemp = '%speaks_temperature_plot_%s.root' % (OutputPath, scan)
f5 = TFile(outputFiletemp, "RECREATE")
grapht.Write()
graph2t.Write()
graph3t.Write()
graph4t.Write()
graph5t.Write()
f5.Close()





# Time plots
#time_min = timestamps[0]
#for i in range(n_points):
#	if time_min > timestamps[i]:
#		time_min = timestamps[i]
#for i in range(n_points):
#	timestamps[i] -= time_min 

time_pdf1 = '%sscan%s_peak1_time.pdf' % (PDFFilePath, scan)
time_pdf2 = '%sscan%s_peak2_time.pdf' % (PDFFilePath, scan)
time_pdf3 = '%sscan%s_peak3_time.pdf' % (PDFFilePath, scan)

# Draw graphs
c1 = TCanvas("c1", "Peak VS Time", 200, 10, 700, 500)
graph1 = TGraphErrors(n_points, timestamps, peak1_array, time_error, error1_array)
graph1.GetYaxis().SetRange(0, 600)
graph1.SetTitle("peak 1")
graph1.GetXaxis().SetTitle("Time (sec)")
graph1.GetYaxis().SetTitle("Peaks Amp (mV)")
graph1.Draw()
c1.Update()
c1.Print(time_pdf1)

c1.Clear()
graph2 = TGraphErrors(n_points, timestamps, peak2_array, time_error, error2_array)
graph2.SetTitle("peak 2")
graph2.GetXaxis().SetTitle("Time (sec)")
graph2.GetYaxis().SetTitle("Peaks Amp (mV)")
graph2.Draw()
c1.Update()
c1.Print(time_pdf2)

c1.Clear()
graph3 = TGraphErrors(n_points, timestamps, peak3_array, time_error, error3_array)
graph3.SetTitle("peak 3")
graph3.GetXaxis().SetTitle("Time (sec)")
graph3.GetYaxis().SetTitle("Peaks Amp (mV)")
graph3.Draw()
c1.Update()
c1.Print(time_pdf3)

# Save graphs to file
outputFile = '%speaks_time_plot_%s.root' % (OutputPath, scan)
f1 = TFile(outputFile, "RECREATE")
graph1.Write()
graph2.Write()
graph3.Write()
f1.Close()





# Visibilty plot versus time
visTime = '%sscan%s_visibility_time.pdf' % (PDFFilePath, scan)
c4 = TCanvas("c4", "Visibility VS Time", 200, 10, 700, 500)
vist = TGraph(n_points, timestamps, visibility)
vist.SetTitle("Visibility")
vist.GetXaxis().SetTitle("Time(sec)")
vist.GetYaxis().SetTitle("Visibility")
vist.Draw()
c4.Update()
c4.Print(visTime) # save to pdf
# Save graph to file
OutputFilevistime = '%svisibility_time_plot_%s.root' % (OutputPath, scan)
f4 = TFile(OutputFilevistime, "RECREATE")
vist.Write()
f4.Close()


import ROOT
import h5py
import sys
import optparse
import argparse
import time
import numpy as np
import os,sys
import ctypes
from array import array

parser = argparse.ArgumentParser(description='Reconstruction')

parser.add_argument('--inputFiles', metavar='input', type=str, nargs = '+', help='input files from 4 channels',required=True)
args = parser.parse_args()

##---Read the input files
f1 = h5py.File('Wavenewscope_CH'+args.inputFiles[0]+'.h5', 'r') #---Channel 1
f2 = h5py.File('Wavenewscope_CH'+args.inputFiles[1]+'.h5', 'r') #---Channel 2
f3 = h5py.File('Wavenewscope_CH'+args.inputFiles[2]+'.h5', 'r') #---Channel 3
f4 = h5py.File('Wavenewscope_CH'+args.inputFiles[3]+'.h5', 'r') #---Channel 4

##---Prepare output file
outputFile = 'output.root'
outRoot = ROOT.TFile(outputFile, "RECREATE")
outTree = ROOT.TTree("reco","reco")

i_evt = np.zeros(1,dtype=np.dtype("u4"))
channel = np.zeros([4,32005],dtype=np.float32)
time = np.zeros([1,32005],dtype=np.float32)

outTree.Branch('i_evt',i_evt,'i_evt/i')
outTree.Branch( 'channel', channel, 'channel[4][32005]/F' )
outTree.Branch( 'time', time, 'time[1][32005]/F')

#---Begin reconstruction method

n_events = f1['Waveforms']['Channel 1'].attrs['NumSegments'] #---number of events or segments
n_points = f1['Waveforms']['Channel 1'].attrs['NumPoints']   #---number of points acquired for each segment (same for each channel)

Channel1 = f1['Waveforms']['Channel 1']
Channel2 = f2['Waveforms']['Channel 2']
Channel3 = f3['Waveforms']['Channel 3']
Channel4 = f4['Waveforms']['Channel 4']

#---Store the time(same for each channel and every event)
time_temp = []
for point in range(n_points):
    time_temp.append(Channel1attrs['XDispOrigin'] + point*Channel1.attrs['XInc'])

time[0] = time_temp
for event in range(n_events):
    i_evt[0] = event
    channel[0] = Channel1['Channel 1 Seg'+str(event+1)+'Data'].value
    channel[1] = Channel2['Channel 2 Seg'+str(event+1)+'Data'].value
    channel[2] = Channel3['Channel 3 Seg'+str(event+1)+'Data'].value
    channel[3] = Channel4['Channel 4 Seg'+str(event+1)+'Data'].value

    outTree.Fill()

outRoot.cd()
outTree.Write()
outRoot.Close()

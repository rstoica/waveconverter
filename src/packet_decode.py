#!/usr/bin/env python
# This file contains the top level code for extracting binary packet
# data from an input digital waveform. It opens the file, does a first
# pass over the waveform to extract the timing between all rising and
# falling edges, divides the waveform into packets, validates the legality
# of the packet and finally extracts the data from each packet.
#
# This file assumes that each bit of the bitstream is contained in a
# single byte, each with a value of either 0x00 or 0x01.
#
import sys
import io
import os
from breakWave import breakdownWaveform
from widthToBits import separatePackets
from widthToBits import decodePacket
from widthToBits import printPacket
from waveConvertVars import *
from config import *
from manual_protocol_def import *

# execfile('waveConvertVars.py')
# execfile('config.py')


##################################### main
# should have three command line arguments: *.py inputfile outputfile
# if there are only two arguments, then we'll auto-generate the output file
# NEED: switch this to getopt
if len(sys.argv)  == 4:
    waveformFileName = sys.argv[1]
    outFileName = sys.argv[2]
    optionFlag = sys.argv[3]
elif len(sys.argv)  == 3:
    waveformFileName = sys.argv[1]
    outFileName = sys.argv[2]
    optionFlag = ""
#elif len(sys.argv)  == 2:
#    waveformFileName = sys.argv[1]
#    outFileName = "" # will assign this later after building
#    optionFlag = ""
else:
    print "    Usage: python packet_decode.py <input file>"
    print "           python packet_decode.py <input file> <output file>"
    print "           python packet_decode.py <input file> <output file> -x"
    print "           -x: hex output"
    print ""
    print "           If no output file is specified, one will be"
    print "           automatically generated by appending '.pkt' to the"
    print "           name of the input file and storing in the directory"
    print "           from which the program was invoked"
    print ""
    exit(0)

# parse input file name to extract capture parameters
# file name formate: <name>_<func>_<number>_c<center_freq>_s<samp_rate>.dat
#path, fileName = waveformFileName.rsplit("/", 1)
#prefix, suffix = fileName.split(".")
#print("file prefix: " + prefix)
# if no output file was given, generate it from the input file name
#if outFileName == "":
#    outFileName = prefix + ".pkt"

# extract the capture parameters from the input file name
#name, function, number, center, sample = prefix.split("_")
#print(" name: " + name)
#print(" function: " + function)
#print(" number: " + number)
#print(" center: " + center)
#print(" sample: " + sample)

# center freq string may contain a 'p' as a decimal point
#centerWhole, centerFract = center.split("p")
#centerWhole = centerWhole[1:] # remove 'c' character
#if centerFract: # found decimal point
#    centerFrequency = int(centerWhole) + int(centerFract[:-1])/10
#    # values have suffixes of 'k', 'M' or 'G'
#    if centerFract.endswith('k'):
#        centerFrequency *= 1000
#    elif centerFract.endswith('M'):
#        centerFrequency *= 1000000
#    elif centerFract.endswith('G'):
#        centerFrequency *= 1000000000
#else: # no decimal point
#    centerFrequency = int(centerWhole[:-1])
#    # values have suffixes of 'k', 'M' or 'G'
#    if centerWhole.endswith('k'):
#        centerFrequency *= 1000
#    elif centerWhole.endswith('M'):
#        centerFrequency *= 1000000
#    elif centerWhole.endswith('G'):
#        centerFrequency *= 1000000000
#print(centerFrequency)

# sample rates will not have decimal points
#sampleRate = int(sample[1:-1])
#if sample.endswith('k'):
#   sampleRate *= 1000
#elif sample.endswith('M'):
#    sampleRate *= 1000000
#elif sample.endswith('G'):
#    sampleRate *= 1000000000
#print(sampleRate)

# based on command line, choose the protocol
# manual assignment
if (1):
    protocol = manualProtocolAssign()
# fetch from database


masterWidthList = [] # contains the widths for the entire file
packetWidthsList = [] # list of packet width lists
packetList = [] # list of decoded packets
rawPacketList = [] # list of pre-decoded packets

# open input file for read access in binary mode
with io.open(waveformFileName, 'rb') as waveformFile: 

    # open output file for write access
    outFile = open(outFileName, 'w')

    # scan through waveform and get widths
    if (breakdownWaveform(protocol, waveformFile, masterWidthList) == END_OF_FILE):

        # separate master list into list of packets
        separatePackets(protocol, masterWidthList, packetWidthsList)

        # decode each packet and add it to the list
        i=0
        for packetWidths in packetWidthsList:
            # print("Packet #" + str(i+1) + ": ") 
            # print(packetWidths)
            decodedPacket = [] # move out of loop to main vars?
            rawPacket = [] # move out of loop to main vars?
            decodePacket(protocol, packetWidths, decodedPacket, rawPacket)
            # print "Raw and Decoded Packets:"
            # print(rawPacket)
            # print(decodedPacket)
            packetList.append(decodedPacket[:])
            rawPacketList.append(rawPacket[:])
            i+=1
            #break # debug - only do first packet

        # print packets to file
        # print masterWidthList
        # print packetWidthsList
        i=0
        for packet in packetList:
            outFile.write("Packet #" + str(i+1) + ": ") 
            printPacket(outFile, packet, optionFlag)
            i+=1
    

# after we finish, close out files and exit
outFile.close()
waveformFile.close()
exit(0)

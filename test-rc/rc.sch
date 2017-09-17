EESchema Schematic File Version 2
LIBS:power
LIBS:device
LIBS:transistors
LIBS:conn
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
LIBS:2x rc-cache
EELAYER 25 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 2 3
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L R R1
U 1 1 5932F03B
P 3450 3000
AR Path="/5932F1E3/5932F03B" Ref="R1"  Part="1" 
AR Path="/5932F205/5932F03B" Ref="R2"  Part="1" 
F 0 "R1" V 3530 3000 50  0000 C CNN
F 1 "R" V 3450 3000 50  0000 C CNN
F 2 "Resistors_SMD:R_0805_HandSoldering" V 3380 3000 50  0001 C CNN
F 3 "" H 3450 3000 50  0000 C CNN
	1    3450 3000
	0    1    1    0   
$EndComp
$Comp
L C C1
U 1 1 5932F0A8
P 3800 3350
AR Path="/5932F1E3/5932F0A8" Ref="C1"  Part="1" 
AR Path="/5932F205/5932F0A8" Ref="C2"  Part="1" 
F 0 "C1" H 3825 3450 50  0000 L CNN
F 1 "C" H 3825 3250 50  0000 L CNN
F 2 "Capacitors_SMD:C_0805_HandSoldering" H 3838 3200 50  0001 C CNN
F 3 "" H 3800 3350 50  0000 C CNN
	1    3800 3350
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR2
U 1 1 5932F0ED
P 3800 3800
AR Path="/5932F1E3/5932F0ED" Ref="#PWR2"  Part="1" 
AR Path="/5932F205/5932F0ED" Ref="#PWR3"  Part="1" 
F 0 "#PWR2" H 3800 3550 50  0001 C CNN
F 1 "GND" H 3800 3650 50  0000 C CNN
F 2 "" H 3800 3800 50  0000 C CNN
F 3 "" H 3800 3800 50  0000 C CNN
	1    3800 3800
	1    0    0    -1  
$EndComp
Wire Wire Line
	3800 3800 3800 3500
Wire Wire Line
	3800 3000 3800 3200
Wire Wire Line
	3600 3000 4050 3000
Text HLabel 4050 3000 2    60   Input ~ 0
Out
Connection ~ 3800 3000
Text HLabel 3150 3000 0    60   Input ~ 0
In
Wire Wire Line
	3150 3000 3300 3000
$EndSCHEMATC

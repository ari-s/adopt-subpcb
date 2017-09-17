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
EELAYER 25 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 3
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Sheet
S 3600 2450 550  300 
U 5932F1E3
F0 "rc" 60
F1 "rc.sch" 60
F2 "Out" I R 4150 2600 60 
F3 "In" I L 3600 2600 60 
$EndSheet
$Sheet
S 3600 3050 550  300 
U 5932F205
F0 "rc2" 60
F1 "rc.sch" 60
F2 "Out" I R 4150 3200 60 
F3 "In" I L 3600 3200 60 
$EndSheet
$Comp
L GND #PWR01
U 1 1 59BE59CA
P 3550 3800
F 0 "#PWR01" H 3550 3550 50  0001 C CNN
F 1 "GND" H 3550 3650 50  0000 C CNN
F 2 "" H 3550 3800 50  0001 C CNN
F 3 "" H 3550 3800 50  0001 C CNN
	1    3550 3800
	1    0    0    -1  
$EndComp
$Comp
L CONN_01X02 J2
U 1 1 59BE5A02
P 4650 2900
F 0 "J2" H 4650 3050 50  0000 C CNN
F 1 "CONN_01X02" V 4750 2900 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02" H 4650 2900 50  0001 C CNN
F 3 "" H 4650 2900 50  0001 C CNN
	1    4650 2900
	1    0    0    -1  
$EndComp
Wire Wire Line
	4150 2600 4450 2600
Wire Wire Line
	4450 2600 4450 2850
Wire Wire Line
	4450 2950 4450 3200
Wire Wire Line
	4450 3200 4150 3200
$Comp
L CONN_01X02 J1
U 1 1 59BE5A8A
P 3050 2900
F 0 "J1" H 3050 3050 50  0000 C CNN
F 1 "CONN_01X02" V 3150 2900 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02" H 3050 2900 50  0001 C CNN
F 3 "" H 3050 2900 50  0001 C CNN
	1    3050 2900
	-1   0    0    -1  
$EndComp
Wire Wire Line
	3250 2850 3250 2600
Wire Wire Line
	3250 2600 3600 2600
Wire Wire Line
	3250 2950 3250 3200
Wire Wire Line
	3250 3200 3600 3200
NoConn ~ 3550 3800
$EndSCHEMATC

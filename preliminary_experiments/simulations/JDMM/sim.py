"""
Simulation program JDMM.
Assembly line for short study.

Medium arrival rate: 0.30
Medium service rate: 0.55
"""
from __future__ import division

import random
import numpy as np
import functools
import simpy
import csv
import os.path
from classes import Generator, Sink, Workstation, Monitor, Inventory, Branch

#Interarrival and service time.
def Arrival():
	return 1.0/0.3

def Service():
	return 1.0/0.55

if __name__ == '__main__':
	sim_id = 'JDMM'
	env = simpy.Environment()
	
	#Distribution
	Sampling = functools.partial(random.expovariate, 1.0)

	#Elements
	gen = dict()
	for i in range(3):
		gen[i] = Generator(env, "G" + str(i), interarr=Arrival)

	sink = dict()
	for i in range(3):
		sink[i] = Sink(env, "S" + str(i))

	ws= dict()
	for i in range(30):
		ws[i] = Workstation(env, "WS" + str(i), servtime=Service, rec_csv=True, csv_name=sim_id)

	#Monitor
	mon = dict()
	for i in range(30):
		mon[i] = Monitor(env, ws[i], Sampling())

	inv = Inventory(env, gen, sink, Sampling())

	#Branch
	twobr = dict() #2 branches
	for i in range(3):
		twobr[i] = Branch(env, [0.50, 0.50])

	tribr = dict() #3 branches
	for i in range(2):
		tribr[i] = Branch(env, [1.0/3.0, 1.0/3.0, 1.0/3.0])

	forbr= dict() #4 branches etc...
	for i in range(2):
		forbr[i] = Branch(env, [0.25, 0.25, 0.25, 0.25])

	fivbr = dict()
	for i in range(10):
		fivbr[i] = Branch(env, [0.20, 0.20, 0.20, 0.20, 0.20])

	sixbr = dict()
	for i in range(4):
		sixbr[i] = Branch(env, [1.0/6.0, 1.0/6.0, 1.0/6.0, 1.0/6.0, 1.0/6.0, 1.0/6.0])

	eibr = dict()
	for i in range(12):
		eibr[i] = Branch(env, [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125])

	#Routing
	"""Generators"""
	#g0 -> 0, 5
	gen[0].out = twobr[0]
	twobr[0].outs[0] = ws[0]
	twobr[0].outs[1] = ws[5]

	#g1 -> 10, 15
	gen[1].out = twobr[1]
	twobr[1].outs[0] = ws[10]
	twobr[1].outs[1] = ws[15]

	#g2 -> 20, 25
	gen[2].out = twobr[2]
	twobr[2].outs[0] = ws[20]
	twobr[2].outs[1] = ws[25]

	"""Workstations"""
	#0 -> 1, 5, 6
	ws[0].out = tribr[0]
	tribr[0].outs[0] = ws[1]
	tribr[0].outs[1] = ws[6]
	tribr[0].outs[2] = ws[5]

	#1 -> 0, 5, 6, 7, 2
	ws[1].out = fivbr[0]
	fivbr[0].outs[0] = ws[0]
	fivbr[0].outs[1] = ws[5]
	fivbr[0].outs[2] = ws[6]
	fivbr[0].outs[3] = ws[7]
	fivbr[0].outs[4] = ws[2]

	#2 -> 1, 6, 7, 8, 3
	ws[2].out = fivbr[1]
	fivbr[1].outs[0] = ws[1]
	fivbr[1].outs[1] = ws[6]
	fivbr[1].outs[2] = ws[7]
	fivbr[1].outs[3] = ws[8]
	fivbr[1].outs[4] = ws[3]

	#3 -> 2, 7, 8, 9, 4
	ws[3].out = fivbr[2]
	fivbr[2].outs[0] = ws[2]
	fivbr[2].outs[1] = ws[7]
	fivbr[2].outs[2] = ws[8]
	fivbr[2].outs[3] = ws[9]
	fivbr[2].outs[4] = ws[4]

	#4 -> 3, 8, 9, s2
	ws[4].out = forbr[0]
	forbr[0].outs[0] = ws[3]
	forbr[0].outs[1] = ws[8]
	forbr[0].outs[2] = ws[9]
	forbr[0].outs[3] = sink[0]

	#5 -> 10, 11, 6, 1, 0
	ws[5].out = fivbr[3]
	fivbr[3].outs[0] = ws[10]
	fivbr[3].outs[1] = ws[11]
	fivbr[3].outs[2] = ws[6]
	fivbr[3].outs[3] = ws[1]
	fivbr[3].outs[4] = ws[0]

	#6 -> 5, 10, 11, 12, 7, 2, 1, 0
	ws[6].out = eibr[0]
	eibr[0].outs[0] = ws[5]
	eibr[0].outs[1] = ws[10]
	eibr[0].outs[2] = ws[11]
	eibr[0].outs[3] = ws[12]
	eibr[0].outs[4] = ws[7]
	eibr[0].outs[5] = ws[2]
	eibr[0].outs[6] = ws[1]
	eibr[0].outs[7] = ws[0]

	#7 -> 6, 11, 12, 13, 8, 3, 2, 1
	ws[7].out = eibr[1]
	eibr[1].outs[0] = ws[6]
	eibr[1].outs[1] = ws[11]
	eibr[1].outs[2] = ws[12]
	eibr[1].outs[3] = ws[13]
	eibr[1].outs[4] = ws[8]
	eibr[1].outs[5] = ws[3]
	eibr[1].outs[6] = ws[2]
	eibr[1].outs[7] = ws[1]

	#8 -> 7, 12, 13, 14, 9, 4, 3, 2
	ws[8].out = eibr[2]
	eibr[2].outs[0] = ws[7]
	eibr[2].outs[1] = ws[12]
	eibr[2].outs[2] = ws[13]
	eibr[2].outs[3] = ws[14]
	eibr[2].outs[4] = ws[9]
	eibr[2].outs[5] = ws[4]
	eibr[2].outs[6] = ws[3]
	eibr[2].outs[7] = ws[2]

	#9 -> 8, 13, 14, s2, 4, 3
	ws[9].out = sixbr[0]
	sixbr[0].outs[0] = ws[8]
	sixbr[0].outs[1] = ws[13]
	sixbr[0].outs[2] = ws[14]
	sixbr[0].outs[3] = sink[0]
	sixbr[0].outs[4] = ws[4]
	sixbr[0].outs[5] = ws[3]

	#10 -> 15, 16, 11, 6, 5
	ws[10].out = fivbr[4]
	fivbr[4].outs[0] = ws[15]
	fivbr[4].outs[1] = ws[16]
	fivbr[4].outs[2] = ws[11]
	fivbr[4].outs[3] = ws[6]
	fivbr[4].outs[4] = ws[5]

	#11 -> 10, 15, 16, 17, 12, 7, 6, 5
	ws[11].out = eibr[3]
	eibr[3].outs[0] = ws[10]
	eibr[3].outs[1] = ws[15]
	eibr[3].outs[2] = ws[16]
	eibr[3].outs[3] = ws[17]
	eibr[3].outs[4] = ws[12]
	eibr[3].outs[5] = ws[7]
	eibr[3].outs[6] = ws[6]
	eibr[3].outs[7] = ws[5]

	#12 -> 11, 16, 17, 18, 13, 8, 7, 6
	ws[12].out = eibr[4]
	eibr[4].outs[0] = ws[11]
	eibr[4].outs[1] = ws[16]
	eibr[4].outs[2] = ws[17]
	eibr[4].outs[3] = ws[18]
	eibr[4].outs[4] = ws[13]
	eibr[4].outs[5] = ws[8]
	eibr[4].outs[6] = ws[7]
	eibr[4].outs[7] = ws[6]

	#13 -> 12, 17, 18, 19, 14, 9, 8, 7
	ws[13].out = eibr[5]
	eibr[5].outs[0] = ws[12]
	eibr[5].outs[1] = ws[17]
	eibr[5].outs[2] = ws[18]
	eibr[5].outs[3] = ws[19]
	eibr[5].outs[4] = ws[14]
	eibr[5].outs[5] = ws[9]
	eibr[5].outs[6] = ws[8]
	eibr[5].outs[7] = ws[7]

	#14 -> 13, 18, 19, s1, 9, 8
	ws[14].out = sixbr[1]
	sixbr[1].outs[0] = ws[13]
	sixbr[1].outs[1] = ws[18]
	sixbr[1].outs[2] = ws[19]
	sixbr[1].outs[3] = sink[1]
	sixbr[1].outs[4] = ws[9]
	sixbr[1].outs[5] = ws[8]

	#15 -> 20, 21, 16, 11, 10
	ws[15].out = fivbr[5]
	fivbr[5].outs[0] = ws[20]
	fivbr[5].outs[1] = ws[21]
	fivbr[5].outs[2] = ws[16]
	fivbr[5].outs[3] = ws[11]
	fivbr[5].outs[4] = ws[10]

	#16 -> 15, 20, 21, 22, 17, 12, 11, 10
	ws[16].out = eibr[6]
	eibr[6].outs[0] = ws[15]
	eibr[6].outs[1] = ws[20]
	eibr[6].outs[2] = ws[21]
	eibr[6].outs[3] = ws[22]
	eibr[6].outs[4] = ws[17]
	eibr[6].outs[5] = ws[12]
	eibr[6].outs[6] = ws[11]
	eibr[6].outs[7] = ws[10]

	#17 -> 16, 21, 22, 23, 18, 13, 12, 11
	ws[17].out = eibr[7]
	eibr[7].outs[0] = ws[16]
	eibr[7].outs[1] = ws[21]
	eibr[7].outs[2] = ws[22]
	eibr[7].outs[3] = ws[23]
	eibr[7].outs[4] = ws[18]
	eibr[7].outs[5] = ws[13]
	eibr[7].outs[6] = ws[12]
	eibr[7].outs[7] = ws[11]

	#18 -> 17, 22, 23, 24, 19, 14, 13, 12
	ws[18].out = eibr[8]
	eibr[8].outs[0] = ws[17]
	eibr[8].outs[1] = ws[22]
	eibr[8].outs[2] = ws[23]
	eibr[8].outs[3] = ws[24]
	eibr[8].outs[4] = ws[19]
	eibr[8].outs[5] = ws[14]
	eibr[8].outs[6] = ws[13]
	eibr[8].outs[7] = ws[12]

	#19 -> 18, 23, 24, s1, 14, 13
	ws[19].out = sixbr[2]
	sixbr[2].outs[0] = ws[18]
	sixbr[2].outs[1] = ws[23]
	sixbr[2].outs[2] = ws[24]
	sixbr[2].outs[3] = sink[1]
	sixbr[2].outs[4] = ws[14]
	sixbr[2].outs[5] = ws[13]

	#20 -> 15, 16, 21, 26, 25
	ws[20].out = fivbr[6]
	fivbr[6].outs[0] = ws[15]
	fivbr[6].outs[1] = ws[16]
	fivbr[6].outs[2] = ws[21]
	fivbr[6].outs[3] = ws[26]
	fivbr[6].outs[4] = ws[25]

	#21 -> 20, 25, 26, 27, 22, 17, 16, 15
	ws[21].out = eibr[9]
	eibr[9].outs[0] = ws[20] 
	eibr[9].outs[1] = ws[25]
	eibr[9].outs[2] = ws[26]
	eibr[9].outs[3] = ws[27]
	eibr[9].outs[4] = ws[22]
	eibr[9].outs[5] = ws[17]
	eibr[9].outs[6] = ws[16]
	eibr[9].outs[7] = ws[15]

	#22 -> 21, 26, 27, 28, 23, 18, 17, 16
	ws[22].out = eibr[10]
	eibr[10].outs[0] = ws[21]
	eibr[10].outs[1] = ws[26]
	eibr[10].outs[2] = ws[27]
	eibr[10].outs[3] = ws[28]
	eibr[10].outs[4] = ws[23]
	eibr[10].outs[5] = ws[18]
	eibr[10].outs[6] = ws[17]
	eibr[10].outs[7] = ws[16]

	#23 -> 22, 27, 28, 29, 24, 19, 18, 17
	ws[23].out = eibr[11]
	eibr[11].outs[0] = ws[22]
	eibr[11].outs[1] = ws[27]
	eibr[11].outs[2] = ws[28]
	eibr[11].outs[3] = ws[29]
	eibr[11].outs[4] = ws[24]
	eibr[11].outs[5] = ws[19]
	eibr[11].outs[6] = ws[18]
	eibr[11].outs[7] = ws[17]

	#24 -> 23, 28, 29, s2, 19 18
	ws[24].out = sixbr[3]
	sixbr[3].outs[0] = ws[23]
	sixbr[3].outs[1] = ws[28]
	sixbr[3].outs[2] = ws[29]
	sixbr[3].outs[3] = sink[2]
	sixbr[3].outs[4] = ws[19]
	sixbr[3].outs[5] = ws[18]

	#25 -> 20, 21, 26
	ws[25].out = tribr[1]
	tribr[1].outs[0] = ws[20]
	tribr[1].outs[1] = ws[21]
	tribr[1].outs[2] = ws[26]

	#26 -> 25, 20, 21, 22, 27
	ws[26].out = fivbr[7]
	fivbr[7].outs[0] = ws[25]
	fivbr[7].outs[1] = ws[20]
	fivbr[7].outs[2] = ws[21]
	fivbr[7].outs[3] = ws[22]
	fivbr[7].outs[4] = ws[27]

	#27 -> 26, 21, 22, 23, 28
	ws[27].out = fivbr[8]
	fivbr[8].outs[0] = ws[26]
	fivbr[8].outs[1] = ws[21]
	fivbr[8].outs[2] = ws[22]
	fivbr[8].outs[3] = ws[23]
	fivbr[8].outs[4] = ws[28]

	#28 -> 27, 22, 23, 24, 29
	ws[28].out = fivbr[9]
	fivbr[9].outs[0] = ws[27]
	fivbr[9].outs[1] = ws[22]
	fivbr[9].outs[2] = ws[23]
	fivbr[9].outs[3] = ws[24]
	fivbr[9].outs[4] = ws[29]

	#29 -> 28, 23, 24 s2
	ws[29].out = forbr[1]
	forbr[1].outs[0] = ws[28]
	forbr[1].outs[1] = ws[23]
	forbr[1].outs[2] = ws[24]
	forbr[1].outs[3] = sink[2]

	#Run!
	env.run(until=1000)

	#Concatanate lists.
	throughputs = []
	for i in sink:
		throughputs += sink[i].ttp

	utils = []
	for i in mon:
		utils += mon[i].util

	q = []
	for i in mon:
		q += mon[i].queue

	#Performance
	mean_throughput = np.mean(throughputs)
	var_throughput = np.var(throughputs)
	cap_util = np.mean(utils)
	wip = np.mean(inv.wiplevels)
	qlen = np.mean(q) #Mean queue size. An alternative performance measure not commonly used in manufacturing.

	#Performance CSV Writer
	save_path = '/Users/manuelschipper/Documents/spring_15/thesis/07-Test/simulations/REC_DATA'
	name_of_file = 'performance'
	complete_filename = os.path.join(save_path, name_of_file + '.csv')
	sectarget = open(complete_filename, 'a')
	try:
		write = csv.writer(sectarget)
		write.writerow((sim_id, mean_throughput, var_throughput, cap_util, wip, qlen))
	except:
		raise Exception('Error writing performance into CSV file')
	finally:
		sectarget.close()

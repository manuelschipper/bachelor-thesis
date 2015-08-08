"""MM1 Queue"""
from __future__ import division

import random
import numpy as np
import functools
import simpy
from classes import Generator, Sink, Workstation, Monitor, Inventory

if __name__ == '__main__':
	env = simpy.Environment()

	"""The parameter for the expovariate function is 1/mean, 
	thus we talk about arrival and service rates"""
	Arrival = functools.partial(random.expovariate, 0.5)
	Service = functools.partial(random.expovariate, 1.0) 
	Sampling = functools.partial(random.expovariate, 1.0)

	#Elements
	gen = Generator(env, "G01", interarr=Arrival)
	sink = Sink(env, "S01")
	ws = Workstation(env, "WS1", servtime=Service)

	#Routing
	gen.out = ws
	ws.out = sink

	#Monitor
	mon = Monitor(env, ws, Sampling())

	#Inventory
	g = []
	g.append(gen)
	s = []
	s.append(sink)
	inv = Inventory(env, g, s, Sampling())

	#Run!
	env.run(until=8000)

	#Computations
	mean_throughput = np.mean(sink.ttp)
	var_throughput = np.var(sink.ttp)
	emp_cap_util = np.mean(mon.util)
	emp_wip = np.mean(inv.wiplevels)
	eff_arr = np.mean(gen.ir)
	eff_ser = np.mean(ws.processings)
	real_cu = sum(ws.processings)/8000
	qlen = np.mean(mon.queue)

	#Prints
	"""
	print "\n"
	print "Testing parameters" #Measures used to test the correctness of the implementation.
	print "-----------------------------------------"
	print "Effective Service Time: " + str(eff_ser)
	print "Effective Service Rate: " + str(1/eff_ser)
	print "Effective Inter-Arrival Time: " + str(eff_arr)
	print "Effective Arrival Rate: " + str(1/eff_arr)
	print "\n"
	print "Testing measures computation" #A comparison of different means to compute performance indicators.
	print "-----------------------------------------"
	print "Average Throughput Time: " + str(mean_throughput)
	print "Empirical WIP: " + str(emp_wip)
	print "Analytical WIP: " + str((1/eff_arr) * mean_throughput)
	print "Empirical Capacity Utilization: " + str(emp_cap_util)
	print "Analytical Capacity Utilization: " + str(real_cu)
	print "\n"
	"""
	print "PERFORMANCE MEASURES" #Chosen means of computing performance.
	print "-----------------------------------------"
	print "Mean Throughput Time: " + str(mean_throughput)
	print "Variance Throughput Time: " + str(var_throughput)
	print "Analytical Capacity Utilization: " + str(real_cu)
	print "Empirical WIP: " + str(emp_wip)
	print "\n"
	print "ADDITIONAL MEASURES" 
	print "-------------------------------------------"
	print "Mean Queue Size: " + str(qlen)

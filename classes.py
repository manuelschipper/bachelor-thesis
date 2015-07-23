"""
	Manuel Schipper
	Bachelor Thesis
	A set of classes suited to model queueing manufacturing systems.
"""

from __future__ import division
import simpy
import random
import csv
import itertools

class Job(object):
	"""Simple class representing a job.

	Parameters
	----------
	time : float
		the time when it was generated.
	id : id
		an identifier
	src : id
		a source identifier"""
	#Create new unique id.
	newid = itertools.count().next
	def __init__(self, time, src = 'a'):
		self.time = time
		self.id = Job.newid()
		self.src = src

	def __repr__(self):
		return "Id: {}, Generated: {}, Source: {}" .\
			format(self.id, self.time, self.src)


class Generator(object):
	"""Generates job with a given inter-arrival time.
	The out member variable is set to the entity receiving the job

	Parameters
	----------
	interarr : function
		succesive inter-arrival times (def = 1)
	finish : float
		stop generating at a time (def = infinite)"""
	def __init__ (self, env, id, interarr, finish = float("inf")):
		self.id = id
		self.env = env
		self.interarr = interarr
		self.finish = finish
		self.out = None
		self.jobs_sent = 0
		self.ir = []#Track effective interarrivals.
		self.action = env.process(self.run())

	def run(self):
		while self.env.now < self.finish:
			start = self.env.now
			yield self.env.timeout(self.interarr())
			end = self.env.now
			self.ir.append(end-start)
			self.jobs_sent += 1
			order = Job(self.env.now, src=self.id)
			self.out.put(order)

class Sink(object):
	"""Receives jobs and collects arrival information

	Parameters
	----------
	rec_arrivals : boolean
		record inter-arrivals (def = True)
	abs_arrivals : boolean
		record absolute arrivals (def = False)
	rec_ttp : boolean
		record (throughput) time it took a job to arrive to sink since generated. (def = True)
	debug : boolean
		if true, print contents of job to screen (def = False)"""
	def __init__(self, env, id, rec_arrivals= True, abs_arrivals= False, rec_ttp= True, debug= False):
		self.store = simpy.Store(env) #Simpy store class allows to put in the store and retrieve in FIFO discipline
		self.env = env
		self.id = id
		self.rec_arrivals = rec_arrivals
		self.abs_arrivals = abs_arrivals
		self.rec_ttp = rec_ttp
		self.ttp = [] 
		self.arrivals = []
		self.storage = 0 #Counter of jobs received
		self.debug = debug 
		self.action = env.process(self.run())

	def run (self):
		last_arrival = 0.0
		while True:
			wip = (yield self.store.get()) #Get a job from the 'store'
			now = self.env.now
			if self.rec_ttp:
				self.ttp.append(self.env.now - wip.time)
			if self.rec_arrivals:
				if self.abs_arrivals:
					self.arrivals.append(now)
				else:
					self.arrivals.append(now - last_arrival)
				last_arrival = now
			self.storage += 1
			if self.debug:
				print wip

	def put(self, order):
		self.store.put(order)

class Workstation(object):
	"""Jobs arrive and get processed one by one.
	Retrieved from the store in FIFO discipline.
	The 'out' is set to entity to receive the job after a processing step.

	Parameters
	----------
	servtime : function
		the time spent processing a job (def = 1)
	rec_csv : boolean (def = False)
		dump feedback data into csv: job_id, workstation_id, start_time, end_time, total_time
	csv_name : string (def = None)
		csv file name
	debug : boolean (def = False) """
	def __init__(self, env, id, servtime, rec_csv = False, csv_name = None, debug=False):
		self.store = simpy.Store(env)
		self.env = env
		self.id = id
		self.servtime = servtime
		self.rec_csv = rec_csv
		self.csv_name = csv_name
		self.debug = debug
		self.out = None
		self.processed = 0 #Counter of jobs processed
		self.busy = 0 #Track if station is busy
		self.processings = []#Track processing times.
		self.action = env.process(self.run())

	def run(self):
		while True:
			wip = (yield self.store.get())
			start_time = self.env.now
			self.busy = 1
			if self.debug:
				print wip
			yield self.env.timeout(self.servtime())
			self.out.put(wip)
			self.busy = 0
			self.processed += 1
			end_time = self.env.now
			total_time = end_time - start_time
			self.processings.append(total_time)
			if self.debug:
				print wip
			if self.rec_csv:
				target = open(self.csv_name, 'a')
				try:
					writer = csv.writer(target)
					writer.writerow((wip.id, self.id, start_time, end_time, total_time))
				except:
					print("Error writing data into CSV File")
				finally:
					target.close()

	def put(self, order):
		return self.store.put(order)

class Monitor(object):
	"""Monitors the queue and utilization of a station at time inter-arrivals

	Parameters
	----------
	station : Workstation
	dist : function
		a no parameter function that returns successive sampling times.
	"""
	def __init__(self, env, station, dist):
		self.env = env
		self.station = station
		self.dist = dist
		self.queue = []
		self.util = []
		self.action = env.process(self.run())

	def run(self):
		while True:
			yield self.env.timeout(self.dist)
			size = len(self.station.store.items) + self.station.busy
			self.queue.append(size)
			process = self.station.busy
			self.util.append(process)

class Inventory(object):
	"""A monitor that looks at WIP levels. It samples
	at period of times given by a distribuition the amount of
	Job instances in the system by computing the difference
	of generated from the Generator and arrivals from the Sink.

	Parameters
	----------
	generators : list of Generator instances
	sinks : list of Sink instances
	dist : function
	"""

	def __init__(self, env, generators, sinks, dist):
		self.env = env
		self.generators = generators
		self.sinks = sinks
		self.dist = dist
		self.wiplevels = []
		self.action = env.process(self.run())

	def run(self):
		while True:
			yield self.env.timeout(self.dist)
			for i, j, in zip(self.generators, self.sinks):
				total = i.jobs_sent - j.storage
				self.wiplevels.append(total)

class Branch(object):
	"""A brancher that chooses the output station at random.
	Contains a list of output stations of the same length as the probability list
	in the constructor.  Use these to connect to other network elements.

	Parameters
	-----------
	probs : list"""
	def __init__(self, env, probs):
		self.env = env
		self.probs = probs
		self.ranges = [sum(probs[0:n+1]) for n in range(len(probs))]
		if self.ranges[-1] - 1.0 > 1.0e-6:
			raise Exception("Probabilities must sum to 1.0")
		self.n_stations = len(self.probs)
		self.outs = [None for i in range(self.n_stations)]
		self.jobs_sent = 0

	def weighted_choice(self, weights):
		rnd = random.random() * sum(weights)
		for i, w in enumerate(weights):
			rnd -= w
			if rnd < 0:
				return i

	def put(self, order):
		self.jobs_sent += 1
		index = self.weighted_choice(self.probs)
		self.outs[index].put(order)

"""
	Acknowledgements:

	Thanks to Greg Bernstein of Grotto Networking for 
	hosting code on queueing networks in his website.
	This set of classes and other example code 
	are partially taken of his demonstration code.

	Thanks Eli Bendersky's for his discussion on weighted choice
	algorithms and his implementations. The weighted_choice function
	is taken from there.
"""

## Synchronization in manufacturing systems. ##

In my bachelor thesis we attempt to gain a more profound understanding on how does synchronization emerges and affects manufacturing systems.

It is in line with the ongoing research goal outlined in:

[Chankov, S. M., Becker, T., & Windt, K. 2014. Towards Definition of Synchronization in Logistics Systems. Procedia CIRP, 17, 594-599.](http://www.sciencedirect.com/science/article/pii/S2212827114003436)

And in particular synchronization measures follow the path presented in:

[Becker, T., Chankov, M. S., & Windt, K. 2013. Synchronization Measures in Job Shop Manufacturing Environments. Procedia CIRP, 7, 157-162.](http://www.sciencedirect.com/science/article/pii/S2212827113002345)

We conduct an exploratory study for which I have programmed computer simulations of manufacturing systems. It is primarly implemented using the SimPy module in Python. We use the Simpy.Store container to model a queueing station in this case representing an abstraction of a work system. 

The files classes.py contain scalable Python classes to simulate dynamic queueing systems and is well documented with comments. The mm1.py file models an M/M/1 queue. More complex manufacturing system networks can be found in the preliminary_experiments subdirectory.

function [baseMVA, bus, gen, branch] = threebus
%   $Id: 3bus.m,v 1.1 2007/10/29 16:27:59 rawl Exp $

%%-----  Power Flow Data  -----%%
%% system MVA base
baseMVA = 100;

%% bus data
%
%    1  PQ    PQ bus
%    2  PV    PV bus
%    3  REF   reference bus
%    4  NONE  isolated bus
%
%	bus_i	type	Pd	Qd	Gs	Bs	area	Vm	Va	baseKV	zone	Vmax	Vmin
bus = [
	1	3	0	0	0	0	1	1	0	400	1	1.1	0.9;
	2	2	0	0	0	0	1	1	0	400	1	1.1	0.9;
	3	1	60	30	0	0	1	1	0	400	1	1.1	0.9;
];

%% generator data
%	bus	Pg	Qg	Qmax	Qmin	Vg	mBase	status	Pmax	Pmin
gen = [
	1	60	0	60	-60	1.01	100	1	100	0;
	2	80	0	60	-60	1.02	100	1	100	0;
];

%% branch data
%	fbus	tbus	r	x	b	rateA	rateB	rateC	ratio	angle	status
branch = [
	1	2	0.01	0.04	0.07	250	250	250	0	0	1;
	1	3	0.02	0.05	0.08	250	250	250	0	0	1;
	2	3	0.03	0.06	0.09	250	250	250	0	0	1;
];

%%-----  OPF Data  -----%%
%% area data
%	no.	price_ref_bus
areas = [
	1	1;
];

%% generator cost data
%
% Piecewise linear:
%	1	startup	shutdown	n_point x1	y1	...	xn	yn
%
% Polynomial:
%	2	startup	shutdown	n_coeff	c(n-1)	...	c0
gencost = [
	2	0.0	0.0	3	0.0	2.0	0.0;
	1	0.0	0.0	2	0.0	0.0	1.0	8.0;
]

return;

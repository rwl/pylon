function qp
% problem from from http://www.uc.edu/sashtml/iml/chap8/sect12.htm

H = [   1003.1  4.3     6.3     5.9;
        4.3     2.2     2.1     3.9;
        6.3     2.1     3.5     4.8;
        5.9     3.9     4.8     10  ];

c = zeros(4,1);

A = [   1       1       1       1;
        0.17    0.11    0.10    0.18    ];

l = [1; 0.10];
u = [1; Inf];

xmin = zeros(4,1);

x0 = [1; 0; 0; 1];

opt = struct('verbose', 2);
[x, f, s, out, lam] = qps_matpower(H, c, A, l, u, xmin, [], x0, opt);

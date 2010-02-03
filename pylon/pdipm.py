#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#------------------------------------------------------------------------------

""" Primal-dual interior point method for NLP.

    References:
        Ray Zimmerman, "pdipm.m", MATPOWER, PSERC Cornell, version 4.0b1,
        http://www.pserc.cornell.edu/matpower/, December 2009
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from numpy import nonzero, Inf, any, isnan, asarray
from numpy.linalg import norm, solve

from cvxopt import matrix, spmatrix, sparse, spdiag, div, log

from cvxopt import umfpack #@UnusedImport
from cvxopt import cholmod #@UnusedImport
from cvxopt import lapack #@UnusedImport

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

EPS = 2**-52

#------------------------------------------------------------------------------
#  "pdipm" function:
#------------------------------------------------------------------------------

def pdipm(ipm_f, ipm_gh, ipm_hess, x0, xmin=None, xmax=None,
          A=None, l=None, u=None, opt=None):
    """ x, f, info, output, lmbda = \
            pdipm(f, gh, hess, x0, xmin, xmax, A, l, u, opt)

        min f(x)
          s.t.
        h(x) = 0
        g(x) <= 0
        l <= A*x <= u
        xmin <= x <= xmax
    """
    xmin = matrix(-Inf, x0.size) if xmin is None else xmin
    xmax = matrix( Inf, x0.size) if xmax is None else xmax
    if A is None:
        A = spmatrix([], [], [], (0, x0.size[0]))
        l = matrix(0.0, (0, 1))
        u = matrix(0.0, (0, 1))

    opt = {} if opt is None else opt
    if not opt.has_key("feastol"):
        opt["feastol"] = 1e-06
    if not opt.has_key("gradtol"):
        opt["gradtol"] = 1e-06
    if not opt.has_key("comptol"):
        opt["comptol"] = 1e-06
    if not opt.has_key("costtol"):
        opt["costtol"] = 1e-06
    if not opt.has_key("max_it"):
        opt["max_it"] = 150
    if not opt.has_key("max_red"):
        opt["max_red"] = 20
    if not opt.has_key("step_control"):
        opt["step_control"] = False
    if not opt.has_key("cost_mult"):
        opt["cost_mult"] = 1
    if not opt.has_key("verbose"):
        opt["verbose"] = False

    # constants
    xi = 0.99995
    sigma = 0.1
    z0 = 1
    alpha_min = 1e-8
    rho_min = 0.95
    rho_max = 1.05
    mu_threshold = 1e-5

    # initialize
    i = 0                      # iteration counter
    converged = False          # flag
    nx = x0.size[0]            # number of variables
    nA = A.size[0]             # number of original linear constraints

    # add var limits to linear constraints
    AA = sparse([spmatrix(1.0, range(nx), range(nx)), A])
    ll = matrix([xmin, l])
    uu = matrix([xmax, u])

    # split up linear constraints
    ieq = matrix([j for j, v in enumerate(abs(uu - ll)) if v < EPS])
    igt = matrix([j for j in range(len(ll)) if uu[j] >=  1e10 and ll[j]>-1e10])
    ilt = matrix([j for j in range(len(ll)) if ll[j] <= -1e10 and uu[j]< 1e10])
    ibx = matrix([j for j in range(len(ll))
                  if (abs(uu[j] - ll[j]) > EPS) and
                  (uu[j] < 1e10) and (ll[j] > -1e10)])
    Ae = AA[ieq, :]
    be = uu[ieq, :]
    Ai = sparse([AA[ilt, :], -AA[igt, :], AA[ibx, :], -AA[ibx, :]])
    bi = matrix([uu[ilt], -ll[igt], uu[ibx], -ll[ibx]])

    # evaluate cost f(x0) and constraints g(x0), h(x0)
    x = x0
    f, df, _ = ipm_f(x)                 # cost
    f = f * opt["cost_mult"]
    df = df * opt["cost_mult"]
    gn, hn, dgn, dhn = ipm_gh(x)        # non-linear constraints
    g = matrix([gn, Ai * x - bi])       # inequality constraints
    h = matrix([hn, Ae * x - be])       # equality constraints
    dg = sparse([[dgn], [Ai.H]])        # 1st derivative of inequalities
    dh = sparse([[dhn], [Ae.H]])        # 1st derivative of equalities

    # some dimensions
    neq = h.size[0]           # number of equality constraints
    niq = g.size[0]           # number of inequality constraints
    neqnln = hn.size[0]       # number of non-linear equality constraints
    niqnln = gn.size[0]       # number of non-linear inequality constraints
    nlt = len(ilt)            # number of upper bounded linear inequalities
    ngt = len(igt)            # number of lower bounded linear inequalities
    nbx = len(ibx)            # number of doubly bounded linear inequalities

    # initialize gamma, lam, mu, z, e
    gamma = 1                  # barrier coefficient
    lam = matrix(0.0, (neq, 1))
    z = z0 * matrix(1.0, (niq, 1))
    mu = z
#    k = matrix(map(lambda x, y: x < y, g, -z0))
    k = matrix([j for j in range(len(g)) if g[j] < -z0])
    z[k] = -g[k]
    k = matrix([j for j in range(len(z)) if (gamma / z[j]) > z0])
    mu[k] = div(gamma, z[k])
    e = matrix(1.0, (niq, 1))

    # check tolerance
    f0 = f
    if opt["step_control"]:
        L = f + lam.H * h + mu.H * (g + z) - gamma * sum(log(z))

    Lx = df + dh * lam + dg * mu
    feascond = \
        max([norm(h, Inf), max(g)]) / (1 + max([norm(x, Inf), norm(z, Inf)]))
    gradcond = \
        norm(Lx, Inf) / (1 + max([norm(lam, Inf), norm(mu, Inf)]))
    compcond = (z.H * mu) / (1 + norm(x, Inf))
    costcond = abs(f - f0) / (1 + abs(f0))
    if opt["verbose"]:
        logger.info(" it    objective   step size   feascond     gradcond     "
                    "compcond     costcond  ")
        logger.info("----  ------------ --------- ------------ ------------ "
                    "------------ ------------")
        logger.info("%3d  %12.8f %10s %12.f %12.f %12.f %12.f" %
            (i, (f / opt["cost_mult"]), "", feascond, gradcond,
             compcond[0], costcond))
    if feascond < opt["feastol"] and gradcond < opt["gradtol"] and \
        compcond[0] < opt["comptol"] and costcond[0] < opt["costtol"]:
        converged = True
        if opt["verbose"]:
            logger.info("Converged!")

    # do Newton iterations
    while (not converged and i < opt["max_it"]):
        # update iteration counter
        i += 1

        # compute update step
        lmbda = {"eqnonlin": lam[range(neqnln)],
                 "ineqnonlin": mu[range(niqnln)]}
        Lxx = ipm_hess(x, lmbda)

        zinvdiag = spdiag(div(1.0, z))
        mudiag = spdiag(mu)
        dg_zinv = dg * zinvdiag
        M = Lxx + dg_zinv * mudiag * dg.H
        N = Lx + dg_zinv * (mudiag * g + gamma * e)
        Ab = sparse([[M, dh.H],
                     [dh, spmatrix([], [], [], (neq, neq))]])
        bb = matrix([-N, -h])

#        umfpack.linsolve(Ab, bb)
        lapack.gesv(matrix(Ab), bb)
        dxdlam = bb
#        xx = solve(asarray(matrix(Ab)), asarray(bb))

        print "dxdlam\n", bb

        dx = dxdlam[:nx]
        dlam = dxdlam[nx:nx + neq]
        dz = -g - z - dg.H * dx
        dmu = -mu + zinvdiag * (gamma * e - mudiag * dz)

        # optional step-size control
        sc = False
        if opt["step_control"]:
            x1 = x + dx

            # evaluate cost, constraints, derivatives at x1
            f1, df1 = ipm_f(x1)          # cost
            f1 = f1 * opt["cost_mult"]
            df1 = df1 * opt["cost_mult"]
            gn1, hn1, dgn1, dhn1 = ipm_gh(x1) # non-linear constraints
            g1 = matrix([gn1, Ai * x1 - bi])  # inequality constraints
            h1 = matrix([hn1, Ae * x1 - be])  # equality constraints
            dg1 = sparse([dgn1.T, Ai.H.T]).T  # 1st derivative of inequalities
            dh1 = sparse([dhn1.T, Ae.H.T]).T  # 1st derivative of equalities

            # check tolerance
            Lx1 = df1 + dh1 * lam + dg1 * mu
            feascond1 = max([ norm(h1, Inf), max(g1) ]) / \
                (1 + max([ norm(x1, Inf), norm(z, Inf) ]))
            gradcond1 = norm(Lx1, Inf) / \
                (1 + max([ norm(lam, Inf), norm(mu, Inf) ]))

            if feascond1 > feascond and gradcond1 > gradcond:
                sc = True
        if sc:
            alpha = 1.0
            for j in range(opt["max_red"]):
                dx1 = alpha * dx
                x1 = x + dx1
                f1 = ipm_f(x1)             # cost
                f1 = f1 * opt["cost_mult"]
                gn1, hn1 = ipm_gh(x1)              # non-linear constraints
                g1 = matrix([gn1, Ai * x1 - bi])   # inequality constraints
                h1 = matrix([hn1, Ae * x1 - be])   # equality constraints
                L1 = f1 + lam.H * h1 + mu.H * (g1 + z) - gamma * sum(log(z))
                if opt["verbose"]:
                    logger.info("\n   %3d            %10.f" % (-j, norm(dx1)))
                rho = (L1 - L) / (Lx.H * dx1 + 0.5 * dx1.H * Lxx * dx1)
                if rho > rho_min and rho < rho_max:
                    break
                else:
                    alpha = alpha / 2.0
            dx = alpha * dx
            dz = alpha * dz
            dlam = alpha * dlam
            dmu = alpha * dmu

        # do the update
        k = matrix([j for j in range(len(dz)) if dz[j] < 0.0])
        alphap = min( matrix([xi * min(div(z[k], -dz[k])), 1]) )

        k = matrix([j for j in range(len(dmu)) if dmu[j] < 0.0])
#        alphad = min( matrix([xi * min(div(mu[k], -dmu[k])), 1]) )
        alphad = min( matrix([xi * min(matrix([div(mu[k], -dmu[k]), 1])), 1]) )

        x = x + alphap * dx
        z = z + alphap * dz
        lam = lam + alphad * dlam
        mu = mu + alphad * dmu
        gamma = sigma * (z.H * mu) / niq

        # evaluate cost, constraints, derivatives
        f, df, _ = ipm_f(x)             # cost
        f = f * opt["cost_mult"]
        df = df * opt["cost_mult"]

        gn, hn, dgn, dhn = ipm_gh(x)           # non-linear constraints
        g = matrix([gn, Ai * x - bi])          # inequality constraints
        h = matrix([hn, Ae * x - be])          # equality constraints
        dg = sparse([[dgn], [Ai.H]])           # 1st derivative of inequalities
        dh = sparse([[dhn], [Ae.H]])           # 1st derivative of equalities

#        print "\n", df

        Lx = df + dh * lam + dg * mu
#        print "Lx\n", dh * lam, dg * mu, Lx

        feascond = \
            max([norm(h, Inf), max(g)]) / (1 + max([norm(x,Inf), norm(z,Inf)]))
        gradcond = \
            norm(Lx, Inf) / (1 + max([norm(lam, Inf), norm(mu, Inf)]))
        compcond = (z.H * mu) / (1 + norm(x, Inf))
        costcond = abs(f - f0) / (1 + abs(f0))
        if opt["verbose"]:
            logger.info("%3d  %12.8f %10.5f %12.f %12.f %12.f %12.f" %
                (i, (f / opt["cost_mult"]), norm(dx), feascond, gradcond,
                 compcond[0], costcond))
        if feascond < opt["feastol"] and gradcond < opt["gradtol"] and \
            compcond[0] < opt["comptol"] and costcond[0] < opt["costtol"]:
            converged = True
            if opt["verbose"]:
                logger.info("Converged!")
        else:
            if any(isnan(x)) or alphap < alpha_min or alphad < alpha_min or \
                    gamma[0] < EPS or gamma[0] > 1.0 / EPS:
                if opt["verbose"]:
                    logger.info("Numerically failed.")
                break
            f0 = f
            if opt["step_control"]:
                L = f + lam.H * h + mu.H * (g + z) - gamma * sum(log(z))

    if opt["verbose"]:
        if not converged:
            logger.info("Did not converge in %d iterations." % i)

    # zero out multipliers on non-binding constraints
    k = [j for j in range(len(mu))
         if g[j] < -opt["feastol"] and mu[j] < mu_threshold]
    mu[k] = 0.0

    # un-scale cost and prices
    f   = f / opt["cost_mult"]
    lam = lam / opt["cost_mult"]
    mu  = mu / opt["cost_mult"]

    # re-package multipliers into struct
    lam_lin = lam[neqnln:neq]              # lambda for linear constraints
    mu_lin = mu[niqnln:niq]                # mu for linear constraints
    kl = matrix([j for j, v in enumerate(lam_lin) if v < 0.0])
#    kl = nonzero(lam_lin < 0)              # lower bound binding
    ku = matrix([j for j, v in enumerate(lam_lin) if v > 0.0])
#    ku = nonzero(lam_lin > 0)              # upper bound binding

    mu_l = matrix(0.0, (nx + nA, 1))
    mu_l[ieq[kl]] = -lam_lin[kl]
    mu_l[igt] = mu_lin[nlt:nlt + ngt]
    mu_l[ibx] = mu_lin[nlt + ngt + nbx:nlt + ngt + nbx + nbx]

    mu_u = matrix(0.0, (nx + nA, 1))
    mu_u[ieq[ku]] = lam_lin[ku]
    mu_u[ilt] = mu_lin[:nlt]
    mu_u[ibx] = mu_lin[nlt + ngt:nlt + ngt + nbx]

    lmbda = {"eqnonlin": lam[:neqnln], 'ineqnonlin': mu[:niqnln],
        'mu_l': mu_l[nx:], 'mu_u': mu_u[nx:],
        'lower': mu_l[:nx], 'upper': mu_u[:nx]}

    solution =  {"x": x, "f": f, "converged": converged, "lmbda": lmbda,
                 "iterations": i, "feascond": feascond, "gradcond": gradcond,
                 "compcond": compcond, "costcond": costcond}

    return solution

#------------------------------------------------------------------------------
#  "pdipm_qp" function:
#------------------------------------------------------------------------------

def pdipm_qp(H, c, A, b, VLB=None, VUB=None, x0=None, N=0, opt=None):
#             verbose=True, cost_mult=1):
    """ Wrapper function for a primal-dual interior point QP solver.
    """
    nx = len(c)

    if H is None:
        H = spmatrix([], [], [], (nx, nx))

    if VLB is None:
        VLB = matrix(-Inf, (nx, 1))

    if VUB is None:
        VUB = matrix(Inf, (nx, 1))

    if x0 is None:
        x0 = matrix(0.0, (nx, 1))
        k = nonzero(VUB < 1e10 and VLB > -1e10)
        x0[k] ((VUB[k] + VLB[k]) / 2)
        k = nonzero(VUB < 1e10 and VLB <= -1e10)
        x0[k] = VUB[k] - 1
        k = nonzero(VUB >= 1e10 and VLB > -1e10)
        x0[k] = VLB[k] + 1

    opt = {} if opt is None else opt
    if not opt.has_key("cost_mult"):
        opt["cost_mult"] = 1

    def qp_f(x):
        f = 0.5 * x.H * H * x + c.H * x
        df = H * x + c
        return f, df, H

    def qp_gh(x):
        g = matrix(0.0, (0, 1))
        h = matrix(0.0, (0, 1))
        n, _ = x.size
        dg = spmatrix([], [], [], (n, 0))
        dh = spmatrix([], [], [], (n, 0))
        return g, h, dg, dh

    def qp_hessian(x, lmbda):
        Lxx = H * opt["cost_mult"]
        return Lxx

    l = matrix(-Inf, b.size)
    l[:N] = b[:N]

    solution = pdipm(qp_f, qp_gh, qp_hessian, x0, VLB, VUB, A, l, b, opt)

    return solution

# EOF -------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------

""" Python interior point solver [1].

    [1] Ray Zimmerman, "mips.m", MATPOWER, PSERC Cornell, version 4.0b2,
        http://www.pserc.cornell.edu/matpower/, March 2010
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from numpy import \
    array, flatnonzero, Inf, any, isnan, ones, r_, finfo, zeros, dot, \
    absolute

from numpy.linalg import norm

from scipy.sparse import csr_matrix, vstack, hstack, eye
from scipy.sparse.linalg import spsolve

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

EPS = finfo(float).eps

#------------------------------------------------------------------------------
#  "pips" function:
#------------------------------------------------------------------------------

def pips(f_fcn, x0, A=None, l=None, u=None, xmin=None, xmax=None,
         gh_fcn=None, hess_fcn=None, opt=None):
    """ x, f, exitflag, output, lmbda = \
            pips(f_fcn, x0, A, l, u, xmin, xmax, gh_fcn, hess_fcn, opt)

            min f(x)
             x

        subject to

            h(x) = 0
            g(x) <= 0
            l <= A*x <= u
            xmin <= x <= xmax
    """
    nx = x0.shape[0]                        # number of variables
    nA = A.shape[0] if A is not None else 0 # number of original linear constr

    # default argument values
#    l = array([]) if A is None else l
#    u = array([]) if A is None else u
    l = -Inf * ones(nA) if l is None else l
    u =  Inf * ones(nA) if u is None else u
    xmin = -Inf * ones(x0.shape[0]) if xmin is None else xmin
    xmax =  Inf * ones(x0.shape[0]) if xmax is None else xmax
    if gh_fcn is None:
        nonlinear = False
        gn = array([])
        hn = array([])
    else:
        nonlinear = True

    opt = {} if opt is None else opt
    # options
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

    # initialize history
    hist = {}

    # constants
    xi = 0.99995
    sigma = 0.1
    z0 = 1
    alpha_min = 1e-8
#    rho_min = 0.95
#    rho_max = 1.05
    mu_threshold = 1e-5

    # initialize
    i = 0                       # iteration counter
    converged = False           # flag
    eflag = False               # exit flag

    # add var limits to linear constraints
    eyex = eye(nx, nx, format="csr")
    AA = eyex if A is None else vstack([eyex, A], "csr")
    ll = r_[xmin, l]
    uu = r_[xmax, u]

    # split up linear constraints
    ieq = flatnonzero( absolute(uu - ll) <= EPS )
    igt = flatnonzero( (uu >=  1e10) & (ll > -1e10) )
    ilt = flatnonzero( (ll <= -1e10) & (uu <  1e10) )
    ibx = flatnonzero( (absolute(uu - ll) > EPS) & (uu < 1e10) & (ll > -1e10) )
    # zero-sized sparse matrices unsupported
    Ae = AA[ieq, :] if len(ieq) else None
    if len(ilt) or len(igt) or len(ibx):
        idxs = [(1, ilt), (-1, igt), (1, ibx), (-1, ibx)]
        Ai = vstack([sig * AA[idx, :] for sig, idx in idxs if len(idx)])
    else:
        Ai = None
    be = uu[ieq, :]
    bi = r_[uu[ilt], -ll[igt], uu[ibx], -ll[ibx]]

    # evaluate cost f(x0) and constraints g(x0), h(x0)
    x = x0
    f, df, _ = f_fcn(x)                 # cost
    f = f * opt["cost_mult"]
    df = df * opt["cost_mult"]
    if nonlinear:
        hn, gn, dhn, dgn = gh_fcn(x)        # non-linear constraints
        h = hn if Ai is None else r_[hn, Ai * x - bi] # inequality constraints
        g = gn if Ae is None else r_[gn, Ae * x - be] # equality constraints

        if (dhn is None) and (Ai is None):
            dh = None
        elif dhn is None:
            dh = Ai.T
        elif Ae is None:
            dh = dhn
        else:
            dh = hstack([dhn, Ai.T])

        if (dgn is None) and (Ae is None):
            dg = None
        elif dgn is None:
            dg = Ae.T
        elif Ae is None:
            dg = dgn
        else:
            dg = hstack([dgn, Ae.T])
    else:
        h = -bi if Ai is None else Ai * x - bi        # inequality constraints
        g = -be if Ae is None else Ae * x - be        # equality constraints
        dh = None if Ai is None else Ai.T     # 1st derivative of inequalities
        dg = None if Ae is None else Ae.T     # 1st derivative of equalities

    # some dimensions
    neq = g.shape[0]           # number of equality constraints
    niq = h.shape[0]           # number of inequality constraints
    neqnln = gn.shape[0]       # number of non-linear equality constraints
    niqnln = hn.shape[0]       # number of non-linear inequality constraints
    nlt = len(ilt)             # number of upper bounded linear inequalities
    ngt = len(igt)             # number of lower bounded linear inequalities
    nbx = len(ibx)             # number of doubly bounded linear inequalities

    # initialize gamma, lam, mu, z, e
    gamma = 1                  # barrier coefficient
    lam = zeros(neq)
    z = z0 * ones(niq)
    mu = z0 * ones(niq)
    k = flatnonzero(h < -z0)
    z[k] = -h[k]
    k = flatnonzero((gamma / z) > z0)
    mu[k] = gamma / z[k]
    e = ones(niq)

    # check tolerance
    f0 = f
#    if opt["step_control"]:
#        L = f + lam.T * g + mu.T * (h + z) - gamma * sum(log(z))

    Lx = df
    Lx = Lx + dg * lam if dg is not None else Lx
    Lx = Lx + dh * mu  if dh is not None else Lx

    gnorm = norm(g, Inf) if len(g) else 0.0
    lam_norm = norm(lam, Inf) if len(lam) else 0.0
    mu_norm = norm(mu, Inf) if len(mu) else 0.0
    feascond = \
        max([gnorm, max(h)]) / (1 + max([norm(x, Inf), norm(z, Inf)]))
    gradcond = \
        norm(Lx, Inf) / (1 + max([lam_norm, mu_norm]))
    compcond = dot(z, mu) / (1 + norm(x, Inf))
    costcond = absolute(f - f0) / (1 + absolute(f0))

    # save history
    hist[i] = {'feascond': feascond, 'gradcond': gradcond,
        'compcond': compcond, 'costcond': costcond, 'gamma': gamma,
        'stepsize': 0, 'obj': f / opt["cost_mult"], 'alphap': 0, 'alphad': 0}

    if opt["verbose"]:
#        s = '-sc' if opt["step_control"] else ''
#        version, date = '1.0b2', '24-Mar-2010'
#        print 'Python Interior Point Solver - PIPS%s, Version %s, %s' % \
#                    (s, version, date)
        print " it    objective   step size   feascond     gradcond     " \
              "compcond     costcond  "
        print "----  ------------ --------- ------------ ------------ " \
              "------------ ------------"
        print "%3d  %12.8g %10s %12g %12g %12g %12g" % \
            (i, (f / opt["cost_mult"]), "",
             feascond, gradcond, compcond, costcond)

    if feascond < opt["feastol"] and gradcond < opt["gradtol"] and \
        compcond < opt["comptol"] and costcond < opt["costtol"]:
        converged = True
        if opt["verbose"]:
            print "Converged!"

    # do Newton iterations
    while (not converged and i < opt["max_it"]):
        # update iteration counter
        i += 1

        # compute update step
        lmbda = {"eqnonlin": lam[range(neqnln)],
                 "ineqnonlin": mu[range(niqnln)]}
        if nonlinear:
            if hess_fcn is None:
                print "pips: Hessian evaluation via finite differences " \
                      "not yet implemented.\nPlease provide " \
                      "your own hessian evaluation function."
            Lxx = hess_fcn(x, lmbda)
        else:
            _, _, d2f = f_fcn(x)      # cost
            Lxx = d2f * opt["cost_mult"]
        rz = range(len(z))
        zinvdiag = csr_matrix((1.0 / z, (rz, rz))) if len(z) else None
        rmu = range(len(mu))
        mudiag = csr_matrix((mu, (rmu, rmu))) if len(mu) else None
        dh_zinv = None if dh is None else dh * zinvdiag
        M = Lxx if dh is None else Lxx + dh_zinv * mudiag * dh.T
        N = Lx if dh is None else Lx + dh_zinv * (mudiag * h + gamma * e)

        Ab = M if dg is None else vstack([
            hstack([M, dg]),
            hstack([dg.T, csr_matrix((neq, neq))])
        ])
        bb = r_[-N, -g]

        dxdlam = spsolve(Ab.tocsr(), bb)

        dx = dxdlam[:nx]
        dlam = dxdlam[nx:nx + neq]
        dz = -h - z if dh is None else -h - z - dh.T * dx
        dmu = -mu if dh is None else -mu + zinvdiag * (gamma * e - mudiag * dz)

        # optional step-size control
#        sc = False
        if opt["step_control"]:
            raise NotImplementedError
#            x1 = x + dx
#
#            # evaluate cost, constraints, derivatives at x1
#            f1, df1 = ipm_f(x1)          # cost
#            f1 = f1 * opt["cost_mult"]
#            df1 = df1 * opt["cost_mult"]
#            gn1, hn1, dgn1, dhn1 = ipm_gh(x1) # non-linear constraints
#            g1 = gn1 if Ai is None else r_[gn1, Ai * x1 - bi] # ieq constraints
#            h1 = hn1 if Ae is None else r_[hn1, Ae * x1 - be] # eq constraints
#            dg1 = dgn1 if Ai is None else r_[dgn1, Ai.T]      # 1st der of ieq
#            dh1 = dhn1 if Ae is None else r_[dhn1, Ae.T]      # 1st der of eqs
#
#            # check tolerance
#            Lx1 = df1 + dh1 * lam + dg1 * mu
#            feascond1 = max([ norm(h1, Inf), max(g1) ]) / \
#                (1 + max([ norm(x1, Inf), norm(z, Inf) ]))
#            gradcond1 = norm(Lx1, Inf) / \
#                (1 + max([ norm(lam, Inf), norm(mu, Inf) ]))
#
#            if feascond1 > feascond and gradcond1 > gradcond:
#                sc = True
#        if sc:
#            alpha = 1.0
#            for j in range(opt["max_red"]):
#                dx1 = alpha * dx
#                x1 = x + dx1
#                f1 = ipm_f(x1)             # cost
#                f1 = f1 * opt["cost_mult"]
#                gn1, hn1 = ipm_gh(x1)              # non-linear constraints
#                g1 = r_[gn1, Ai * x1 - bi]         # inequality constraints
#                h1 = r_[hn1, Ae * x1 - be]         # equality constraints
#                L1 = f1 + lam.H * h1 + mu.H * (g1 + z) - gamma * sum(log(z))
#                if opt["verbose"]:
#                    logger.info("\n   %3d            %10.f" % (-j, norm(dx1)))
#                rho = (L1 - L) / (Lx.H * dx1 + 0.5 * dx1.H * Lxx * dx1)
#                if rho > rho_min and rho < rho_max:
#                    break
#                else:
#                    alpha = alpha / 2.0
#            dx = alpha * dx
#            dz = alpha * dz
#            dlam = alpha * dlam
#            dmu = alpha * dmu

        # do the update
        k = flatnonzero(dz < 0.0)
        alphap = min([xi * min(z[k] / -dz[k]), 1]) if len(k) else 1.0
        k = flatnonzero(dmu < 0.0)
        alphad = min([xi * min(mu[k] / -dmu[k]), 1]) if len(k) else 1.0
        x = x + alphap * dx
        z = z + alphap * dz
        lam = lam + alphad * dlam
        mu = mu + alphad * dmu
        if niq > 0:
            gamma = sigma * dot(z, mu) / niq

        # evaluate cost, constraints, derivatives
        f, df, _ = f_fcn(x)             # cost
        f = f * opt["cost_mult"]
        df = df * opt["cost_mult"]
        if nonlinear:
            hn, gn, dhn, dgn = gh_fcn(x)                   # nln constraints
#            g = gn if Ai is None else r_[gn, Ai * x - bi] # ieq constraints
#            h = hn if Ae is None else r_[hn, Ae * x - be] # eq constraints
            h = hn if Ai is None else r_[hn, Ai * x - bi] # ieq constr
            g = gn if Ae is None else r_[gn, Ae * x - be]  # eq constr

            if (dhn is None) and (Ai is None):
                dh = None
            elif dhn is None:
                dh = Ai.T
            elif Ae is None:
                dh = dhn
            else:
                dh = hstack([dhn, Ai.T])

            if (dgn is None) and (Ae is None):
                dg = None
            elif dgn is None:
                dg = Ae.T
            elif Ae is None:
                dg = dgn
            else:
                dg = hstack([dgn, Ae.T])
        else:
            h = -bi if Ai is None else Ai * x - bi    # inequality constraints
            g = -be if Ae is None else Ae * x - be    # equality constraints
            # 1st derivatives are constant, still dh = Ai.T, dg = Ae.T

        Lx = df
        Lx = Lx + dg * lam if dg is not None else Lx
        Lx = Lx + dh * mu  if dh is not None else Lx

        gnorm = norm(g, Inf) if len(g) else 0.0
        lam_norm = norm(lam, Inf) if len(lam) else 0.0
        mu_norm = norm(mu, Inf) if len(mu) else 0.0
        feascond = \
            max([gnorm, max(h)]) / (1+max([norm(x, Inf), norm(z, Inf)]))
        gradcond = \
            norm(Lx, Inf) / (1 + max([lam_norm, mu_norm]))
        compcond = dot(z, mu) / (1 + norm(x, Inf))
        costcond = float(absolute(f - f0) / (1 + absolute(f0)))

        hist[i] = {'feascond': feascond, 'gradcond': gradcond,
            'compcond': compcond, 'costcond': costcond, 'gamma': gamma,
            'stepsize': norm(dx), 'obj': f / opt["cost_mult"],
            'alphap': alphap, 'alphad': alphad}

        if opt["verbose"]:
            print "%3d  %12.8g %10.5g %12g %12g %12g %12g" % \
                (i, (f / opt["cost_mult"]), norm(dx), feascond, gradcond,
                 compcond, costcond)

        if feascond < opt["feastol"] and gradcond < opt["gradtol"] and \
            compcond < opt["comptol"] and costcond < opt["costtol"]:
            converged = True
            if opt["verbose"]:
                print "Converged!"
        else:
            if any(isnan(x)) or (alphap < alpha_min) or \
                (alphad < alpha_min) or (gamma < EPS) or (gamma > 1.0 / EPS):
                if opt["verbose"]:
                    print "Numerically failed."
                eflag = -1
                break
            f0 = f

#            if opt["step_control"]:
#                L = f + dot(lam, g) + dot(mu * (h + z)) - gamma * sum(log(z))

    if opt["verbose"]:
        if not converged:
            print "Did not converge in %d iterations." % i

    # package results
    if eflag != -1:
        eflag = converged

    if eflag == 0:
        message = 'Did not converge'
    elif eflag == 1:
        message = 'Converged'
    elif eflag == -1:
        message = 'Numerically failed'
    else:
        raise

    output = {"iterations": i, "history": hist, "message": message}

    # zero out multipliers on non-binding constraints
    mu[flatnonzero( (h < -opt["feastol"]) & (mu < mu_threshold) )] = 0.0

    # un-scale cost and prices
    f = f / opt["cost_mult"]
    lam = lam / opt["cost_mult"]
    mu = mu / opt["cost_mult"]

    # re-package multipliers into struct
    lam_lin = lam[neqnln:neq]           # lambda for linear constraints
    mu_lin = mu[niqnln:niq]             # mu for linear constraints
    kl = flatnonzero(lam_lin < 0.0)     # lower bound binding
    ku = flatnonzero(lam_lin > 0.0)     # upper bound binding

    mu_l = zeros(nx + nA)
    mu_l[ieq[kl]] = -lam_lin[kl]
    mu_l[igt] = mu_lin[nlt:nlt + ngt]
    mu_l[ibx] = mu_lin[nlt + ngt + nbx:nlt + ngt + nbx + nbx]

    mu_u = zeros(nx + nA)
    mu_u[ieq[ku]] = lam_lin[ku]
    mu_u[ilt] = mu_lin[:nlt]
    mu_u[ibx] = mu_lin[nlt + ngt:nlt + ngt + nbx]

    lmbda = {'mu_l': mu_l[nx:], 'mu_u': mu_u[nx:],
             'lower': mu_l[:nx], 'upper': mu_u[:nx]}

    if niqnln > 0:
        lmbda['ineqnonlin'] = mu[:niqnln]
    if neqnln > 0:
        lmbda['eqnonlin'] = lam[:neqnln]

#    lmbda = {"eqnonlin": lam[:neqnln], 'ineqnonlin': mu[:niqnln],
#             "mu_l": mu_l[nx:], "mu_u": mu_u[nx:],
#             "lower": mu_l[:nx], "upper": mu_u[:nx]}

    solution =  {"x": x, "f": f, "converged": converged,
                 "lmbda": lmbda, "output": output}

    return solution

#------------------------------------------------------------------------------
#  "qps_pips" function:
#------------------------------------------------------------------------------

def qps_pips(H, c, A, l, u, xmin=None, xmax=None, x0=None, opt=None):
    """ Quadratic Program Solver based on PIPS.
    """
    if H is None or H.nnz == 0:
        if A is None or A.nnz == 0 and \
           xmin is None or len(xmin) == 0 and \
           xmax is None or len(xmax) == 0:
            print 'qps_pips: LP problem must include constraints or variable bounds'
            return
        else:
            if A is not None and A.nnz >= 0:
                nx = A.shape[1]
            elif xmin is not None and len(xmin) > 0:
                nx = xmin.shape[0]
            elif xmax is not None and len(xmax) > 0:
                nx = xmax.shape[0]
        H = csr_matrix((nx, nx))
    else:
        nx = H.shape[0]

    xmin = -Inf * ones(nx) if xmin is None else xmin
    xmax =  Inf * ones(nx) if xmax is None else xmax

    c = zeros(nx) if c is None else c

#    if x0 is None:
#        x0 = zeros(nx)
#        k = flatnonzero( (VUB < 1e10) & (VLB > -1e10) )
#        x0[k] = ((VUB[k] + VLB[k]) / 2)
#        k = flatnonzero( (VUB < 1e10) & (VLB <= -1e10) )
#        x0[k] = VUB[k] - 1
#        k = flatnonzero( (VUB >= 1e10) & (VLB > -1e10) )
#        x0[k] = VLB[k] + 1

    x0 = zeros(nx) if x0 is None else x0

    opt = {} if opt is None else opt
    if not opt.has_key("cost_mult"):
        opt["cost_mult"] = 1

    def qp_f(x):
        f = 0.5 * dot(x.T * H, x) + dot(c.T, x)
        df = H * x + c
        d2f = H
        return f, df, d2f

#    def qp_gh(x):
#        g = array([])
#        h = array([])
#        dg = None
#        dh = None
#        return g, h, dg, dh
#
#    def qp_hessian(x, lmbda):
#        Lxx = H * opt["cost_mult"]
#        return Lxx

#    l = -Inf * ones(b.shape[0])
#    l[:N] = b[:N]

    return pips(qp_f, x0, A, l, u, xmin, xmax, opt=opt)

# EOF -------------------------------------------------------------------------

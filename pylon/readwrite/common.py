#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
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

bus_attrs = ["name", "mode", "slack", "v_base", "v_magnitude_guess",
    "v_angle_guess", "v_max", "v_min", "v_magnitude", "v_angle", "g_shunt",
    "b_shunt", "zone"]

branch_attrs = ["name", "mode", "online", "r", "x", "b", "s_max",
    "phase_shift", "phase_shift_max", "phase_shift_min", "online"]

generator_attrs = ["name", "base_mva", "v_magnitude", "p", "p_max", "p_min",
    "q", "q_max", "q_min", "c_startup", "c_shutdown", "cost_model",
    "cost_coeffs", "pwl_points", "p_cost", "u", "rate_up", "rate_down",
    "min_up", "min_down", "initial_up", "initial_down", "online"]

load_attrs = ["name", "p", "q", "online"]

# EOF -------------------------------------------------------------------------

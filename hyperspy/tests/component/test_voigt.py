# -*- coding: utf-8 -*-
# Copyright 2007-2016 The HyperSpy developers
#
# This file is part of  HyperSpy.
#
#  HyperSpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
#  HyperSpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.from hyperspy.utils import stack

#
# You should have received a copy of the GNU General Public License
# along with  HyperSpy.  If not, see <http://www.gnu.org/licenses/>.

import itertools
import numpy as np
from numpy.testing import assert_allclose
import pytest

from hyperspy.signals import Signal1D
from hyperspy.components1d import Voigt
from hyperspy.components1d import PESVoigt
from hyperspy.utils import stack

TRUE_FALSE_2_TUPLE = [p for p in itertools.product((True, False), repeat=2)]

class TestVoigt:
        
    def test_function():
        g = Voigt(legacy=False)
        g.area.value = 5
        g.gwidth.value=0.5
        g.lwidth.value=0.2
        g.centre.value=1
        assert_allclose(g.function(0), 0.35380168)
        assert_allclose(g.function(1), 5.06863535)

    @pytest.mark.parametrize(("lazy"), (True, False))
    @pytest.mark.parametrize(("only_current", "binned"), TRUE_FALSE_2_TUPLE)
    def test_estimate_parameters_binned(only_current, binned, lazy):
        s = Signal1D(np.empty((200,)))
        s.metadata.Signal.binned = binned
        axis = s.axes_manager.signal_axes[0]
        axis.scale = .05
        axis.offset = -5
        g1 = Voigt(centre=1,area=5,lwidth=0.001,gwidth=0.5,legacy=False)
        s.data = g1.function(axis.axis)
        if lazy:
            s = s.as_lazy()
        g2 = Voigt(legacy=False)
        factor = axis.scale if binned else 1
        assert g2.estimate_parameters(s, None, None, only_current=only_current)
        assert g2.binned == binned
        assert_allclose(g2.gwidth.value, 0.5, 0.04)
        assert_allclose(g1.area.value, g2.area.value * factor, 0.04)
        assert_allclose(g2.centre.value, 1, 1e-3)

    @pytest.mark.parametrize(("lazy"), (True, False))
    @pytest.mark.parametrize(("binned"), (True, False))
    def test_function_nd(binned, lazy):
        s = Signal1D(np.empty((200,)))
        s.metadata.Signal.binned = binned
        axis = s.axes_manager.signal_axes[0]
        axis.scale = .05
        axis.offset = -5
        g1 = Voigt(centre=1,area=5,lwidth=0,gwidth=0.5,legacy=False)
        s.data = g1.function(axis.axis)
        s2 = stack([s] * 2)
        if lazy:
            s2 = s2.as_lazy()
        g2 = Voigt(legacy=False)
        factor = axis.scale if binned else 1
        g2.estimate_parameters(s2, axis.low_value, axis.high_value, False)
        assert g2.binned == binned
        assert_allclose(g2.function_nd(axis.axis) * factor, s2.data)

    def test_util_gamma_set():
        g1 = Voigt(legacy=False)
        g1.gamma = 3.0
        assert_allclose(g1.lwidth.value, g1.gamma)

    def test_util_gamma_get():
        g1 = Voigt(legacy=False)
        g1.lwidth.value = 3.0
        assert_allclose(g1.lwidth.value, g1.gamma)

    def test_util_gamma_getset():
        g1 = Voigt(legacy=False)
        g1.gamma = 3.0
        assert_allclose(g1.gamma, 3.0)

    def test_util_sigma_set():
        g1 = Voigt(legacy=False)
        g1.sigma = 1.0
        assert_allclose(g1.gwidth.value, 1.0 * (2 * np.sqrt(2 * np.log(2))))
    
    def test_util_sigma_get():
        g1 = Voigt(legacy=False)
        g1.gwidth.value = 1.0
        assert_allclose(g1.sigma, 1.0 / (2 * np.sqrt(2 * np.log(2))))
    
    def test_util_sigma_getset():
        g1 = Voigt(legacy=False)
        g1.sigma = 1.0
        assert_allclose(g1.sigma, 1.0)


class TestPESVoigt:

    def test_function():
        g = PESVoigt()
        g.area.value = 5
        g.FWHM.value=0.5
        g.gamma.value=0.2
        g.centre.value=1
        assert_allclose(g.function(0), 0.35380168)
        assert_allclose(g.function(1), 5.06863535)

    @pytest.mark.parametrize(("lazy"), (True, False))
    @pytest.mark.parametrize(("only_current", "binned"), TRUE_FALSE_2_TUPLE)
    def test_estimate_parameters_binned(only_current, binned, lazy):
        s = Signal1D(np.empty((200,)))
        s.metadata.Signal.binned = binned
        axis = s.axes_manager.signal_axes[0]
        axis.scale = .05
        axis.offset = -5
        g1 = PESVoigt()
        g1.centre.value=1
        g1.area.value=5.
        g1.gamma.value=0.001
        g1.FWHM.value=0.5
        s.data = g1.function(axis.axis)
        if lazy:
            s = s.as_lazy()
        g2 = PESVoigt()
        factor = axis.scale if binned else 1
        assert g2.estimate_parameters(s, None, None, only_current=only_current)
        assert g2.binned == binned
        assert_allclose(g2.FWHM.value, 1, 0.5)
        assert_allclose(g1.area.value, g2.area.value * factor, 0.04)
        assert_allclose(g2.centre.value, 1, 1e-3)

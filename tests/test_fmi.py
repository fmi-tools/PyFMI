#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2019 Modelon AB
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import nose
import os
import numpy as np

from pyfmi import testattr
from pyfmi.fmi import FMUModel, FMUException, FMUModelME1, FMUModelCS1, load_fmu, FMUModelCS2, FMUModelME2, PyEventInfo
import pyfmi.fmi_util as fmi_util
import pyfmi.fmi as fmi
import pyfmi.fmi_algorithm_drivers as fmi_algorithm_drivers

file_path = os.path.dirname(os.path.abspath(__file__))

class Test_FMUModelME1:
    
    @testattr(stddist = True)
    def test_get_variable_by_valueref(self):
        bounce = FMUModelME1("bouncingBall.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME1.0"), _connect_dll=False)
        assert "der(v)" == bounce.get_variable_by_valueref(3)
        assert "v" == bounce.get_variable_by_valueref(2)

        nose.tools.assert_raises(FMUException, bounce.get_variable_by_valueref,7)
    
    @testattr(windows_full = True)
    def test_default_experiment(self):
        model = FMUModelME1("CoupledClutches.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME1.0"), _connect_dll=False)
        
        assert np.abs(model.get_default_experiment_start_time()) < 1e-4
        assert np.abs(model.get_default_experiment_stop_time()-1.5) < 1e-4
        assert np.abs(model.get_default_experiment_tolerance()-0.0001) < 1e-4

    
    @testattr(stddist = True)
    def test_log_file_name(self):
        model = FMUModelME1("bouncingBall.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME1.0"), _connect_dll=False)
        assert os.path.exists("bouncingBall_log.txt")
        model = FMUModelME1("bouncingBall.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME1.0"), _connect_dll=False, log_file_name="Test_log.txt")
        assert os.path.exists("Test_log.txt")

    @testattr(stddist = True)
    def test_ode_get_sizes(self):
        bounce = FMUModelME1("bouncingBall.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME1.0"), _connect_dll=False)
        dq = FMUModelME1("dq.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME1.0"), _connect_dll=False)
        
        [nCont,nEvent] = bounce.get_ode_sizes()
        assert nCont == 2
        assert nEvent == 1

        [nCont,nEvent] = dq.get_ode_sizes()
        assert nCont == 1
        assert nEvent == 0
    
    @testattr(stddist = True)
    def test_get_name(self):
        bounce = FMUModelME1("bouncingBall.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME1.0"), _connect_dll=False)
        dq = FMUModelME1("dq.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME1.0"), _connect_dll=False)
        
        assert bounce.get_name() == 'bouncingBall'
        assert dq.get_name() == 'dq'
    
    @testattr(stddist = True)
    def test_instantiate_jmu(self):
        """
        Test that FMUModel can not be instantiated with a JMU file.
        """
        nose.tools.assert_raises(FMUException,FMUModelME1,'model.jmu')
    
    @testattr(stddist = True)
    def test_get_fmi_options(self):
        """
        Test that simulate_options on an FMU returns the correct options
        class instance.
        """
        bounce = FMUModelME1("bouncingBall.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME1.0"), _connect_dll=False)
        assert isinstance(bounce.simulate_options(), fmi_algorithm_drivers.AssimuloFMIAlgOptions)

class Test_FMUModelCS1:
    
    @testattr(stddist = True)
    def test_default_experiment(self):
        model = FMUModelCS1("CoupledClutches.fmu", os.path.join(file_path, "files", "FMUs", "XML", "CS1.0"), _connect_dll=False)
        
        assert np.abs(model.get_default_experiment_start_time()) < 1e-4
        assert np.abs(model.get_default_experiment_stop_time()-1.5) < 1e-4
        assert np.abs(model.get_default_experiment_tolerance()-0.0001) < 1e-4

    @testattr(stddist = True)
    def test_log_file_name(self):
        model = FMUModelCS1("bouncingBall.fmu", os.path.join(file_path, "files", "FMUs", "XML", "CS1.0"), _connect_dll=False)
        assert os.path.exists("bouncingBall_log.txt")
        model = FMUModelCS1("bouncingBall.fmu", os.path.join(file_path, "files", "FMUs", "XML", "CS1.0"), _connect_dll=False, log_file_name="Test_log.txt")
        assert os.path.exists("Test_log.txt")

class Test_FMUModelBase:
    
    @testattr(stddist = True)
    def test_caching(self):
        negated_alias = FMUModelME1("NegatedAlias.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME1.0"), _connect_dll=False)

        assert len(negated_alias.cache) == 0 #No starting cache
        
        vars_1 = negated_alias.get_model_variables()
        vars_2 = negated_alias.get_model_variables()
        assert id(vars_1) == id(vars_2)
        
        vars_3 = negated_alias.get_model_variables(filter="*")
        assert id(vars_1) != id(vars_3)
        
        vars_4 = negated_alias.get_model_variables(type=0)
        assert id(vars_3) != id(vars_4)
        
        vars_5 = negated_alias.get_model_time_varying_value_references()
        vars_7 = negated_alias.get_model_time_varying_value_references()
        assert id(vars_5) != id(vars_1)
        assert id(vars_5) == id(vars_7)
        
        negated_alias = FMUModelME1("NegatedAlias.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME1.0"), _connect_dll=False)

        assert len(negated_alias.cache) == 0 #No starting cache
        
        vars_6 = negated_alias.get_model_variables()
        assert id(vars_1) != id(vars_6)
    
    @testattr(stddist = True)
    def test_get_scalar_variable(self):
        negated_alias = FMUModelME1("NegatedAlias.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME1.0"), _connect_dll=False)

        sc_x = negated_alias.get_scalar_variable("x")
        
        assert sc_x.name == "x"
        assert sc_x.value_reference >= 0
        assert sc_x.type == fmi.FMI_REAL
        assert sc_x.variability == fmi.FMI_CONTINUOUS
        assert sc_x.causality == fmi.FMI_INTERNAL
        assert sc_x.alias == fmi.FMI_NO_ALIAS

        nose.tools.assert_raises(FMUException, negated_alias.get_scalar_variable, "not_existing")
        

class Test_FMUModelCS2:
    @testattr(stddist = True)
    def test_log_file_name(self):
        full_path = os.path.join(file_path, "files", "FMUs", "XML", "CS2.0", "CoupledClutches.fmu")
        model = FMUModelCS2(full_path, _connect_dll=False)
        
        path, file_name = os.path.split(full_path)
        assert model.get_log_file_name() == file_name.replace(".","_")[:-4]+"_log.txt"

class Test_FMUModelME2:
    @testattr(stddist = True)
    def test_malformed_xml(self):
        nose.tools.assert_raises(FMUException, load_fmu, os.path.join(file_path, "files", "FMUs", "XML", "ME2.0", "MalFormed.fmu"))
        
    @testattr(stddist = True)
    def test_log_file_name(self):
        full_path = os.path.join(file_path, "files", "FMUs", "XML", "ME2.0", "CoupledClutches.fmu")
        
        model = FMUModelME2(full_path, _connect_dll=False)
        
        path, file_name = os.path.split(full_path)
        assert model.get_log_file_name() == file_name.replace(".","_")[:-4]+"_log.txt"
    
    @testattr(stddist = True)
    def test_units(self):
        model = FMUModelME2("CoupledClutches.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME2.0"), _connect_dll=False)
        
        assert model.get_variable_unit("J1.w") == "rad/s"
        assert model.get_variable_unit("J1.phi") == "rad"
        
        nose.tools.assert_raises(FMUException, model.get_variable_unit, "clutch1.useHeatPort")
        nose.tools.assert_raises(FMUException, model.get_variable_unit, "clutch1.sss")
        nose.tools.assert_raises(FMUException, model.get_variable_unit, "clutch1.sss")
    
    @testattr(stddist = True)
    def test_display_units(self):
        model = FMUModelME2("CoupledClutches.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME2.0"), _connect_dll=False)
        
        assert model.get_variable_display_unit("J1.phi") == "deg"
        nose.tools.assert_raises(FMUException, model.get_variable_display_unit, "J1.w")

class Test_FMUModelBase2:
    
    @testattr(stddist = True)
    def test_caching(self):
        negated_alias = FMUModelME2("NegatedAlias.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME2.0"), _connect_dll=False)

        assert len(negated_alias.cache) == 0 #No starting cache
        
        vars_1 = negated_alias.get_model_variables()
        vars_2 = negated_alias.get_model_variables()
        assert id(vars_1) == id(vars_2)
        
        vars_3 = negated_alias.get_model_variables(filter="*")
        assert id(vars_1) != id(vars_3)
        
        vars_4 = negated_alias.get_model_variables(type=0)
        assert id(vars_3) != id(vars_4)
        
        vars_5 = negated_alias.get_model_time_varying_value_references()
        vars_7 = negated_alias.get_model_time_varying_value_references()
        assert id(vars_5) != id(vars_1)
        assert id(vars_5) == id(vars_7)
        
        negated_alias = FMUModelME2("NegatedAlias.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME2.0"), _connect_dll=False)

        assert len(negated_alias.cache) == 0 #No starting cache
        
        vars_6 = negated_alias.get_model_variables()
        assert id(vars_1) != id(vars_6)
    
    @testattr(stddist = True)
    def test_get_scalar_variable(self):
        negated_alias = FMUModelME2("NegatedAlias.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME2.0"), _connect_dll=False)

        sc_x = negated_alias.get_scalar_variable("x")
        
        assert sc_x.name == "x"
        assert sc_x.value_reference >= 0
        assert sc_x.type == fmi.FMI2_REAL
        assert sc_x.variability == fmi.FMI2_CONTINUOUS
        assert sc_x.causality == fmi.FMI2_LOCAL

        nose.tools.assert_raises(FMUException, negated_alias.get_scalar_variable, "not_existing")
    

class Test_load_fmu_only_XML:
    
    @testattr(stddist = True)
    def test_loading_xml_me1(self):
        
        model = FMUModelME1("CoupledClutches.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME1.0"), _connect_dll=False)
        
        assert model.get_name() == "CoupledClutches"

    @testattr(stddist = True)
    def test_loading_xml_cs1(self):
        
        model = FMUModelCS1("CoupledClutches.fmu", os.path.join(file_path, "files", "FMUs", "XML", "CS1.0"), _connect_dll=False)
        
        assert model.get_name() == "CoupledClutches"
        
    @testattr(stddist = True)
    def test_loading_xml_me2(self):
        
        model = FMUModelME2("CoupledClutches.fmu", os.path.join(file_path, "files", "FMUs", "XML", "ME2.0"), _connect_dll=False)
        
        assert model.get_name() == "CoupledClutches"
        
    @testattr(stddist = True)
    def test_loading_xml_cs2(self):
        
        model = FMUModelCS2("CoupledClutches.fmu", os.path.join(file_path, "files", "FMUs", "XML", "CS2.0"), _connect_dll=False)
        
        assert model.get_name() == "CoupledClutches"

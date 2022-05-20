"""
Tests for the analysis_var_cont.py script

:author: Tessa Johnson
:email: tessa<dot>johnson<at>geomdata<dot>com
:created: 2019 12 13
:copyright: (c) 2019, GDA
:license: All Rights Reserved, see LICENSE for more details
"""

# from diagnose.analysis_var_cont import *
# import numpy as np
import pytest


class TestAnalyzeCont(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        """
        setup for analysis of continuous data tests
        """
        self.data = 0

    def teardown(self):
        """
        teardown step
        """
        del self.data

    # ------------------------------------------------------------------------------------------------------------------
    # Testing analyze_by_var function
    # ------------------------------------------------------------------------------------------------------------------
    @pytest.mark.xfail(run=False, reason="Not Implemented")
    def test_analyze_by_var(self):
        """
        ToDo: Testing the analyze_by_var function
        """
        assert NotImplementedError

    # ------------------------------------------------------------------------------------------------------------------
    # Testing save_df_stats_var function
    # ------------------------------------------------------------------------------------------------------------------
    @pytest.mark.xfail(run=False, reason="Not Implemented")
    def test_save_df_stats_var(self):
        """
        ToDo: Testing the save_df_stats_var function
        """
        assert NotImplementedError

    # ------------------------------------------------------------------------------------------------------------------
    # Testing save_df_depend function
    # ------------------------------------------------------------------------------------------------------------------
    @pytest.mark.xfail(run=False, reason="Not Implemented")
    def save_df_depend(self):
        """
        ToDo: Testing the save_df_depend
        """
        assert NotImplementedError

    # ------------------------------------------------------------------------------------------------------------------
    # Testing run function
    # ------------------------------------------------------------------------------------------------------------------
    @pytest.mark.xfail(run=False, reason="Not Implemented")
    def test_run(self):
        """
        ToDo: Testing the run
        """
        assert NotImplementedError

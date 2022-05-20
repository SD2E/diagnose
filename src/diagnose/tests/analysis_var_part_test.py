"""
Tests for the analysis_var_part.py script

:author: Anastasia Deckard, Tessa Johnson
:email: anastasia<dot>deckard<at>geomdata<dot>com, tessa<dot>johnson<at>geomdata<dot>com
:copyright: (c) 2019, GDA
:license: All Rights Reserved, see LICENSE for more details
"""

# from diagnose.analysis_var_part import *
# import numpy as np
import pytest


class TestAnalyzePart(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        """
        setup for analysis_var_part tests
        """
        self.data = 0

    def teardown(self):
        """
        teardown
        """
        del self.data

    # ------------------------------------------------------------------------------------------------------------------
    # Testing analyze_by_part function
    # ------------------------------------------------------------------------------------------------------------------
    @pytest.mark.xfail(run=False, reason="Not Implemented")
    def test_analyze_by_part(self):
        """
        ToDo: Testing the analyze_by_part function
        """
        assert NotImplementedError

    # ------------------------------------------------------------------------------------------------------------------
    # Testing summarize_results function
    # ------------------------------------------------------------------------------------------------------------------
    @pytest.mark.xfail(run=False, reason="Not Implemented")
    def test_summarize_results(self):
        """
        ToDo: Testing the summarize_results function
        """
        assert NotImplementedError

    # ------------------------------------------------------------------------------------------------------------------
    # Testing combine_cat_vars function
    # ------------------------------------------------------------------------------------------------------------------
    @pytest.mark.xfail(run=False, reason="Not Implemented")
    def test_combine_cat_vars(self):
        """
        ToDo: Testing the combine_cat_vars function
        """
        assert NotImplementedError

    # ------------------------------------------------------------------------------------------------------------------
    # Testing combine_cat_vars_nonp function
    # ------------------------------------------------------------------------------------------------------------------
    @pytest.mark.xfail(run=False, reason="Not Implemented")
    def test_combine_cat_vars_nonp(self):
        """
        ToDo: Testing the combine_cat_vars_nonp function
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
    # Testing save_df_stats_val function
    # ------------------------------------------------------------------------------------------------------------------
    @pytest.mark.xfail(run=False, reason="Not Implemented")
    def test_save_df_stats_val(self):
        """
        ToDo: Testing the save_df_stats_val function
        """
        assert NotImplementedError

    # ------------------------------------------------------------------------------------------------------------------
    # Testing save_df_stats_val_worry function
    # ------------------------------------------------------------------------------------------------------------------
    @pytest.mark.xfail(run=False, reason="Not Implemented")
    def test_save_df_stats_val_worry(self):
        """
        ToDo: Testing the save_df_stats_val_worry function
        """
        assert NotImplementedError

    # ------------------------------------------------------------------------------------------------------------------
    # Testing plot_result_distibution function
    # ------------------------------------------------------------------------------------------------------------------
    @pytest.mark.xfail(run=False, reason="Not Implemented")
    def test_plot_result_distibution(self):
        """
        ToDo: Testing the plot_result_distibution function
        """
        assert NotImplementedError

    # ------------------------------------------------------------------------------------------------------------------
    # Testing run function
    # ------------------------------------------------------------------------------------------------------------------
    @pytest.mark.xfail(run=False, reason="Not Implemented")
    def test_run(self):
        """
        ToDo: Testing the run function
        """
        assert NotImplementedError

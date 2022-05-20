"""
Tests for the analysis_var_cat.py script

:author: Tessa Johnson
:email: tessa<dot>johnson<at>geomdata<dot>com
:created: 2019 12 13
:copyright: (c) 2019, GDA
:license: All Rights Reserved, see LICENSE for more details
"""

from diagnose.analysis_var_cat import *
import numpy as np
import pandas as pd
import pytest


class TestAnalyzeCat(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        """
        setup for categorical analysis code tests
        """
        np.random.seed(27705)

        self.cv = ['a', 'b', 'c']
        self.data = pd.DataFrame(
            {"group": ['test0'] * 50 + ['test1'] * 50, 'a': ['apple'] * 25 + ['dog'] * 25 + ['apple'] * 25 +
                                                            ['dog'] * 25, 'b': ['t', 's'] * 50,
             'c': ['rory', 'dog'] * 25 + ['rory'] * 50,
             "score": np.r_[np.linspace(0, 1), np.linspace(0, 1)]})

    # ------------------------------------------------------------------------------------------------------------------
    # Testing analyze_by_var function
    # ------------------------------------------------------------------------------------------------------------------
    def test_analyze_by_var(self):
        """
        Using a fake data set where one variable 'a' has a clear relationship with score (i.e. 'apple' always has
        a score less than 0.5, and 'dog' always has one greater than 0.5), and another variable 'b' is unrelated to
        score (i.e. 's' and 't' are just repeated and have no relationship with score) - we test that reasonable
        p-values are returns. Also we check that the data is being appropriately subset according to group and we only
        gather statistics on variables that have more than 2 categories using variable 'c' (i.e. 'a', 'b', 'c' should
        appear with statistics for test0 and 'a' and 'b' should appear with statistics for test1)

        """
        results_df = analyze_by_var('group', 'score', self.cv, self.data)

        assert (results_df.variable.values == ['a', 'b', 'c', 'a', 'b']).all()
        assert results_df[results_df.variable == 'a'].var_kw_pval_corrected.values[0] < 0.05
        assert results_df[results_df.variable == 'b'].var_kw_pval_corrected.values[0] > 0.05

    # ------------------------------------------------------------------------------------------------------------------
    # Testing summarize_results function
    # ------------------------------------------------------------------------------------------------------------------
    def test_summarize_results(self):
        """
        Testing the summarize_results functions to check there are the correct variables being summarized and the
        output is the correct shape
        """
        results_df = analyze_by_var('group', 'score', self.cv, self.data)

        summarize_df, subset_df = summarize_results(self.data, results_df, "group", "score", self.cv)

        variables = []
        for v in self.cv:
            variables.extend(np.unique(self.data[v].values).tolist())

        variables = np.unique(variables)

        assert (np.unique(summarize_df.value.values) == variables).all()

    # ------------------------------------------------------------------------------------------------------------------
    # Testing plot_result_heatmap_stat function
    # ------------------------------------------------------------------------------------------------------------------
    def test_plot_result_heatmap_stat(self):
        """
        Testing to see if the plot_result_heatmap_stat function runs
        """

        results_df = analyze_by_var('group', 'score', self.cv, self.data)

        try:
            plot_result_heatmap_stat(results_df, 'group', './pytest_data')
            assert True

        except:
            assert False

    # ------------------------------------------------------------------------------------------------------------------
    # Testing plot_result_heatmap_pval function
    # ------------------------------------------------------------------------------------------------------------------
    def test_plot_result_heatmap_pval(self):
        """
        Testing to see if the plot_result_heatmap_pval function runs
        """
        results_df = analyze_by_var('group', 'score', self.cv, self.data)

        try:
            plot_result_heatmap_pval(results_df, 'group', './pytest_data')
            assert True

        except:
            assert False

    # ------------------------------------------------------------------------------------------------------------------
    # Testing plot_result_distibution function
    # ------------------------------------------------------------------------------------------------------------------
    def test_plot_result_distibution(self):
        """
        ToDo: Testing the plot_result_distibution function
        """
        results_df = analyze_by_var('group', 'score', self.cv, self.data)

        try:
            plot_result_distibution(results_df, 'group', 'score', self.data, './pytest_data')
            assert True

        except:
            assert False
    # ------------------------------------------------------------------------------------------------------------------
    # Testing save_df_stats_var function
    # ------------------------------------------------------------------------------------------------------------------
    def test_save_df_stats_var(self):
        """
        ToDo: Testing the save_df_stats_var function
        """
        results_df = analyze_by_var('group', 'score', self.cv, self.data)

        try:
            save_df_stats_var(results_df, 'group', 'test', './pytest_data')
            assert True

        except:
            assert False

    # ------------------------------------------------------------------------------------------------------------------
    # Testing save_df_stats_val function
    # ------------------------------------------------------------------------------------------------------------------
    def test_save_df_stats_val(self):
        """
        ToDo: Testing the save_df_stats_val function
        """
        results_df = analyze_by_var('group', 'score', self.cv, self.data)

        try:
            save_df_stats_val(results_df, 'group', 'test', './pytest_data')
            assert True

        except:
            assert False

    # ------------------------------------------------------------------------------------------------------------------
    # Testing run function
    # ------------------------------------------------------------------------------------------------------------------
    def test_run(self):
        """
        ToDo: Testing the run function
        """

        try:
            run('group', self.cv, self.data, 'score', './pytest_data')
            assert True

        except:
            assert False
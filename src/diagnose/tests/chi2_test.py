"""
Tests for the chi2_test_for_indep.py script

:author: Tessa Johnson
:email: tessa<dot>johnson<at>geomdata<dot>com
:created: 2019 11 13
:copyright: (c) 2019, GDA
:license: All Rights Reserved, see LICENSE for more details
"""

from builtins import breakpoint
from diagnose.analysis_for_dep import *
import numpy as np
import pytest


class TestChi2Indep:
    """
    class of tests to test the chi2 for independence test
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """
        setup
        """
        # set seed
        np.random.seed(27705)

        self.cv = ['a', 'b', 'c']
        self.data = pd.DataFrame({'a': ['alice'] * 5 + ['bob'] * 5, 'b': ['fish'] * 5 + ['pig'] * 5,
                                  'c': np.random.choice(['bar', 'dog', 'cat'], 10)})

    def teardown(self):
        """
        teardown
        """
        pass

    # ------------------------------------------------------------------------------------------------------------------
    # Testing chi2_test function
    # ------------------------------------------------------------------------------------------------------------------
    def test_chi2_test(self):
        """
        given a data set where two unrandomized columns and one randomized columns, test that the the chi-squared
        test appropriately identifies this

        :return:
        """

        df = chi2_test(self.cv, self.data, 'test')

        assert df.p_values[(df.cat_var_1 == 'a') & (df.cat_var_2 == 'b')].values < .05 and \
            df.p_values[(df.cat_var_1 == 'a') & (df.cat_var_2 == 'c')].values > 0.05

    # ------------------------------------------------------------------------------------------------------------------
    # Testing multiple_testing_correction function
    # ------------------------------------------------------------------------------------------------------------------
    def test_multiple_testing_correction(self):
        """
        Using the same data used in `test_chi2_test()` make sure that the FDR is working correctly and saving correctly
        We will do this checking that the corrected p-value is greater than the original p-value

        :return:
        """

        df = chi2_test(self.cv, self.data, 'test')
        df = multiple_testing_correction(df)

        assert df.p_values.values[0] < df.corrected_p_value.values[0]

    # ------------------------------------------------------------------------------------------------------------------
    # Testing plot_heatmap function
    # ------------------------------------------------------------------------------------------------------------------
    def test_plot_heatmap(self):
        """
        Test that the plot_heatmap function runs

        :return:
        """

        df = chi2_test(self.cv, self.data, 'test')
        df = multiple_testing_correction(df)

        try:
            plot_heatmap(self.cv, df, './pytest_data/', 'test')
            assert True

        except:
            assert False

    # ------------------------------------------------------------------------------------------------------------------
    # Testing save_df function
    # ------------------------------------------------------------------------------------------------------------------
    def test_save_df(self):
        """
        Test that the save_df function runs

        :return:
        """
        df = chi2_test(self.cv, self.data, 'test')
        df = multiple_testing_correction(df)

        try:
            save_df('test', df, './pytest_data/')
            assert True

        except:
            assert False

    # ------------------------------------------------------------------------------------------------------------------
    # Testing run function
    # ------------------------------------------------------------------------------------------------------------------

    def test_run(self):
        """
        Test that the run() functions works - this is an end to end test for the chi^2 test since it combines all of
        the function

        """
        data = pd.DataFrame({'a': ['alice'] * 5 + ['bob'] * 5, 'b': ['fish'] * 5 + ['pig'] * 5,
                            'c': np.random.choice(['bar', 'dog', 'cat'], 10), 'test': ['test0']*5 + ['test1']*5})

        try:
            run('test', self.cv, data, './pytest_data/')
            assert True

        except:
            assert False

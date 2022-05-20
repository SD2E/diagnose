"""
File needed so pip install works properly

:author: Tessa Johnson (tessa.johnson@geomdata.com)
:created: 2020
:copyright: (c) 2020, GDA
:license: see LICENSE for more details
"""

import numpy as np
import itertools


def check_varying_categories(df):
    """
    function to check if any columns don't vary in their values

    :param df: experimental setup dataframe
    :return:
        - number of unique values in each column
        - which columns have non-varying categories
    """

    return df.nunique(), list(df.nunique()[df.nunique().values == 1].index)


def get_num_replicates(df):
    """
    For variables that do vary - see how many replicates there are for each group

    :param df: experimental setup dataframe
    :return: number of replicates per combination of covariates
    """

    return df.groupby(df.columns.tolist(), as_index=False).size()


def get_covered_combinations(df):
    """
    Checking Covered vs. missing combinations of variables

    :param df: experimental setup dataframe
    :return: percentage of combinations covered and which combinations are not covered
    """

    if np.prod(df.nunique()) == len(df.drop_duplicates()):
        return 1, None
    else:
        unique_col_vals = []
        for col in df.columns:
            unique_col_vals.append(df[col].unique())

        missing = []
        for comb in list(itertools.product(*unique_col_vals)):
            if list(comb) not in df.values.tolist():
                missing.append(comb)
        return 1 - len(missing)/len(list(itertools.product(*unique_col_vals))), missing

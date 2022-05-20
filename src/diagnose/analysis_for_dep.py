"""
conduct an chi-squared test for independence test on all pairwise combinations of categorical variables 

:author: Tessa Johnson (tessa.johnson@geomdata.com)
:created: 2019
:copyright: (c) 2020, GDA
:license: see LICENSE for more details
"""

from builtins import breakpoint
import matplotlib
import platform

if platform.system() == "Darwin":
    matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import pandas as pd
import itertools
import numpy as np
import statsmodels.stats.multitest as stat
import os


def chi2_test(cat_vars, data_df, group):
    """
    function to perform the chi^2 test for independence on a given data set - every combination of categorical
    variables is tested for dependence (with the idea that dependence indicates a lack of randomization in the
    experimental design

    :param cat_vars: vector of strings for the names of the categorical variables (since the data frame also contains
    continuous variables/variables that aren't being analyzed for one reason or another
    :param data_df: data set of the experiments performed
    :param group: categorical variable by which to group and then analyze the data
    :return: df: dataframe with the group, combinations of the categorical variables, chi^2 values, p-values, and
    degrees of freedom
    """

    # function to get chi-squared test statistics and p-values 
    p_val = []
    chi2 = []
    df = []
    cat_var_1 = []
    cat_var_2 = []

    # loop through combinations of categorical variables
    for i in list(itertools.combinations(cat_vars, 2)):

        # complete chi^2 test
        ct = pd.crosstab(data_df[i[0]].astype('str'), data_df[i[1]].astype('str'))
        chi2_t = stats.chi2_contingency(ct)

        # record pertinent variables
        chi2.append(chi2_t[0])
        p_val.append(chi2_t[1])
        df.append(chi2_t[2])
        cat_var_1.append(i[0])
        cat_var_2.append(i[1])

    # populate data frame with information from lists
    df = pd.DataFrame({'group': [group] * len(p_val),
                       'cat_var_1': cat_var_1,
                       'cat_var_2': cat_var_2,
                       'chi_squared_val': chi2,
                       'p_values': p_val,
                       'deg_of_fr': df})

    return df


def multiple_testing_correction(df):
    """
    due to the quantity of tests being conducted, it is appropriate to utilize a multiple testing correction

    :param df: dataframe with original uncorrected values
    :return: df: dataframe with corrected values appended onto the end of it
    """

    # doing FDR correction since we did so many tests

    df = df.reset_index()

    # calculate correction - Benjamini & Hochberg/Yekutieli false discovery rate control procedure 
    fdr = stat.multipletests(df.p_values, alpha=0.01, method='fdr_bh')

    # record statistics/hypothesis test decision
    df['reject'] = fdr[0]
    df['corrected_p_value'] = fdr[1]

    # get new chi-squared values based on corrected p-value (for some values of p, the inverse cdf of the chi-squared
    # returns infinity rather than an exact value)
    corrected_chi_squared = []

    for i in range(len(df)):
        # if the corrected p-value is the same as the original p-value, don't recalculate the chi-squared value
        if df.p_values[i] == df.corrected_p_value[i]:
            corrected_chi_squared.append(df.chi_squared_val[i])
        else:
            # use inverse cdf of chi-squared distribution to get corrected chi-squared value, i.e. the value that
            # corresponds to the corrected p-value
            corrected_chi_squared.append(stats.chi2.ppf(q=df.corrected_p_value[i], df=df.deg_of_fr[i]))

    df['corrected_chi_squared'] = corrected_chi_squared

    return df


def plot_heatmap(cat_vars, df, output_dir, group=" "):
    """
    function to plot the heatmaps of the corrected_chi_squared values and the corrected_p_value values

    :param cat_vars: categorical variables
    :param df: data frame with data on the variables to be plotted
    :param output_dir: directory to save data to 
    :param group: group within the group_col that corresponds to the data, e.g. XNOR or AND
    """

    cols_to_plot = ['corrected_p_value']  # ['corrected_chi_squared', 'corrected_p_value']
    for i in cols_to_plot:

        # reorganize data to make plotting nicer
        dta = df[['cat_var_1', 'cat_var_2', i]]
        dta_hm = dta.append(dta.reindex(columns = ['cat_var_2', 'cat_var_1', i]).rename(columns={'cat_var_1':'cat_var_2', 'cat_var_2':'cat_var_1'}))

        ax = sns.heatmap(dta_hm.pivot_table(values=i, index='cat_var_1', columns='cat_var_2'), annot=True)
        ax.set(xlabel=None)
        ax.set(ylabel=None)
        ax.invert_yaxis()
        plt.title(i)

        output = os.path.join(output_dir, 'dep_{}_{}_heatmap.png'.format(group, i))
        if not os.path.exists(os.path.join(output_dir)):
            os.makedirs(os.path.join(output_dir), exist_ok=True)

        print("saving to: " + output)
        plt.savefig(output, bbox_inches='tight')
        plt.close()


def save_df(group_col, df, output_dir):
    """
    function to save the full dataframe for each group 

    :param group_col: column the data is grouped by
    :param df:  data frame with data on the variables to be saved
    :param output_dir: directory to save data to 
    """

    # sort by corrected p-value
    df = df.sort_values(by=['corrected_p_value']).reset_index()

    df = df.drop(df.columns[[0, 1]], axis=1)

    output = os.path.join(output_dir, 'dep_{}_chi_squared_independence_test.tsv'.format(group_col))

    print("saving to: " + output)
    df.to_csv(output, sep='\t', index=False)

    return output


def run(group_col, cat_vars, data_df, output_dir):
    """
    function to run everything

    :param group_col: column to group data by, e.g. group by gate and save results on a per gate basis
    :param cat_vars: categorical variables to analyze
    :param data_df: dataframe of results to analyze
    :param output_dir: directory to save results to 
    """
    # safe copy
    cat_vars_copy = cat_vars.copy()
    data_df_copy = data_df.copy(deep=True)
    cat_vars_all = cat_vars_copy.copy()

    # clean data
    # make sure group col is not in cat vars
    if group_col in cat_vars_copy:
        cat_vars_copy.remove(group_col)
    # replace nan with 'NaN' in cat var columns
    data_df_copy.fillna('NAN', inplace=True)

    # run analysis on results subset by group col
    groups = data_df_copy[group_col].unique()

    if group_col not in cat_vars_all:
        cat_vars_all.append(group_col)
    df = chi2_test(cat_vars_all, data_df_copy, 'all')

    for group in groups:
        subset_df = data_df_copy[(data_df_copy[group_col] == group)]

        df = df.append(chi2_test(cat_vars_copy, subset_df, group), ignore_index=True)

    df = multiple_testing_correction(df)

    files = []

    # subset_df = df[(df['group'] == 'all')]
    # plot_heatmap(cat_vars_all, subset_df, output_dir, 'all')
    # files.append(save_df('all', df, output_dir))
    # # check_df('all', df, output_dir)

    for i, group in enumerate(groups):
        subset_df = df[(df['group'] == group)]

        plot_heatmap(cat_vars_copy, subset_df, output_dir, group)
        files.append(save_df(group, subset_df, output_dir))
        # check_df(group, subset_df, output_dir)

    return files

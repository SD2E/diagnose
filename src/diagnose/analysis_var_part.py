"""
compare distributions by parts

:author: anastasia deckard (anastasia.deckard@geomdata.com)
:created: 2019
:copyright: (c) 2020, GDA
:license: see LICENSE for more details
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
import platform
if platform.system() == "Darwin":
    matplotlib.use("TkAgg")
else:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import kruskal
import itertools
import diagnose.dal.cp_ys as dat
import diagnose.data_tracking as dattrk
import statsmodels.stats.multitest as stat


def analyze_by_part(score_col, cat_vars, data_df):
    """
    get kruskal-wallis p-value (corrected for multiple tests) for each part

    :param score_col: the score column
    :param cat_vars: list of parts ToDo: We probably shouldn't reuse this variable name because it's confusing
    :param data_df: dataframe
    :return: results_df: dataframe with corrected kw p-values for each of the parts (or combinations of parts)
    """

    results_list = list()
    for var in cat_vars:
        vals = [group[score_col].values for name, group in data_df.groupby(var)]
        if len(vals) >= 2:
            kw_hstat, kw_pval = kruskal(*vals)
            record = {'variable': var, 'var_kw_hstat': kw_hstat, 'var_kw_pval': kw_pval}
            results_list.append(record)

    results_df = pd.DataFrame(results_list)

    fdr = stat.multipletests(results_df.var_kw_pval, method='fdr_bh')
    results_df['var_kw_pval_corrected'] = fdr[1]

    results_df.sort_values(by=['var_kw_pval_corrected'], ascending=[True], inplace=True)

    return results_df


def summarize_results(data_df, results_df, score_col, cat_vars):
    """
    Function to group and compute statistics on the samples per value of each part for each group and then merge
    with the results of the analyze_by_part() function

    :param data_df: full dataframe
    :param results_df: dataframe with results from kw test in the analyze_by_part() function
    :param score_col: the score column
    :param cat_vars: list of parts
    :return:
         summarize_df: dataframe with summary values on each part (or combination of parts) as well as the kw test
         values
        subset_summarize_df: subset of summarize_df values such that the p-values < 0.05 and median value < 0.5
    """

    # reform and summarize by variable
    results_list = list()
    for var_col in cat_vars:
        # reformat the data into a consistent format for each variable
        temp_df = data_df[[var_col, score_col]]
        temp_df["variable"] = var_col
        temp_df.rename(columns={var_col: "value", score_col: "score"}, inplace=True)
        temp_df = temp_df[['variable', 'value', 'score']]

        # group and compute statistics on the samples per value of the variable for each group
        grouped_df = temp_df.groupby(['variable', 'value'])
        grouped_df = grouped_df['score'].agg({"val": ['count', 'min', 'median', 'max', 'std']})
        new_cols = ['_'.join(t) if isinstance(t, tuple) else t for t in grouped_df.columns.values]
        grouped_df.columns = new_cols
        grouped_df.reset_index(drop=False, inplace=True)

        # merge with the statistic for how much that variable accounts for the variation in performance
        merged_df = pd.merge(grouped_df, results_df, how='left',
                             left_on=['variable'], right_on=['variable'])

        results_list.append(merged_df)

    summarize_df = pd.concat(results_list)
    summarize_df.sort_values(by=['var_kw_pval_corrected', 'variable', 'val_median'], ascending=[True, True, True],
                             inplace=True)

    subset_summarize_df = summarize_df[
        (summarize_df['var_kw_pval_corrected'] < 0.05) & (summarize_df['val_median'] < 0.5)]

    return summarize_df, subset_summarize_df


def combine_cat_vars(data_df, cat_vars):
    """
    For combination of parts get information on whether each samples has neither, one, or both of
    the parts

    :param data_df: dataframe w/ part information
    :param cat_vars: list of parts
    :return:
        combos_df: dataframe with information on whether or not each combination appears in the data
        combo_vars_str: list of combinations of parts
    """

    # make combos of the cat vars
    combo_vars = list(itertools.combinations(cat_vars, r=2))
    combos_df = data_df.copy(deep=True)
    combo_vars_str = list()
    for combo in combo_vars:
        combo = list(combo)
        combo_str = '_'.join(combo)
        combo_vars_str.append(combo_str)
        temp_col = data_df[combo].apply(
            lambda x: ''.join(x.astype(str)),
            axis=1, raw=True).to_list()
        # recode nn -> Nan, leave other distributions as is
        val_map = {'nn': np.nan, 'yn': 'one', 'ny': 'one', 'yy': 'both'}
        temp_col = [val_map[x] for x in temp_col]
        combos_df[combo_str] = temp_col

    combos_df.drop(columns=cat_vars, inplace=True)

    return combos_df, combo_vars_str


# ToDo: Deprecate? This isn't used anywhere?
def combine_cat_vars_nonp(data_df, cat_vars, score_col):
    """
    Function to create a column of categorical variable combinations

    :param data_df: dataframe
    :param cat_vars: categorical variables
    :param score_col: score column
    :return: (combo_vars_str, combos_df): A tuple of a list of the combinations of variables and a new dataframe with
    the categorical variables
    """

    combo_vars = list(itertools.combinations(cat_vars, r=2))
    new_cols = dict()
    new_cols[score_col] = data_df[score_col].to_list()
    combo_vars_str = list()
    for c_i, combo in enumerate(combo_vars):
        combo = list(combo)
        combo_str = '_'.join(combo)
        combo_vars_str.append(combo_str)
        new_col = [i + j for i, j in zip(data_df[combo[0]].to_list(), data_df[combo[1]].to_list())]
        new_cols[combo_str] = new_col

    combos_df = pd.DataFrame(new_cols)

    return combo_vars_str, combos_df


def save_df_stats_var(results_df, doc_info, output_dir, prefix):
    """
    Saving results_df to file

    :param results_df: dataframe of parts analysis to save
    :param doc_info: Information about what was run to get these results (e.g. what script was run, what command was
    run)
    :param output_dir: output directory
    :param prefix: prefix for file name
    """

    out_path = os.path.join(output_dir, prefix + "__stats_var.tsv")
    print("saving to: " + out_path)
    with open(out_path, 'w') as out_file:
        out_file.write(doc_info)
        out_file.write("# analysis of variance performed for each part\n")
        out_file.write("# Kruskal-Wallace p-val with correction (lower value -> investigate)\n")
        out_file.write("# \n")
        results_df.to_csv(out_file, sep='\t', header=True, index=False)


def save_df_stats_val(results_df, doc_info, output_dir, prefix):
    """
    Save summary dataframe to file

    :param results_df: dataframe with summary values on each part (or combination of parts) as well as the kw test
    values
    :param doc_info: Information about what was run to get these results (e.g. what script was run, what command was
    run)
    :param output_dir: output directory
    :param prefix: prefix for file name
    """

    out_path = os.path.join(output_dir, prefix + "__stats_val.tsv")
    print("saving to: " + out_path)
    with open(out_path, 'w') as out_file:
        out_file.write(doc_info)
        out_file.write("# stats on values of each variable, and analysis of variance for each group \n")
        out_file.write("# Kruskal-Wallace p-val with correction (lower value -> investigate)\n")
        out_file.write("# \n")
        results_df.to_csv(out_file, sep='\t', header=True, index=False)


def save_df_stats_val_worry(results_df, doc_info, output_dir, prefix):
    """
    Save subset of summary dataframe to file

    :param results_df: subset of summarize_df values such that the p-values < 0.05 and median value < 0.5
    :param doc_info:  Information about what was run to get these results (e.g. what script was run, what command was
    run)
    :param output_dir: output directory
    :param prefix: prefix for file name
    """

    out_path = os.path.join(output_dir, prefix + "__stats_val_CHECK.tsv")
    print("saving to: " + out_path)
    with open(out_path, 'w') as out_file:
        out_file.write(doc_info)
        out_file.write("# stats on values of each variable, and analysis of variance for each group \n")
        out_file.write("# Kruskal-Wallace p-val with correction (lower value -> investigate)\n")
        out_file.write("# var_kw_pval_corrected < 0.05, val_median < 0.5 \n")
        out_file.write("# \n")
        results_df.to_csv(out_file, sep='\t', header=True, index=False)


def plot_result_distibution(results_df, score_col, data_df, output_dir, prefix):
    """
    Boxplot of Performance Distributions for each part with corrected KW p-values

    :param results_df: analyze of parts (either individual or in combination)
    :param score_col: the score column
    :param data_df: dataframe
    :param output_dir: output directory
    :param prefix: prefix for file name
    """

    pal = sns.color_palette("hls", 8)

    vars_sorted = results_df['variable']

    heights_list = [1]  # first plot will be whole distribution
    for col in vars_sorted:
        heights_list.append(len(data_df[col].unique()))

    fig_height = 2 + sum(heights_list) * 0.5

    fig, axes = plt.subplots(len(vars_sorted) + 1,
                             figsize=(7, fig_height),
                             gridspec_kw={'height_ratios': heights_list},
                             sharex=True)

    # show whole distribution
    sns.boxplot(x=score_col,
                data=data_df,
                orient="h",
                ax=axes[0],
                palette=pal)
    axes[0].set(ylabel='ALL')

    for i, var in enumerate(vars_sorted):
        order = data_df.groupby(by=[var])[score_col].median().sort_values(ascending=True).iloc[::-1].index
        sns.boxplot(x=score_col, y=var,
                    data=data_df,
                    orient="h",
                    order=order,
                    ax=axes[i + 1],
                    palette=pal)
        pval = results_df[(results_df['variable'] == var)].iloc[0]['var_kw_pval_corrected']
        axes[i + 1].annotate("p-value: {0:.5e}".format(pval), xy=(0, 1), xycoords="axes fraction",
                             xytext=(5, 10), textcoords="offset points",
                             ha="left", va="top")

    fig.suptitle('Performance Distributions for Parts \nwith corrected KW p-values', fontsize=16)

    out_path = os.path.join(output_dir, prefix + "__dist.png")
    print("saving to: " + out_path)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(out_path)
    # plt.close() ToDo: Deprecated? Can we delete this?


def run(data_df, cat_vars, score_col, output_dir):
    """
    function to run analysis of parts

    :param data_df: dataframe with parts information
    :param cat_vars: list of parts
    :param score_col: the score column
    :param output_dir: output directory
    """

    doc_info = dattrk.get_doc_info_string(__file__, sys.argv, None)

    # we can't run a row that doesn't have a score for it
    data_df.dropna(subset=[score_col], inplace=True)
    # replace nan with 'NaN' in cat var columns
    data_df.fillna('NAN', inplace=True)

    # run analysis for individual parts
    results_df = analyze_by_part(score_col, cat_vars, data_df)
    save_df_stats_var(results_df, doc_info, output_dir, 'av_part')

    summary_df, subset_summarize_df = summarize_results(data_df, results_df, score_col, cat_vars)

    save_df_stats_val(summary_df, doc_info, output_dir, 'av_part')
    save_df_stats_val_worry(subset_summarize_df, doc_info, output_dir, 'av_part')
    plot_result_distibution(results_df, score_col, data_df, output_dir, 'av_part')

    # analysis for combinations of parts, pairs
    combos_df, combo_vars_str = combine_cat_vars(data_df=data_df, cat_vars=cat_vars, score_col=score_col)
    results_df = analyze_by_part(score_col, combo_vars_str, combos_df)
    save_df_stats_var(results_df, doc_info, output_dir, 'av_partcombos')

    summary_df, subset_summarize_df = summarize_results(combos_df, results_df, score_col, combo_vars_str)

    save_df_stats_val(summary_df, doc_info, output_dir, 'av_partcombos')
    save_df_stats_val_worry(subset_summarize_df, doc_info, output_dir, 'av_partcombos')
    plot_result_distibution(results_df[0:25], score_col, combos_df, output_dir, 'av_partcombos')


if __name__ == '__main__':
    import json

    config_path = "configs/diagnose_config_bio.json"
    dta_json = json.load(open(config_path))

    # Initialize data access layer
    dal = dat.CpYs(dta_json["path_to_score_vars"], dta_json["path_to_parts"], dta_json["correctness_col"],
                   dta_json["group_ids"], dta_json["cat_vars"], dta_json["cont_vars"])
    group_col_ex = 'gate'  # dal.group_ids[2]
    score_col_ex = dal.correctness_col

    cat_vars_ex, data_df_ex = dal.get_correctness_by_circuit_parts()

    # by pass config output dir for testing
    output_dir_ex = "../output/avp_test/"

    run(data_df_ex, cat_vars_ex, score_col_ex, output_dir_ex)

    print("finished!")

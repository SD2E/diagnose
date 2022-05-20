"""
compare continuous variables to see which group
has dominant variation

:author: anastasia deckard (anastasia.deckard@geomdata.com)
:created: 2019
:copyright: (c) 2020, GDA
:license: see LICENSE for more details
"""

import os
import sys
import json
import pandas as pd
import matplotlib
import platform

if platform.system() == "Darwin":
    matplotlib.use("TkAgg")
else:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import diagnose.dal.cp_ys as dat
import diagnose.data_tracking as dattrk


def analyze_by_var(group_col, score_col, cont_vars, data_df):
    """
    Functoin to get spearman's correlation for both the score column vs. the continuous variables and between the
    covariates/predictors.

    :param group_col: which column to group the data by
    :param score_col: the score column
    :param cont_vars: list of continous variables
    :param data_df: dataframe
    :return:
        results_df: List of dataframes containing the correlation values between each continuous variable and the score
        variable subset by group.
        depend_df:  List of dataframes containing the correlation values between each continuous variable subset by
        group.
    """

    # need to evaluate results on a per gate basis
    # though these should be technically further subset by strain;
    # e.g. which 4 strains do we consider to be one "circuit"
    results_list = list()
    depend_list = list()
    groups = data_df[group_col].unique()
    for group in groups:
        cols_to_keep = [score_col] + cont_vars
        subset_df = data_df[(data_df[group_col] == group)]

        cols_to_use = list()
        # try converting columns to floats
        for col_to_use in cols_to_keep:
            try:
                subset_df[col_to_use] = subset_df[col_to_use].astype('float')
                cols_to_use.append(col_to_use)
            except ValueError as e:
                print(col_to_use, e)

                # TODO: see if col could be split?

        subset_df = subset_df[cols_to_use]

        # TODO: this is inefficient!
        corr_mat = subset_df.corr(method='spearman')  # get correlation between all variables

        # get the correlation between each continuous variable and the score variable
        # this should be a list
        corr_score = corr_mat[score_col]
        corr_score = pd.DataFrame(corr_score.sort_values())
        corr_score.drop(index=score_col, inplace=True)
        corr_score.index.name = 'variable'
        corr_score.reset_index(level=0, inplace=True)
        corr_score.rename(columns={score_col: "spearman"}, inplace=True)
        corr_score['group'] = group
        corr_score = corr_score[['group', 'variable', 'spearman']]
        results_list.append(corr_score)

        # get the correlation between the covariates/predictors
        # (this should be the upper triangular portion of the correlation matrix)
        mat_size = len(cont_vars)
        corr_comp_df = corr_mat.iloc[0:(mat_size - 1), (mat_size - 1):]
        corr_list_df = pd.DataFrame(corr_comp_df.stack())
        corr_list_df.reset_index(inplace=True)
        corr_list_df.columns = ['name_1', 'name_2', 'spearman']
        corr_list_df['variables'] = list(zip(corr_list_df['name_1'], corr_list_df['name_2']))
        corr_list_df['group'] = group
        corr_list_df = corr_list_df[['group', 'variables', 'spearman']]
        corr_list_df.sort_values(by=['spearman'], inplace=True)
        depend_list.append(corr_list_df)

    results_df = pd.concat(results_list)
    results_df['spearman_abs'] = results_df['spearman'].abs()
    results_df.sort_values(by=['group', 'spearman_abs'], ascending=[True, False], inplace=True)

    depend_df = pd.concat(depend_list)
    depend_df['spearman_abs'] = depend_df['spearman'].abs()
    depend_df.sort_values(by=['group', 'spearman_abs'], ascending=[True, False], inplace=True)

    return results_df, depend_df


def plot_result_score_corr(results_df, group_col, score_col, data_df, output_dir):
    """
    create a scatter plot of the score variable plotted against each of the continuous with spearman correlation
    in the title. There should be one plot per group.

    :param results_df:  List of dataframes containing the correlation values between each continuous variable and the
    score variable subset by group.
    :param group_col:  which column to group the data by
    :param score_col: the score column
    :param data_df: dataframe
    :param output_dir: output directory
    """

    pal = sns.color_palette("hls", 8)

    groups = results_df['group'].unique()
    for group in groups:
        subset_df = data_df[(data_df[group_col] == group)]
        vars_sorted = results_df[results_df["group"] == group]['variable']

        # convert to numeric
        for var in vars_sorted:
            subset_df[var] = subset_df[var].astype('float')

        # TODO: put corr val in plot title

        # TODO: trying to get plots to be square
        fig_width = 5
        fig_height = fig_width * len(vars_sorted) * 0.85

        fig, axes = plt.subplots(nrows=len(vars_sorted), ncols=1,
                                 figsize=(fig_width, fig_height),
                                 sharex=True)

        if len(vars_sorted) <= 1:
            axes = [axes]

        for i, var in enumerate(vars_sorted):
            # ToDo: Is order deprecated/unused?
            order = subset_df.groupby(by=[var])[score_col].median().sort_values(ascending=True).iloc[::-1].index
            sns.scatterplot(x=score_col, y=var,
                            data=subset_df,
                            ax=axes[i],
                            palette=pal
                            )

            # ToDo: why is this labeled pval? I thought this was a correlation value
            pval = results_df[(results_df['group'] == group) & (results_df['variable'] == var)].iloc[0][
                'spearman']
            axes[i].annotate("spearman: {0:.5f}".format(pval), xy=(0, 1), xycoords="axes fraction",
                             xytext=(5, 10), textcoords="offset points",
                             ha="left", va="top")

            margin = (max(subset_df[var]) - min(subset_df[var])) * 0.05
            axes[i].set(ylim=(min(subset_df[var]) - margin, max(subset_df[var]) + margin))

        fig.suptitle('Performance for {0:s} = {1:s} '.format(group_col, group),
                     fontsize=16)

        out_path = os.path.join(output_dir, "avco__" + group_col + "_" + group + "__scatter.png")
        print("saving to: " + out_path)
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        fig.savefig(out_path)
        plt.close()


def save_df_stats_var(results_df, group_col, doc_info, output_dir):
    """
    Function to save the results_df as a tsv

    :param results_df: List of dataframes containing the correlation values between each continuous variable and the
    score variable subset by group.
    :param group_col: which column the data is grouped by
    :param doc_info: Information about what was run to get these results (e.g. what script was run, what command was
    run)
    :param output_dir: output directory
    :return: out_path: path to saved file
    """

    out_path = os.path.join(output_dir, "avco__" + group_col + "__stats_var.tsv")
    print("saving to: " + out_path)
    with open(out_path, 'w') as out_file:
        out_file.write(doc_info)
        out_file.write("# spearman correlation to score, for each group\n")
        out_file.write("# spearman correlation (bigger positive/negative number -> investigate)\n")
        out_file.write("# \n")
        results_df.to_csv(out_file, sep='\t', header=True, index=False)
    return out_path


def save_df_depend(results_df, group_col, doc_info, output_dir):
    """
    Function to save the depend_df as a tsv

    :param results_df:  List of dataframes containing the correlation values between each continuous variable subset by
        group.
    :param group_col: which column the data is grouped by
    :param doc_info: Information about what was run to get these results (e.g. what script was run, what command was
    run)
    :param output_dir: output directory
    :return: out_path: path to saved file
    """

    out_path = os.path.join(output_dir, "avco_depend__" + group_col + ".tsv")
    print("saving to: " + out_path)
    with open(out_path, 'w') as out_file:
        out_file.write(doc_info)
        out_file.write("# spearman correlation between variables for each group\n")
        out_file.write("# spearman correlation (bigger positive/negative number -> dependency)\n")
        out_file.write("# \n")
        results_df.to_csv(out_file, sep='\t', header=True, index=False)
    return out_path


def run(group_col, cont_vars, data_df, score_col, output_dir):
    """
    Function to run analysis of continous variables

    :param group_col: which column to group the data by
    :param cont_vars: list of continous variables
    :param data_df: dataframe
    :param score_col: the score column
    :param output_dir: output directory
    :return: files: list of files output by the script
    """

    doc_info = dattrk.get_doc_info_string(__file__, sys.argv, None)

    # safe copy
    cont_vars_copy = cont_vars.copy()
    data_df_copy = data_df.copy(deep=True)

    # clean data
    # make sure group col is not in cat vars
    if group_col in cont_vars_copy:
        cont_vars_copy.remove(group_col)
    # replace nan with 'NaN' in cat var columns
    data_df_copy.fillna('NAN', inplace=True)

    files = []
    # run analysis
    results_df, depend_df = analyze_by_var(group_col, score_col, cont_vars_copy, data_df_copy)
    files.append(save_df_stats_var(results_df, group_col, doc_info, output_dir))
    files.append(save_df_depend(depend_df, group_col, doc_info, output_dir))

    plot_result_score_corr(results_df, group_col, score_col, data_df_copy, output_dir)

    return files


if __name__ == '__main__':
    config_path = "configs/diagnose_config_bio.json"
    dta_json = json.load(open(config_path))

    # Initialize data access layer
    dal = dat.CpYs(dta_json["path_to_score_vars"], dta_json["path_to_parts"], dta_json["correctness_col"],
                   dta_json["group_ids"], dta_json["cat_vars"], dta_json["cont_vars"])
    group_col_ex = 'gate'  # dal.group_ids[2]
    score_col_ex = dal.correctness_col

    group_ids, cont_vars_ex, data_df_ex = dal.get_correctness_by_cont_var()

    # by pass config output dir for testing
    output_dir_ex = "../output/avcont_test/"

    run(group_col_ex, cont_vars_ex, data_df_ex, score_col_ex, output_dir_ex)

    print("finished!")

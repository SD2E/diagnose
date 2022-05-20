"""
compare categorical variables to see which group
has dominate variation

:author: anastasia deckard (anastasia.deckard@geomdata.com)
:copyright: (c) 2019, GDA
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
from scipy.stats import kruskal
import diagnose.data_tracking as dattrk
import statsmodels.stats.multitest as stat


def analyze_by_var(group_col, score_col, cat_vars, data_df):
    """
    run a kruskal-wallis h test between each of the categorical variables and the score columns

    :param group_col: which column to group the data by
    :param score_col: the score column
    :param cat_vars: list of categorical variables
    :param data_df: dataframe
    :return:
        results_df: dataframe with the kruskal-wallis h-stat and kruskal-wallis p-value for each group/variable
        combination
    """

    # need to evaluate results on a per gate basis
    # though these should be technically further subset by strain;
    # e.g. which 4 strains do we consider to be one "circuit"
    results_list = list()
    groups = data_df[group_col].unique()
    for group in groups:
        subset_df = data_df[(data_df[group_col] == group)]
        for var in cat_vars:
            vals = [group[score_col].values for name, group in subset_df.groupby(var)]
            if len(vals) >= 2:
                kw_hstat, kw_pval = kruskal(*vals)
                record = {'group': group, 'variable': var, 'var_kw_hstat': kw_hstat, 'var_kw_pval': kw_pval}
                results_list.append(record)

    results_df = pd.DataFrame(results_list)

    # do a multiple tests correction to adjust for the number of hypothesis tests we've done
    fdr = stat.multipletests(results_df.var_kw_pval, method='fdr_bh')
    results_df['var_kw_pval_corrected'] = fdr[1]

    results_df.sort_values(by=['group', 'var_kw_pval_corrected'], ascending=[True, True], inplace=True)

    return results_df


def summarize_results(data_df, results_df, group_col, score_col, cat_vars):
    """
    Function to group and compute statistics on the samples per value of the variable for each group and then merge
    with the results of the analyze_by_var() function

    :param data_df: full dataframe
    :param results_df: dataframe with results from kw test in the analyze_by_var() function
    :param group_col: column by which to group data_df by
    :param score_col: score column
    :param cat_vars: list of categorical variables
    :return:
        summarize_df: dataframe with summary values on each group/variables combination as well as the kw test values
        subset_summarize_df: subset of summarize_df values such that the p-values < 0.05 and median value < 0.5
    """

    # reform and summarize by variable
    results_list = list()
    for var_col in cat_vars:
        # reformat the data into a consistent format for each variable
        temp_df = data_df[[group_col, var_col, score_col]]
        temp_df = temp_df.assign(variable=var_col)
        temp_df.rename(columns={group_col: "group", var_col: "value", score_col: "val"}, inplace=True)
        temp_df = temp_df[['group', 'variable', 'value', 'val']]
        temp_df['val'] = temp_df['val'].astype('float')

        # group and compute statistics on the samples per value of the variable for each group
        grouped_df = temp_df.groupby(['group',
                                      'variable', 'value']).agg({"val": ['count', 'min', 'median', 'max', 'std']})
        new_cols = ['_'.join(t) if isinstance(t, tuple) else t for t in grouped_df.columns.values]
        grouped_df.columns = new_cols
        grouped_df.reset_index(drop=False, inplace=True)

        # merge with the statistic for how much that variable accounts for the variation in performance
        merged_df = pd.merge(grouped_df, results_df, how='left',
                             left_on=['group', 'variable'], right_on=['group', 'variable'])

        results_list.append(merged_df)

    summarize_df = pd.concat(results_list)
    summarize_df.sort_values(by=['group', 'var_kw_pval_corrected', 'variable', 'val_median'],
                             ascending=[True, True, True, True], inplace=True)

    subset_summarize_df = summarize_df[
        (summarize_df['var_kw_pval_corrected'] < 0.05) & (summarize_df['val_median'] < 0.5)]

    return summarize_df, subset_summarize_df


def plot_result_heatmap_stat(results_df, group_col, output_dir):
    """
    ToDo: Deprecated? This is commented out in run()
    Plot a heatmap of the kruskal-wallace h-stats for the groups in the group_col

    :param results_df: dataframe with results from kw test in the analyze_by_var() function
    :param group_col: column by which to the data is grouped by
    :param output_dir: output directory
    """

    if len(results_df['group'].unique()) >= 2:
        results_wide = results_df.pivot("group", "variable", "var_kw_hstat")

        cmap = "YlGnBu"
        width = 1 + (0.9 * len(results_wide.columns.values))
        height = 1 + (0.9 * len(results_wide.index.values))
        fig, ax = plt.subplots(figsize=(width, height))
        sns_plot = sns.heatmap(results_wide,
                               # figsize=(width, height),
                               annot=True, fmt='.2f',
                               cmap=cmap, center=0)
        plt.title('Analysis of Variation of Performance by {0:s}\n'
                  'Kruskal-Wallace h-stat (higher value -> investigate)'.format(group_col), loc='left')

        plt.tight_layout()
        # sns_plot.ax_row_dendrogram.set_visible(False) ToDo: Deprecated?
        # sns_plot.ax_col_dendrogram.set_visible(False)
        out_path = os.path.join(output_dir, "avca__" + group_col + "__heatmap_stat.png")
        print("saving to: " + out_path)
        plt.savefig(out_path)
        plt.close()


def plot_result_heatmap_pval(results_df, group_col, output_dir):
    """
    Plot a heatmap of the kruskal-wallace p-values for the groups in the group_col

    :param results_df: dataframe with results from kw test in the analyze_by_var() function
    :param group_col: column by which to the data is grouped by
    :param output_dir: output directory
    """

    if len(results_df['group'].unique()) >= 2:
        results_wide = results_df.pivot("group", "variable", "var_kw_pval_corrected")

        cmap = "YlGnBu"
        width = 1.5 + (0.9 * len(results_wide.columns.values))
        height = 1.5 + (0.9 * len(results_wide.index.values))

        fig, ax = plt.subplots(figsize=(width, height))
        sns_plot = sns.heatmap(results_wide,
                               # figsize=(width, height),
                               annot=True, fmt='.2f',
                               cmap=cmap, center=0)
        plt.title('Analysis of Variation of Performance by {0:s}\n'
                  'Corrected Kruskal-Wallis p-val (lower value -> investigate)'.format(group_col), loc='left')

        plt.tight_layout()

        # sns_plot.ax_row_dendrogram.set_visible(False)
        # sns_plot.ax_col_dendrogram.set_visible(False)
        out_path = os.path.join(output_dir, "avca__" + group_col + "__heatmap_corrected_pval.png")
        print("saving to: " + out_path)
        plt.savefig(out_path)
        plt.close()


def plot_result_distibution(results_df, group_col, score_col, data_df, output_dir):
    """
    Boxplot of Performance Distributions for Groups in group_col with corrected KW p-values

    :param results_df: dataframe with results from kw test in the analyze_by_var() function
    :param group_col: column by which to the data is grouped by
    :param score_col: the score column
    :param data_df: full dataframe
    :param output_dir: output directory
    """

    pal = sns.color_palette("hls", 8)

    groups = results_df['group'].unique()
    for group in groups:
        subset_df = data_df[(data_df[group_col] == group)]
        vars_sorted = results_df[results_df["group"] == group]['variable']

        heights_list = [1]  # first plot will be whole distribution
        for col in vars_sorted:
            heights_list.append(len(subset_df[col].unique()))

        fig_height = 2 + sum(heights_list) * 0.2 + len(vars_sorted) * 0.5

        fig, axes = plt.subplots(len(vars_sorted) + 1,
                                 figsize=(7, fig_height),
                                 gridspec_kw={'height_ratios': heights_list},
                                 sharex=True)

        # show whole distribution
        sns.boxplot(x=score_col,
                    data=subset_df,
                    orient="h",
                    ax=axes[0],
                    palette=pal)
        axes[0].set(ylabel='ALL')

        for i, var in enumerate(vars_sorted):
            order = subset_df.groupby(by=[var])[score_col].median().sort_values(ascending=True).iloc[::-1].index
            sns.boxplot(x=score_col, y=var,
                        data=subset_df,
                        orient="h",
                        order=order,
                        ax=axes[i + 1],
                        palette=pal)
            pval = results_df[(results_df['group'] == group) & (results_df['variable'] == var)].iloc[0][
                'var_kw_pval_corrected']
            axes[i + 1].annotate("p-value: {0:.5e}".format(pval), xy=(0, 1), xycoords="axes fraction",
                                 xytext=(5, 10), textcoords="offset points",
                                 ha="left", va="top")
            axes[i + 1].set_ylabel(var, loc='top', rotation='horizontal', fontweight='bold')

        fig.suptitle('Performance Distributions for\n {0:s} = {1:s} \nwith corrected KW p-values'.format(group_col,
                                                                                                         group),
                     fontsize=16)

        # fix xaxis
        for a in fig.axes: # [fig.axes[0], fig.axes[-1]]:
            a.tick_params(
                axis='x',  # changes apply to the x-axis
                which='both',  # both major and minor ticks are affected
                bottom=True,
                top=False,
                labelbottom=True)
            # a.xaxis.label.set_visible(False)

        out_path = os.path.join(output_dir, "avca__" + group_col + "_" + group + "__dist.png")
        print("saving to: " + out_path)
        fig.tight_layout(rect=[0, 0, 1, .97])
        fig.savefig(out_path)
        plt.close()


# ToDo: Do we need all three of these functions? Couldn't we just have title and comment as arguments? Since that's the
#  only difference?
def save_df_stats_var(results_df, group_col, doc_info, output_dir):
    """
    Saving results_df to file

    :param results_df: dataframe with results from kw test in the analyze_by_var() function
    :param group_col: column by which to the data is grouped by
    :param doc_info: Information about what was run to get these results (e.g. what script was run, what command was
    run)
    :param output_dir: output directory
    :return: out_path: where the file was saved to
    """

    out_path = os.path.join(output_dir, "avca__" + group_col + "__stats_var.tsv")
    print("saving to: " + out_path)
    with open(out_path, 'w') as out_file:
        out_file.write(doc_info)
        out_file.write("# analysis of variance performed for each group\n")
        out_file.write("# Kruskal-Wallace p-val with correction (lower value -> investigate)\n")
        out_file.write("# \n")
        results_df.to_csv(out_file, sep='\t', header=True, index=False)
    return out_path


def save_df_stats_val(results_df, group_col, doc_info, output_dir):
    """
    Saving results_df to file

    :param results_df: dataframe with summary values on each group/variables combination as well as the kw test values
    :param group_col: column by which to the data is grouped by
    :param doc_info: Information about what was run to get these results (e.g. what script was run, what command was
    run)
    :param output_dir: output directory
    :return: out_path: where the file was saved to
    """

    out_path = os.path.join(output_dir, "avca__" + group_col + "__stats_val.tsv")
    print("saving to: " + out_path)
    with open(out_path, 'w') as out_file:
        out_file.write(doc_info)
        out_file.write("# stats on values of each variable, and analysis of variance for each group \n")
        out_file.write("# Kruskal-Wallace p-val with correction (lower value -> investigate)\n")
        out_file.write("# \n")
        results_df.to_csv(out_file, sep='\t', header=True, index=False)
    return out_path


def run(group_col, cat_vars, data_df, score_col, output_dir):
    """
    Function to analyze categorical variables

    :param group_col: which column to group the data by
    :param cat_vars: list of categorical variables
    :param data_df: dataframe
    :param score_col: the score column
    :param output_dir: output directory
    :return: files: list of files output by the script
    """

    doc_info = dattrk.get_doc_info_string(__file__, sys.argv, None)

    # safe copy
    cat_vars_copy = cat_vars.copy()
    data_df_copy = data_df.copy(deep=True)

    # clean data
    # make sure group col is not in cat vars
    if group_col in cat_vars_copy:
        cat_vars_copy.remove(group_col)
    # replace nan with 'NaN' in cat var columns
    data_df_copy.fillna('NAN', inplace=True)

    files = []
    # run analysis
    results_df = analyze_by_var(group_col, score_col, cat_vars_copy, data_df_copy)
    files.append(save_df_stats_var(results_df, group_col, doc_info, output_dir))

    # summarize the results
    summary_df, subset_summarize_df = summarize_results(data_df_copy, results_df, group_col, score_col, cat_vars_copy)
    files.append(save_df_stats_val(summary_df, group_col, doc_info, output_dir))
    # save_df_stats_val_worry(subset_summarize_df, group_col, doc_info, output_dir)
    # ToDo: Is this supposed to be commented out?

    # remove NAs and plot
    results_df.dropna(inplace=True)
    # plot_result_heatmap_stat(results_df, group_col, output_dir) todo: deprecated?
    plot_result_heatmap_pval(results_df, group_col, output_dir)
    plot_result_distibution(results_df, group_col, score_col, data_df_copy, output_dir)

    return files


if __name__ == '__main__':
    config_path = "configs/diagnose_config_bio.json"
    dta_json = json.load(open(config_path))

    # Initialize data access layer
    dal = dat.CpYs(dta_json["path_to_score_vars"], dta_json["path_to_parts"], dta_json["correctness_col"],
                   dta_json["group_ids"], dta_json["cat_vars"], dta_json["cont_vars"])
    group_col_ex = 'gate'  # dal.group_ids[2]
    score_col_ex = dal.correctness_col

    cat_vars_ex, data_df_ex = dal.get_correctness_by_cat_var()

    # by pass config output dir for testing
    output_dir_ex = "../output/avcat_test/"

    run(group_col_ex, cat_vars_ex, data_df_ex, score_col_ex, output_dir_ex)

    print("finished!")

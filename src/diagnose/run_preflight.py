"""
before an experiment is run, review metadata to see what can be analyzed.

:author: Tessa Johnson (tessa.johnson@geomdata.com)
:created: 2020
:copyright: (c) 2020, GDA
:license: see LICENSE for more details
"""

import argparse
import json
from diagnose.preflight import *
import diagnose.analysis_for_dep as chi2
import os


def main():
    """
    running the preflight analysis
    """

    # Load the config file, experimental data file, parts file, and output directory
    # from user input file location
    parser = argparse.ArgumentParser()

    parser.add_argument("path_to_metadata", help="metadata for a proposed experiment")
    parser.add_argument("output_dir", help="output directory")
    parser.add_argument("--ignore_cols", help='columns to ignore when running preflight check', nargs='*', default=None)

    args = parser.parse_args()
    path_to_metadata = args.path_to_metadata
    ignore_cols = args.ignore_cols
    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # ToDo: I feel like we might need to write another DAL and/or append to the current one for this, but I'm just going
    #  to assume you can normally import the data for now and we should add another issue and edit this later

    meta_df = pd.read_csv(path_to_metadata, dtype=object, comment="#", sep='\t', index_col=0)

    if ignore_cols is not None:
        meta_df.drop(columns=ignore_cols, inplace=True)

    results = {}

    # Checking which variables never vary

    var_nums, nonvar = check_varying_categories(meta_df)
    results.update({"analysis_of_static_categories": [{'static_variables': list(nonvar),
                                                       'num_unique_cat_per_var': var_nums.to_dict()}]})

    # Checking how many replicates for variables that do vary
    replicates = get_num_replicates(meta_df)

    # reformat JSON because it formats incorrectly
    r = replicates.to_dict()

    for k in r.keys():
        r[", ".join(k)] = r.pop(k)

    results.update({"analysis_of_replicates": [{'num_replicates': r}]})

    # Checking Covered vs. missing combinations of variables
    perc, missing = get_covered_combinations(meta_df)
    results.update({"analysis_of_combination_coverage": [{'prop_poss_combos_covered': perc,
                                                          'missing_combos': [list(m) for m in missing]}]})

    # Only compute Chi-Squared Test for Dependence if there are missing combinations of variables

    if perc < 1:
        results.update({"chi2_test_results": "See Heatmaps and tsv files for output from chi-squared test for "
                                             "independence"})
        df = chi2.chi2_test(meta_df.columns, meta_df, 'all')
        df = chi2.multiple_testing_correction(df)
        chi2.plot_heatmap(meta_df.columns, df, output_dir, 'all')
        chi2.save_df('all', df, output_dir)

    f = os.path.join(output_dir, 'preflight_check.json')

    with open(f, 'w') as outfile:
        json.dump(results, outfile, indent=2)


if __name__ == '__main__':
    main()


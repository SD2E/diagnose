"""
run analysis of categorical, continous, and parts data

:author: anastasia deckard (anastasia.deckard@geomdata.com)
:created: 2019
:copyright: (c) 2020, GDA
:license: see LICENSE for more details
"""

import os
from datetime import datetime
import argparse
import json
import shutil
import pandas as pd
import diagnose.analysis_var_cat as avcat
import diagnose.analysis_var_cont as avcont
import diagnose.analysis_for_dep as dep
import diagnose.make_record as rec


def make_sub_directory(output_dir):
    """
    Function to make an optional subdirectory based on the datetime and experiment name

    :param output_dir: output directory
    :return: out_dir: new output directory name
    """

    now = datetime.now()
    datetime_stamp = now.strftime('%Y%m%d%H%M%S')
    out_path = os.path.join(output_dir, "dd__{0:s}".format(datetime_stamp))
    print("making directory... ", out_path)
    if not os.path.exists(out_path):
        os.makedirs(out_path, exist_ok=True)

    return out_path


def main():
    """
    run analysis of categorical, continous, and parts data
    """

    # Load the config file, experimental data file, parts file, and output directory
    # from user input file location
    parser = argparse.ArgumentParser()

    parser.add_argument("--config_file", help="config file")
    parser.add_argument("--exp_file", help="path to data frame with variables and performance metric/score")
    parser.add_argument("--part_file", help="the path to the information of the parts of the logic gate",  default=None)
    parser.add_argument("--output_dir", help="output directory")
    parser.add_argument('-m', "--merge_files", help='if there is a separate metadata file, specify its location here')
    parser.add_argument("-n", "--no_sub_dir", help="do not make a subdirectory (not recommended except for reactor)",
                        action="store_true")

    args = parser.parse_args()
    config_file = args.config_file
    exp_file = args.exp_file
    part_file = args.part_file
    output_dir = args.output_dir
    merge_files = args.merge_files
    arg_no_sub_dir = args.no_sub_dir

    if part_file in ['none', 'None', 'NA']:
        part_file = None  # ToDo: Are we still doing the part analysis?

    dta_json = json.load(open(config_file))

    # set up vars
    groups = dta_json["group_ids"]
    score_col = dta_json["correctness_col"]
    cat_vars = dta_json["cat_vars"]
    cont_vars = dta_json["cont_vars"]
    sample_id = dta_json["sample_id"]
    if "invert_log10_score" in dta_json.keys():
        invert_log10_score = dta_json["invert_log10_score"]
    else:
        invert_log10_score = False

        # read data files
    data_df = pd.read_csv(exp_file, dtype=object, comment="#", sep='\t')
    data_df[score_col] = data_df[score_col].astype('float')

    if merge_files is not None:
        metadata_df = pd.read_csv(merge_files, dtype=object, comment="#")
        # keep all metadata, drop dupes from data
        data_keep = [sample_id] + list(data_df.columns.difference(metadata_df.columns))
        data_df = pd.merge(metadata_df, data_df[data_keep], on=sample_id)

    # clean up data a bit
    if invert_log10_score:
        new_score_col = "10^" + score_col
        data_df[new_score_col] = 10 ** data_df[score_col]
        score_col = new_score_col

    # keep only groups that have 2+ values to subset
    discard_groups = list()
    for group in groups:
        count = data_df[group].nunique()
        if count < 2:
            discard_groups.append(group)

    print('discarding groups with only one value:', discard_groups)
    groups = [x for x in groups if x not in discard_groups]

    # make a group called all, so we are sure to run all the samples together
    data_df['ALL'] = 'true'
    groups.append('ALL')

    # we can't do anything with records that have no score
    data_df = data_df.dropna(subset=[score_col])

    # discard variables that are not in the data set and log
    discard_cat_vars = list()
    for cat_var in cat_vars:
        if cat_var not in data_df.columns:
            discard_cat_vars.append(cat_var)
    print('discarding cat_vars not in data set:', discard_cat_vars)
    cat_vars = [x for x in cat_vars if x not in discard_cat_vars]

    discard_cont_vars = list()
    for cont_var in cont_vars:
        if cont_var not in data_df.columns:
            discard_cont_vars.append(cont_var)
    print('discarding cont_vars not in data set:', discard_cont_vars)
    cont_vars = [x for x in cont_vars if x not in discard_cont_vars]

    # make timestamped folder if there is supposed to be a subdirectory, copy config file to it
    if not arg_no_sub_dir:
        output_dir = make_sub_directory(output_dir)
    else:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

    shutil.copy(config_file, output_dir)

    saved_files = list()

    if exp_file is not None:
        for group_col in groups:
            # categorical variables analysis of variance ----------------------------
            print("\nanalyze categorical variables........")
            out_path_cat = os.path.join(output_dir, "avcat_" + group_col)
            if not os.path.exists(out_path_cat):
                os.makedirs(out_path_cat, exist_ok=True)

            # make cont->cat binned columns to test
            # but just for AV, don't use these in dependence testing
            cat_cont_data_df = data_df.copy(deep=True)
            cat_converted_vars = list()
            for cont_var in cont_vars:
                try:
                    cat_converted = cont_var + " BIN"
                    cat_cont_data_df[cat_converted] = pd.cut(cat_cont_data_df[cont_var].astype(float),
                                                             5).astype(str).str.strip('()[]')
                    cat_converted_vars.append(cat_converted)
                except ValueError as e:
                    print(cont_var, e)

            cat_cont_vars = cat_vars + cat_converted_vars

            # subset and run
            cols_to_keep = list(set([sample_id] + [score_col] + groups + cat_cont_vars))
            cat_cont_data_df = cat_cont_data_df[cols_to_keep]

            avcat_files = avcat.run(group_col, cat_cont_vars, cat_cont_data_df, score_col, out_path_cat)
            saved_files.extend(avcat_files)

            # categorical variables dependence test ----------------------------
            print("\ndependence test........")
            out_path_dep = out_path_cat + "/dependence"
            dep_files = dep.run(group_col, cat_vars, data_df, out_path_dep)
            saved_files.extend(dep_files)

            # continuous variables correlation ----------------------------
            print("\nanalyze continuous variables........")
            out_path_cont = os.path.join(output_dir, "avcont_" + group_col)
            if not os.path.exists(out_path_cont):
                os.makedirs(out_path_cont, exist_ok=True)

            cols_to_keep = list(set([sample_id] + [score_col] + groups + cont_vars))
            cont_data_df = data_df[cols_to_keep]

            cont_files = avcont.run(group_col, cont_vars, cont_data_df, score_col, out_path_cont)
            saved_files.extend(cont_files)

            # get files together for summarizing and hashing
            files = [{'name': x} for x in saved_files]

            # make hash for data sets
            print("hashing output...")
            files = rec.make_hashes_for_files(files)

            # make data record
            print("making product record...")
            record = rec.make_product_record(output_dir, files, exp_file, merge_files)

            record_path = os.path.join(output_dir, "record.json")
            with open(record_path, 'w') as json_file:
                json.dump(record, json_file, indent=2)

            print("finished!")


if __name__ == '__main__':
    main()


# ToDo: Is this deprecated?
# # part variables analysis of variance ------------------------------
# if dal.path_to_parts is not None:
#     print("\nanalyze part variables........")
#     out_path_part = os.path.join(out_path, "avpart")
#     if not os.path.exists(out_path_part):
#         os.makedirs(out_path_part, exist_ok=True)
#
#     cat_vars, parts_scores_df = dal.get_correctness_by_circuit_parts()
#
#     avpart.run(parts_scores_df, cat_vars, score_col, out_path_part)



# Diagnostic Tests for SD2 Experiments
This repository contains code for a variety of diagnostic tests for both experimental design 
and experimental performance. These look for variables that are associated with variations in performance, and identifies values of the variables associated with poor (or good) performance. Dependence between variables is also checked to identify variables that behave in a similar way.


## Quickstart
1. Install code and python requirements. See [Install](#install)
2. Edit configuration files to point to csv dataframe files for metadata and experiment output and parts lists, what performance metric to analyze, how to group variables, and what continuous and categorical variables to analyze, where to save output. See [Config File](#config-file) and [Input Data Frame Files](#input-dataframe-files)
3. Run code by using the runner:  
```python run_diagnosis.py "examples/example_diagnose_config.json"```  
See [Run](#Run)
4. Output will be stored in the output directory specified in the config, in a datetime stamped directory. Subdirectories are made for each analysis and group. 
  In the output files:
   * Analysis of variance tests report variables that vary with performance, and which values should be investigated first. 
   * Dependence tests report pairs of variables that appear to be related (same underlying variable or lack of randomization in experimental design).   
   See [Output](#output)
6. For more information on the output and statistical tests, see [Detailed Methods and Output](#detailed-methods-and-output)


## User Guide
### Install

**Option 1: Conda**: This installation method assumes that the user has conda previously installed on their 
computer. If you do not, you can choose to install conda with Miniconda or Anaconda 
[here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html).
```
cd diagnose
conda env create -f conda_env.yml
source activate sd2_gda_diagnose
pip install .
```

**Option 2: Docker**: This installation method assumes that users have docker previously installed on their computer.
If you do not, see the documentation [here](https://docs.docker.com/get-docker/).
```
cd diagnose
docker build . -t sd2_gda_diagnose
# if you want to enter the container to use the code
docker run --name diagnose -i -t  sd2_gda_diagnose
```


### Config File
example file: examples/example_diagnose_config.json

* "path_to_score_vars": path to data frame with variables and performance metric/score.  
* "path_to_parts": path to part listing from SBH.  

NOTE:  either path can be set to null to skip that type of analysis, e.g. `"path_to_parts": null,`
* "path_to_output_dir": path to output directory.  
* "correctness_col": what performance metric to analyze.  
* "group_ids": what variables to treat as groups. analysis will be run separately on each variable in each group.  
* "cat_vars": what categorical variables to analyze in the data frame (columns)  
* "cont_vars": what continuous variables to analyze in the data frame (columns)  

NOTES: 
* The software will determine if there are enough values to analyze for each variable. For automation/batches, it is better to list everything you would like to analyze and it will skip columns that only have one value in them.
* If you list a variable (column) that is not in the data, the software will skip it. For automation/batches, it is better to list all columns you might expect and let the software skip what doesn't exist in specific data sets.
* The software will automatically make one variable (column) to group all your samples together, so that it will analyze all your samples together, so you do not need to add another variable for this.
* For the categorical analysis, the program will also analyze binned continuous variables. It will make a new column for each continuous variable called "variable BIN" with the values in five bins.
* Any variables or valuables that can't be used for analysis will be logged to output.

### Input Dataframe Files
example files in: examples/data1.csv

* Variable and Performance Metric/Score File
  * csv
  * samples in rows
  * variables/metrics in columns
  * example: correctness.csv

* Parts File
  * json
  * example: strain_parts_results__nr_20190820.json
  
  
### Run
then you can run with: 

```python run_diagnosis.py "examples/example_diagnose_config.json"```


### Output
Output will be stored in the output directory specified in the config, in a datetime stamped directory.
* `perf_av_<date_time_stamp>`
    * `avcat_<group>`
       analysis of variance for categorical variables, one for each group.
       * smaller pval_corrected indicate that a variable varies with performance and values with low scores should be investigated first. 
       * depend: for dependence/randomization tests, the smaller pval_corrected for a pair of variables indicate that these variables appear to be related (depend) on one another, and might not need to be debugged separately or need to be tested separately.
    * `avcont_<group>`
       analysis of variance for continuous variables, one for each group
       * spearman correlation closer to 1 or -1 indicate that a variable varies with performance and should be investigated first. 
       * depend: spearman correlation closer to 1 or -1 for a pair of variables indicate that these variables appear to be related (depend) on one another, and might not need to be debugged separately or need to be tested separately.
    * `av_part`
       analysis of variance for parts
       * av: the smaller pval_corrected indicate that a variable varies with performance and values with low scores should be investigated first. 
    * `<diagnose_config>.json`
       copy of configuration file for the run
       
For more information on the output and statistical tests, see [Detailed Methods and Output](#detailed-methods-and-output)


# Detailed Methods and Output

## Performance Tests

*  Kruskal-Wallis H-test for Categorical Variables (av_cat)
    * **Code**: analysis_var_cat.py 
    
    * **Analysis**: Looks for variables that are associated with differences in performance. This completes non-parametric analysis of variance (i.e. a normal distribution of residual is not required) for the 
    categorical variables grouped by a user selected variable. We are assuming the the randomization test was run prior 
    to this test, so we will interpret results in this context. (Note: There are two p-values presented in the results, we recommend researchers utilized the corrected p-value because it controls for false discovery rate via the Benjamini & Hochber (1995) procedure.)
    
    * **Input**:  A dataframe with samples in rows and variables in columns. The columns associated with categorical variables 
        will be analyzed, and the user can group on a column name, e.g. group by gate to see performance per gate. different stakeholders will be interested in different in different groupings, like "lab", "strain_id", or "gate". 
        
    * **Output**:
        * avca_{group_name}_heatmap_{statistic}.png: Heatmaps for each p-value (lower values should be investigated first) and Kruskal-Wallace
        h-stat (higher values should be investigated first). The columns correspond to dependent variables and the row are the groups.
        One should interpret each block in the following manner: Within subgroup associated with the row, the variable
        associated with the row has a significant (or insignificant) effect on the performance variable.
        * avca_{group_name}_stats_var.tsv: Subset by each group within the column of interest, the kruskal-wallis
        h-stat and it's associated p-value is available. Statistical significance in this context is interpreted as 
        follows: All else held constant if the p-value is below 0.05 then at least one value of the variable is stochastically dominate
        over the other values - but it provides no information on which value in particular is of interest.
        * avca_{group_name}_stats_val.tsv: reports the significance of the variable, and also aggregate measures of samples for each value within the variable. e.g. the kw_pval shows that the variable "input" has significant differences in performance by variable, and reports the median performance for each value ("00", "01, "10", "11") of that variable.
        * avca_{group_name}_stats_val_CHECK.tsv: A subset of the avc_{group_name}_stats_val.tsv with specifically what 
        groups the researchers should be investigating as causes of poor performance.
        * avca_{group_name}_{group}_dist.png: For each group, a file of plots is output. For a group, a plot is made per variable and the plots are ordered from the variable having the most significant differences in performances to the least significant. The plots show the distributions in the performance score for eah value in the variable, e.g. variable "input" has values "00", "01, "10", "11". 
        * depend, see [Dependence Tests](#dependence-tests)
     
                
*  Spearman Correlation for Continuous Variables (av_co)
    * **Code**: analysis_var_cont.py 
    
    * **Analysis**: Looks for continuous variables that are associated with differences in performance. Uses spearman correlation to measure association between the performance variable and each continuous variable. 
    
    * **Input**:  A dataframe with samples in rows and variables in columns. The columns associated with continuous variables 
        will be analyzed, and the user can group on a column name, e.g. group by gate to see performance per gate. different stakeholders will be interested in different in different groupings, like "lab", "strain_id", or "gate". 
        
    * **Output**:
        * avco_stats_var.tsv: For each group, shows the spearman correlation between each continuous variable and the performance variable. Spearman values approaching 1 or -1 indicate that they correlate with the performance variable. THe spearman_abs is the absolute value so they can be sorted to show the strongest positive or negative correlations.
        * avco_{group_name}_{group}_scatter.png: For each group, a file of plots is output. For a group, a plot is made per variable and the plots are ordered from largest positive/negative correlation to smallest. 
        * avco_depend__{group}.tsv: measures the dependence between the continuous variables with each other. If two variables are highly correlated, indicating they are dependent (same underlying variable or lack of randomization in experimental design).
            
            
* Kruskal-Wallis H-test for Parts (av_part)
    * **Code**: analysis_var_parts.py 
    
    * **Analysis**: Looks for variables that are associated with differences in performance. Categorical variables exist for each part, and the values are whether the sample contains or does not contain the part. This completes non-parametric analysis of variance (i.e. a normal distribution of residual is not required) for the 
    categorical variables.  No grouping is performed, since parts should be examined across all samples. (Note: There are two p-values presented in the results, we recommend researchers utilized the corrected p-value because it controls for false discovery rate via the Benjamini & Hochberg (1995) procedure.)
    
    * **Input**:  A dataframe with samples in rows and variables in columns. The columns associated with categorical variables 
        will be analyzed.
        
    * **Output**:
        * avp_stats_var.tsv: The kruskal-wallis
        h-stat and it's associated p-value is available. Statistical significance in this context is interpreted as 
        follows: All else held constant if the p-value is below 0.05 then at least one group is stochastically dominate
        over the other groups - but it provides no information on which group in particular is of interest.
        * avp_stats_val.tsv: reports the significance of the variable, and also aggregate measures of samples for each value within the variable. e.g. the kw_pval shows that the variable for part "site:r6" shows significant differences in performance by variable, and reports the median performance for each value (y = has part "site:r6", n = does not have part "site:r6") of that variable.
        * avp_stats_val_CHECK.tsv: A subset of the avp_stats_val.tsv with specifically what 
        groups the researchers should be investigating as causes of poor performance.
        * avp_dist.png: A plot is made per variable and the plots are ordered from the variable having the most significant differences in performances to the least significant. The plots show the distributions in the performance score for eah value in the variable, e.g. variable "site:r6" has values y = has part "site:r6", n = does not have part "site:r6".
        
        
 ## Dependence Tests
This test provides information on whether or not your experiment was designed properly. It should 
be run prior to an experiment to ensure you can obtain the appropriate information on the variables
of interest, but can also be run post-hoc to determine what conclusions can be drawn from the data and/or if the 
experimental design should be revised for further iterations. (Note: Users can group by a column to analyze variation across categories within a group, however the test will also always output an analysis of all the data without any grouping that should always be viewed first. In particular, users should determine if the variable they wish to group by has a dependency with any other variable because the other tests will miss this effect.). 

* Randomization Test:
    * **Code**: chi2_indep_test.py 
    
    * **Analysis**: This test determines if the dependent variables were properly randomized by running a Chi-Squared 
    Test for Independence between all pairs of categorical features. If the experiment was properly 
    randomized then none of the pairs should be dependent. 
        * **Important Note**: This analysis is performed independent of the response variable and can provide zero
    information on performance of a circuit. This can only provide information on the experimental design which in turn
    can affect how the results ought to be interpreted.
    
    * **Input**:
        * A dataframe with samples in rows and variables in columns. The columns associated with categorical variables 
        will be analyzed, and the user can group on a column name, e.g. group by gate to see how randomized the 
        experiment was within groups.
        
    * **Output**:
        * **Note**: A multiple testing correction with Benjamini & Hochberg/Yekutieli false discovery 
        rate control procedure was done, so we present the corrected and uncorrected p-values & chi-squared values
        in our analysis
        * For each group in whatever column the user selected you obtain the following:
            * Heatmaps: {group_name}_{statistic}_heatmap.png for the p-value, corrected p-value, chi-squared, 
            corrected chi-squared statistics. (The p-value plots are much more informative and we suggest users view
            those unless you have prior understanding of the relationship between chi-squared distributions and degrees
            of freedom, i.e. the chi-squared value's meaning changes depending on the DOF). Pairs that have a low 
            p-value indicate statistical significance and suggest some issue with the experimental design because 
            hypothetically all predictors should be independent.
            * Tables:
                * {group_name}_chi_squared_independence_test.tsv: table with the pairs of categorical variables and the 
                results of their chi-squared test for independence (with and without the FDR correction). The 
                chi-squared values (with and without the FDR correction), degrees of freedom, p-values (with and 
                without the FDR correction), and conclusion from the hypothesis test are recorded. 
                    * DOF determines how heavy the tails of the chi-squared distribution is, i.e. if you have high DOF
                    and high chi-squared values then likely you have a robust statistical significance results. However,
                    one should not directly compare the chi-squared statistics since they do not actually correspond to 
                    the same distribution
                    * P-Value: Anything below 0.01 is considered statistical significant and is of interest to 
                    researchers
                * {group_name}_CHECK.tsv: This table has the same information as the above table, but is subset to only
                include combinations with a p-value of 0. This is then sorted by degrees of freedom and chi-squared
                values (i.e. to show the most robust and significant results first) to present the combinations 
                that should be examined by researchers. Additionally, when using the tests for the next section 
                researchers should be aware that if the experiment wasn't properly randomized then there will be an
                identifiability issue with main effects, i.e. you may not be able to identify which variable is actually
                having an effect the response.       
        
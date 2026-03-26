# Custom Code in Automation Designer

## 5-parameter-logistic

Example snippet fits a 5-Parameter Logistic (5PL) curve to dose-response data to extract EC50, Hill slope, and asymmetry, with AIC comparison against a standard 4PL fit and an interactive plot with residuals subplot.

- **[Input File](./snippets/5-parameter-logistic/docs/input/dose_response_5pl_data.xlsx)**
- **[Custom Code Block](./snippets/5-parameter-logistic/dose_response_5pl.py)**
- **[Output Files](./snippets/5-parameter-logistic/docs/output)**

## kinetic-timecourse

Example snippet fits one-phase association kinetic curves per compound to extract parameters (Emax, kobs, t½, AUC, R²), with t-test comparison at the inflection point and a multi-compound time-course plot with 95% CI ribbons.

- **[Input File](./snippets/kinetic-timecourse/docs/input/timecourse_data.xlsx)**
- **[Custom Code Block](./snippets/kinetic-timecourse/kinetics_timecourse.py)**
- **[Output Files](./snippets/kinetic-timecourse/docs/output)**

## multi-group-anova

Example snippet performs one-way ANOVA to test for significant differences across treatment groups, followed by Tukey HSD post-hoc analysis for pairwise comparisons, with descriptive statistics and an annotated bar chart output.

- **[Input File](./snippets/multi-group-anova/docs/input/multigroup_efficacy_data.xlsx)**
- **[Custom Code Block](./snippets/multi-group-anova/multigroup_anova.py)**
- **[Output Files](./snippets/multi-group-anova/docs/output)**

## plot-chromatogram

Example snippet demonstrates plotting a multi-axis HPLC chromatogram (retention volume X Absorbance (mAU), Temperature (degC), pH) with custom code.

![image info](./snippets/plot-chromatogram/docs/Example_Chromatogram_Plot.gif)

- **[Input File](./snippets/plot-chromatogram/docs/input/HPLC_Chromtogram_Plot%20(Absorbance,%20pH,%20Temperature).csv)**
- **[Custom Code Block](./snippets/plot-chromatogram/HPLC_Chromatogram_Plot_(Absorbance,%20pH,%20Temperature).py)**
- **[Output File](./snippets/plot-chromatogram/docs/output/Chromatogram_New.png)**

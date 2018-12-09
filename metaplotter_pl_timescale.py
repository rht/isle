import matplotlib.pyplot as plt
import numpy as np
import pdb
import os
import time
import glob

from metaplotter import read_data


def plotting(output_label, timeseries_dict, riskmodelsetting1, riskmodelsetting2, series1, series2=None, additionalriskmodelsetting3=None, additionalriskmodelsetting4=None, plottype1="mean", plottype2="mean", labels=None):
    # dictionaries
    colors = {"one": "red", "two": "blue", "three": "green", "four": "yellow"}
    if labels is None:
        labels = {"profitslosses": "Profits and Losses (Insurer)", "contracts": "Contracts (Insurers)", "cash": "Liquidity (Insurers)", "operational": "Active Insurers", "premium": "Premium", "reinprofitslosses": "Profits and Losses (Reinsurer)", "reincash": "Liquidity (Reinsurers)", "reincontracts": "Contracts (Reinsurers)", "reinoperational": "Active Reinsurers"}
    
    # prepare labels, timeseries, etc.
    color1 = colors[riskmodelsetting1]
    color2 = colors[riskmodelsetting2]
    label1 = str.upper(riskmodelsetting1[0]) + riskmodelsetting1[1:] + " riskmodels"
    label2 = str.upper(riskmodelsetting2[0]) + riskmodelsetting2[1:] + " riskmodels"
    plot_1_1 = "data/" + riskmodelsetting1 + "_" + series1 + ".dat"
    plot_1_2 = "data/" + riskmodelsetting2 + "_" + series1 + ".dat"
    if series2 is not None:
        plot_2_1 = "data/" + riskmodelsetting1 + "_" + series2 + ".dat"
        plot_2_2 = "data/" + riskmodelsetting2 + "_" + series2 + ".dat"
    if additionalriskmodelsetting3 is not None:
        color3 = colors[additionalriskmodelsetting3]
        label3 = str.upper(additionalriskmodelsetting3[0]) + additionalriskmodelsetting3[1:] + " riskmodels"
        plot_1_3 = "data/" + additionalriskmodelsetting3 + "_" + series1 + ".dat"
        if series2 is not None:
            plot_2_3 = "data/" + additionalriskmodelsetting3 + "_" + series2 + ".dat"
    if additionalriskmodelsetting4 is not None:
        color4 = colors[additionalriskmodelsetting4]
        label4 = str.upper(additionalriskmodelsetting4[0]) + additionalriskmodelsetting4[1:] + " riskmodels"
        plot_1_4 = "data/" + additionalriskmodelsetting4 + "_" + series1 + ".dat"
        if series2 is not None:
            plot_2_4 = "data/" + additionalriskmodelsetting4 + "_" + series2 + ".dat"
    
    # Backup existing figures (so as not to overwrite them)
    outputfilename = "data/" + output_label + ".pdf"
    backupfilename = "data/" + output_label + "_old_" + time.strftime('%Y_%b_%d_%H_%M') + ".pdf"
    if os.path.exists(outputfilename):
        os.rename(outputfilename, backupfilename)
    
    # Plot and save
    fig = plt.figure()
    if series2 is not None:
        ax0 = fig.add_subplot(211)
    else:
        ax0 = fig.add_subplot(111)
    maxlen_plots = 0
    if additionalriskmodelsetting3 is not None:
        ax0.plot(range(len(timeseries_dict[plottype1][plot_1_3]))[200:], timeseries_dict[plottype1][plot_1_3][200:], color=color3, label=label3)
        maxlen_plots = max(maxlen_plots, len(timeseries_dict[plottype1][plot_1_3]))
    if additionalriskmodelsetting4 is not None:
        ax0.plot(range(len(timeseries_dict[plottype1][plot_1_4]))[200:], timeseries_dict[plottype1][plot_1_4][200:], color=color4, label=label4)   
        maxlen_plots = max(maxlen_plots, len(timeseries_dict[plottype1][plot_1_4]))
    ax0.plot(range(len(timeseries_dict[plottype1][plot_1_1]))[200:], timeseries_dict[plottype1][plot_1_1][200:], color=color1, label=label1)
    ax0.plot(range(len(timeseries_dict[plottype1][plot_1_2]))[200:], timeseries_dict[plottype1][plot_1_2][200:], color=color2, label=label2)
    ax0.fill_between(range(len(timeseries_dict["quantile25"][plot_1_1]))[200:], timeseries_dict["quantile25"][plot_1_1][200:], timeseries_dict["quantile75"][plot_1_1][200:], facecolor=color1, alpha=0.25)
    ax0.fill_between(range(len(timeseries_dict["quantile25"][plot_1_1]))[200:], timeseries_dict["quantile25"][plot_1_2][200:], timeseries_dict["quantile75"][plot_1_2][200:], facecolor=color2, alpha=0.25)
    ax0.set_ylabel(labels[series1])#"Contracts")
    maxlen_plots = max(maxlen_plots, len(timeseries_dict[plottype1][plot_1_1]), len(timeseries_dict[plottype1][plot_1_2]))
    xticks =  np.arange(200, maxlen_plots, step=120)
    ax0.set_xticks(xticks)
    ax0.set_xticklabels(["${0:d}$".format(int((xtc-200)/12)) for xtc in xticks]);

    ax0.legend(loc='best')
    if series2 is not None:
        ax1 = fig.add_subplot(212)
        maxlen_plots = 0
        if additionalriskmodelsetting3 is not None:
            ax1.plot(range(len(timeseries_dict[plottype2][plot_2_3]))[200:], timeseries_dict[plottype2][plot_2_3][200:], color=color3, label=label3)
            maxlen_plots = max(maxlen_plots, len(timeseries_dict[plottype1][plot_2_3]))
        if additionalriskmodelsetting4 is not None:
            ax1.plot(range(len(timeseries_dict[plottype2][plot_2_4]))[200:], timeseries_dict[plottype2][plot_2_4][200:], color=color4, label=label4)   
            maxlen_plots = max(maxlen_plots, len(timeseries_dict[plottype1][plot_2_4]))
        ax1.plot(range(len(timeseries_dict[plottype2][plot_2_1]))[200:], timeseries_dict[plottype2][plot_2_1][200:], color=color1, label=label1)
        ax1.plot(range(len(timeseries_dict[plottype2][plot_2_2]))[200:], timeseries_dict[plottype2][plot_2_2][200:], color=color2, label=label2)
        ax1.fill_between(range(len(timeseries_dict["quantile25"][plot_2_1]))[200:], timeseries_dict["quantile25"][plot_2_1][200:], timeseries_dict["quantile75"][plot_2_1][200:], facecolor=color1, alpha=0.25)
        ax1.fill_between(range(len(timeseries_dict["quantile25"][plot_2_1]))[200:], timeseries_dict["quantile25"][plot_2_2][200:], timeseries_dict["quantile75"][plot_2_2][200:], facecolor=color2, alpha=0.25)
        maxlen_plots = max(maxlen_plots, len(timeseries_dict[plottype1][plot_2_1]), len(timeseries_dict[plottype1][plot_2_2]))
        xticks =  np.arange(200, maxlen_plots, step=120)
        ax1.set_xticks(xticks)
        ax1.set_xticklabels(["${0:d}$".format(int((xtc-200)/12)) for xtc in xticks]);
        ax1.set_ylabel(labels[series2])
        ax1.set_xlabel("Years")
    else:
        ax0.set_xlabel("Years")
    plt.savefig(outputfilename)
    plt.show()

timeseries = read_data()

## for just two different riskmodel settings
#plotting(output_label="fig_pl_survival_1_2", timeseries_dict=timeseries, riskmodelsetting1="one", \
#    riskmodelsetting2="two", series1="profitslosses", series2="operational", plottype1="mean", plottype2="median")
#plotting(output_label="fig_reinsurers_pl_survival_1_2", timeseries_dict=timeseries, riskmodelsetting1="one", \
#    riskmodelsetting2="two", series1="reinprofitslosses", series2="reinoperational", plottype1="mean", plottype2="median")
#plotting(output_label="fig_premium_1_2", timeseries_dict=timeseries, riskmodelsetting1="one", riskmodelsetting2="two", \
#    series1="premium", series2=None, plottype1="mean", plottype2=None)
#
#raise SystemExit
# for four different riskmodel settings
plotting(output_label="fig_pl_survival_1_2", timeseries_dict=timeseries, riskmodelsetting1="one", \
        riskmodelsetting2="two", series1="profitslosses", series2="operational", additionalriskmodelsetting3="three", \
        additionalriskmodelsetting4="four", plottype1="mean", plottype2="median")
plotting(output_label="fig_pl_survival_3_4", timeseries_dict=timeseries, riskmodelsetting1="three", \
        riskmodelsetting2="four", series1="profitslosses", series2="operational",  additionalriskmodelsetting3="one", \
        additionalriskmodelsetting4="two", plottype1="mean", plottype2="median")
plotting(output_label="fig_reinsurers_pl_survival_1_2", timeseries_dict=timeseries, riskmodelsetting1="one", \
        riskmodelsetting2="two", series1="reinprofitslosses", series2="reinoperational", \
        additionalriskmodelsetting3="three", additionalriskmodelsetting4="four", plottype1="mean", plottype2="median")
plotting(output_label="fig_reinsurers_pl_survival_3_4", timeseries_dict=timeseries, riskmodelsetting1="three", \
        riskmodelsetting2="four", series1="reinprofitslosses", series2="reinoperational", \
        additionalriskmodelsetting3="one", additionalriskmodelsetting4="two", plottype1="mean", plottype2="median")
plotting(output_label="fig_premium_1_2", timeseries_dict=timeseries, riskmodelsetting1="one", riskmodelsetting2="two", \
        series1="premium", series2=None, additionalriskmodelsetting3="three", additionalriskmodelsetting4="four", \
        plottype1="mean", plottype2=None)

#pdb.set_trace()

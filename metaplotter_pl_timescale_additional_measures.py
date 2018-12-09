import matplotlib.pyplot as plt
import numpy as np
import pdb
import os
import time
import glob

from metaplotter import read_data
from metaplotter_pl_timescale import plotting as _plotting


def plotting(output_label, timeseries_dict, riskmodelsetting1, riskmodelsetting2, series1, series2=None, additionalriskmodelsetting3=None, additionalriskmodelsetting4=None, plottype1="mean", plottype2="mean"):
    labels = {"reinexcess_capital": "Excess Capital (Reinsurers)", "excess_capital": "Excess Capital (Insurers)", "cumulative_unrecovered_claims": "Uncovered Claims (cumulative)", "cumulative_bankruptcies": "Bankruptcies (cumulative)", "profitslosses": "Profits and Losses (Insurer)", "contracts": "Contracts (Insurers)", "cash": "Liquidity (Insurers)", "operational": "Active Insurers", "premium": "Premium", "reinprofitslosses": "Profits and Losses (Reinsurer)", "reincash": "Liquidity (Reinsurers)", "reincontracts": "Contracts (Reinsurers)", "reinoperational": "Active Reinsurers"}
    _plotting(output_label, timeseries_dict, riskmodelsetting1, riskmodelsetting2, series1, series2, additionalriskmodelsetting3, additionalriskmodelsetting4, plottype1, plottype2, labels=labels)

timeseries = read_data()

# for just two different riskmodel settings
#plotting(output_label="fig_pl_excap_1_2", timeseries_dict=timeseries, riskmodelsetting1="one", \
#    riskmodelsetting2="two", series1="profitslosses", series2="excess_capital", plottype1="mean", plottype2="mean")
#plotting(output_label="fig_reinsurers_pl_excap_1_2", timeseries_dict=timeseries, riskmodelsetting1="one", \
#    riskmodelsetting2="two", series1="reinprofitslosses", series2="reinexcess_capital", plottype1="mean", plottype2="mean")
#plotting(output_label="fig_bankruptcies_unrecovered_claims_1_2", timeseries_dict=timeseries, riskmodelsetting1="one", \
#    riskmodelsetting2="two", series1="cumulative_bankruptcies", series2="cumulative_unrecovered_claims", plottype1="mean", plottype2="median")
#plotting(output_label="fig_premium_1_2", timeseries_dict=timeseries, riskmodelsetting1="one", riskmodelsetting2="two", \
#    series1="premium", series2=None, plottype1="mean", plottype2=None)
#
#raise SystemExit
# for four different riskmodel settings
plotting(output_label="fig_pl_excap_1_2", timeseries_dict=timeseries, riskmodelsetting1="one", \
    riskmodelsetting2="two", series1="profitslosses", series2="excess_capital", additionalriskmodelsetting3="three", \
        additionalriskmodelsetting4="four", plottype1="mean", plottype2="mean")
plotting(output_label="fig_reinsurers_pl_excap_1_2", timeseries_dict=timeseries, riskmodelsetting1="one", \
    riskmodelsetting2="two", series1="reinprofitslosses", series2="reinexcess_capital", additionalriskmodelsetting3="three", \
        additionalriskmodelsetting4="four", plottype1="mean", plottype2="mean")
plotting(output_label="fig_bankruptcies_unrecovered_claims_1_2", timeseries_dict=timeseries, riskmodelsetting1="one", \
    riskmodelsetting2="two", series1="cumulative_bankruptcies", series2="cumulative_unrecovered_claims", additionalriskmodelsetting3="three", \
        additionalriskmodelsetting4="four", plottype1="mean", plottype2="median")
plotting(output_label="fig_premium_1_2", timeseries_dict=timeseries, riskmodelsetting1="one", riskmodelsetting2="two", \
    series1="premium", series2=None, additionalriskmodelsetting3="three", additionalriskmodelsetting4="four", plottype1="mean", plottype2=None)

plotting(output_label="fig_pl_excap_3_4", timeseries_dict=timeseries, riskmodelsetting1="three", \
    riskmodelsetting2="four", series1="profitslosses", series2="excess_capital", additionalriskmodelsetting3="one", \
        additionalriskmodelsetting4="two", plottype1="mean", plottype2="mean")
plotting(output_label="fig_reinsurers_pl_excap_3_4", timeseries_dict=timeseries, riskmodelsetting1="three", \
    riskmodelsetting2="four", series1="reinprofitslosses", series2="reinexcess_capital", additionalriskmodelsetting3="one", \
        additionalriskmodelsetting4="two", plottype1="mean", plottype2="mean")
plotting(output_label="fig_bankruptcies_unrecovered_claims_3_4", timeseries_dict=timeseries, riskmodelsetting1="three", \
    riskmodelsetting2="four", series1="cumulative_bankruptcies", series2="cumulative_unrecovered_claims", additionalriskmodelsetting3="one", \
        additionalriskmodelsetting4="two", plottype1="mean", plottype2="median")
plotting(output_label="fig_premium_3_4", timeseries_dict=timeseries, riskmodelsetting1="three", riskmodelsetting2="four", \
    series1="premium", series2=None, additionalriskmodelsetting3="one", additionalriskmodelsetting4="two", plottype1="mean", plottype2=None)


#pdb.set_trace()

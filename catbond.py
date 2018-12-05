
import isleconfig
import numpy as np
import scipy.stats
from insurancecontract import InsuranceContract
from reinsurancecontract import ReinsuranceContract
from metainsuranceorg import MetaInsuranceOrg
from riskmodel import RiskModel
import sys, pdb
import uuid

class CatBond(MetaInsuranceOrg):
    def init(self, simulation, per_period_premium, owner, interest_rate = 0):   # do we need simulation parameters
        self.simulation = simulation
        self.id = 0
        self.underwritten_contracts = []
        self.cash = 0
        self.profits_losses = 0
        self.obligations = []
        self.operational = True
        self.owner = owner
        self.per_period_dividend = per_period_premium
        self.interest_rate = interest_rate  # TODO: shift obtain_yield method to insurancesimulation, thereby making it unnecessary to drag parameters like self.interest_rate from instance to instance and from class to class
        #self.simulation_no_risk_categories = self.simulation.simulation_parameters["no_categories"]
    
    # TODO: change start and InsuranceSimulation so that it iterates CatBonds
    #old parent class init, cat bond class should be much smaller
    def parent_init(self, simulation_parameters, agent_parameters):
        #def init(self, simulation_parameters, agent_parameters):
        self.simulation = simulation_parameters['simulation']
        self.simulation_parameters = simulation_parameters
        self.contract_runtime_dist = scipy.stats.randint(simulation_parameters["mean_contract_runtime"] - \
                  simulation_parameters["contract_runtime_halfspread"], simulation_parameters["mean_contract_runtime"] \
                  + simulation_parameters["contract_runtime_halfspread"] + 1)
        self.default_contract_payment_period = simulation_parameters["default_contract_payment_period"]
        self.id = agent_parameters['id']
        self.cash = agent_parameters['initial_cash']
        self.premium = agent_parameters["norm_premium"]
        self.profit_target = agent_parameters['profit_target']
        self.acceptance_threshold = agent_parameters['initial_acceptance_threshold']  # 0.5
        self.acceptance_threshold_friction = agent_parameters['acceptance_threshold_friction']  # 0.9 #1.0 to switch off
        self.interest_rate = agent_parameters["interest_rate"]
        self.reinsurance_limit = agent_parameters["reinsurance_limit"]
        self.simulation_no_risk_categories = simulation_parameters["no_categories"]
        self.simulation_reinsurance_type = simulation_parameters["simulation_reinsurance_type"]
        
        rm_config = agent_parameters['riskmodel_config']
        self.riskmodel = RiskModel(damage_distribution=rm_config["damage_distribution"], \
                                     expire_immediately=rm_config["expire_immediately"], \
                                     cat_separation_distribution=rm_config["cat_separation_distribution"], \
                                     norm_premium=rm_config["norm_premium"], \
                                     category_number=rm_config["no_categories"], \
                                     init_average_exposure=rm_config["risk_value_mean"], \
                                     init_average_risk_factor=rm_config["risk_factor_mean"], \
                                     init_profit_estimate=rm_config["norm_profit_markup"], \
                                     margin_of_safety=rm_config["margin_of_safety"], \
                                     var_tail_prob=rm_config["var_tail_prob"], \
                                     inaccuracy=rm_config["inaccuracy_by_categ"])
        
        self.category_reinsurance = [None for i in range(self.simulation_no_risk_categories)]
        if self.simulation_reinsurance_type == 'non-proportional':
            self.np_reinsurance_deductible_fraction = simulation_parameters["default_non-proportional_reinsurance_deductible"]
            self.np_reinsurance_excess_fraction = simulation_parameters["default_non-proportional_reinsurance_excess"]
            self.np_reinsurance_premium_share = simulation_parameters["default_non-proportional_reinsurance_premium_share"]
        self.obligations = []
        self.underwritten_contracts = []
        #self.reinsurance_contracts = []
        self.operational = True
        self.is_insurer = True
        self.is_reinsurer = False
        
        """set up risk value estimate variables"""
        self.var_counter = 0                # sum over risk model inaccuracies for all contracts
        self.var_counter_per_risk = 0       # average risk model inaccuracy across contracts
        self.var_sum = 0                    # sum over initial VaR for all contracts
        self.counter_category = np.zeros(self.simulation_no_risk_categories)    # var_counter disaggregated by category
        self.var_category = np.zeros(self.simulation_no_risk_categories)        # var_sum disaggregated by category

    def iterate(self, time):
        """obtain investments yield"""
        self.obtain_yield(time)

        """realize due payments"""
        self.effect_payments(time)
        if isleconfig.verbose:
            print(time, ":", self.id, len(self.underwritten_contracts), self.cash, self.operational)
            
            """mature contracts"""
            print("Number of underwritten contracts ", len(self.underwritten_contracts))
        maturing = [contract for contract in self.underwritten_contracts if contract.expiration <= time]
        for contract in maturing:
            self.underwritten_contracts.remove(contract)
            contract.mature(time)
        contracts_dissolved = len(maturing)

        """effect payments from contracts"""
        [contract.check_payment_due(time) for contract in self.underwritten_contracts]
        
        if self.underwritten_contracts == []:
            self.mature_bond()  #TODO: mature_bond method should check if operational
            
        else:   #TODO: dividend should only be payed according to pre-arranged schedule, and only if no risk events have materialized so far
            if self.operational:
                self.pay_dividends(time)

        #self.estimated_var()   # cannot compute VaR for catbond as catbond does not have a riskmodel
   
    def set_owner(self, owner):
        self.owner = owner
        if isleconfig.verbose:
            print("SOLD")
        #pdb.set_trace()
    
    def set_contract(self, contract):
        self.underwritten_contracts.append(contract)
    
    def mature_bond(self):
        obligation = {"amount": self.cash, "recipient": self.simulation, "due_time": 1, "purpose": 'mature'}
        self.pay(obligation)
        self.simulation.delete_agents("catbond", [self])
        self.operational = False



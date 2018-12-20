# import common packages
import numpy as np
import scipy.stats
import math
import sys, pdb
import argparse
import os
import pickle
import hashlib
import random
import copy
import importlib

# import config file and apply configuration
import isleconfig

simulation_parameters = isleconfig.simulation_parameters
replic_ID = None
override_no_riskmodels = False

from insurancesimulation import InsuranceSimulation
from agents.insurancefirm import InsuranceFirm
from riskmodel import RiskModel
from reinsurancefirm import ReinsuranceFirm
import logger
import calibrationscore
    
# ensure that logging directory exists
if not os.path.isdir("data"):
    assert not os.path.exists("data"), "./data exists as regular file. This filename is required for the logging directory"
    os.makedirs("data")

# create conditional decorator
def conditionally(decorator_function, condition):
    def wrapper(target_function):
        if not condition:
            return target_function
        return decorator_function(target_function)
    return wrapper

# create non-abce placeholder gui decorator
# TODO: replace this with more elegant solution if possible. Currently required since script will otherwise crash at the conditional decorator below since gui is then undefined
if not isleconfig.use_abce:
    def gui(*args, **kwargs):
        pass


# main function

#@gui(simulation_parameters, serve=True)
@conditionally(gui(simulation_parameters, serve=False), isleconfig.use_abce)
def main(simulation_parameters, rc_event_schedule, rc_event_damage, np_seed, random_seed, save_iter):

    np.random.seed(np_seed)
    random.seed(random_seed)

    # create simulation and world objects (identical in non-abce mode)
    if isleconfig.use_abce:
        simulation = abce.Simulation(processes=1,random_seed = random_seed)

    simulation_parameters['simulation'] = world = InsuranceSimulation(override_no_riskmodels, replic_ID, simulation_parameters, rc_event_schedule, rc_event_damage)

    if not isleconfig.use_abce:
        simulation = world
    
    # create agents: insurance firms 
    insurancefirms_group = simulation.build_agents(InsuranceFirm,
                                             'insurancefirm',
                                             parameters=simulation_parameters,
                                             agent_parameters=world.agent_parameters["insurancefirm"])
    
    if isleconfig.use_abce:
        insurancefirm_pointers = insurancefirms_group.get_pointer()
    else:
        insurancefirm_pointers = insurancefirms_group
    world.accept_agents("insurancefirm", insurancefirm_pointers, insurancefirms_group)

    # create agents: reinsurance firms 
    reinsurancefirms_group = simulation.build_agents(ReinsuranceFirm,
                                               'reinsurance',
                                               parameters=simulation_parameters,
                                               agent_parameters=world.agent_parameters["reinsurance"])
    if isleconfig.use_abce:
        reinsurancefirm_pointers = reinsurancefirms_group.get_pointer()
    else:
        reinsurancefirm_pointers = reinsurancefirms_group
    world.accept_agents("reinsurance", reinsurancefirm_pointers, reinsurancefirms_group)
    
    # time iteration
    for t in range(simulation_parameters["max_time"]):
        
        # abce time step
        simulation.advance_round(t)
        
        # create new agents             # TODO: write method for this; this code block is executed almost identically 4 times
        if world.insurance_firm_market_entry(agent_type="InsuranceFirm"):
            parameters = [np.random.choice(world.agent_parameters["insurancefirm"])]
            parameters = [world.agent_parameters["insurancefirm"][simulation.insurance_entry_index()]]
            parameters[0]["id"] = world.get_unique_insurer_id()
            new_insurance_firm = simulation.build_agents(InsuranceFirm,
                                             'insurancefirm',
                                             parameters=simulation_parameters,
                                             agent_parameters=parameters)
            insurancefirms_group += new_insurance_firm
            if isleconfig.use_abce:
                # TODO: fix abce
                # may fail in abce because addressing individual agents may not be allowed
                # may also fail because agent methods may not be callable directly
                new_insurancefirm_pointer = [new_insurance_firm[0].get_pointer()]        # index 0 because this is a list with just 1 object
            else:
                new_insurancefirm_pointer = new_insurance_firm
            world.accept_agents("insurancefirm", new_insurancefirm_pointer, new_insurance_firm, time=t)
        
        if world.insurance_firm_market_entry(agent_type="ReinsuranceFirm"):
            parameters = [np.random.choice(world.agent_parameters["reinsurance"])]
            parameters[0]["initial_cash"] = world.reinsurance_capital_entry()     #Since the value of the reinrisks varies overtime it makes sense that the market entry of reinsures depends on those values. The method world.reinsurance_capital_entry() determines the capital market entry of reinsurers.
            parameters = [world.agent_parameters["reinsurance"][simulation.reinsurance_entry_index()]]
            parameters[0]["id"] = world.get_unique_reinsurer_id()
            new_reinsurance_firm = simulation.build_agents(ReinsuranceFirm,
                                             'reinsurance',
                                             parameters=simulation_parameters,
                                             agent_parameters=parameters)
            reinsurancefirms_group += new_reinsurance_firm
            if isleconfig.use_abce:
                # TODO: fix abce
                # may fail in abce because addressing individual agents may not be allowed
                # may also fail because agent methods may not be callable directly
                new_reinsurancefirm_pointer = [new_reinsurance_firm[0].get_pointer()]        # index 0 because this is a list with just 1 object
            else:
                new_reinsurancefirm_pointer = new_reinsurance_firm
            world.accept_agents("reinsurance", new_reinsurancefirm_pointer, new_reinsurance_firm, time=t)
        
        # iterate simulation
        world.iterate(t)
        
        # log data
        if isleconfig.use_abce:
            #insurancefirms.logme()
            #reinsurancefirms.logme()
            insurancefirms_group.agg_log(variables=['cash', 'operational'], len=['underwritten_contracts'])
            #reinsurancefirms_group.agg_log(variables=['cash'])
        else:
            world.save_data()
        
        if t%50 == save_iter:
            save_simulation(t, simulation, simulation_parameters, exit_now=False)
    
    # finish simulation, write logs
    simulation.finalize()

    return simulation.obtain_log()    #It is required to return this list to download all the data generated by a single run of the model from the cloud.

# save function
def save_simulation(t, sim, sim_param, exit_now=False):
    d = {}
    d["np_seed"] = np.random.get_state()
    d["random_seed"] = random.getstate()
    d["time"] = t
    d["simulation"] = sim
    d["simulation_parameters"] = sim_param
    with open("data/simulation_save.pkl", "bw") as wfile:
        pickle.dump(d, wfile, protocol=pickle.HIGHEST_PROTOCOL)
    with open("data/simulation_save.pkl", "br") as rfile:
        file_contents = rfile.read()
    #print("\nSimulation hashes: ", hashlib.sha512(str(d).encode()).hexdigest(), "; ",  hashlib.sha512(str(file_contents).encode()).hexdigest())
    # note that the hash over the dict is for some reason not identical between runs. The hash over the state saved to the file is.
    print("\nSimulation hash: ",  hashlib.sha512(str(file_contents).encode()).hexdigest())
    if exit_now:
        exit(0)

# main entry point
if __name__ == "__main__":

    """ use argparse to handle command line arguments"""
    parser = argparse.ArgumentParser(description='Model the Insurance sector')
    parser.add_argument("--abce", action="store_true", help="use abce")
    parser.add_argument("--oneriskmodel", action="store_true",
                        help="allow overriding the number of riskmodels from the standard config (with 1)")
    parser.add_argument("--riskmodels", type=int, choices=[1, 2, 3, 4],
                        help="allow overriding the number of riskmodels from standard config (with 1 or other numbers)")
    parser.add_argument("--replicid", type=int,
                        help="if replication ID is given, pass this to the simulation so that the risk profile can be restored")
    parser.add_argument("--replicating", action="store_true",
                        help="if this is a simulation run designed to replicate another, override the config file parameter")
    parser.add_argument("--randomseed", type=float, help="allow setting of numpy random seed")
    parser.add_argument("--foreground", action="store_true",
                        help="force foreground runs even if replication ID is given (which defaults to background runs)")
    parser.add_argument("--shownetwork", action="store_true", help="show reinsurance relations as network")
    parser.add_argument("-p", "--showprogress", action="store_true", help="show timesteps")
    parser.add_argument("-v", "--verbose", action="store_true", help="more detailed output")
    parser.add_argument("--save_iterations", type=int, help="number of iterations to iterate before saving world state")
    args = parser.parse_args()

    if args.abce:
        isleconfig.use_abce = True
    if args.oneriskmodel:
        isleconfig.oneriskmodel = True
        override_no_riskmodels = 1
    if args.riskmodels:
        override_no_riskmodels = args.riskmodels
    if args.replicid is not None:
        replic_ID = args.replicid
    if args.replicating:
        isleconfig.replicating = True
        assert replic_ID is not None, "Error: Replication requires a replication ID to identify run to be replicated"
    if args.randomseed:
        randomseed = args.randomseed
        seed = int(randomseed)
    else:
        np.random.seed()
        seed = np.random.randint(0, 2 ** 31 - 1)
    if args.foreground:
        isleconfig.force_foreground = True
    if args.shownetwork:
        isleconfig.show_network = True
        """Option requires reloading of InsuranceSimulation so that modules to show network can be loaded.
            # TODO: change all module imports of the form "from module import class" to "import module". """   
        import insurancesimulation
        importlib.reload(insurancesimulation)
        from insurancesimulation import InsuranceSimulation
    if args.showprogress:
        isleconfig.showprogress = True
    if args.verbose:
        isleconfig.verbose = True
    if args.save_iterations:
        save_iter = args.save_iterations
    else:
        save_iter = 200

    """ import abce module if required """
    if isleconfig.use_abce:
        # print("Importing abce")
        import abce
        from abce import gui
    
    from setup import SetupSim
    setup = SetupSim()       #Here the setup for the simulation is done.
    [general_rc_event_schedule, general_rc_event_damage, np_seeds, random_seeds] = setup.obtain_ensemble(1)   #Only one ensemble. This part will only be run locally (laptop).

    log = main(simulation_parameters, general_rc_event_schedule[0], general_rc_event_damage[0], np_seeds[0], random_seeds[0], save_iter)
    
    """ Restore the log at the end of the single simulation run for saving and for potential further study """
    L = logger.Logger()
    L.restore_logger_object(log)
    L.save_log(True)
    
    """ Obtain calibration score """
    CS = calibrationscore.CalibrationScore(L)
    score = CS.test_all()
    

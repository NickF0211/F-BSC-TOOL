memtime_available = False

### define your command_hear here

if memtime_available:
    command_header = ["../../memtime-master/memtime", "python3"]
else:
    command_header = ["python3"]

from BST import trans_exp
from CFH import covid_exp
from NASA import NASA_exp
from PBC import approve_req_exp
from PHIM import baby_exp
from DGraph import graph_exp, graph_exp_nopt, graph_exp_nopt_wr, graph_exp_wr
from Player import play_exp, play_exp_nopt, play_exp_wr, play_exp_nopt_wr
from magic_sequence import magic_exp, magic_exp_wr, magic_exp_nopt, magic_exp_nopt_wr
from Banking import bank_exp_hour, bank_exp_day, bank_exp_day_nopt, bank_exp_hour_nopt
from Banking_WR import bank_exp_day_wr, bank_exp_day_nopt_wr, bank_exp_hour_wr, bank_exp_hour_nopt_wr

if __name__ == "__main__":
    import os
    from os import path
    os.chdir(path.join("BST"))
    trans_exp.run_exp(command_header)
    os.chdir(path.join(path.pardir, "CFH" ))
    covid_exp.run_exp(command_header)
    os.chdir(path.join(path.pardir, "NASA" ))
    NASA_exp.run_exp(command_header)
    os.chdir(path.join(path.pardir, "PBC" ))
    approve_req_exp.run_exp(command_header)
    os.chdir(path.join(path.pardir, "PHIM" ))
    baby_exp.run_exp(command_header)
    # baby_aggr_exp.run_exp(command_header)
    # os.chdir(path.join(path.pardir, "DGraph" ))
    # graph_exp.run_exp(command_header)
    # graph_exp_nopt.run_exp(command_header)
    # graph_exp_wr.run_exp(command_header)
    # graph_exp_nopt_wr.run_exp(command_header)
    # os.chdir(path.join(path.pardir, "Player"))
    # play_exp.run_exp(command_header)
    # play_exp_nopt.run_exp(command_header)
    # play_exp_wr.run_exp(command_header)
    # play_exp_nopt_wr.run_exp(command_header)
    # os.chdir(path.join(path.pardir, "magic_sequence"))
    # magic_exp.run_exp(command_header)
    # magic_exp_nopt.run_exp(command_header)
    # magic_exp_wr.run_exp(command_header)
    # magic_exp_nopt_wr.run_exp(command_header)
    # os.chdir(path.join(path.pardir, "Banking"))
    # bank_exp_day.run_exp(command_header)
    # bank_exp_day_nopt.run_exp(command_header)
    # bank_exp_hour.run_exp(command_header)
    # bank_exp_hour_nopt.run_exp(command_header)
    # os.chdir(path.join(path.pardir, "Banking_WR"))
    # bank_exp_day_wr.run_exp(command_header)
    # bank_exp_day_nopt_wr.run_exp(command_header)
    # bank_exp_hour_wr.run_exp(command_header)
    # bank_exp_hour_nopt_wr.run_exp(command_header)



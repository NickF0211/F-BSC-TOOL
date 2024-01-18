memtime_available = False
z3 = False
cvc5 = False
vampire = False
### define your command_hear here

if memtime_available:
    command_header = ["../../memtime-master/memtime", "python3"]
else:
    command_header = ["python3"]



from DGraph import graph_exp, graph_exp_nopt, graph_exp_nopt_wr, graph_exp_wr, graph_exp_wr_fol, graph_exp_wr_cvc5, graph_exp_wr_vampire
from Player import play_exp, play_exp_nopt, play_exp_wr, play_exp_nopt_wr, play_exp_wr_fol, play_exp_wr_cvc5, play_exp_wr_vampire
from magic_sequence import magic_exp, magic_exp_wr, magic_exp_nopt, magic_exp_nopt_wr, magic_exp_wr_fol, magic_exp_wr_cvc5, magic_exp_wr_vampire
from Banking import bank_exp_hour, bank_exp_day, bank_exp_day_nopt, bank_exp_hour_nopt
from Banking_WR import bank_exp_day_wr, bank_exp_day_nopt_wr, bank_exp_hour_wr, bank_exp_hour_nopt_wr, bank_exp_day_wr_fol, \
    bank_exp_day_wr_cvc5,bank_exp_day_wr_vampire, bank_exp_hour_wr_fol, bank_exp_hour_wr_cvc5, bank_exp_hour_wr_vampire
from PHIM import baby_aggr_exp, baby_aggr_exp_nopt, baby_aggr_exp_wr, baby_aggr_exp_nopt_wr, baby_aggr_exp_wr_fol, baby_aggr_exp_wr_cvc5, baby_aggr_exp_wr_vampire

if __name__ == "__main__":
    import os
    from os import path
    os.chdir(path.join(path.curdir, "PHIM" ))
    baby_aggr_exp.run_exp(command_header)
    baby_aggr_exp_nopt.run_exp(command_header)
    baby_aggr_exp_wr.run_exp(command_header)
    baby_aggr_exp_nopt_wr.run_exp(command_header)
    if z3:
        baby_aggr_exp_wr_fol.run_exp(command_header)
    if cvc5:
        baby_aggr_exp_wr_cvc5.run_exp(command_header)
    if vampire:
        baby_aggr_exp_wr_vampire.run_exp(command_header)

    os.chdir(path.join(path.curdir, "DGraph" ))
    graph_exp.run_exp(command_header)
    graph_exp_nopt.run_exp(command_header)
    graph_exp_wr.run_exp(command_header)
    graph_exp_nopt_wr.run_exp(command_header)
    if z3:
        graph_exp_wr_fol.run_exp(command_header)
    if cvc5:
        graph_exp_wr_cvc5.run_exp(command_header)
    if vampire:
        graph_exp_wr_vampire.run_exp(command_header)
    os.chdir(path.join(path.curdir, "Player"))
    play_exp.run_exp(command_header)
    play_exp_nopt.run_exp(command_header)
    play_exp_wr.run_exp(command_header)
    play_exp_nopt_wr.run_exp(command_header)
    if z3:
        play_exp_wr_fol.run_exp(command_header)
    if cvc5:
        play_exp_wr_cvc5.run_exp(command_header)
    if vampire:
        play_exp_wr_vampire.run_exp(command_header)

    os.chdir(path.join(path.curdir, "magic_sequence"))
    magic_exp.run_exp(command_header)
    magic_exp_nopt.run_exp(command_header)
    magic_exp_wr.run_exp(command_header)
    magic_exp_nopt_wr.run_exp(command_header)
    if z3:
        magic_exp_wr_fol.run_exp(command_header)
    if cvc5:
        magic_exp_wr_cvc5.run_exp(command_header)
    if vampire:
        magic_exp_wr_vampire.run_exp(command_header)

    os.chdir(path.join(path.curdir, "Banking"))
    bank_exp_day.run_exp(command_header)
    bank_exp_day_nopt.run_exp(command_header)
    bank_exp_hour.run_exp(command_header)
    bank_exp_hour_nopt.run_exp(command_header)
    os.chdir(path.join(path.curdir, "Banking_WR"))
    bank_exp_day_wr.run_exp(command_header)
    bank_exp_day_nopt_wr.run_exp(command_header)
    bank_exp_hour_wr.run_exp(command_header)
    bank_exp_hour_nopt_wr.run_exp(command_header)
    if z3:
        bank_exp_day_wr_fol.run_exp(command_header)
        bank_exp_hour_wr_fol.run_exp(command_header)
    if cvc5:
        bank_exp_day_wr_cvc5.run_exp(command_header)
        bank_exp_hour_wr_cvc5.run_exp(command_header)
    if vampire:
        bank_exp_day_wr_vampire.run_exp(command_header)
        bank_exp_hour_wr_vampire.run_exp(command_header)



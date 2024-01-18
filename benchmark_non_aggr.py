memtime_available = False

z3 = False
cvc5 = False
vampire = False
### define your command_hear here

if memtime_available:
    command_header = ["../../memtime-master/memtime", "python3"]
else:
    command_header = ["python3"]

from BST import trans_exp, trans_exp_fol, trans_exp_cvc5, trans_exp_vampire
from CFH import covid_exp, covid_exp_cvc5, covid_exp_fol, covid_exp_vampire
from NASA import NASA_exp, NASA_exp_fol, NASA_exp_cvc5, NASA_exp_vampire
from PBC import approve_req_exp, approve_req_exp_fol, approve_req_exp_cvc5, approve_req_exp_vampire
from PHIM import baby_exp, baby_exp_fol, baby_exp_cvc5, baby_exp_vampire

if __name__ == "__main__":
    import os
    from os import path

    os.chdir(path.join("BST"))
    trans_exp.run_exp(command_header)
    if z3:
        trans_exp_fol.run_exp(command_header)
    if cvc5:
        trans_exp_cvc5.run_exp(command_header)
    if vampire:
        trans_exp_vampire.run_exp(command_header)

    os.chdir(path.join(path.curdir, "CFH"))
    covid_exp.run_exp(command_header)
    if z3:
        covid_exp_fol.run_exp(command_header)
    if cvc5:
        covid_exp_cvc5.run_exp(command_header)
    if vampire:
        covid_exp_vampire.run_exp(command_header)

    os.chdir(path.join(path.curdir, "NASA"))
    NASA_exp.run_exp(command_header)
    if z3:
        NASA_exp_fol.run_exp(command_header)
    if cvc5:
        NASA_exp_cvc5.run_exp(command_header)
    if vampire:
        NASA_exp_vampire.run_exp(command_header)

    os.chdir(path.join(path.curdir, "PBC"))
    approve_req_exp.run_exp(command_header)
    if z3:
        approve_req_exp_fol.run_exp(command_header)
    if cvc5:
        approve_req_exp_cvc5.run_exp(command_header)
    if vampire:
        approve_req_exp_vampire.run_exp(command_header)

    os.chdir(path.join(path.curdir, "PHIM"))
    baby_exp.run_exp(command_header)
    if z3:
        baby_exp_fol.run_exp(command_header)
    if cvc5:
        baby_exp_cvc5.run_exp(command_header)
    if vampire:
        baby_exp_vampire.run_exp(command_header)



import bank_exp_day_nopt
import bank_exp_hour_nopt
def run_exp(command_header):
    bank_exp_day_nopt.run_exp(command_header)
    bank_exp_hour_nopt.run_exp(command_header)

if __name__ == "__main__":
    command_header = ["../../../memtime/memtime", "python3"]
    run_exp(command_header)
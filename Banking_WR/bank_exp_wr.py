import bank_exp_day_wr
import bank_exp_hour_wr
def run_exp(command_header):
    bank_exp_day_wr.run_exp(command_header)
    bank_exp_hour_wr.run_exp(command_header)

if __name__ == "__main__":
    command_header = ["../../../memtime/memtime", "python3"]
    run_exp(command_header)
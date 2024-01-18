
import subprocess
import os

RESULT_DIR = 'results_wr'

def run_exp(command_header):
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)


    timeout = 5000
    rule_file  = "graph_rule_wr_cvc5.py"
    properties_remap = [1,2,3,4,5]
    properties = [2, 3, 7, 8, 9]
    for j, index in zip(properties, properties_remap):
        result_file = "{}/dg_{}_cvc5.txt".format(RESULT_DIR, index)
        print(result_file)
        with open(result_file, 'w') as f:
            try:
                result = subprocess.run(command_header + [ rule_file, str(j), "f", "f", "f", "t"], stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        universal_newlines=True,
                                        timeout=timeout)
                f.write(result.stdout)
                f.write(result.stderr)

            except subprocess.TimeoutExpired as t:
                f.write("timeout {}".format(timeout))
                #continue






if __name__ == "__main__":
    command_header = ["../../../memtime/memtime", "python3"]
    run_exp(command_header)




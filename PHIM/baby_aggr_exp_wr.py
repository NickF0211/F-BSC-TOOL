
import os
import subprocess

RESULT_DIR = "results_wr"
def run_exp(command_header):

    timeout = 5000
    #init value

    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)


    vol_bound = 5000

    rule_file = "baby_rule.py"

    for j in range(7, 11):
        j = str(j)
        result_file = "{}/pha_{}.txt".format(RESULT_DIR, j)
        print(result_file)
        with open(result_file, 'w') as f:
            try:
                result = subprocess.run(command_header + [ rule_file, j, "t"], stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        universal_newlines=True,
                                        timeout=timeout)
                f.write(result.stdout)
                f.write(result.stderr)

            except subprocess.TimeoutExpired as t:
                f.write("timeout {}".format(timeout))
                #continue


        result_file = "{}/pha_{}_bcr.txt".format(RESULT_DIR, j)
        print(result_file)
        with open(result_file, 'w') as f:
            try:
                result = subprocess.run(command_header + [rule_file, j, "t", "f", "t"], stdout=subprocess.PIPE,
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


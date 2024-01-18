
import subprocess
import os

RESULT_DIR = "results"

def run_exp(command_header):
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)


    timeout = 5000
    rule_file  = "magic_rule.py"

    trails = [2,4, 10, 100, 1000, 10000]

    for j in trails:

        result_file = "{}/m_{}.txt".format(RESULT_DIR, str(j))
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
                continue




        result_file = "{}/m_{}_bcr.txt".format(RESULT_DIR, str(j))
        print(result_file)
        with open(result_file, 'w') as f:
            try:
                result = subprocess.run(command_header + [rule_file, str(j), "f", "t", "f", "t"], stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        universal_newlines=True,
                                        timeout=timeout)

                f.write(result.stdout)
                f.write(result.stderr)

            except subprocess.TimeoutExpired as t:
                f.write("timeout {}".format(timeout))
                continue






if __name__ == "__main__":
    command_header = ["../../../memtime/memtime", "python3"]
    run_exp(command_header)


# This is the anonymous repository for TOOL

### prerequisite:
1. Python 3.5 and later

2. memtime for measuring time and memory usage: https://github.com/phuseman/memtime 
(only available on Linux OS). Please add memtime executable to the path.

3. z3-solver with python binding:
    `pip install z3-solver` or 
    `pip3 install z3-solver`
    
4. pysmt:
    `pip install pysmt` or 
    `pip3 install pysmt`

5. ordered-set:
   `pip install ordered-set` or
   `pip3 install ordered-set`

6. If you would like to compare TOOL against cvc5 or vampire, please download their executables
   
    cvc5: https://cvc5.github.io/downloads.html
   
    vampire: https://github.com/vprover/vampire/releases/download/v4.8casc2023/vampire_z3_rel_static_casc2023_6749.zip
   
    update the executable locations in Analyzer/solver_config.py

   

### repository structure


    1. Analyzer contains the implementation of the bounded satisfiability checking algorithm 
    2. CFH for case study CovidFree@Home
    3. PHIM for case study PHIM, and PHIM-A
    4. PBC for case study PBC
    5. NASA for case study NASA
    6. DGraph for case study DG
    7. magic_seqeunce for case study Magic
    8. Player for case study Player
    9. Banking for case study Bank
    


### launch experiments 
To launch experiment for case studies with aggregations, run `python3 benchmark_aggr.py`
To launch experiment for case studies without aggregations, run `python3 benchmark_non_aggr.py`
If (memtime) is not installed, change variable `memtime_available = False` before running the script.
If you wish to compare TOOL against z3, cvc5, and vampire, please change 

`z3 = True`,   `cvc5 = True`, and  `vampire = True` in both experiment scripts.


To launch individual case study, go to the case study folder, and run `python3 {name}_exp.py`
where the name depends on the case study. 

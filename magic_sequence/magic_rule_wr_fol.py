import sys

sys.path.append('../Analyzer')
from logic_operator import *
from magic_domain_wr import *
from analyzer import check_property_refining, check_property_fol
import time

'''
This problem is inspired by the magic sequence problem introduced in: DPLL(Agg): an efficient SMT module for aggregates.
We want to synthesize a function f: [0 ... N - 1] -> [0... N] such that f(x) = #{y | f(y) = x}


The problem is encoded with a default f(x) = 0
'''


#
# def number_of_y(x):
#     return Count(Magic, lambda m1: EQ(m1.y, x))


def mc_init(mc, N):
    return AND(
        EQ(mc.x, Int(-1)),
        EQ(mc.count, Int(0))
        # Implication(EQ(mc.y, Int(0)),
        #             EQ(mc.count, Int(N))),
        # Implication(NEQ(mc.y, Int(0)),
        #             EQ(mc.count, Int(0))),
    )

def the_one_before(mc, mc_old):
    return NOT(exist(Magic_count, lambda mc_mid:
                  AND(
                      EQ(mc.y, mc_mid.y),
                      mc_mid.x < mc.x,
                      mc_mid.x > mc_old.x
                  )
                  ))

def mc_counting(mc, N):
    return AND(
        mc.x >= 0,
                    OR(
                        # case one, no update
                        exist(Magic_count, lambda mc_old, mc=mc:
                            AND(
                                # the_one_before(mc, mc_old),
                                EQ(mc.y, mc_old.y),
                                mc.x > mc_old.x,
                                EQ(mc.count, mc_old.count),
                                NOT(exist(Magic, lambda m, mc_old =mc_old, mc=mc:
                                            AND(m.x <= mc.x,
                                                m.x > mc_old.x,
                                                Implication(EQ(mc.y, Int(0)), TRUE()),
                                                Implication(NEQ(mc.y, Int(0)), EQ(m.y, mc.y))
                                          ))
                            )
                            ))
                        ,
                        # case two, a update
                        exist(Magic_count, lambda mc_old, mc=mc:
                              AND(
                                  # the_one_before(mc, mc_old),
                                  EQ(mc.y, mc_old.y),
                                  mc.x > mc_old.x,
                                  # Implication(EQ(mc.y, Int(0)), EQ(mc.count, mc_old.count - Int(1))),
                                  # Implication(NEQ(mc.y, Int(0)), EQ(mc.count, mc_old.count + Int(1))),
                                  EQ(mc.count, mc_old.count + Int(1)),
                                  exist(Magic, lambda m, mc_old=mc_old, mc=mc:
                                  AND(m.x <= mc.x,
                                      m.x > mc_old.x,
                                      Implication(EQ(mc.y, Int(0)), NEQ(m.y, Int(0))),
                                      Implication(NEQ(mc.y, Int(0)), EQ(m.y, mc.y))
                                      )

                              )
                              )

                    )
                    )
    )


def effect_of_magic(x, y):
    return exist([Magic_count, Magic_count], lambda old_mc, new_mc, x=x, y=y:
    AND(
        EQ(old_mc.y, y),
        old_mc.x < x,
        NOT(exist(Magic_count, lambda mid_mc, old_mc=old_mc, x=x:
        AND(
            EQ(old_mc.y, mid_mc.y),
            mid_mc.x > old_mc.x,
            mid_mc.x < x,
        )
                  )),
        EQ(new_mc.x, x),
        EQ(new_mc.y, y),
        EQ(new_mc.count, old_mc.count  + Int(1))
    )
          )


if __name__ == '__main__':
    args = sys.argv[1:]
    N = int(args[0])

    args = args[1:]
    mymin = True
    restart = False
    bcr = False
    ub = False
    arg_len = len(args)
    if arg_len >= 1:
        restart = args[0].lower().startswith('t')
    if arg_len >= 2:
        bcr = args[1].lower().startswith('t')
    if arg_len >= 3:
        ub = args[2].lower().startswith('t')

    if arg_len >= 4:
        mymin = args[3].lower().startswith('t')

    complete_rules = []

    # Magic count property
    complete_rules.append(forall(Magic_count, lambda mc:
        OR(mc_counting(mc, N), mc_init(mc, N))))

    complete_rules.append(forall(Magic, lambda m: exist(Magic_count, lambda mc:
    AND(
        Implication(NEQ(m.x, Int(0)), EQ(m.y, mc.count)),
        Implication(EQ(m.x, Int(0)), EQ(m.y, Int(N) - mc.count )),
        EQ(m.x, mc.y),
        EQ(mc.x, Int(N - 1)))
                                                        )))


    #MC uniqueness
    complete_rules.append(forall([Magic_count, Magic_count], lambda mc1, mc2:
                                 Implication(AND(EQ(mc1.x, mc2.x), EQ(mc1.y, mc2.y)), EQ(mc1.count, mc2.count))
                                 ))

    # Magic property
    # complete_rules.append(forall(Magic, lambda m: Implication(m.x > 0, EQ(m.y, number_of_y(m.x)))))

    # function definition
    complete_rules.append(forall([Magic, Magic], lambda m1, m2: Implication(EQ(m1.x, m2.x), EQ(m1, m2))))
    complete_rules.append(forall(Magic, lambda m: effect_of_magic(m.x, m.y)))

    # value bound on the x and y
    complete_rules.append(forall(Magic, lambda m: AND(m.x < N, m.y <= N, m.y>0)))

    # if f(x) > 0, then f(f(x)) > 0
    complete_rules.append(
        forall(Magic, lambda m: Implication(m.y > 0, exist(Magic, lambda m1: AND(EQ(m1.x, m.y), m1.y > 0)))))

    # f(0) > 0
    # target_rule = exist(Magic, lambda m: AND(EQ(m.x, Int(0)),
    #                                          EQ(Int(N) - m.y, Sum(Magic, lambda _: Int(1), lambda m: m.y > 0))))

    # target_rule = exist(Magic_count, lambda mc: AND(EQ(mc.y, Int(0)),
    #     #                                                 EQ(mc.x, Int(N - 1))))

    target_rule = exist(Magic, lambda m: EQ(m.x, Int(0)))

    rules = set()
    start = time.time()
    check_property_fol(target_rule, complete_rules, ACTION)
    print(time.time() - start)

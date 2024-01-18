import sys
sys.path.append('../Analyzer')
from logic_operator import *
from bank_domain_wr import *
import time
from analyzer import check_property_fol, check_property_vampire
from type_constructor import union


complete_rules = []
TS = union(Trans, Depo, Withdraw)

# every transication has a unqiue tid, and the id's are ordered by time
# Trans_action = union(Trans, Withdraw, Depo)
complete_rules.append(forall([TS, TS], lambda t1, t2: Implication(NEQ(t1, t2), NEQ(t1.id, t2.id))))
complete_rules.append(forall([TS, TS], lambda t1, t2: Implication(t1 > t2, t1.id > t2.id)))


def update_balance(b, b1):
    cond1 = b.id >= b1.id
    cond2 = b.time >= b1.time
    cond3 = EQ(b.uid, b1.uid)
    # case1, update by depo
    dp_case1 = exist(Depo, lambda dp,  b=b, b1=b1,:
            AND(
                b.id > b1.id,
                b1.time <= dp.time,
                EQ(dp.user, b.uid),
                EQ(dp.id, b.id),
                EQ(b.amount, dp.amount + b1.amount),
                EQ(dp.time, b.time)
            )
          )

    trans_in_case2 = exist(Trans, lambda trans, b=b, b1=b1, :
            AND(
                b.id > b1.id,
                b1.time <= trans.time,
                EQ(trans.receiver, b.uid),
                EQ(trans.id, b.id),
                EQ(b.amount, trans.amount + b1.amount),
                EQ(trans.time, b.time),
                exist([Balance, Balance], lambda b2, b4, b=b, b1=b1:
                      # the sender must have enough balance
                      AND(b2.amount >= trans.amount,
                          EQ(b2.uid, trans.sender),
                          EQ(b2.time, trans.time),
                          b2.id < trans.id,
                          EQ(b4.uid, b2.uid),
                          EQ(b4.time, trans.time),
                          EQ(b4.amount, b2.amount - trans.amount),
                          EQ(b4.id, trans.id)
                          )
                      )
            )
          )

    trans_out_case3 = exist(Trans, lambda trans, b=b, b1=b1, :
    AND(
        b.id > b1.id,
        b1.time <= trans.time,
        EQ(trans.sender, b.uid),
        EQ(trans.id, b.id),
        EQ(b.amount, b1.amount - trans.amount),
        EQ(trans.time, b.time),
        exist([Balance, Balance], lambda b2, b4, b=b, b1=b1:
        # the sender must have enough balance
        AND(
            EQ(b2.uid, trans.receiver),
            EQ(b2.time, trans.time),
            b2.id < trans.id,
            EQ(b4.uid, b2.uid),
            EQ(b4.time, trans.time),
            EQ(b4.amount, b2.amount + trans.amount),
            EQ(b4.id, trans.id)
            )
        )
    )

    )
    no_change_case_4 = AND(EQ(b.amount, b1.amount), EQ(b.id, b1.id), b.time > b1.time)
    return AND(cond1, cond2, cond3, OR(dp_case1, trans_in_case2, trans_out_case3, no_change_case_4))


# rules go here
def balance_ge(user, time, target):
    return exist(Balance, lambda b, time = time, target =target
                                    : AND(EQ(b.uid, user),
                                        EQ(b.time, time),
                                        b.amount >= target
                                        ))



#the balance update rule
complete_rules.append(forall(Balance, lambda balance:

                             OR(
                                # init case
                                AND(EQ(balance.id, Int(0)), EQ(balance.time, Int(0)), EQ(balance.amount, Int(0)))
                                 ,
                                # update case
                                 exist(Balance, lambda balance1, balance = balance:
                                       AND(update_balance(balance, balance1),
                                           NOT(exist(Balance, lambda b3:
                                                     AND(EQ(b3.uid, balance.uid),
                                                          b3.time <= balance.time,
                                                         b3.time >= balance1.time,
                                                         b3.id < balance.id,
                                                         b3.id > balance1.id)
                                                     )))
                                       )

                             )
                             ))



#
# # every transication has a unqie tid
# complete_rules.append(NOT(exist([Trans, Trans], lambda ts1, ts2: AND(NEQ(ts1, ts2), EQ(ts1.id, ts2.id)))))
# complete_rules.append(NOT(exist([Withdraw, Withdraw], lambda ts1, ts2: AND(NEQ(ts1, ts2), EQ(ts1.id, ts2.id)))))
# complete_rules.append(NOT(exist([Depo, Depo], lambda ts1, ts2: AND(NEQ(ts1, ts2), EQ(ts1.id, ts2.id)))))

# every deposite can have at most 500 dollars
complete_rules.append(forall(Depo, lambda depo: depo.amount <= 500))
# every user can deposite at most once every day
complete_rules.append(forall([Depo, Depo], lambda depo1, depo2: Implication(AND(depo1.id > depo2.id,
                                                                                EQ(depo1.user, depo2.user)),
                                                                            NEQ(depo1.time, depo2.time))))

# if a user withdraw, then it must have sufficent balance
complete_rules.append(forall(Withdraw, lambda wd: balance_ge(wd.user, wd.time - Int(1), wd.amount)))

# if a user transfer out, then it must have sufficent balance
complete_rules.append(forall(Trans, lambda tr: balance_ge(tr.sender, tr.time - Int(1), tr.amount)))
# complete_rules.append(forall(Trans, lambda tr: balance_ge(tr.sender, tr.time - Int(1), tr.amount)))
complete_rules.append(forall(Trans, lambda tr: NEQ(tr.sender, tr.receiver)))

# a user can receive at most 2 transfer a day
complete_rules.append(NOT(exist([Trans, Trans, Trans], lambda trans1, trans2, trans3:
AND([trans1.id > trans2.id,
     trans2.id > trans3.id,
     EQ(trans1.receiver, trans2.receiver),
     EQ(trans2.receiver, trans3.receiver),
     EQ(trans1.time, trans2.time),
     EQ(trans2.time, trans3.time)]
    )
                                )))

# a user can send at most 1 transfer
complete_rules.append(NOT(exist([Trans, Trans], lambda trans1, trans2:
AND([trans1.id > trans2.id,
     EQ(trans1.sender, trans2.sender),
     EQ(trans1.time, trans2.time)])
                                )))

rule_1 = exist(Withdraw, lambda wd: AND(EQ(wd.amount, Int(1273)), wd.time <= 2))
rule_2 = exist(Withdraw, lambda wd: AND(EQ(wd.amount, Int(1800)), wd.time <= 2))
rule_3 = exist(Withdraw, lambda wd: AND(EQ(wd.amount, Int(2001)), wd.time <= 2))
rule_4 = exist(Withdraw, lambda wd: AND(EQ(wd.amount, Int(2001)), wd.time <= 3))
rule_5 = exist(Withdraw, lambda wd: AND(EQ(wd.amount, Int(4000)), wd.time <= 3))
rule_6 = exist(Withdraw, lambda wd: AND(EQ(wd.amount, Int(6000)), wd.time <= 3))
rule_7 = exist(Withdraw, lambda wd: AND(EQ(wd.amount, Int(6500)), wd.time <= 3))
rule_8 = exist(Withdraw, lambda wd: AND(EQ(wd.amount, Int(6501)), wd.time <= 3))
rule_9 = exist(Withdraw, lambda wd: AND(EQ(wd.amount, Int(7000)), wd.time <= 4))
rule_10 = exist(Withdraw, lambda wd: AND(EQ(wd.amount, Int(12000)), wd.time <= 4))
rule_11 = exist(Withdraw, lambda wd: AND(EQ(wd.amount, Int(200000)), wd.time <= 4))

if __name__ == '__main__':
    args = sys.argv[1:]
    target_rule = globals()["rule_{}".format(args[0])]

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

    rules = set()
    start = time.time()
    check_property_vampire(target_rule, complete_rules, ACTION)
    print(time.time() - start)


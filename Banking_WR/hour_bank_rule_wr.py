import sys
sys.path.append('../Analyzer')
from logic_operator import *
from bank_domain_wr import *
import time
from analyzer import check_property_refining
from type_constructor import union

Balance_delay = 12


# rules go here
def b_init(balance):
    return AND(EQ(balance.time, Int(0)),
               EQ(balance.amount, Int(0)),
               EQ(balance.id, Int(0))
               )


def no_update(new_b, old_b):
    cond1 = EQ(new_b.amount, old_b.amount)
    uid = new_b.uid
    no_depo = NOT(exist(Depo, lambda depo, new_b=new_b, old_b=old_b:
    AND(EQ(depo.user, uid),
        depo.id > old_b.id,
        depo.id <= new_b.id,
        # special case considering delay
        depo.time <= new_b.time - Int(Balance_delay)
        )
                        ))

    no_withdraw = NOT(exist(Withdraw, lambda wd, new_b=new_b, old_b=old_b:
    AND(EQ(wd.user, uid),
        wd.id > old_b.id,
        wd.id <= new_b.id,
        )
                            ))

    no_transfer_in = NOT(exist(Trans, lambda tr, new_b=new_b, old_b=old_b:
    AND(EQ(tr.receiver, uid),
        tr.id > old_b.id,
        tr.id <= new_b.id,
        # special case for delay
        tr.time <= new_b.time - Int(Balance_delay)
        )
                               ))

    no_transfer_out = NOT(exist(Trans, lambda tr, new_b=new_b, old_b=old_b:
    AND(EQ(tr.sender, uid),
        tr.id > old_b.id,
        tr.id <= new_b.id
        )
                                ))

    return AND(cond1, no_depo, no_withdraw, no_transfer_in, no_transfer_out)


def deposited(new_b, old_b):
    deposited_cond = exist(Depo, lambda depo, new_b=new_b, old_b=old_b:
    AND(
        EQ(depo.user, new_b.uid),
        depo.id > old_b.id,
        depo.id <= new_b.id,
        # special case considering delay
        depo.time <= new_b.time - Int(Balance_delay),
        EQ(depo.amount, new_b.amount - old_b.amount)
    )
                           )
    return deposited_cond


def transferred_in(new_b, old_b):
    transfer_in_cond = exist(Trans, lambda trans, new_b=new_b, old_b=old_b:
    AND(
        EQ(trans.receiver, new_b.uid),
        trans.id > old_b.id,
        trans.id <= new_b.id,
        # special case considering delay
        trans.time <= new_b.time - Int(Balance_delay),
        EQ(trans.amount, new_b.amount - old_b.amount)
    )
                             )
    return transfer_in_cond


def transferred_out(new_b, old_b):
    transfer_out_cond = exist(Trans, lambda trans, new_b=new_b, old_b=old_b:
    AND(
        EQ(trans.sender, new_b.uid),
        trans.id > old_b.id,
        trans.id <= new_b.id,
        EQ(trans.amount, old_b.amount - new_b.amount)
    )
                              )
    return transfer_out_cond


def b_update(new_b, old_b):
    same_user_update_in_the_past = AND(EQ(new_b.uid, old_b.uid), new_b.id > old_b.id)
    no_update_rel = no_update(new_b, old_b)
    repo_rel = deposited(new_b, old_b)
    transfer_in_rel = transferred_in(new_b, old_b)
    transfer_out_rel = transferred_out(new_b, old_b)
    return AND(same_user_update_in_the_past, OR(no_update_rel, repo_rel, transfer_in_rel, transfer_out_rel))

    # case 1, there is no update during the time


def successor(new_b, old_b, Class=Balance):
    return AND( new_b.id > old_b.id, NOT(exist(Class, lambda  bs, new_b=  new_b, old_b= old_b:
                     AND(EQ(new_b.uid, bs.uid),
                         new_b.id > bs.id,
                         old_b.id < bs.id
                         )
                     )))

def b_validity(balance):
    # option, init balance
    balance_init = b_init(balance)

    # now, consider balance with successor
    balance_pred = exist(Balance, lambda old_b, new_b=balance:
        AND(b_update(new_b, old_b),
            successor(new_b, old_b)
                         ))

    return OR(balance_init, balance_pred)


def cost_of_transfer_out(trans):
    # the moment a tansfer-out is issued, outdate the balance of the user
    return exist(Balance, lambda new_bs, trans =trans:
          AND(
              # same time
              EQ(new_bs.time, trans.time),
              # same user
              EQ(new_bs.uid, trans.sender),
              # same id
              EQ(new_bs.id, trans.id),
              # update amount
              exist(Balance, lambda old_bs, new_bs = new_bs, trans =trans:
                    AND(
                        successor(new_bs, old_bs),
                        EQ(new_bs.amount, old_bs.amount - trans.amount)
                    )

              )

          )
                          )

def balance(user, time, action, comparsion):
    return exist(Balance, lambda bs, time=time, action= action, comparsion=comparsion:
                 AND(
                     EQ(bs.uid, user),
                     EQ(bs.time, time),
                     EQ(bs.id, action.id),
                     bs.amount >= comparsion
                 )
                 )


def dto_init(dto):
    return AND(EQ(dto.id, Int(0)),
               EQ(dto.amount, Int(0))
               )


def dto_update(new_dto, old_dto):
    # in this case, we can assume there was a transfer out at some point
    same_user_same_time = AND(EQ(new_dto.uid, old_dto.uid), EQ(new_dto.time, old_dto.time))
    previous_event = new_dto.id > old_dto.id
    outdated_balance = exist(Trans, lambda ts, new_dto=new_dto, old_dto=old_dto:
                             AND(
                                 EQ(ts.sender, new_dto.uid),
                                 ts.id <= new_dto.uid,
                                 ts.id > old_dto.uid,
                                 ts.time < new_dto.time,
                                 ts.time >= new_dto.time - Int(24),
                                 # transferred_amount
                                 EQ(new_dto.amount, old_dto.amount + ts.amount)
                             )
                             )
    return AND(same_user_same_time, previous_event, outdated_balance)


def dto_validity(dto):
    return OR(dto_init(dto),
              exist(DTO, lambda old_dto, dto=dto:
              AND( successor(dto, old_dto, Class=DTO),
                    dto_update(dto))))


def daily_transfer_out_sum(user, time, action, comparsion):
    return exist(DTO, lambda dto, user=user, time=time, action=action, comparsion = comparsion:
            AND(
                EQ(dto.uid, user),
                EQ(dto.time, time),
                EQ(dto.id, action.id),
                dto.amount > comparsion
            )
          )




# balance = _balance
complete_rules = []
add_background_theories(ACTION, state_action, complete_rules)
TS = union(Trans, Depo, Withdraw)

# every transication has a unqiue tid, and the id's are ordered by time
# Trans_action = union(Trans, Withdraw, Depo)
complete_rules.append(forall([TS, TS], lambda t1, t2: Implication(NEQ(t1, t2), NEQ(t1.id, t2.id))))
complete_rules.append(forall([TS, TS], lambda t1, t2: Implication(t1 > t2, t1.id > t2.id)))

# now, all balance need to be valid
complete_rules.append(forall(Balance, lambda bs: b_validity(bs)))

# if transfer is issued, balance has to be updated
complete_rules.append(forall(Trans, lambda ts: cost_of_transfer_out(ts)))

# every deposite can have at most 500 dollars
complete_rules.append(forall(Depo, lambda depo: depo.amount <= 500))
# every user can deposite at most once every day
complete_rules.append(forall([Depo, Depo], lambda depo1, depo2: Implication(AND(depo1.id > depo2.id,
                                                                                EQ(depo1.user, depo2.user)),
                                                                            depo1.time > depo2.time + Int(24))))

# if a user withdraw, then it must have sufficent balance
complete_rules.append(forall(Withdraw, lambda wd: balance(wd.user, wd.time, wd, wd.amount)))

# if a user transfer out, then it must have sufficent balance
complete_rules.append(forall(Trans, lambda tr: balance(tr.sender, tr.time, tr, tr.amount) ))
complete_rules.append(forall(Trans, lambda tr: NEQ(tr.sender, tr.receiver)))

# a user can receive at most 2 transfer a day
complete_rules.append(NOT(exist([Trans, Trans, Trans], lambda trans1, trans2, trans3:
AND([trans1.id > trans2.id,
     trans2.id > trans3.id,
     EQ(trans1.receiver, trans2.receiver),
     EQ(trans2.receiver, trans3.receiver),
     trans1.time < trans3.time + Int(24),
     trans2.time < trans3.time + Int(24), ]
    )
                                )))

# a user can send at most 1 transfer at every hour
complete_rules.append(NOT(exist([Trans, Trans], lambda trans1, trans2:
AND([trans1.id > trans2.id,
     EQ(trans1.sender, trans2.sender),
     trans1.time <= trans2.time])
                                )))

# if a user transfer out an amount that is greater than 3000, then there is at least one day
# in the last week the user has transfer out more than 3000
transfer_protection = forall(Trans, lambda trans: Implication(trans.amount > 1500,
                                                              once(Trans,
                                                                   lambda trans1: AND(EQ(trans.sender, trans1.sender),
                                                                                      daily_transfer_out_sum(
                                                                                          trans1.sender, trans1.time,
                                                                                          trans1, 1500),
                                                                                      trans1.time < trans.time - 24,
                                                                                      trans1.time >= trans.time - Int(
                                                                                          144)),
                                                                   trans.time
                                                                   )))

rule_1 = exist(Trans, lambda wd: AND(EQ(wd.amount, Int(325)), wd.time <= 24))
rule_2 = exist(Trans, lambda wd: AND(EQ(wd.amount, Int(1000)), wd.time <= 36))
rule_3 = exist(Trans, lambda wd: AND(EQ(wd.amount, Int(3000)), wd.time <= 41))
rule_4 = exist(Trans, lambda wd: AND(EQ(wd.amount, Int(4000)), wd.time <= 48))
rule_5 = exist(Trans, lambda wd: AND(EQ(wd.amount, Int(4001)), wd.time <= 48))
rule_6 = exist(Trans, lambda wd: AND(EQ(wd.amount, Int(4001)), wd.time <= 50))
rule_7 = exist(Trans, lambda wd: AND(EQ(wd.amount, Int(6500)), wd.time <= 52))
rule_8 = exist(Trans, lambda wd: AND(EQ(wd.amount, Int(6501)), wd.time <= 60))
rule_9 = AND(transfer_protection, exist(Trans, lambda wd: wd.amount > 1001))
rule_10 = AND(transfer_protection, exist(Trans, lambda wd: wd.amount > 1501))
rule_11 = AND(transfer_protection, exist(Trans, lambda wd: wd.amount > 2000))
rule_12 = AND(transfer_protection, exist(Trans, lambda wd: wd.amount > 2500))

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
    complete_rules = add_background_theories(ACTION, state_action, complete_rules, bcr)
    check_property_refining(target_rule, set(complete_rules), complete_rules, ACTION, state_action, True,
                            min_solution=mymin,
                            final_min_solution=True, restart=restart, boundary_case=bcr, universal_blocking=ub)
    print(time.time() - start)



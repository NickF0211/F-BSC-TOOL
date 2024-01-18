"""
A player can play with at most X players at the same time.
If a player A plays with B, then he has two play with at most $Turn_Around$ players before playing with B again
A player becomes friend with another player if they have played at least 3 times

Is it possible to have a player befriend with everyone he has ever played with X days
"""
import sys
sys.path.append('../Analyzer')
from logic_operator import *
from player_domain_wr import *
from analyzer import check_property_refining, check_property_fol
import time




if __name__ == '__main__':

    args = sys.argv[1:]

    FRIEND_THRESHOLD = int(args[0])
    Group_Size = int(args[1])
    Turn_Around_Players = int(args[2])

    args = args[3:]
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

    if arg_len >= 3:
        mymin = args[3].lower().startswith('t')


    def PTC_init(ptc):
        return AND(EQ(ptc.id, Int(-1)),
                   EQ(ptc.count, Int(0)))

    def PTC_no_change(ptc, old_ptc):
        return AND(
            EQ(ptc.count, old_ptc.count),
            NOT(exist(Play, lambda play, ptc = ptc, old_ptc = old_ptc:
                      AND(
                          EQ(play.a, ptc.a),
                          EQ(play.b, ptc.b),
                          play < ptc,
                          play.id <= ptc.id,
                          play.id > old_ptc.id
                      )
            ))

        )

    def PTC_change(ptc, old_ptc):
        return AND(
            EQ(ptc.count, old_ptc.count + Int(1)),
            exist(Play, lambda play, ptc=ptc, old_ptc=old_ptc:
            AND(
                EQ(play.a, ptc.a),
                EQ(play.b, ptc.b),
                play < ptc,
                play.id <= ptc.id,
                play.id > old_ptc.id
            )
                      )

        )


    def PTC_update(ptc):
        return AND(
            exist(PTC, lambda old_ptc, ptc=ptc:
                  AND(
                      EQ(ptc.a, old_ptc.a),
                      EQ(ptc.b, old_ptc.b),
                      EQ(ptc.time, old_ptc.time),
                      ptc.id > old_ptc.id,
                      OR(
                          PTC_no_change(ptc, old_ptc),
                          PTC_change(ptc, old_ptc)
                      )
                  )

            )
        )


    def PTC_status(ptc):
        return OR(
            PTC_init(ptc),
            PTC_update(ptc)
        )




    def ptc_no_less(a, b, time, threshold):
        return exist(PTC, lambda ptc:
                     AND(
                         EQ(ptc.a, a),
                         EQ(ptc.b, b),
                         EQ(ptc.time, time),
                         ptc.count >= Int(threshold),
                         #
                         NOT(exist(PTC, lambda other_ptc, ptc=ptc:
                                   AND(EQ(other_ptc.a, ptc.a),
                                       EQ(other_ptc.b, ptc.b),
                                       EQ(other_ptc.time, ptc.time),
                                       other_ptc.id > ptc.id
                                       )
                                   ))
                     )

                     )

    # A palyer is friend with player B at time t if A and B has played more than FRIEND_THRESHOLD number of times since t,
    # and they have, and the most recent play was within the last 3 days
    def friend(a, b, time, trigger_action):
        return AND(
            ptc_no_less(a, b, time, FRIEND_THRESHOLD)
            # Count(Play, lambda p: AND(EQ(p.a, a),
            #                              EQ(p.b, b),
            #                              p.time < time), trigger_act=trigger_action, input_subs={"a": a,
            #                                                                                      "b": b}) >= Int(
            # FRIEND_THRESHOLD)
                   ,
                   exist(Play, lambda play: AND(EQ(play.a, a),
                                                            EQ(play.b, b),
                                                            play.time < time,
                                                            play.time >= (time - Int(Turn_Around_Players + 1))), input_subs={"a": a,
                                                                                                "b": b}))



    complete_rules = []


    # No self play
    complete_rules.append(forall(Play, lambda play: NEQ(play.a, play.b)))

    def daily_player_init(dpc):
        return AND(EQ(dpc.b, Int(0)), EQ(dpc.count, Int(0)))

    def daily_player_no_change(old_dpc, dpc):
        return AND(
            EQ(old_dpc.count, dpc.count),
            NOT(exist(Play, lambda play, dpc=dpc, old_dpc = old_dpc:
                      AND(
                          # the play happen at the same time
                          EQ(play.time, dpc.time),
                          EQ(play.a, dpc.a),
                          play.b <= dpc.b,
                          play.b > old_dpc.b
                      )
                      ))
        )

    def daily_player_change(old_dpc, dpc):
        return AND(
            EQ(dpc.count, old_dpc.count + 1),
            exist(Play, lambda play, dpc=dpc, old_pc =old_dpc:
            AND(
                # the play happen at the same time
                EQ(play.time, dpc.time),
                EQ(play.a, dpc.a),
                play.b <= dpc.b,
                play.b > old_dpc.b
            )
            )
        )


    def daily_player_update(dpc):
        return exist(DPC, lambda old_dpc, dpc=dpc:
                     AND(
                            EQ(old_dpc.a, dpc.a),
                            EQ(old_dpc.time, dpc.time),
                            old_dpc.b < dpc.b,
                         OR(
                            daily_player_no_change(old_dpc, dpc),
                            daily_player_change(old_dpc, dpc)
                         )
                     )
                     )

    def daily_player_status(dpc):
        return OR(
            daily_player_init(dpc),
            daily_player_update(dpc)
        )

    def DPC_update_rule(play):
        return exist([DPC, DPC], lambda dpc, old_dpc:
                     AND(
                         EQ(play.a, dpc.a),
                         EQ(dpc.a, old_dpc.a),
                         EQ(play.time, dpc.time),
                         EQ(dpc.time, old_dpc.time),
                         # check count
                         EQ(dpc.count, old_dpc.count + Int(1)),
                         EQ(dpc.b, play.b),
                         dpc.b > old_dpc.b,
                         NOT(exist(DPC, lambda other_dpc, dpc=dpc, old_dpc=old_dpc:
                                   AND(EQ(other_dpc.a, dpc.a),
                                       EQ(other_dpc.time, dpc.time),
                                       other_dpc.b < dpc.b,
                                       old_dpc.b > other_dpc.b
                                       ),
                                   ))
                     )
                     )


    complete_rules.append(forall(DPC, lambda dpc: daily_player_status(dpc)))
    complete_rules.append(forall(Play, lambda p: DPC_update_rule(p)))
    complete_rules.append(NOT(exist([Play, Play], lambda p1, p2:
                                    AND(
                                        EQ(p1.a, p2.a),
                                        EQ(p1.b, p2.b),
                                        EQ(p1.time, p2.time),
                                        NEQ(p1.id, p2.id)
                                    )
                                    )))


    def daily_play_count_no_more(id, time, threshold):
        return exist(DPC, lambda dpc:
                    AND(
                        EQ(dpc.a, id),
                        EQ(dpc.time, time),
                        dpc.count <= Int(threshold),
                        # there is no more count greater than the current
                        NOT(exist(DPC, lambda other_dpc, dpc=dpc:
                               AND(
                                   EQ(other_dpc.a, dpc.a),
                                   EQ(other_dpc.time, dpc.time),
                                   other_dpc.b > dpc.b
                               )
                               ))
                    )
                     )



    # at any point, A player should not play with more than Group_Size of players at one time
    complete_rules.append(forall(Play, lambda p: daily_play_count_no_more(p.a, p.time, Group_Size)))


    # play id corresponding time
    complete_rules.append(forall([Play, Play], lambda p1, p2:
                                 Implication(p1 > p2, p1.id > p2.id)
                                 ))

    def poc_init(poc):
        return AND(
            EQ(poc.count, Int(0)),
            EQ(poc.id, Int(-1))
        )

    def poc_no_change(poc, old_poc):
        return AND(
            EQ(poc.count, old_poc.count),
            NOT(exist(Play, lambda play, poc=poc, old_poc = old_poc:
                      AND(
                          EQ(play.a, poc.a),
                          NEQ(play.b, poc.b),
                          play.id <= poc.id,
                          play.id > old_poc.id,
                          play.time < poc.time,
                          play.time > poc.previous_time
                      )
                      ))
        )

    def poc_change(poc, old_poc):
        return AND(
            EQ(poc.count, old_poc.count + Int(1)),
            exist(Play, lambda play, poc=poc, old_poc=old_poc:
            AND(
                EQ(play.a, poc.a),
                NEQ(play.b, poc.b),
                play.id <= poc.id,
                play.id > old_poc.id,
                play.time < poc.time,
                play.time > poc.previous_time
            )
        )
        )

    def poc_update(poc):
        return AND(
            # poc.id >=0,
            exist(POC, lambda old_poc, poc = poc:
                     AND(EQ(poc.time, old_poc.time),
                         EQ(poc.previous_time, old_poc.previous_time),
                         EQ(poc.a, old_poc.a),
                         EQ(poc.b, old_poc.b),
                         poc.id > old_poc.id,
                         OR(
                             poc_no_change(poc, old_poc),
                             poc_change(poc, old_poc)
                         )
                     )

                     ))

    def player_with_other_count(poc):
        return OR(
            poc_init(poc),
            poc_update(poc)
        )



    # now, add the validity of POC
    complete_rules.append(forall(POC, lambda poc:
                    player_with_other_count(poc)
                                 ))


    def poc_no_less(a, b, time, old_time, threshold):
        return exist(POC, lambda poc, a=a, b=b, time=time, old_time=old_time, threshold= threshold:
                     AND(
                         EQ(poc.a, a),
                         EQ(poc.b, b),
                         EQ(poc.time, time),
                         EQ(poc.previous_time, old_time),
                         poc.count >= Int(threshold),
                         # we need to show this is the final count
                         NOT(exist(POC, lambda poc_other, poc=poc:
                                   AND(
                                       EQ(poc.a, poc_other.a),
                                       EQ(poc.b, poc_other.b),
                                       EQ(poc.time, poc_other.time),
                                       EQ(poc.previous_time, poc_other.previous_time),
                                       poc_other.id > poc.id
                                       )

                         ))
                     )

                     )

    # if A plays with B, then it must play with at least Turn_Around_Players players before play with B again
    complete_rules.append(forall([Play, Play], lambda p1, p2:
    Implication(AND(EQ(p1.a, p2.a), EQ(p1.b, p2.b), p1 < p2),
                poc_no_less(p1.a, p1.b, p2.time, p1.time, Turn_Around_Players)
                # Count(Play, lambda p3: AND(EQ(p3.a, p1.a),
                #                            NEQ(p3.b, p2.b),
                #                            p3 > p1,
                #                            p3 < p2
                #                            ), trigger_act=p2, input_subs={"a": p1.a}) >= Int(Turn_Around_Players)
                )
                                 ))

    complete_rules.append(forall(PTC, lambda ptc: PTC_status(ptc)))

    complete_rules.append(forall(Friend, lambda f: friend(f.a, f.b, f.time, f)
                                 ))



    # property, exists a user who has at least one friend who befriended everyone he ever played with
    target_rule = exist(Friend, lambda f: forall(Play, lambda play: Implication(EQ(f.a, play.a),
                                                                           exist(Friend,
                                                                                 lambda f1: AND(EQ(play.a, f1.a),
                                                                                                EQ(play.b, f1.b),
                                                                                                EQ(f.time, f1.time)),
                                                                                 input_subs={"a": play.a, "b": play.b, "time":f.time})
                                                                           )), input_subs=({"a": Int(1), "b": Int(2)}))

    # target_rule = exist([Play, Play], lambda p1, p2:
    #                     AND(EQ(p1.a, p2.a),
    #                         EQ(p1.b, p2.b),
    #                         p1 > p2
    #                         )
    #                     )

    # target_rule = exist(Friend, lambda f: TRUE())

    rules = set()
    start = time.time()
    check_property_fol(target_rule, complete_rules, ACTION)
    print(time.time() - start)
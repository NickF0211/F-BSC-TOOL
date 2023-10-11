import sys
sys.path.append('../Analyzer')
from logic_operator import *
import time
from analyzer import check_property_refining

'''
TODO: The domain file need to be linked
'''


from graph_domain_wr import *

#now we write rules here, we want to being able to construct a tree with a single root



def is_node_available(node, time, add_node = None):
    if add_node and isinstance(add_node, AddNode):
        return AND(add_node.time <= time, NOT(exist(RemoveNode, lambda rn: AND(EQ(rn.node, add_node.node), rn.time <= time, rn > add_node))))
    else:
        return since(AddNode, lambda an: EQ(an.node, node), RemoveNode, lambda rn:
                     EQ(rn.node, node),time, input_subs={"node":node})

def same_edge(edge, f, t):
    return AND(EQ(edge.f, f), EQ(edge.t, t))

def is_edge_available(f, t, time, add_edges = None):
    if add_edges:
        return AND(add_edges <= time, same_edge(add_edges, f, t),
                   NOT(exist(RemoveEdge, lambda re: AND(same_edge(re, f, t), add_edges < re, re <= time))))
    return since(AddEdge, lambda ae: same_edge(ae, f, t), RemoveEdge, lambda re:
    same_edge(re, f, t), time, input_subs={"f":f, "t":t})

def has_edge_established(f, t, time):
    return once(AddEdge, lambda ae: same_edge(ae, f, t), time, input_subs={"f":f, "t":t})

def has_parent(node, time):
    return once(AddEdge, lambda ae: AND( EQ(ae.t, node),
                                        is_edge_available(ae.f, ae.t, time, add_edges=ae)), time, input_subs={"t":node})

def has_child(node, time):
    return once(AddEdge, lambda ae: AND(EQ(ae.f, node),
                                        is_edge_available(ae.f, ae.t, time, add_edges=ae)), time, input_subs={"f":node})

# a node is a root if it doesn't have any parent
def is_root(node, time):
    return AND(is_node_available(node, time),
               has_parent(node, time))




#
# def get_num_child(node, time, trigger_action, historical = False):
#     if historical:
#         return Count(AddEdge, lambda ae: AND(EQ(ae.f, node),
#                                              has_edge_established(ae.f, ae.t, time)), trigger_act=trigger_action)
#     else:
#         return Count(AddEdge, lambda ae: AND(EQ(ae.f, node),
#                                                               is_edge_available(ae.f, ae.t, time)), trigger_act=trigger_action)
#
# def get_num_parent(node, time, tigger_action, historical = False):
#     if historical:
#         return Count(AddEdge, lambda ae: AND(EQ(ae.t, node),
#                                              has_edge_established(ae.f, ae.t, time)), trigger_act=tigger_action)
#     else:
#         return Count(AddEdge, lambda ae: AND(EQ(ae.t, node),
#                                                               is_edge_available(ae.f, ae.t, time)), trigger_act=tigger_action)

# get_num_child = make_predicate(_get_num_child, 2)
# get_num_parent = make_predicate(_get_num_parent, 2)

complete_rules = []

'''
part1: NOC
'''
def init_NOC(noc):
    return AND(EQ(noc.id, Int(-1)), EQ(noc.count, Int(0)))


def edge_added_child(new_counter, old_counter):
        return exist(AddEdge, lambda ae, new_c=new_counter, old_c=old_counter:
        AND(
            EQ(ae.f, new_c.node),
            ae.id <= new_c.id,
            ae.id > old_c.id,
            is_edge_available(ae.f, ae.t, new_c.time),
            NOT(exist(AddEdge, lambda ae2, ae=ae:
                      AND(EQ(ae2.f, ae.f),
                          EQ(ae2.t, ae.t),
                          ae2.id < ae.t)
                      ))
        )
        )



def no_change_NOC(noc, old_noc):
    return AND(
        EQ(noc.count, old_noc.count),
        NOT(edge_added_child(noc, old_noc))
    )


def change_NOC(noc, old_noc):
    return AND(
        EQ(noc.count, old_noc.count + Int(1)),
        edge_added_child(noc, old_noc)
    )

def update_NOC(noc):
    return AND( noc.id >=0,
        exist(NOC, lambda old_noc, noc=noc:
              AND(EQ(noc.node, old_noc.node),
                  EQ(noc.time, old_noc.time),
                  noc.id > old_noc.id,
                  OR(
                      no_change_NOC(noc, old_noc),
                      change_NOC(noc, old_noc)
                  )
                  )
              ))

def NOC_status(noc):
    return OR(init_NOC(noc),
              update_NOC(noc))

complete_rules.append(forall(NOC, lambda noc: NOC_status(noc)))


'''
part2: HNOC
'''
def init_HNOC(noc):
    return AND(EQ(noc.id, Int(-1)), EQ(noc.count, Int(0)))


def edge_added_child_H(new_counter, old_counter):
        return exist(AddEdge, lambda ae, new_c=new_counter, old_c=old_counter:
        AND(
            EQ(ae.f, new_c.node),
            ae.id <= new_c.id,
            ae.id > old_c.id,
            has_edge_established(ae.f, ae.t, new_c.time),
            NOT(exist(AddEdge, lambda ae2, ae=ae:
                      AND(EQ(ae2.f, ae.f),
                          EQ(ae2.t, ae.t),
                          ae2.id < ae.t)
                      ))
        )
        )



def no_change_HNOC(noc, old_noc):
    return AND(
        EQ(noc.count, old_noc.count),
        NOT(edge_added_child_H(noc, old_noc))
    )


def change_HNOC(noc, old_noc):
    return AND(
        EQ(noc.count, old_noc.count + Int(1)),
        edge_added_child_H(noc, old_noc)
    )

def update_HNOC(noc):
    return AND( noc.id >=0,
        exist(HNOC, lambda old_noc, noc=noc:
              AND(EQ(noc.node, old_noc.node),
                  EQ(noc.time, old_noc.time),
                  noc.id > old_noc.id,
                  OR(
                      no_change_HNOC(noc, old_noc),
                      change_HNOC(noc, old_noc)
                  )
                  )
              ))

def HNOC_status(noc):
    return OR(init_HNOC(noc),
              update_HNOC(noc))

complete_rules.append(forall(HNOC, lambda noc: HNOC_status(noc)))



'''
part3: NOP
'''
def init_NOP(noc):
    return AND(EQ(noc.id, Int(-1)), EQ(noc.count, Int(0)))


def edge_added_parent(new_counter, old_counter):
        return exist(AddEdge, lambda ae, new_c=new_counter, old_c=old_counter:
        AND(
            EQ(ae.t, new_c.node),
            ae.id <= new_c.id,
            ae.id > old_c.id,
            is_edge_available(ae.f, ae.t, new_c.time),
            NOT(exist(AddEdge, lambda ae2, ae=ae:
                      AND(EQ(ae2.f, ae.f),
                          EQ(ae2.t, ae.t),
                          ae2.id < ae.t)
                      ))
        )
        )



def no_change_NOP(noc, old_noc):
    return AND(
        EQ(noc.count, old_noc.count),
        NOT(edge_added_parent(noc, old_noc))
    )


def change_NOP(noc, old_noc):
    return AND(
        EQ(noc.count, old_noc.count + Int(1)),
        edge_added_parent(noc, old_noc)
    )

def update_NOP(noc):
    return AND( noc.id >=0,
        exist(NOP, lambda old_noc, noc=noc:
              AND(EQ(noc.node, old_noc.node),
                  EQ(noc.time, old_noc.time),
                  noc.id > old_noc.id,
                  OR(
                      no_change_NOP(noc, old_noc),
                      change_NOP(noc, old_noc)
                  )
                  )
              ))

def NOP_status(noc):
    return OR(init_NOP(noc),
              update_NOP(noc))

complete_rules.append(forall(NOP, lambda noc: NOC_status(noc)))


'''
part4: HNOP
'''
def init_HNOP(noc):
    return AND(EQ(noc.id, Int(-1)), EQ(noc.count, Int(0)))


def edge_added_parent_H(new_counter, old_counter):
        return exist(AddEdge, lambda ae, new_c=new_counter, old_c=old_counter:
        AND(
            EQ(ae.t, new_c.node),
            ae.id <= new_c.id,
            ae.id > old_c.id,
            has_edge_established(ae.f, ae.t, new_c.time),
            NOT(exist(AddEdge, lambda ae2, ae=ae:
                      AND(EQ(ae2.f, ae.f),
                          EQ(ae2.t, ae.t),
                          ae2.id < ae.t)
                      ))
        )
        )



def no_change_HNOP(noc, old_noc):
    return AND(
        EQ(noc.count, old_noc.count),
        NOT(edge_added_parent_H(noc, old_noc))
    )


def change_HNOP(noc, old_noc):
    return AND(
        EQ(noc.count, old_noc.count + Int(1)),
        edge_added_parent_H(noc, old_noc)
    )

def update_HNOP(noc):
    return AND( noc.id >=0,
        exist(NOP, lambda old_noc, noc=noc:
              AND(EQ(noc.node, old_noc.node),
                  EQ(noc.time, old_noc.time),
                  noc.id > old_noc.id,
                  OR(
                      no_change_HNOP(noc, old_noc),
                      change_HNOP(noc, old_noc)
                  )
                  )
              ))

def HNOP_status(noc):
    return OR(init_HNOP(noc),
              update_HNOP(noc))

complete_rules.append(forall(HNOP, lambda noc: NOC_status(noc)))


'''
part 5: other rules
'''

complete_rules.append(forall([AddEdge, AddEdge], lambda e1, e2:
                            AND(
                             Implication(EQ(e1.id, e2.id), EQ(e1, e2)
                                         ),
                            Implication(e1 > e2, e1.id > e2.id)
                            )
                             ))

complete_rules.append(forall([AddNode, AddNode], lambda e1, e2:
                            AND(
                             Implication(EQ(e1.id, e2.id), EQ(e1, e2)
                                         ),
                            Implication(e1 > e2, e1.id > e2.id)
                            )
                             ))

#a node can be added if it was not already there
complete_rules.append(forall(AddNode, lambda an:
    NOT(is_node_available(an.node, an.time-1))))

#a node can be removed if it was already there
complete_rules.append(forall(RemoveNode, lambda rn:
    is_node_available(rn.node, rn.time-1)))

#a node can be removed if all of its edges have been removed
complete_rules.append(forall(RemoveNode, lambda rn:
    AND(NOT(has_child(rn.node, rn.time)),
                                                        NOT(has_parent(rn.node, rn.time)))))



#an edge can be added if the edge was not already there, and both f and t are available
complete_rules.append(forall(AddEdge, lambda ae: AND(is_node_available(ae.f, ae.time),
                                                     is_node_available(ae.t, ae.time),
                                                     NOT(is_edge_available(ae.f, ae.t, ae.time-1)))))

#no self edge is allowed
complete_rules.append(forall(AddEdge, lambda ae: NEQ(ae.f, ae.t)))

#each node can only have at most 1 parent
complete_rules.append(forall(AddEdge, lambda ae:AND(NOT(has_parent(ae.t, ae.time-1)),
                                                        NOT(exist(AddEdge, lambda ae1: AND(EQ(ae1.time, ae.time),
                                                                                           EQ(ae1.t, ae.t),
                                                                                           NEQ(ae1.f, ae.f)))))))

#an edge can be removed if the edge is available
complete_rules.append(forall(RemoveEdge, lambda re: is_edge_available(re.f, re.t, re.time-1)))



def HNOP_no_more_than(node, time, threshold):
    return exist(HNOP, lambda hnop, node=node, time=time, threshold = threshold:
                 AND(
                     EQ(hnop.time, time),
                     EQ(hnop.node, node),
                     hnop.count <= Int(threshold),
                     NOT(exist(HNOP, lambda other_hnop, hnop=hnop:
                            AND(
                                EQ(hnop.time, other_hnop.time),
                                EQ(hnop.node, other_hnop.node),
                                other_hnop.id > hnop.id
                            )
                            ))
                 )
                 )

def NOP_no_less_than(node, time, threshold):
    return exist(NOP, lambda hnop, node=node, time=time, threshold = threshold:
                 AND(
                     EQ(hnop.time, time),
                     EQ(hnop.node, node),
                     hnop.count >= Int(threshold),
                     NOT(exist(NOP, lambda other_hnop, hnop=hnop:
                            AND(
                                EQ(hnop.time, other_hnop.time),
                                EQ(hnop.node, other_hnop.node),
                                other_hnop.id > hnop.id
                            )
                            ))
                 )
                 )

def HNOC_no_more_than(node, time, threshold):
    return exist(HNOC, lambda hnop, node=node, time=time, threshold = threshold:
                 AND(
                     EQ(hnop.time, time),
                     EQ(hnop.node, node),
                     hnop.count <= Int(threshold),
                     NOT(exist(HNOC, lambda other_hnop, hnop=hnop:
                            AND(
                                EQ(hnop.time, other_hnop.time),
                                EQ(hnop.node, other_hnop.node),
                                other_hnop.id > hnop.id
                            )
                            ))
                 )
                 )

#tree
# tree_req = forall(AddEdge, lambda ae: get_num_parent(ae.f, ae.time, ae, historical=True) <= Int(2))
tree_req = forall(AddEdge, lambda ae: HNOP_no_more_than(ae.f, ae.time, 2))

# binary_tree_req = forall(AddEdge, lambda ae: get_num_child(ae.f, ae.time, ae, historical=True) <= Int(2))
binary_tree_req = forall(AddEdge, lambda ae: HNOC_no_more_than(ae.f, ae.time, 2))


# connected_rule = forall(AddNode, lambda an: get_num_parent(an.node, an.time, an) >= Int(1))
connected_rule = forall(AddNode, lambda an: NOP_no_less_than(an.node, an.time, 1) )


complete_rules.append(tree_req )
complete_rules.append(binary_tree_req)
complete_rules.append(connected_rule)

def make_available_nodes(node_target, t):
    constraints = []
    nodes = [AddNode(input_subs={"node": Int(i), "presence":TRUE()}) for i in range(node_target)]
    for node in nodes:
        constraints.append(is_node_available(node.node, t, add_node=node))
    return AND(constraints)


def nc_init(nc):
    return AND(EQ(nc.id, Int(-1)), EQ(nc.count, Int(0)))

def node_added(nc, old_nc):
    return exist(AddNode, lambda ad, nc=nc, old_nc = old_nc:
                    AND(
                        is_node_available(ad.node, nc.time),
                        ad.id <= nc.id,
                        ad.id > old_nc.id
                    )
                 )

def no_change_NC(nc, old_nc):
    return AND(
        EQ(nc.count, old_nc.count),
        NOT(node_added(nc, old_nc))

    )

def change_NC(nc, old_nc):
    return AND(
        EQ(nc.count, old_nc.count + Int(1)),
        node_added(nc, old_nc)
    )

def nc_update(nc):
    return AND(nc.id >= 0,
        exist(NC, lambda old_nc, nc = nc:
                AND(
                 EQ(old_nc.time, nc.time),
                 nc.id > old_nc.id,
                    OR(no_change_NC(nc, old_nc),
                       change_NC(nc, old_nc))
                )
                 ))


def NC_status(nc):
    return OR(nc_init(nc),
              nc_update(nc))

complete_rules.append(forall(NC, lambda nc: NC_status(nc)))

def NC_less_than(time, threshold):
    return exist(NC, lambda nc, time=time, threshold=threshold:
                 AND(
                     EQ(nc.time, time),
                     nc.count < Int(threshold),
                     NOT(exist(NC, lambda other_nc, nc =nc:
                               AND(
                                   EQ(nc.time, other_nc.time),
                                   other_nc.id > nc.id
                               )
                               ))
                 )
                 )

rule_1 = exist(Var, lambda var: make_available_nodes(2, var.v))
rule_2 = exist(Var, lambda var: make_available_nodes(4, var.v))
rule_3 = exist(Var, lambda var: make_available_nodes(6, var.v))
rule_4 = exist(Var, lambda var: make_available_nodes(8, var.v))
rule_5 = exist(Var, lambda var: make_available_nodes(10, var.v))
rule_6 = exist(Var, lambda var: make_available_nodes(12, var.v))
rule_7 = exist([Var, Var], lambda var1, var2:
                AND(make_available_nodes(5, var1.v),
                    NC_less_than(var2.v, 5),
                   # Count(AddNode, lambda addnode1: is_node_available(addnode1.node, var2.v, add_node=addnode1)) < Int(5),
                    var1.v < var2.v)
                )
rule_8 = exist([Var, Var], lambda var1, var2:
                AND(make_available_nodes(6, var1.v),
                    NC_less_than(var2.v, 5),
                   # Count(AddNode, lambda addnode1: is_node_available(addnode1.node, var2.v, add_node=addnode1)) < Int(5),
                    var1.v < var2.v)
                )
rule_9 = exist([Var, Var], lambda var1, var2:
                AND(make_available_nodes(7, var1.v),
                    NC_less_than(var2.v, 5),
                   # Count(AddNode, lambda addnode1: is_node_available(addnode1.node, var2.v, add_node=addnode1)) < Int(5),
                    var1.v < var2.v)
                )
rule_10 = exist([AddEdge, AddEdge, AddEdge, AddEdge], lambda ae1, ae2, ae3, ae4:
                               AND(EQ(ae1.t, ae2.f),
                                   EQ(ae2.t, ae3.f),
                                   EQ(ae3.t, ae4.f)))

rule_11 = exist([Var, Var, Var, TimeStamp], lambda v1, v2, v3, t: AND( NEQ(v3.v, v1.v),
                                                                                is_node_available(v1.v, t.time),
                                                                                is_node_available(v2.v, t.time),
                                                                                is_node_available(v3.v, t.time),
                                                                                is_edge_available(v3.v, v2.v, t.time),
                                                                                is_edge_available(v1.v, v2.v, t.time)))



if __name__ == '__main__':
    args = sys.argv[1:]
    target_rule = globals()["rule_{}".format(args[0])]

    args = args[1:]

    restart = False
    bcr = False
    ub = False
    mymin = True
    arg_len = len(args)
    if arg_len >= 1:
        restart = args[0].lower().startswith('t')
    if arg_len >= 2:
        bcr = args[1].lower().startswith('t')
    if arg_len >= 3:
        ub = args[2].lower().startswith('t')
    if arg_len >= 4:
        mymin = args[3].lower().startswith('t')


    start = time.time()
    '''
    TODO: Specify parameters, the following parameters need to 
    be changed based on parsed input  
    '''
    is_minimized = False
    complete_rules = add_background_theories(ACTION, state_action, complete_rules, bcr)
    check_property_refining(target_rule, set(), complete_rules, ACTION, state_action, True, min_solution=mymin,
                            final_min_solution=True, restart=restart, boundary_case=bcr, universal_blocking=ub)
    print(time.time() - start)

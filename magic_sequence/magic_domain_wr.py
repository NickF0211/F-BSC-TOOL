from type_constructor import create_type, create_action, create_pair_action
from random import randint
type_dict = dict()

N = 10000
knat = create_type("knat", type_dict, lower_bound=-1, upper_bound=N)
nat = create_type("nat", type_dict, lower_bound=0, upper_bound=N)
time = create_type("time", type_dict, lower_bound=0)

Magic = create_action("Magic", [("x", "nat"), ("y", "nat"), ("time", "time")],type_dict)
Magic_count = create_action("Magic_count", [("y", "nat"), ("x", "knat"), ("count", "nat"), ("time", "time")], type_dict)
TimeStamp = create_action("TimeStamp", [("time", "time")],type_dict)


ACTION = [TimeStamp, Magic, Magic_count]
state_action = [TimeStamp]

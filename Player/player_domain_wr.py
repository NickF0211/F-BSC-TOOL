from type_constructor import create_type, create_action, create_pair_action
type_dict = dict()

player = create_type("player", type_dict, lower_bound=1)
time = create_type("time", type_dict, lower_bound=0)
nat = create_type("nat", type_dict, lower_bound=0)
counter = create_type("counter", type_dict, lower_bound=-1)

Play = create_action("Play", [("a", "player"), ("b", "player"), ("id", "nat"), ("time", "time")],type_dict)
Friend = create_action("Friend", [("a", "player"), ("b", "player"), ("time", "time")],type_dict)
TimeStamp = create_action("TimeStamp", [("time", "time")],type_dict)
DPC = create_action("DailyPlayCount", [("a", "player"), ("b", "nat"), ("time", "time"), ("count", "nat")], type_dict)
PTC = create_action("PlayTogetherCount", [("a", "player"), ("b", "nat"), ("time", "time"), ("count", "nat"), ("id", "counter")], type_dict)
POC = create_action("PlayWithOthersCount", [("a", "player"), ("b", "nat"), ("id", "counter"),
                                          ("time", "time"), ("previous_time", "time"), ("count", "nat")], type_dict)

ACTION = [TimeStamp, Play, Friend, DPC, PTC, POC]
state_action = [TimeStamp]

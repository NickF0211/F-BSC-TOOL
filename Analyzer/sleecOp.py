from pysmt.fnode import FNode

from logic_operator import *
from logic_operator import _polymorph_args_to_tuple


def unless(*args, reference=None):
    # if no consequence, then the defeater is on the condition
    cum_condition = TRUE()
    constraints = []
    processed = _polymorph_args_to_tuple(args)
    for i in range(len(processed) - 1, -1, -1):
        condition, action = processed[i]
        if reference:
            if i == 0:
                pass
            else:
                d = reference.defeater[i - 1]
                t_cond, t_resp = d.expr, d.response
                condition = check_and_mark(condition, t_cond)
                action = check_and_mark(action, t_resp)

        constraints.append(Implication(AND(cum_condition, condition), action))
        cum_condition = AND(cum_condition, NOT(condition))
    return AND(constraints)


# TODO, convert to xor
def otherwise(cond, primary, alt):
    return Implication(cond, OR(primary, alt))


M = None


def complie_measure(MEASURE):
    global M
    M = MEASURE


def check_and_mark(expr, reference):
    if reference and isinstance(expr, FNode) and expr.get_type() == BOOL:
        expr = Bool_Terminal(expr)
        text_ref[expr] = reference
    return expr


def when_assert(trigger, action, rule_condition=None, reference=None):
    if reference:
        t_trigger = reference.trigger
        t_condition = reference.condition
    else:
        t_trigger = t_condition = None

    if rule_condition is None:
        return exist(trigger, lambda t, t_trigger=t_trigger: exist(M, lambda m: AND(EQ(t.time, m.time),
                                                                                     NOT(action(t, m))
                                                                                     )), reference=t_trigger)
    else:
        return exist(trigger,
                      lambda t, t_trigger=t_trigger, t_condition=t_condition: exist(M, lambda m: AND(EQ(t.time, m.time),
                                                                                                     AND(check_and_mark(
                                                                                                         rule_condition(
                                                                                                             t, m),
                                                                                                         t_condition),
                                                                                                         NOT(action(t, m)))
                                                                                                     )),
                      reference=t_trigger)


def when(trigger, action, rule_condition=None, reference=None):
    if reference:
        t_trigger = reference.trigger
        t_condition = reference.condition
    else:
        t_trigger = t_condition = None

    if rule_condition is None:
        return forall(trigger, lambda t, t_trigger=t_trigger: exist(M, lambda m: AND(EQ(t.time, m.time),
                                                                                     action(t, m)
                                                                                     )), reference=t_trigger)
    else:
        return forall(trigger,
                      lambda t, t_trigger=t_trigger, t_condition=t_condition: exist(M, lambda m: AND(EQ(t.time, m.time),
                                                                                                     OR(check_and_mark(
                                                                                                         NOT(rule_condition(
                                                                                                             t, m)),
                                                                                                         t_condition),
                                                                                                         action(t, m))
                                                                                                     )),
                      reference=t_trigger)


def when_concern(trigger, action, rule_condition=None, reference=None):
    if reference:
        t_trigger = reference.trigger
        t_condition = reference.condition
    else:
        t_trigger = t_condition = None

    if rule_condition is None:
        return exist(trigger, lambda t, t_trigger=t_trigger: exist(M, lambda m: AND(EQ(t.time, m.time),
                                                                                    action(t, m)
                                                                                    )), reference=t_trigger)
    else:
        return exist(trigger,
                     lambda t, t_trigger=t_trigger, t_condition=t_condition: exist(M, lambda m: AND(EQ(t.time, m.time),
                                                                                                    AND(check_and_mark(
                                                                                                        rule_condition(
                                                                                                            t, m),
                                                                                                        t_condition),
                                                                                                        action(t, m))
                                                                                                    )),
                     reference=t_trigger)


def when_premise(trigger, rule_condition, reference=None):
    if reference:
        t_trigger = reference.trigger
        t_condition = reference.condition
    else:
        t_trigger = t_condition = None

    if rule_condition is None:
        return exist([trigger, M], lambda t, m: EQ(t.time, m.time), reference=t_trigger)
    else:
        return exist([trigger, M], lambda t, m: AND(EQ(t.time, m.time), check_and_mark(rule_condition(t, m), t_condition)),
                     reference=t_trigger)


def valid(t, rule_condition):
    if rule_condition is None:
        return TRUE()
    else:
        return exist(M, lambda m, t=t, cond=rule_condition: AND(EQ(m.time, t.time), cond(t, m)))


def last(last_t, trigger, rule_condition):
    return forall(trigger, lambda t, last_t=last_t, cond=rule_condition:
    Implication(valid(t, cond), last_t >= t))


def when_last_trigger(trigger, rule_condition, reference=None):
    return Implication(exist(trigger,
                             lambda t, trigger=trigger, rule_condition=rule_condition: valid(t, rule_condition)),
                       exist(trigger, lambda t_last,
                                             trigger=trigger,
                                             rule_condition=rule_condition:
                       AND(valid(t_last,
                                 rule_condition),
                           last(t_last, trigger,
                                rule_condition)
                           )
                             )
                       )


def happen_within(target_class, reference, start, end, constraints=None, ref=None):
    def make_constraint(t, reference=reference, start=start, end=end, ref=ref):
        lower_limit = t.time >= reference.time + start
        upper_limit = t.time <= reference.time + end

        if ref and ref.limit:
            lower_limit = t.time >= reference.time + start
            upper_limit = t.time <= reference.time + end
            lower_limit = Bool_Terminal(lower_limit)
            upper_limit = Bool_Terminal(upper_limit)

            text_ref[lower_limit] = ref.limit.start
            text_ref[upper_limit] = ref.limit.end
            res = AND(upper_limit, lower_limit)
        else:
            res = AND(upper_limit, lower_limit)
        return res

    def make_constraint_unlimited(t, reference=reference, ref=ref):
        term = t.time >= reference.time
        if ref:
            res = Bool_Terminal(term)
            text_ref[res] = ref.inf
        else:
            res = term
        return res

    if ref is not None:
        event = ref.event
    else:
        event = None

    if end >= 0:
        if constraints is None:
            return exist(target_class, lambda t: make_constraint(t, reference, start, end, ref), reference=event)
        else:
            return exist(target_class,
                         lambda t: AND(make_constraint(t, reference, start, end, ref), constraints(t, reference)),
                         reference=event)
    else:
        if constraints is None:
            return exist(target_class, lambda t: make_constraint_unlimited(t, reference, ref), reference=event)
        else:
            return exist(target_class,
                         lambda t: AND(make_constraint_unlimited(t, reference, ref), constraints(t, reference)),
                         reference=event)


class Concern():
    def __init__(self, trigger, action, rule_condition=None, reference=None, next=None):
        self.concern = when_concern(trigger, action, rule_condition=rule_condition, reference=reference)
        self.next = next

    def get_concern(self):
        if not self.next:
            return self.concern
        else:
            return AND(self.next.get_concern(), self.concern)


class WhenRule:

    def __init__(self, trigger, action, neg_action, rule_condition=None, reference=None):
        self.rule = when(trigger, action, rule_condition=rule_condition, reference=reference)
        self.neg_rule = when_assert(trigger, neg_action, rule_condition=rule_condition, reference=reference)
        self.premise = when_premise(trigger, rule_condition=rule_condition, reference=reference)
        self.last_trigger = when_last_trigger(trigger, rule_condition, reference)

    def get_rule(self):
        return self.rule

    def get_neg_rule(self):
        return self.neg_rule

    def get_premise(self):
        return self.premise

    def encode(self):
        return encode(self.get_rule())


def process_event(op_str, lhs, rhs, reference):
    if op_str == "witness":
        return forall(lhs, lambda l, rhs=rhs: exist(rhs, lambda r: EQ(r.time, l.time)), reference=reference)
    # elif op_str == "exclusion":
    #     return forall(lhs, lambda l, rhs=rhs: NOT(exist(rhs, lambda r: EQ(r.time, l.time))), reference=reference)
    elif op_str == "coincide":
        return AND(forall(lhs, lambda l, rhs=rhs: exist(rhs, lambda r: EQ(r.time, l.time)), reference=reference),
                   forall(rhs, lambda r, lhs=lhs: exist(lhs, lambda l: EQ(r.time, l.time)), reference=reference))
    elif op_str == "conflict":
        return AND(forall(lhs, lambda l, rhs=rhs: NOT(exist(rhs, lambda r: EQ(r.time, l.time))), reference=reference),
            forall(rhs, lambda r, lhs=lhs: NOT(exist(lhs, lambda l: EQ(r.time, l.time))), reference=reference))
    elif op_str == "happenBefore":
        return forall(rhs, lambda r, lhs=lhs: exist(lhs, lambda l: l < r), reference=reference)
    else:
        print("unsupport rel: {}".format(op_str))
        assert False


class EventRelation:
    def __init__(self, op, lhs, rhs, reference=None):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
        self.reference = reference
        self.encoded = None
        # self.encoded = process_event(self.op, self.lhs, self.rhs, self.reference)

    def clear(self):
        if self.encoded:
            self.encoded.clear()

    def encode(self, refresh=False):
        if self.encoded and not refresh:
            return self.encoded
        else:
            self.encoded = process_event(self.op, self.lhs, self.rhs, self.reference)
            return self.encoded


class MeasureRelation:
    def __init__(self, expr, reference=None):
        self.expr = expr
        self.reference = reference
        self.encoded = None

    def clear(self):
        if self.encoded:
            self.encoded.clear()

    def encode(self, refresh=False):
        if self.encoded and not refresh:
            return self.encoded
        else:
            self.encoded = forall(M,
                                  lambda m, self=self:
                                    check_and_mark(self.expr(m), self.reference),
                                  self.reference)
            return self.encoded


class Causation:

    def __init__(self, cause, effect, reference = None):
        self.cause = cause
        self.effect = effect
        self.reference = reference
        self.encoded = None

    def clear(self):
        if self.encoded:
            self.encoded.clear()

    def encode(self, refresh=False):
        if self.encoded and not refresh:
            return self.encoded
        else:
            self.encoded = forall(M,
                                  lambda m, self=self:
                                    Implication(check_and_mark(self.effect(m), self.reference.effect),
                                                exist(self.cause, lambda c, m=m, self=self:
                                                      EQ(c.time, m.time), reference=self.reference.cause
                                                      ))
                                  )
            return self.encoded


class Effect:

    def __init__(self, cause, effect, reference = None):
        self.cause = cause
        self.effect = effect
        self.reference = reference
        self.encoded = None

    def clear(self):
        if self.encoded:
            self.encoded.clear()

    def encode(self, refresh=False):
        if self.encoded and not refresh:
            return self.encoded
        else:
            self.encoded = forall(self.cause,
                                  lambda c, self=self:
                                            exist(M, lambda m, c=c, self=self:
                                                      AND(EQ(c.time, m.time),
                                                          check_and_mark(self.effect(m), self.reference.effect)
                                                      )
                                  ), reference=self.reference.cause)
            return self.encoded





class Rule:
    def __init__(self, name, citation, produces, condition, action):
        self.name = name          # human-readable rule name
        self.citation = citation  # statutory clause, e.g. "Section 80C"
        self.produces = produces  # the fact key this rule derives
        self.condition = condition  # function(facts) -> bool
        self.action = action        # function(facts) -> value

    def can_fire(self, facts):
        return self.produces not in facts and self.condition(facts)

    def fire(self, facts):
        facts[self.produces] = self.action(facts)


def forward_chain(initial_facts, rules):
    facts = dict(initial_facts)
    trace = []
    changed = True
    while changed:
        changed = False
        for rule in rules:
            if rule.can_fire(facts):
                rule.fire(facts)
                trace.append({
                    "rule": rule.name,
                    "citation": rule.citation,
                    "derived_fact": rule.produces,
                    "value": facts[rule.produces],
                })
                changed = True
    return facts, trace


class Rule:
    def __init__(self, name, citation, produces, condition, action, depends_on=None):
        self.name = name
        self.citation = citation
        self.produces = produces
        self.condition = condition
        self.action = action
        self.depends_on = depends_on or []  # fact keys this rule actually reads

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
                    "depends_on": rule.depends_on,
                })
                changed = True
    return facts, trace

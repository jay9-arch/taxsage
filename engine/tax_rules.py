from engine.rule_engine import Rule, forward_chain

def slab_tax(taxable_income, slabs):
    tax = 0
    lower = 0
    for upper, rate in slabs:
        if upper is None or taxable_income > upper:
            span = (upper - lower) if upper is not None else (taxable_income - lower)
        else:
            span = taxable_income - lower
        if taxable_income > lower:
            taxed_amount = min(span, taxable_income - lower)
            tax += taxed_amount * rate
        lower = upper if upper is not None else taxable_income
        if upper is not None and taxable_income <= upper:
            break
    return round(tax)

OLD_SLABS = [(250000, 0.0), (500000, 0.05), (1000000, 0.20), (None, 0.30)]
NEW_SLABS = [(400000, 0.0), (800000, 0.05), (1200000, 0.10),
             (1600000, 0.15), (2000000, 0.20), (2400000, 0.25), (None, 0.30)]

old_regime_rules = [
    Rule("std_deduction_old", "Section 16(ia)", "std_deduction_old",
         lambda f: "gross_income" in f, lambda f: 50000,
         depends_on=["gross_income"]),

    Rule("cap_80C", "Section 80C", "capped_80C",
         lambda f: "section_80C" in f, lambda f: min(f["section_80C"], 150000),
         depends_on=["section_80C"]),

    Rule("cap_80D", "Section 80D", "capped_80D",
         lambda f: "section_80D" in f, lambda f: min(f["section_80D"], 25000),
         depends_on=["section_80D"]),

    Rule("hra_pass_through", "Section 10(13A)", "capped_hra",
         lambda f: "hra_exemption" in f, lambda f: f["hra_exemption"],
         depends_on=["hra_exemption"]),

    Rule("taxable_income_old", "Derived (Old Regime)", "taxable_income_old",
         lambda f: "gross_income" in f and "std_deduction_old" in f
                    and "capped_80C" in f and "capped_80D" in f and "capped_hra" in f,
         lambda f: max(0, f["gross_income"] - f["std_deduction_old"]
                       - f["capped_80C"] - f["capped_80D"] - f["capped_hra"]),
         depends_on=["gross_income", "std_deduction_old", "capped_80C", "capped_80D", "capped_hra"]),

    Rule("tax_before_rebate_old", "Old Regime Slabs", "tax_before_rebate_old",
         lambda f: "taxable_income_old" in f,
         lambda f: slab_tax(f["taxable_income_old"], OLD_SLABS),
         depends_on=["taxable_income_old"]),

    Rule("rebate_87A_old", "Section 87A", "tax_after_rebate_old",
         lambda f: "taxable_income_old" in f and "tax_before_rebate_old" in f,
         lambda f: 0 if f["taxable_income_old"] <= 500000 else f["tax_before_rebate_old"],
         depends_on=["taxable_income_old", "tax_before_rebate_old"]),

    Rule("cess_old", "Health & Education Cess", "final_tax_old",
         lambda f: "tax_after_rebate_old" in f,
         lambda f: round(f["tax_after_rebate_old"] * 1.04),
         depends_on=["tax_after_rebate_old"]),
]

new_regime_rules = [
    Rule("std_deduction_new", "Section 16(ia) (New Regime)", "std_deduction_new",
         lambda f: "gross_income" in f, lambda f: 75000,
         depends_on=["gross_income"]),

    Rule("taxable_income_new", "Derived (New Regime)", "taxable_income_new",
         lambda f: "gross_income" in f and "std_deduction_new" in f,
         lambda f: max(0, f["gross_income"] - f["std_deduction_new"]),
         depends_on=["gross_income", "std_deduction_new"]),

    Rule("tax_before_rebate_new", "New Regime Slabs (Sec 115BAC)", "tax_before_rebate_new",
         lambda f: "taxable_income_new" in f,
         lambda f: slab_tax(f["taxable_income_new"], NEW_SLABS),
         depends_on=["taxable_income_new"]),

    Rule("rebate_87A_new", "Section 87A (New Regime)", "tax_after_rebate_new",
         lambda f: "taxable_income_new" in f and "tax_before_rebate_new" in f,
         lambda f: 0 if f["taxable_income_new"] <= 1200000 else f["tax_before_rebate_new"],
         depends_on=["taxable_income_new", "tax_before_rebate_new"]),

    Rule("cess_new", "Health & Education Cess", "final_tax_new",
         lambda f: "tax_after_rebate_new" in f,
         lambda f: round(f["tax_after_rebate_new"] * 1.04),
         depends_on=["tax_after_rebate_new"]),
]

def compute_tax(profile):
    defaults = {"section_80C": 0, "section_80D": 0, "hra_exemption": 0}
    initial_facts = {**defaults, **profile}
    old_facts, old_trace = forward_chain(initial_facts, old_regime_rules)
    new_facts, new_trace = forward_chain(initial_facts, new_regime_rules)
    return old_facts, old_trace, new_facts, new_trace

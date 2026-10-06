from engine.tax_rules import compute_tax

def find_breakeven_deduction(gross_income, existing_80C=0, existing_80D=0,
                              existing_hra=0, tolerance=100, max_deduction=2000000):
    """
    Finds the extra deduction amount (beyond what's already claimed) needed
    under the Old Regime so that Old Regime tax <= New Regime tax.
    """
    base_profile = {"gross_income": gross_income}
    _, _, new_facts, _ = compute_tax(base_profile)
    new_regime_tax = new_facts["final_tax_new"]

    def old_tax_with_extra(extra):
        profile = {
            "gross_income": gross_income,
            "section_80C": existing_80C,
            "section_80D": existing_80D,
            "hra_exemption": existing_hra + extra,
        }
        old_facts, _, _, _ = compute_tax(profile)
        return old_facts["final_tax_old"]

    low, high = 0, max_deduction
    if old_tax_with_extra(low) <= new_regime_tax:
        return {"breakeven_extra_deduction": 0,
                "note": "Old Regime is already cheaper or equal with current deductions.",
                "new_regime_tax": new_regime_tax,
                "old_regime_tax_at_zero_extra": old_tax_with_extra(low)}

    if old_tax_with_extra(high) > new_regime_tax:
        return {"breakeven_extra_deduction": None,
                "note": f"Even ₹{max_deduction:,} of extra deductions isn't enough to beat the New Regime.",
                "new_regime_tax": new_regime_tax}

    iterations = 0
    while high - low > tolerance:
        mid = (low + high) // 2
        if old_tax_with_extra(mid) <= new_regime_tax:
            high = mid
        else:
            low = mid
        iterations += 1

    return {"breakeven_extra_deduction": high,
            "new_regime_tax": new_regime_tax,
            "old_regime_tax_at_breakeven": old_tax_with_extra(high),
            "search_iterations": iterations}

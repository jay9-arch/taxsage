# Held-out evaluation set — intentionally written in a different, messier
# style than the training data to test genuine generalization, not just
# memorized phrasing patterns.

EVAL_SET = [
    ("can my mom count as someone i pay rent to for hra", "rag"),
    ("does health insurance for my wife count under 80d", "rag"),
    ("so if i go new regime i lose all my deductions right", "rag"),
    ("whats the deal with home loan interest can i deduct that", "rag"),
    ("i dont have proof of rent paid will that be an issue", "rag"),
    ("quick q - are freelancers even eligible for hra", "rag"),

    ("23l income new regime wyd tax come to", "compute"),
    ("ok so if i make 6.5 lakhs and claim nothing whats my tax", "compute"),
    ("27 lakhs old regime with 1L in 80c, number pls", "compute"),
    ("8 lakh salary tax ???", "compute"),
    ("made 31 lakhs this yr need the tax number", "compute"),
    ("4.5l income owe how much", "compute"),

    ("is 80d a thing for me and also whats my tax, 15L income 20k premium", "both"),
    ("ok explain hra to me AND tell me tax for 21L income 3.5L rent", "both"),
    ("whats eligible under 80c and what would i owe if i max it, salary is 18 lakhs", "both"),
    ("old vs new regime which is cheaper for someone making 26L, explain + compute", "both"),
    ("medical insurance claimable? also whats owed on 9L income w 18k premium", "both"),
    ("whats 87a about and is 11.5L tax free under new regime", "both"),
]

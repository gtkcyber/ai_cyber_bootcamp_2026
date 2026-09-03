# Grouping-variable identification

Rows that share a real-world unit — the same patient across visits, the
same account across transactions, the same device across sessions, the
same session across events — are not independent draws. Treating them as
iid understates standard errors and lets a naive split leak the same unit
across train and test. This step exists to catch that before `ds-model`
picks a CV scheme or `ds-features` builds a split.

## Where the candidate keys come from

Never guessed from column names. Candidates come from `ds-data-models`'
grain contract (Interpret discipline): any field that is *not* the
declared row-grain key, but recurs across multiple rows of that grain, is
a grouping-variable candidate. A dataset graining at
patient-visit with a `patient_id` field is the canonical case; the grain
key is visit, `patient_id` is the candidate group.

## Detection

For each candidate:

1. Compute rows-per-key (a script, not a scan) — mean, median, max.
   Rows-per-key ≈ 1 across the board means the candidate does not
   introduce clustering at this grain; materially >1 does.
2. Where feasible, check whether an outcome or feature of interest
   correlates within-key more than between-key (an intraclass-correlation
   style check) — stronger evidence than group size alone, but group size
   alone is sufficient to flag a candidate as needing declaration; it does
   not need to wait on this stronger check to be recorded.
3. Record every candidate that clears step 1, not just the strongest one —
   a dataset can have more than one non-iid axis (patient *and* device,
   for instance), and `ds-model`'s CV design needs to know about all of
   them, not just the largest.

## Recording the finding

**Absence is also a finding, not a silent gap.** If no candidate clears
step 1, `grouping_variables` still gets an entry: an explicit "no non-iid
structure detected at this grain" record, naming what was checked. This is
what lets `ds-model`'s CV-design gate accept "rows are independent" as a
recorded assertion instead of an unstated default — the gate distinguishes
"checked, none found" from "never checked."

## Downstream consumption (pointers only)

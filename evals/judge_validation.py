"""judge_validation.py: compare judge verdicts with hand labels, report TPR and TNR.

Why TPR/TNR and not "agreement": agreement is inflated when almost everything passes.
TPR = of answers the human called good, how many did the judge pass.
TNR = of answers the human called bad, how many did the judge fail.
With 20 questions, a TNR denominator of 1 is honest and meaningless at the same time; say so.

Usage: .\\.venv\\Scripts\\python.exe evals\\judge_validation.py [results/frozen]
"""
import csv
import sys
from pathlib import Path

run = Path(sys.argv[1] if len(sys.argv) > 1 else "results/frozen")
results = {r["id"]: r for r in csv.DictReader((run / "results.csv").open(encoding="utf-8"))}
labels = {r["id"]: r for r in csv.DictReader((run / "labels.csv").open(encoding="utf-8"))}


def rates(mode: str) -> str:
    """One line of TPR/TNR for a failure mode ('correct' or 'grounded')."""
    tp = tn = fp = fn = 0
    for qid, lab in labels.items():
        human = lab[f"human_{mode}"].strip().lower()
        if human not in ("yes", "no"):
            continue  # unlabelled row
        judge = results[qid][f"judge_{mode}"]
        if judge not in ("PASS", "FAIL"):
            continue
        good, passed = human == "yes", judge == "PASS"
        tp += good and passed; fn += good and not passed
        tn += (not good) and (not passed); fp += (not good) and passed
    tpr = f"{tp}/{tp + fn}" if tp + fn else "n/a"
    tnr = f"{tn}/{tn + fp}" if tn + fp else "n/a (no human-labelled negatives)"
    return f"| {mode} | TPR {tpr} | TNR {tnr} | disagreements {fp + fn} |"


n = sum(1 for l in labels.values() if l["human_correct"].strip())
print(f"labels: {n}/{len(labels)} rows filled\n")
print("| Failure mode | True positive rate | True negative rate | |\n|---|---|---|---|")
print(rates("correct"))
print(rates("grounded"))

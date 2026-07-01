"""
Youth disengagement prediction for BGCDC engagement data.

Task: among CHILDREN (age 5-18) who attended at least once, predict who
DISENGAGES -- fails to reach a 3rd visit (the "retention cliff") -- from
demographic / registration features known up front.

Design choices that keep the result honest (not leaky/inflated):
  * Children only (5-18). The raw membership table also contains adults
    (parents/guardians) who trivially never attend 3x; including them
    inflates AUC by ~0.14 without saying anything about youth retention.
  * NO attendance-derived features (TotalVisits, FirstVisitDate) used as
    inputs -> no target leakage.
  * NO explicit "field is missing" indicator features. Whether a family's
    record was completed is a *consequence* of engagement (staff gather
    info over repeated visits), so it leaks the outcome. Missing values
    are median/most-frequent imputed instead.
"""

import os
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    roc_auc_score, average_precision_score, classification_report,
    confusion_matrix,
)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "processed_engagement_data.csv")
RANDOM_STATE = 42

NUMERIC = ["Age", "TotalInHousehold"]
CATEGORICAL = ["OrganizationName", "IncomeCategory", "HouseholdEconomicStatus"]


def load():
    df = pd.read_csv(DATA, low_memory=False)
    df["Age"] = 2023 - pd.to_datetime(df["BirthDate"], errors="coerce").dt.year
    # Children who attended at least once.
    df = df[(df["TotalVisits"] >= 1) & df["Age"].between(5, 18)].copy()
    df["retained"] = (df["TotalVisits"] >= 3).astype(int)
    df["TotalInHousehold"] = pd.to_numeric(df["TotalInHousehold"], errors="coerce")
    for c in CATEGORICAL:
        df[c] = df[c].astype(object).where(df[c].notna(), np.nan)
    return df


def main():
    df = load()
    rate = df["retained"].mean()
    print(f"Children (5-18, >=1 visit): {len(df)}")
    print(f"Retained (>=3 visits):  {df['retained'].sum()} ({rate*100:.1f}%)")
    print(f"Disengaged (<3 visits): {(1-df['retained']).sum()} ({(1-rate)*100:.1f}%)")

    X, y = df[NUMERIC + CATEGORICAL], df["retained"]

    pre = ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                          ("sc", StandardScaler())]), NUMERIC),
        ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                          ("oh", OneHotEncoder(handle_unknown="ignore", min_frequency=25))]),
         CATEGORICAL),
    ])

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)

    models = {
        "LogisticRegression (baseline)": LogisticRegression(max_iter=2000, class_weight="balanced"),
        "GradientBoosting": GradientBoostingClassifier(random_state=RANDOM_STATE),
    }

    fitted = {}
    print("\n" + "=" * 58)
    for name, clf in models.items():
        pipe = Pipeline([("pre", pre), ("clf", clf)])
        pipe.fit(X_tr, y_tr)
        proba = pipe.predict_proba(X_te)[:, 1]
        auc = roc_auc_score(y_te, proba)
        ap = average_precision_score(y_te, proba)
        cv = cross_val_score(pipe, X_tr, y_tr, cv=5, scoring="roc_auc")
        print(f"### {name}")
        print(f"  Test ROC-AUC      : {auc:.3f}")
        print(f"  Test PR-AUC (AP)  : {ap:.3f}  (base rate {rate:.3f})")
        print(f"  5-fold CV ROC-AUC : {cv.mean():.3f} +/- {cv.std():.3f}\n")
        fitted[name] = (pipe, proba)

    best = max(fitted, key=lambda k: roc_auc_score(y_te, fitted[k][1]))
    pipe, proba = fitted[best]
    print("=" * 58)
    print(f"BEST: {best}")
    print("=" * 58)

    # Practical targeting: flag the 25% highest-risk kids for intervention.
    risk = 1 - proba
    k = int(len(risk) * 0.25)
    flagged = np.argsort(risk)[::-1][:k]
    truly_diseng = (y_te.values == 0)
    print(f"\nFlag the 25% highest-risk ({k} kids) for outreach:")
    print(f"  Precision: {truly_diseng[flagged].mean()*100:.1f}% of flagged truly disengaged")
    print(f"  Recall:    {truly_diseng[flagged].sum()/truly_diseng.sum()*100:.1f}% of disengagers caught")

    print("\nClassification report @0.5 (1=retained):")
    print(classification_report(y_te, (proba >= 0.5).astype(int),
                                target_names=["disengaged", "retained"]))

    names = pipe.named_steps["pre"].get_feature_names_out()
    imp = pipe.named_steps["clf"].feature_importances_
    top = sorted(zip(names, imp), key=lambda t: t[1], reverse=True)[:8]
    print("Top feature importances:")
    for nm, v in top:
        print(f"  {v:6.3f}  {nm}")

    save_figure(fitted, y_te, top)


def _pretty(name):
    """Turn a ColumnTransformer feature name into a readable label."""
    name = name.replace("num__", "").replace("cat__", "")
    name = name.replace("OrganizationName_", "Club: ").replace("BGCDC ", "")
    name = name.replace("IncomeCategory_", "Income ").replace("HouseholdEconomicStatus_", "")
    name = name.replace("TotalInHousehold", "Household size").replace("_", " ")
    return name


def save_figure(fitted, y_te, top):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.metrics import roc_curve

    vis_dir = os.path.join(HERE, "..", "visualization")
    palette = ["#457B9D", "#E63946"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), facecolor="white")

    for (name, (_, pr)), color in zip(fitted.items(), palette):
        fpr, tpr, _ = roc_curve(y_te, pr)
        auc = roc_auc_score(y_te, pr)
        ax1.plot(fpr, tpr, color=color, lw=2.5,
                 label=f"{name.split(' ')[0]}  (AUC = {auc:.2f})")
    ax1.plot([0, 1], [0, 1], "--", color="gray", lw=1)
    ax1.set_xlabel("False Positive Rate", fontsize=13, fontweight="bold")
    ax1.set_ylabel("True Positive Rate", fontsize=13, fontweight="bold")
    ax1.set_title("Predicting Youth Disengagement (ROC)", fontsize=15,
                  fontweight="bold", color="#1D3557")
    ax1.legend(loc="lower right", fontsize=12)
    ax1.grid(alpha=0.3)

    labels = [_pretty(n) for n, _ in top][::-1]
    vals = [v for _, v in top][::-1]
    ax2.barh(labels, vals, color="#2A9D8F")
    ax2.set_xlabel("Relative Importance", fontsize=13, fontweight="bold")
    ax2.set_title("Top Predictors of Disengagement", fontsize=15,
                  fontweight="bold", color="#1D3557")
    ax2.grid(axis="x", alpha=0.3)

    fig.tight_layout()
    out = os.path.join(vis_dir, "slide5_disengagement_model.png")
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"\nSaved visualization: {os.path.normpath(out)}")


if __name__ == "__main__":
    main()

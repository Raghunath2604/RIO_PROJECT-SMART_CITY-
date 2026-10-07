"""
fog_emulation.py
=================
CICIoT2023 has no real fog hierarchy (Gap 3 / limitation noted in the
review), so this module EMULATES several fog nodes by partitioning the
dataset (e.g. by device-category proxy or randomly) and compares three
deployment strategies on the SAME held-out test set:

  1. centralized  - one model trained on all nodes' pooled training data
                     (upper bound on accuracy; needs data to leave the fog
                     layer, which is what motivates edge/fog IDS to begin
                     with).
  2. per_node      - one independently-trained model per fog node, each
                     seeing only its own partition (no coordination; worst
                     case for rare-class coverage since a single node may
                     never see a Brute Force sample).
  3. federated_avg - a simple federated-averaging simulation for a linear
                     model (Logistic Regression coefficients averaged across
                     nodes each round) as a lightweight middle ground that
                     keeps raw data on-node.

This directly operationalises RQ5 in the requirements section of the
literature review.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, f1_score

from .schema import FEATURES, sanitize_feature_matrix
from .train_eval import MODEL_FACTORY


def partition_nodes(train_df: pd.DataFrame, n_nodes: int = 4, seed: int = 42) -> list[pd.DataFrame]:
    """Randomly assigns whole sessions to n_nodes fog nodes (session-aware,
    so a node's data resembles a plausible single fog node's traffic)."""
    sessions = train_df["session_id"].unique()
    rng = np.random.default_rng(seed)
    rng.shuffle(sessions)
    node_of = {s: i % n_nodes for i, s in enumerate(sessions)}
    train_df = train_df.copy()
    train_df["node"] = train_df["session_id"].map(node_of)
    return [train_df[train_df["node"] == i].drop(columns=["node"]) for i in range(n_nodes)]


def _xy(df, label_col):
    # float64 throughout: SGDClassifier's partial_fit is strict about dtype
    # consistency between successive calls (coef_ ends up float64 after the
    # first averaging step, so X must match on every later round).
    # BUG FIX: sanitize inf/NaN here too -- this module extracts X
    # independently of train_eval.prepare_xy, so the same zero-duration
    # rate-feature edge case (packets / duration = inf when duration is 0)
    # could crash StandardScaler here on its own. See
    # schema.sanitize_feature_matrix docstring for the full story.
    X = df[FEATURES].values.astype(np.float64)
    X, _ = sanitize_feature_matrix(X, context=f"fog_emulation/{label_col}")
    return X, df[label_col].values


def run_centralized(node_dfs, test_df, label_col, model_name="RandomForest"):
    train_df = pd.concat(node_dfs, ignore_index=True)
    Xtr, ytr = _xy(train_df, label_col)
    Xte, yte = _xy(test_df, label_col)
    scaler = StandardScaler().fit(Xtr)
    le = LabelEncoder().fit(np.concatenate([ytr, yte]))
    model = MODEL_FACTORY[model_name]()
    model.fit(scaler.transform(Xtr), le.transform(ytr))
    pred = model.predict(scaler.transform(Xte))
    yte_enc = le.transform(yte)
    return dict(strategy="centralized",
                accuracy=accuracy_score(yte_enc, pred),
                macro_f1=f1_score(yte_enc, pred, average="macro"))


def run_per_node(node_dfs, test_df, label_col, model_name="RandomForest"):
    Xte, yte = _xy(test_df, label_col)
    le = LabelEncoder().fit(np.concatenate([test_df[label_col].values] +
                                            [d[label_col].values for d in node_dfs]))
    yte_enc = le.transform(yte)
    accs, f1s, coverage = [], [], []
    for d in node_dfs:
        if d[label_col].nunique() < 2:
            continue
        Xtr, ytr = _xy(d, label_col)
        scaler = StandardScaler().fit(Xtr)
        model = MODEL_FACTORY[model_name]()
        model.fit(scaler.transform(Xtr), le.transform(ytr))
        pred = model.predict(scaler.transform(Xte))
        accs.append(accuracy_score(yte_enc, pred))
        f1s.append(f1_score(yte_enc, pred, average="macro"))
        coverage.append(d[label_col].nunique())
    return dict(strategy="per_node",
                accuracy=float(np.mean(accs)), macro_f1=float(np.mean(f1s)),
                mean_classes_seen_per_node=float(np.mean(coverage)),
                total_classes=test_df[label_col].nunique())


def run_federated_avg(node_dfs, test_df, label_col, rounds: int = 15, local_epochs: int = 5):
    """FedAvg simulation for a linear model (multinomial logistic regression
    trained via SGD). Each communication round: every node runs
    `local_epochs` passes of SGD starting from the current global weights
    (partial_fit does exactly one epoch per call, so local training = a
    loop of partial_fit calls, not a single call with max_iter set); the
    resulting per-node coef_/intercept_ are then averaged, weighted by each
    node's sample count -- this is standard FedAvg for a linear model.
    SGDClassifier.partial_fit takes an explicit `classes` list so a node
    that has not seen every class locally still produces a weight vector of
    the correct global shape, which is what lets nodes with partial class
    coverage participate in the average at all."""
    from sklearn.linear_model import SGDClassifier

    le = LabelEncoder().fit(pd.concat([d[label_col] for d in node_dfs] + [test_df[label_col]]))
    all_classes = np.arange(len(le.classes_))
    # BUG FIX: this scaler used to be fit directly from raw dataframe values,
    # bypassing _xy()'s sanitization -- same inf/NaN crash risk as above,
    # independently, because this is a second, separate extraction point.
    stacked_raw = np.vstack([d[FEATURES].values for d in node_dfs]).astype(np.float64)
    stacked_clean, _ = sanitize_feature_matrix(stacked_raw, context=f"fog_emulation/federated_avg/{label_col}")
    scaler = StandardScaler().fit(stacked_clean)
    Xte, yte = _xy(test_df, label_col)
    yte_enc = le.transform(yte)

    n_features = len(FEATURES)
    global_coef = np.zeros((len(all_classes), n_features))
    global_intercept = np.zeros(len(all_classes))

    usable_nodes = [d for d in node_dfs if len(d) > 0]
    for _ in range(rounds):
        coefs, intercepts, weights = [], [], []
        for d in usable_nodes:
            Xtr, ytr = _xy(d, label_col)
            local = SGDClassifier(loss="log_loss", warm_start=True,
                                   learning_rate="optimal", random_state=0)
            local.classes_ = all_classes
            local.coef_ = global_coef.copy()
            local.intercept_ = global_intercept.copy()
            local.t_ = 1.0
            ytr_enc = le.transform(ytr)
            for _epoch in range(local_epochs):
                local.partial_fit(scaler.transform(Xtr), ytr_enc, classes=all_classes)
            coefs.append(local.coef_)
            intercepts.append(local.intercept_)
            weights.append(len(d))
        w = np.array(weights, dtype=float)
        w /= w.sum()
        global_coef = np.average(np.stack(coefs), axis=0, weights=w)
        global_intercept = np.average(np.stack(intercepts), axis=0, weights=w)

    final = SGDClassifier(loss="log_loss")
    final.classes_ = all_classes
    final.coef_ = global_coef
    final.intercept_ = global_intercept
    final.t_ = 1.0
    pred = final.predict(scaler.transform(Xte))
    return dict(strategy="federated_avg",
                accuracy=accuracy_score(yte_enc, pred),
                macro_f1=f1_score(yte_enc, pred, average="macro"),
                rounds=rounds, local_epochs=local_epochs)


def run_fog_comparison(train_df, test_df, label_col="label_8", n_nodes=4, model_name="RandomForest"):
    """NOTE on model_name="RandomForest" default: this isolates the effect of
    DATA DISTRIBUTION STRATEGY (centralized/per-node/federated) on accuracy,
    independent of which model family is used. It is NOT a recommendation to
    deploy RandomForest on a fog node -- profile_model.py's streaming-latency
    results show RF costs 5.6-5.8 ms/sample there, which would dominate any
    fog-node's latency budget. Re-run with model_name="CompactMLP" (the
    deployability profile's best fog candidate) to see whether the
    centralized/per-node/federated ordering found here holds for a model
    that could actually be deployed -- see PROJECT_PLAN.md next steps.
    """
    nodes = partition_nodes(train_df, n_nodes=n_nodes)
    out = [
        run_centralized(nodes, test_df, label_col, model_name),
        run_per_node(nodes, test_df, label_col, model_name),
        run_federated_avg(nodes, test_df, label_col),
    ]
    return pd.DataFrame(out)

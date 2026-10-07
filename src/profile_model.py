"""
profile_model.py
=================
Measures what the literature review's Gap 3 says is missing: model size,
memory footprint and per-sample inference latency, reported against a
declared fog-hardware budget (defaults approximate a Raspberry Pi 4:
~1.5 GHz ARM core visible to one process, no GPU).

Two latency numbers are reported, on purpose, because they answer
different questions:

  - "batch_us_per_sample": one predict() call over the WHOLE test set,
    elapsed time divided by row count. This is a THROUGHPUT number -- how
    fast could this model process a large backlog of already-buffered
    data. It UNDERSTATES real streaming cost because sklearn's vectorised
    predict() amortises Python/array-validation overhead across thousands
    of rows at once.
  - "streaming_us_per_sample": predict() called on ONE row at a time,
    repeated and averaged. This is what a fog node actually experiences --
    a packet-window arrives, gets classified, the next one arrives. For
    small/fast models (logistic regression, a small MLP) this is often an
    order of magnitude higher than the batch number, because fixed
    per-call overhead (not compute) dominates at that scale. This is the
    number that should drive any real fog-deployment latency budget.

Because this sandbox is not a Raspberry Pi, this module does two honest
things instead of pretending it is:
  1. Measures wall-clock latency and process memory HERE (x86 sandbox) and
     reports it clearly labelled as "sandbox" numbers.
  2. Estimates a Raspberry-Pi-equivalent latency using a documented
     literature-derived CPU slowdown factor RANGE (not a per-machine
     benchmark match, since no target device is reachable from this
     sandbox) applied to the streaming number, since that is the
     deployment-relevant one.
"""

from __future__ import annotations
import io
import pickle
import time
import numpy as np
import pandas as pd


def model_size_bytes(estimator, scaler, label_encoder) -> int:
    buf = io.BytesIO()
    pickle.dump({"model": estimator, "scaler": scaler, "label_encoder": label_encoder}, buf)
    return len(buf.getvalue())


def cpu_benchmark_score(n: int = 300, reps: int = 20) -> float:
    """A tiny fixed-cost benchmark (repeated dense matmul) used only to scale
    latency estimates across machines of different single-core speed. Returns
    seconds for `reps` repetitions -- lower is a faster machine."""
    rng = np.random.default_rng(0)
    A = rng.standard_normal((n, n)).astype(np.float32)
    B = rng.standard_normal((n, n)).astype(np.float32)
    t0 = time.perf_counter()
    for _ in range(reps):
        A @ B
    return time.perf_counter() - t0


# Documented literature range for an ARM Cortex-A72 (Raspberry Pi 4) versus a
# typical x86 CI/sandbox core, from published single-thread benchmark
# comparisons (Geekbench 5 single-core: x86 desktop ~1400-1700 vs Pi4 ~250-300,
# i.e. roughly a 5x-6x slowdown). This range is reported explicitly rather
# than treated as a precise number.
PI4_SLOWDOWN_RANGE = (5.0, 6.5)


def streaming_latency_us(estimator, X_sample: np.ndarray, n_calls: int = 300) -> float:
    """Measures realistic single-row inference latency: predict() called
    once per row, cycling through X_sample if n_calls > len(X_sample), with
    one untimed warm-up call first (so one-off JIT/cache effects on the
    first call don't bias the average). Returns microseconds per call."""
    if len(X_sample) == 0:
        return float("nan")
    one_row = X_sample[0:1]
    estimator.predict(one_row)  # warm-up, not timed

    t0 = time.perf_counter()
    for i in range(n_calls):
        row = X_sample[i % len(X_sample): i % len(X_sample) + 1]
        estimator.predict(row)
    elapsed = time.perf_counter() - t0
    return (elapsed / n_calls) * 1e6


def profile_result(result: dict, n_streaming_calls: int = 300) -> dict:
    """Given a train_eval.train_one_model() result dict, add size/latency
    fields: batch-amortized (from train_eval), streaming single-row
    (measured here), and a Pi4 estimate range applied to the streaming
    number (the deployment-relevant one -- see module docstring)."""
    size_b = model_size_bytes(result["estimator"], result["scaler"], result["label_encoder"])

    batch_us = result["infer_time_us_per_sample"]
    stream_us = streaming_latency_us(result["estimator"], result["latency_sample_X"],
                                      n_calls=n_streaming_calls)

    lo, hi = PI4_SLOWDOWN_RANGE
    est_lo = stream_us * lo
    est_hi = stream_us * hi

    return {
        "model": result["model"],
        "task": result["task"],
        "split": result["split"],
        "size_kb": round(size_b / 1024, 1),
        "batch_us_per_sample": round(batch_us, 3),
        "streaming_us_per_sample": round(stream_us, 2),
        "pi4_est_us_per_sample_low": round(est_lo, 1),
        "pi4_est_us_per_sample_high": round(est_hi, 1),
        "n_test": result["n_test"],
    }


def profile_all(results: list[dict]) -> pd.DataFrame:
    rows = [profile_result(r) for r in results]
    return pd.DataFrame(rows)

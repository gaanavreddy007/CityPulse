# Comprehensive Offline Test Log: CITYPULSE Phase 2 & Phase 3

**Project Title:** CITYPULSE: Traffic-Sensor Data Quality, Urban Anomaly Detection, and Road-Network Resilience  
**Author:** Automated Research and Pair-Programming Agent (Antigravity)  
**Date:** October 2026  
**Primary Project Directory:** `./`  
**Execution Environment:** Windows, Python 3.13.7 (64-bit)  
**Test Framework:** Standard Library `unittest` (Zero external network dependencies)  
**Overall Status:** **ALL 40 TESTS PASSED (100% SUCCESS RATE, ZERO FAILURES)**  

---

## 1. Test Suite Execution Command & Summary Output

```powershell
PS .> python -m unittest discover tests
........................................
----------------------------------------------------------------------
Ran 40 tests in 7.683s

OK
```

---

## 2. Granular Test Inventory Across Modules (40 Tests Total)

### 2.1 Module: `tests/test_dataset_offline.py` (Phase 1 Baseline Verification, 4 Tests)
* **`test_locations_schema_and_bounds`:** Validates `locations.csv` structure, 470 detector records, 0 null coordinates, and verification of Glasgow bounding box ($55.70 \le \text{lat} \le 56.05, -4.55 \le \text{lon} \le -4.00$). `[PASSED]`
* **`test_flow_schema_and_non_negativity`:** Validates time-series schema (`date`, `time`, `flow`), 33,644 rows, hour bounds ($0-23$), integer types, and non-negativity. `[PASSED]`
* **`test_datetime_reindexing_and_gap_detection`:** Verifies continuous hourly date range construction across 35,064 calendar hours and identifies the 1,420 missing hours. `[PASSED]`
* **`test_synthetic_degradation_injection`:** Verifies baseline perturbation generation, MCAR dropout rate bounds, and offset drift. `[PASSED]`

### 2.2 Module: `tests/test_temporal_splits.py` (Gate 1 Regression Suite, 4 Tests)
* **`test_calendar_hour_counts_and_leap_year`:** Verifies leap year 2020 inclusion (Feb 29 = 24 hrs), exact calendar hours: Train = 17,544 hrs (731 days), Val = 8,760 hrs (365 days), Test = 8,760 hrs (365 days), Total = 35,064 hrs. `[PASSED]`
* **`test_split_boundary_non_overlap`:** Proves non-overlapping contiguous boundaries ($\Delta t = 1\text{ hr}$ between splits) and zero temporal leakage. `[PASSED]`
* **`test_observed_records_vs_calendar_missingness`:** Verifies exact census counts for 33,644-row detectors: 16,639 observed train records (905 missing), 8,663 observed val records (97 missing), 8,342 observed test records (418 missing). `[PASSED]`
* **`test_reindex_preserves_zero_flow_as_distinct_from_missing`:** Confirms that omitted rows become `NaN` while legitimate zero traffic ($q=0$) is strictly preserved as `0.0`. `[PASSED]`

### 2.3 Module: `tests/test_data_loader.py` (Gate 2 Ingestion Suite, 5 Tests)
* **`test_load_sensor_locations`:** Tests `citypulse.data.loader.load_sensor_locations` with column checks, coordinate bounds, and error handling. `[PASSED]`
* **`test_load_sensor_flow`:** Tests `citypulse.data.loader.load_sensor_flow` for schema and negative-value assertions. `[PASSED]`
* **`test_reindex_sensor_flow`:** Tests continuous hourly reindexing, ensuring 35,064 float32 entries and exact gap mapping. `[PASSED]`
* **`test_compute_missingness_report`:** Tests `MissingnessReport` generation, computing missing and zero-traffic percentages. `[PASSED]`
* **`test_split_chronological`:** Tests automated partitioning into non-overlapping `SplitName.TRAIN`, `VAL`, and `TEST` series. `[PASSED]`

### 2.4 Module: `tests/test_corruption_engine.py` (Gate 2 Synthetic Engine, 5 Tests)
* **`test_mcar_injection`:** Tests stochastic dropout injection, label alignment (1 = corrupted, 0 = normal), and deep-copy preservation. `[PASSED]`
* **`test_burst_injection`:** Tests contiguous block outages (e.g., 24-hr blocks), label continuity, and missing value injection. `[PASSED]`
* **`test_drift_injection`:** Tests multiplicative offset scaling ($\pm 40\%$) over sustained time windows. `[PASSED]`
* **`test_stuck_value_injection`:** Tests constant freezing at $0.0$ and training mean $\mu_{\text{train}}$. `[PASSED]`
* **`test_reproducibility_with_seed`:** Tests bitwise-identical corrupted data and labels across identical seeds. `[PASSED]`

### 2.5 Module: `tests/test_sensor_matching.py` (Gate 3 Candidate Mapping, 4 Tests)
* **`test_high_confidence_match`:** Tests unambiguous dominant edge assignment when a detector is within 2 meters of an isolated link ($d \le 15\text{m}$, confidence $\ge 0.85$). `[PASSED]`
* **`test_ambiguity_flagging_at_crossroads`:** Tests detector placed equidistant at a crossroad, ensuring it flags `AMBIGUOUS_MULTI_CANDIDATE` ($|d_1 - d_2| < 6\text{m}$) without forcing an edge. `[PASSED]`
* **`test_unmatched_distance_exceeded`:** Tests remote detector placed outside the search radius, ensuring `UNMATCHED_DISTANCE_EXCEEDED` without forced snapping. `[PASSED]`
* **`test_multi_sensor_junction_conflict_detection`:** Tests multi-detector approach conflict detection when two detectors from the same junction snap to the same edge. `[PASSED]`

### 2.6 Module: `tests/test_resilience_prototype.py` (Gate 4 Resilience Prototype, 4 Tests)
* **`test_graph_construction_and_impedance`:** Validates NetworkX graph construction, WebTAG capacities, and BPR parameter assignment. `[PASSED]`
* **`test_baseline_all_pairs_connectivity`:** Validates all-pairs Dijkstra path existence and finite baseline network cost. `[PASSED]`
* **`test_m8_corridor_closure_simulation`:** Tests multi-edge bridge corridor removal (M8 Kingston Bridge 4-edge set), graph partitioning, and finite disconnection penalty ($M = 3,600\text{s}$). `[PASSED]`
* **`test_parameter_sensitivity_audit`:** Tests directional monotonicity: higher traffic volumes or higher $\alpha$ values strictly increase network impedance. `[PASSED]`

### 2.7 Module: `tests/test_anomaly_baselines.py` (Phase 3 Baseline Suite, 6 Tests)
* **`test_seasonal_mad_score_direction_and_shape`:** Validates that injected flow anomalies strictly produce higher anomaly scores and binary flags. `[PASSED]`
* **`test_seasonal_mad_nan_handling_and_fallback`:** Proves that missing observations (`NaN`) yield `NaN` scores and that sparse bins trigger hierarchical hour-of-day/global fallbacks. `[PASSED]`
* **`test_rolling_zscore_strictly_causal_no_future_leakage`:** Proves that rolling Z-scores only depend on past window $[t-W, t-1]$; future changes produce zero change in preceding scores. `[PASSED]`
* **`test_isolation_forest_and_ecod_scoring`:** Verifies PyOD IForest and ECOD wrappers with cyclical temporal features and valid score shapes. `[PASSED]`
* **`test_zero_leakage_calibration`:** Confirms that decision thresholds calibrated on validation data are completely unaffected by test set values. `[PASSED]`
* **`test_missingness_and_static_baselines`:** Validates reference lower-bound detectors (`MissingnessDetector` and `StaticQuantileDetector`). `[PASSED]`

### 2.8 Module: `tests/test_benchmark_metrics.py` (Phase 3 Metric Verification, 5 Tests)
* **`test_perfect_classification`:** Verifies 1.0 values across Precision, Recall, F1, MCC, and PR-AUC on perfect predictions. `[PASSED]`
* **`test_imperfect_classification`:** Verifies exact manual confusion matrix calculations (TP=3, FP=1, FN=1, TN=3). `[PASSED]`
* **`test_undefined_precision_when_no_positive_predictions`:** Confirms that zero positive predictions yield `NaN` precision with documented reason rather than fabricated 0.0. `[PASSED]`
* **`test_undefined_recall_when_no_ground_truth_positives`:** Confirms that zero ground-truth positives yield `NaN` recall and PR-AUC with documented reason. `[PASSED]`
* **`test_nan_filtering_in_metric_computation`:** Verifies clean filtering of input `NaN` values before metric evaluation. `[PASSED]`

### 2.9 Module: `tests/test_experiment_reproducibility.py` (Phase 3 Reproducibility Suite, 3 Tests)
* **`test_track_a_determinism_across_runs`:** Proves bit-for-bit analytical reproducibility across repeated runs with identical random seed. `[PASSED]`
* **`test_track_a_seed_sensitivity`:** Proves that different master seeds produce distinct stochastic corruption masks. `[PASSED]`
* **`test_track_b_separation_and_disclaimer`:** Confirms that Track B operates unsupervised on uncorrupted test data and contains mandatory scientific disclaimers. `[PASSED]`

---

## 3. Benchmark Execution Log

### Command Executed:
```powershell
PS .> python scripts/run_anomaly_benchmark.py
```

### Execution Output:
```
================================================================================
CITYPULSE PHASE 3: BENCHMARK EXECUTION
Master Seeds: [42, 101, 2024, 777, 999]
================================================================================

--- Loading and Reindexing Sensor: GA0151_A ---
Series reindexed to 35064 calendar hours.
Non-null observations: 33644, Null hours: 1420
Running Track A across 5 seeds and 10 corruption scenarios...
Track A completed in 10.96s (300 scenario evaluations).
Running Track B (Unsupervised Discovery on uncorrupted Test split)...
Track B completed: 40 top statistical anomaly records extracted.

--- Loading and Reindexing Sensor: GA0151_C ---
Series reindexed to 35064 calendar hours.
Non-null observations: 33644, Null hours: 1420
Running Track A across 5 seeds and 10 corruption scenarios...
Track A completed in 11.23s (300 scenario evaluations).
Running Track B (Unsupervised Discovery on uncorrupted Test split)...
Track B completed: 40 top statistical anomaly records extracted.

--- Loading and Reindexing Sensor: GA0401_R ---
Series reindexed to 35064 calendar hours.
Non-null observations: 33643, Null hours: 1421
Running Track A across 5 seeds and 10 corruption scenarios...
Track A completed in 11.15s (300 scenario evaluations).
Running Track B (Unsupervised Discovery on uncorrupted Test split)...
Track B completed: 40 top statistical anomaly records extracted.

Granular Track A results saved to: .\reports\anomaly_benchmark_results.csv
Track B top statistical anomalies saved to: .\reports\statistical_anomalies_track_b.csv
Aggregate summary saved to: .\reports\anomaly_benchmark_summary.json
```

All 900 scenario evaluations executed successfully with zero unhandled exceptions.

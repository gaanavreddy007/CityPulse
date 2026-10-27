# Comprehensive Offline Test Log: CITYPULSE Phase 4

**Project Title:** CITYPULSE: Traffic-Sensor Data Quality, Urban Anomaly Detection, and Road-Network Resilience  
**Author:** Automated Research and Pair-Programming Agent (Antigravity)  
**Date:** October 2026  
**Primary Project Directory:** `./`  
**Execution Environment:** Windows, Python 3.13.7 (64-bit)  
**Test Framework:** Standard Library `unittest` (Zero external network dependencies)  
**Overall Status:** **ALL 50 TESTS PASSED (100% SUCCESS RATE, ZERO FAILURES, ZERO ERRORS)**  

---

## 1. Test Suite Execution Command & Summary Output

```powershell
PS .> python -m unittest discover tests
..................................................
----------------------------------------------------------------------
Ran 50 tests in 7.274s

OK
```

---

## 2. Granular Test Inventory Across Modules (50 Tests Total)

### 2.1 Module: `tests/test_dataset_offline.py` (4 Tests)
* **`test_locations_schema_and_bounds`:** Validates `locations.csv` structure, 470 detector records, 0 null coordinates, and verification of Glasgow bounding box ($55.70 \le \text{lat} \le 56.05, -4.55 \le \text{lon} \le -4.00$). `[PASSED]`
* **`test_flow_schema_and_non_negativity`:** Validates time-series schema (`date`, `time`, `flow`), 33,644 rows, hour bounds ($0-23$), integer types, and non-negativity. `[PASSED]`
* **`test_datetime_reindexing_and_gap_detection`:** Verifies continuous hourly date range construction across 35,064 calendar hours and identifies the 1,420 missing hours. `[PASSED]`
* **`test_synthetic_degradation_injection`:** Verifies baseline perturbation generation, MCAR dropout rate bounds, and offset drift. `[PASSED]`

### 2.2 Module: `tests/test_temporal_splits.py` (4 Tests)
* **`test_calendar_hour_counts_and_leap_year`:** Verifies leap year 2020 inclusion (Feb 29 = 24 hrs), exact calendar hours: Train = 17,544 hrs (731 days), Val = 8,760 hrs (365 days), Test = 8,760 hrs (365 days), Total = 35,064 hrs. `[PASSED]`
* **`test_split_boundary_non_overlap`:** Proves non-overlapping contiguous boundaries ($\Delta t = 1\text{ hr}$ between splits) and zero temporal leakage. `[PASSED]`
* **`test_observed_records_vs_calendar_missingness`:** Verifies exact census counts for 33,644-row detectors: 16,639 observed train records (905 missing), 8,663 observed val records (97 missing), 8,342 observed test records (418 missing). `[PASSED]`
* **`test_reindex_preserves_zero_flow_as_distinct_from_missing`:** Confirms that omitted rows become `NaN` while legitimate zero traffic ($q=0$) is strictly preserved as `0.0`. `[PASSED]`

### 2.3 Module: `tests/test_data_loader.py` (5 Tests)
* **`test_load_sensor_locations`:** Tests `citypulse.data.loader.load_sensor_locations` with column checks, coordinate bounds, and error handling. `[PASSED]`
* **`test_load_sensor_flow`:** Tests `citypulse.data.loader.load_sensor_flow` for schema and negative-value assertions. `[PASSED]`
* **`test_reindex_sensor_flow`:** Tests continuous hourly reindexing, ensuring 35,064 float32 entries and exact gap mapping. `[PASSED]`
* **`test_compute_missingness_report`:** Tests `MissingnessReport` generation, computing missing and zero-traffic percentages. `[PASSED]`
* **`test_split_chronological`:** Tests automated partitioning into non-overlapping `SplitName.TRAIN`, `VAL`, and `TEST` series. `[PASSED]`

### 2.4 Module: `tests/test_corruption_engine.py` (5 Tests)
* **`test_mcar_injection`:** Tests stochastic dropout injection, label alignment (1 = corrupted, 0 = normal), and deep-copy preservation. `[PASSED]`
* **`test_burst_injection`:** Tests contiguous block outages (e.g., 24-hr blocks), label continuity, and missing value injection. `[PASSED]`
* **`test_drift_injection`:** Tests multiplicative offset scaling ($\pm 40\%$) over sustained time windows. `[PASSED]`
* **`test_stuck_value_injection`:** Tests constant freezing at $0.0$ and training mean $\mu_{\text{train}}$. `[PASSED]`
* **`test_reproducibility_with_seed`:** Tests bitwise-identical corrupted data and labels across identical seeds. `[PASSED]`

### 2.5 Module: `tests/test_sensor_matching.py` (4 Tests)
* **`test_high_confidence_match`:** Tests unambiguous dominant edge assignment when a detector is within 2 meters of an isolated link ($d \le 15\text{m}$, confidence $\ge 0.85$). `[PASSED]`
* **`test_ambiguity_flagging_at_crossroads`:** Tests detector placed equidistant at a crossroad, ensuring it flags `AMBIGUOUS_MULTI_CANDIDATE` ($|d_1 - d_2| < 6\text{m}$) without forcing an edge. `[PASSED]`
* **`test_unmatched_distance_exceeded`:** Tests remote detector placed outside the search radius, ensuring `UNMATCHED_DISTANCE_EXCEEDED` without forced snapping. `[PASSED]`
* **`test_multi_sensor_junction_conflict_detection`:** Tests multi-detector approach conflict detection when two detectors from the same junction snap to the same edge. `[PASSED]`

### 2.6 Module: `tests/test_resilience_prototype.py` (4 Tests)
* **`test_baseline_graph_construction`:** Tests directed NetworkX graph instantiation across 38 nodes, verifying coordinate properties, edge lengths, capacity, and BPR coefficients. `[PASSED]`
* **`test_disconnection_handling`:** Tests disconnection handling and verifies that disconnected components trigger the $M=3,600\text{s}$ penalty cap. `[PASSED]`
* **`test_multi_edge_bridge_closure`:** Tests simultaneous multi-edge capacity removal for dual-carriageway river crossings. `[PASSED]`
* **`test_parameter_sensitivity`:** Evaluates network cost variance under perturbation of free-flow speeds and design capacities. `[PASSED]`

### 2.7 Module: `tests/test_experiment_reproducibility.py` (3 Tests)
* **`test_track_a_determinism_across_runs`:** Proves bitwise exact reproduction across multiple runs under identical seeds. `[PASSED]`
* **`test_track_a_seed_sensitivity`:** Proves that changing seeds produces bounded, non-zero variance. `[PASSED]`
* **`test_track_b_separation_and_disclaimer`:** Enforces strict isolation of Track B statistical anomalies from Track A evaluation. `[PASSED]`

### 2.8 Module: `tests/test_anomaly_baselines.py` (6 Tests)
* **`test_zero_leakage_calibration`:** Asserts that baseline fit methods only access the training partition. `[PASSED]`
* **`test_rolling_zscore_strictly_causal_no_future_leakage`:** Asserts strictly backward-looking causal rolling windows with zero future data leakage. `[PASSED]`
* **`test_seasonal_mad_score_direction_and_shape`:** Asserts seasonal median and MAD computation across the 168-hour weekly cycle. `[PASSED]`
* **`test_seasonal_mad_nan_handling_and_fallback`:** Asserts robust fallback to global median and global MAD when seasonal bins contain missing data. `[PASSED]`
* **`test_missingness_and_static_baselines`:** Asserts correct flag generation for static threshold and missingness detectors. `[PASSED]`
* **`test_isolation_forest_and_ecod_scoring`:** Tests PyOD ECOD and scikit-learn Isolation Forest model training, continuous score generation, and prediction shape. `[PASSED]`

### 2.9 Module: `tests/test_benchmark_metrics.py` (5 Tests)
* **`test_perfect_classification`:** Verifies metric outputs for perfect classification ($\text{Precision}=1.0, \text{Recall}=1.0, \text{F1}=1.0, \text{MCC}=1.0$). `[PASSED]`
* **`test_imperfect_classification`:** Verifies exact mathematical evaluation of contingency table metrics under controlled false positive and false negative rates. `[PASSED]`
* **`test_undefined_precision_when_no_positive_predictions`:** Verifies graceful handling and fallback when no positive anomalies are predicted. `[PASSED]`
* **`test_undefined_recall_when_no_ground_truth_positives`:** Verifies graceful handling and fallback when no ground-truth positives exist. `[PASSED]`
* **`test_nan_filtering_in_metric_computation`:** Verifies that missing or NaN elements in score or label arrays are systematically excluded without distortion. `[PASSED]`

### 2.10 Module: `tests/test_spatial_consistency.py` (Phase 4, 3 Tests)
* **`test_fit_and_zero_leakage_calibration`:** Validates seasonal median/MAD calibration on training split only, asserting zero access to validation/test partitions. `[PASSED]`
* **`test_isolated_downward_drift_detection`:** Asserts that an isolated -50% drift on sensor $s$ generates a massive residual divergence ($d_{s, n, t} > 3.0$) and correctly triggers the anomaly flag. `[PASSED]`
* **`test_shared_corridor_change_disambiguation`:** Asserts that a simultaneous -30% drop across both primary and neighbor along the same corridor predominantly generates `SHARED_CORRIDOR_CHANGE` classifications, suppressing false single-sensor hardware alarms. `[PASSED]`

### 2.11 Module: `tests/test_resilience_monte_carlo.py` (Phase 4, 3 Tests)
* **`test_seed_reproducibility`:** Verifies that identical random seeds produce bitwise-identical Monte Carlo flow draws and identical $\Delta \mathcal{C}$ metrics. `[PASSED]`
* **`test_sample_convergence`:** Proves empirical Monte Carlo error decay: asserts $\text{SEM}_{500} < \text{SEM}_{50}$ matching theoretical $O(1/\sqrt{N})$ decay. `[PASSED]`
* **`test_closure_disconnection_penalty`:** Asserts that closing the M8 Kingston Bridge disconnects directed OD pairs and rigorously incorporates the $M = 3,600\text{s}$ penalty cap without infinite divergence. `[PASSED]`

### 2.12 Module: `tests/test_observability_index.py` (Phase 4, 4 Tests)
* **`test_geodetic_distance_formula`:** Verifies Haversine geodetic distance calculation against known Glasgow geographic benchmarks within 1.0 meter precision. `[PASSED]`
* **`test_observability_index_mathematical_bounds`:** Asserts $\forall e, \quad \Omega_e \in [0.0, 1.0]$. `[PASSED]`
* **`test_zero_distance_produces_zero_risk`:** Proves that an edge with an exactly co-located detector ($\text{dist}_e = 0\text{m}$) has $\Omega_e \equiv 0.0$. `[PASSED]`
* **`test_distance_monotonicity`:** Asserts that for any edge with non-zero criticality, increasing physical sensor distance strictly increases $\Omega_e$. `[PASSED]`

---

## 3. Benchmark Execution Commands

The complete empirical benchmarks for Phase 4 were executed with the following commands:

```powershell
# 1. Spatial Cross-Consistency Benchmark (450 evaluations across 5 seeds, 3 corridors, 6 scenarios)
python scripts/run_spatial_benchmark.py

# 2. Resilience Uncertainty Monte Carlo & Observability Risk Index Evaluation
python scripts/run_resilience_experiments.py

# 3. Complete Offline Test Suite Discovery
python -m unittest discover tests
```

All 50 unit tests pass 100% offline with zero failures and zero network calls, verifying the software architecture and experimental reproducibility.

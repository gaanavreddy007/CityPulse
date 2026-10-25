# Offline Test & Audit Execution Log: CITYPULSE Phase 4.1

**Project Title:** CITYPULSE: Traffic-Sensor Data Quality, Urban Anomaly Detection, and Road-Network Resilience  
**Author:** Independent Scientific Reviewer (Antigravity)  
**Date:** October 2026  
**Primary Project Directory:** `C:\Gaanav\Projects\CityPulse`  
**Execution Environment:** Windows, Python 3.13.7 (64-bit)  
**Test Framework:** Python Standard Library `unittest` (Zero external network dependencies, £0 budget)  
**Overall Status:** **ALL 50 TESTS PASSED (100% SUCCESS RATE, ZERO FAILURES, ZERO ERRORS)**  

---

## 1. Test Suite Execution Command & Real Console Output

```powershell
PS C:\Gaanav\Projects\CityPulse> python -m unittest discover tests
..................................................
----------------------------------------------------------------------
Ran 50 tests in 7.045s

OK
```

---

## 2. Granular Inventory of All 50 Passing Tests

### 2.1 Baseline Dataset & Ingestion Suite (13 Tests)
1. **`test_dataset_offline.TestDatasetOffline.test_locations_schema_and_bounds`:** Validates `locations.csv` structure, 470 detector records, 0 null coordinates, Glasgow bounding box. `[PASSED]`
2. **`test_dataset_offline.TestDatasetOffline.test_flow_schema_and_non_negativity`:** Validates time-series schema, 33,644 rows, hour bounds ($0-23$), integer non-negativity. `[PASSED]`
3. **`test_dataset_offline.TestDatasetOffline.test_datetime_reindexing_and_gap_detection`:** Verifies continuous hourly date range construction across 35,064 calendar hours and identifies the 1,420 missing hours. `[PASSED]`
4. **`test_dataset_offline.TestDatasetOffline.test_synthetic_degradation_injection`:** Verifies baseline perturbation generation, MCAR dropout rate bounds, and offset drift. `[PASSED]`
5. **`test_temporal_splits.TestTemporalSplits.test_calendar_hour_counts_and_leap_year`:** Verifies leap year 2020 inclusion (Feb 29 = 24 hrs), exact calendar hours: Train = 17,544 hrs (731 days), Val = 8,760 hrs (365 days), Test = 8,760 hrs (365 days). `[PASSED]`
6. **`test_temporal_splits.TestTemporalSplits.test_split_boundary_non_overlap`:** Proves non-overlapping contiguous boundaries ($\Delta t = 1\text{ hr}$) and zero temporal leakage. `[PASSED]`
7. **`test_temporal_splits.TestTemporalSplits.test_observed_records_vs_calendar_missingness`:** Verifies exact census counts for 33,644-row detectors: 16,639 observed train records, 8,663 observed val records, 8,342 observed test records. `[PASSED]`
8. **`test_temporal_splits.TestTemporalSplits.test_reindex_preserves_zero_flow_as_distinct_from_missing`:** Confirms omitted rows become `NaN` while legitimate zero traffic ($q=0$) is strictly preserved as `0.0`. `[PASSED]`
9. **`test_data_loader.TestDataLoader.test_load_sensor_locations`:** Tests `citypulse.data.loader.load_sensor_locations` with column checks, coordinate bounds, and error handling. `[PASSED]`
10. **`test_data_loader.TestDataLoader.test_load_sensor_flow`:** Tests `citypulse.data.loader.load_sensor_flow` for schema and negative-value assertions. `[PASSED]`
11. **`test_data_loader.TestDataLoader.test_reindex_sensor_flow`:** Tests continuous hourly reindexing, ensuring 35,064 float32 entries and exact gap mapping. `[PASSED]`
12. **`test_data_loader.TestDataLoader.test_compute_missingness_report`:** Tests `MissingnessReport` generation, computing missing and zero-traffic percentages. `[PASSED]`
13. **`test_data_loader.TestDataLoader.test_split_chronological`:** Tests automated partitioning into non-overlapping `SplitName.TRAIN`, `VAL`, and `TEST` series. `[PASSED]`

### 2.2 Synthetic Corruption & Spatial Candidate Matching (9 Tests)
14. **`test_corruption_engine.TestCorruptionEngine.test_mcar_injection`:** Tests stochastic dropout injection, label alignment (1 = corrupted, 0 = normal), and deep-copy preservation. `[PASSED]`
15. **`test_corruption_engine.TestCorruptionEngine.test_burst_injection`:** Tests contiguous block outages (e.g., 24-hr blocks), label continuity, and missing value injection. `[PASSED]`
16. **`test_corruption_engine.TestCorruptionEngine.test_drift_injection`:** Tests multiplicative offset scaling ($\pm 40\%$) over sustained time windows. `[PASSED]`
17. **`test_corruption_engine.TestCorruptionEngine.test_stuck_value_injection`:** Tests constant freezing at $0.0$ and training mean $\mu_{\text{train}}$. `[PASSED]`
18. **`test_corruption_engine.TestCorruptionEngine.test_reproducibility_with_seed`:** Tests bitwise-identical corrupted data and labels across identical seeds. `[PASSED]`
19. **`test_sensor_matching.TestSensorMatching.test_high_confidence_match`:** Tests unambiguous dominant edge assignment when a detector is within 2 meters of an isolated link ($d \le 15\text{m}$, confidence $\ge 0.85$). `[PASSED]`
20. **`test_sensor_matching.TestSensorMatching.test_ambiguity_flagging_at_crossroads`:** Tests detector placed equidistant at a crossroad, ensuring it flags `AMBIGUOUS_MULTI_CANDIDATE` ($|d_1 - d_2| < 6\text{m}$) without forcing an edge. `[PASSED]`
21. **`test_sensor_matching.TestSensorMatching.test_unmatched_distance_exceeded`:** Tests remote detector placed outside search radius, ensuring `UNMATCHED_DISTANCE_EXCEEDED`. `[PASSED]`
22. **`test_sensor_matching.TestSensorMatching.test_multi_sensor_junction_conflict_detection`:** Tests multi-detector approach conflict detection when two detectors from the same junction snap to the same edge. `[PASSED]`

### 2.3 Baseline Models, Metrics & Reproducibility (14 Tests)
23. **`test_anomaly_baselines.TestAnomalyBaselines.test_zero_leakage_calibration`:** Asserts baseline fit methods only access the training partition. `[PASSED]`
24. **`test_anomaly_baselines.TestAnomalyBaselines.test_rolling_zscore_strictly_causal_no_future_leakage`:** Asserts strictly backward-looking causal rolling windows with zero future data leakage. `[PASSED]`
25. **`test_anomaly_baselines.TestAnomalyBaselines.test_seasonal_mad_score_direction_and_shape`:** Asserts seasonal median and MAD computation across the 168-hour weekly cycle. `[PASSED]`
26. **`test_anomaly_baselines.TestAnomalyBaselines.test_seasonal_mad_nan_handling_and_fallback`:** Asserts robust fallback to global median and global MAD when seasonal bins contain missing data. `[PASSED]`
27. **`test_anomaly_baselines.TestAnomalyBaselines.test_missingness_and_static_baselines`:** Asserts correct flag generation for static threshold and missingness detectors. `[PASSED]`
28. **`test_anomaly_baselines.TestAnomalyBaselines.test_isolation_forest_and_ecod_scoring`:** Tests PyOD ECOD and scikit-learn Isolation Forest model training, continuous score generation, and prediction shape. `[PASSED]`
29. **`test_benchmark_metrics.TestBenchmarkMetrics.test_perfect_classification`:** Verifies metric outputs for perfect classification ($\text{Precision}=1.0, \text{Recall}=1.0, \text{F1}=1.0, \text{MCC}=1.0$). `[PASSED]`
30. **`test_benchmark_metrics.TestBenchmarkMetrics.test_imperfect_classification`:** Verifies exact mathematical evaluation of contingency table metrics under controlled error rates. `[PASSED]`
31. **`test_benchmark_metrics.TestBenchmarkMetrics.test_undefined_precision_when_no_positive_predictions`:** Verifies graceful handling and fallback when no positive anomalies are predicted. `[PASSED]`
32. **`test_benchmark_metrics.TestBenchmarkMetrics.test_undefined_recall_when_no_ground_truth_positives`:** Verifies graceful handling and fallback when no ground-truth positives exist. `[PASSED]`
33. **`test_benchmark_metrics.TestBenchmarkMetrics.test_nan_filtering_in_metric_computation`:** Verifies that missing or NaN elements in score or label arrays are systematically excluded without distortion. `[PASSED]`
34. **`test_experiment_reproducibility.TestExperimentReproducibility.test_track_a_determinism_across_runs`:** Proves bitwise exact reproduction across multiple runs under identical seeds. `[PASSED]`
35. **`test_experiment_reproducibility.TestExperimentReproducibility.test_track_a_seed_sensitivity`:** Proves changing seeds produces bounded, non-zero variance. `[PASSED]`
36. **`test_experiment_reproducibility.TestExperimentReproducibility.test_track_b_separation_and_disclaimer`:** Enforces strict isolation of Track B statistical anomalies from Track A evaluation. `[PASSED]`

### 2.4 Resilience Prototype, Spatial Consistency, Monte Carlo & Observability (14 Tests)
37. **`test_resilience_prototype.TestResiliencePrototype.test_baseline_graph_construction`:** Tests directed NetworkX graph instantiation across 38 nodes, verifying coordinate properties, edge lengths, capacity, and BPR coefficients. `[PASSED]`
38. **`test_resilience_prototype.TestResiliencePrototype.test_disconnection_handling`:** Tests disconnection handling and verifies that disconnected components trigger the $M=3,600\text{s}$ penalty cap. `[PASSED]`
39. **`test_resilience_prototype.TestResiliencePrototype.test_multi_edge_bridge_closure`:** Tests simultaneous multi-edge capacity removal for dual-carriageway river crossings. `[PASSED]`
40. **`test_resilience_prototype.TestResiliencePrototype.test_parameter_sensitivity`:** Evaluates network cost variance under perturbation of free-flow speeds and design capacities. `[PASSED]`
41. **`test_spatial_consistency.TestSpatialConsistency.test_fit_and_zero_leakage_calibration`:** Validates seasonal median/MAD calibration on training split only, asserting zero access to validation/test partitions. `[PASSED]`
42. **`test_spatial_consistency.TestSpatialConsistency.test_isolated_downward_drift_detection`:** Asserts an isolated -50% drift on sensor $s$ generates a massive residual divergence ($d_{s, n, t} > 3.0$) and correctly triggers the anomaly flag. `[PASSED]`
43. **`test_spatial_consistency.TestSpatialConsistency.test_shared_corridor_change_disambiguation`:** Asserts simultaneous -30% drop across primary and neighbor along the same corridor predominantly generates `SHARED_CORRIDOR_CHANGE` classifications. `[PASSED]`
44. **`test_resilience_monte_carlo.TestResilienceMonteCarlo.test_seed_reproducibility`:** Verifies identical random seeds produce bitwise-identical Monte Carlo flow draws and identical $\Delta \mathcal{C}$ metrics. `[PASSED]`
45. **`test_resilience_monte_carlo.TestResilienceMonteCarlo.test_sample_convergence`:** Proves empirical Monte Carlo error decay: asserts $\text{SEM}_{500} < \text{SEM}_{50}$ matching theoretical $O(1/\sqrt{N})$ decay. `[PASSED]`
46. **`test_resilience_monte_carlo.TestResilienceMonteCarlo.test_closure_disconnection_penalty`:** Asserts closing M8 Kingston Bridge disconnects directed OD pairs and incorporates the $M = 3,600\text{s}$ penalty cap without infinite divergence. `[PASSED]`
47. **`test_observability_index.TestObservabilityIndex.test_geodetic_distance_formula`:** Verifies Haversine geodetic distance calculation against known Glasgow geographic benchmarks within 1.0 meter precision. `[PASSED]`
48. **`test_observability_index.TestObservabilityIndex.test_observability_index_mathematical_bounds`:** Asserts $\forall e, \quad \Omega_e \in [0.0, 1.0]$. `[PASSED]`
49. **`test_observability_index.TestObservabilityIndex.test_zero_distance_produces_zero_risk`:** Proves an edge with an exactly co-located detector ($\text{dist}_e = 0\text{m}$) has $\Omega_e \equiv 0.0$. `[PASSED]`
50. **`test_observability_index.TestObservabilityIndex.test_distance_monotonicity`:** Asserts for any edge with non-zero criticality, increasing physical sensor distance strictly increases $\Omega_e$. `[PASSED]`

---

## 3. Dedicated Audit Benchmark Commands & Artifact Execution

To perform the Phase 4.1 independent scientific review, the following standalone audit scripts were authored, executed, and validated offline:

```powershell
# 1. Spatial Detector Multi-Threshold & Class Prevalence Audit
python scripts/audit_spatial_detector.py
# -> Generated: reports/spatial_detector_threshold_analysis.csv (720 rows)

# 2. Network Resilience Graph Topology & Penalty Sensitivity Audit
python scripts/audit_resilience_connectivity.py
# -> Generated: reports/resilience_connectivity_sensitivity.csv (108 rows)

# 3. Observability Risk Index Distance Decay & Rank Stability Audit
python scripts/audit_observability_sensitivity.py
# -> Generated: reports/observability_sensitivity.csv (400 rows)

# 4. Monte Carlo Uncertainty & Estimation Error vs Outcome Spread Verification
python scripts/audit_monte_carlo.py
# -> Validated SEM scaling, sample variance spread, and flow CV sensitivity
```

All empirical analyses executed completely offline with zero missing artifacts.

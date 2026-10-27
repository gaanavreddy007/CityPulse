# Comprehensive Offline Test Log: CITYPULSE Phase 4.2

**Project Title:** CITYPULSE: Traffic-Sensor Data Quality, Urban Anomaly Detection, and Road-Network Resilience  
**Author:** Transport-Network Data Scientist & Graph Engineer (Antigravity)  
**Date:** October 2026  
**Primary Project Directory:** `./`  
**Execution Environment:** Windows, Python 3.13.7 (64-bit)  
**Test Framework:** Python Standard Library `unittest` (Zero external network dependencies, £0 budget)  
**Overall Status:** **ALL 56 TESTS PASSED (100% SUCCESS RATE, ZERO FAILURES, ZERO ERRORS)**  

---

## 1. Test Suite Execution Command & Real Terminal Output

```powershell
PS .> python -m unittest discover tests
........................................................
----------------------------------------------------------------------
Ran 56 tests in 7.553s

OK
```

---

## 2. Granular Inventory of All 56 Passing Tests Across Modules

### 2.1 Reconstructed Road Graph & Topology Suite (Phase 4.2, 6 Tests)
*File: `tests/test_reconstructed_graph.py`*
1. **`test_node_and_edge_schema_and_lengths`:** Validates reconstructed node ($N=1,047$) and edge ($E=1,932$) tables, asserts zero null attributes, strictly positive piecewise geodetic edge lengths ($1.3\text{m} \le L \le 1,312.8\text{m}$), and verifies elimination of the flat 500m fallback. `[PASSED]`
2. **`test_shared_intersection_connectivity`:** Proves all 1,932 directed edges meet at shared junction nodes with zero coordinate tolerance error ($0.0000000000^\circ$). `[PASSED]`
3. **`test_macro_connectivity_giant_component`:** Proves the network forms a connected urban grid: giant weakly connected component spans **95.1% of all nodes** ($996\text{ nodes}$), and giant strongly connected component spans **87.0% of all nodes** ($911\text{ nodes}$). `[PASSED]`
4. **`test_bridge_representation_and_approach_continuity`:** Validates topological identification and non-zero in-degree approach links and out-degree exit links for all 6 River Clyde crossings (Kingston Bridge, George V Bridge, Glasgow Bridge, Victoria Bridge, Albert Bridge, Clyde Arc). `[PASSED]`
5. **`test_directed_cross_river_routing`:** Proves baseline directed shortest paths exist between southside origins (Tradeston) and northside destinations (City Centre), with realistic travel times ($150.1\text{s}$) across multiple road segments. `[PASSED]`
6. **`test_closure_detour_path_calculation`:** Proves that closing George V Bridge causes a real street detour onto Kingston Bridge, incurring positive finite detour delay ($+32.0\text{s}$, $+21.3\%$) without infinite disconnection. `[PASSED]`

### 2.2 Anomaly Detection Baselines & Spatial Cross-Consistency (9 Tests)
7. **`test_spatial_consistency.TestSpatialConsistency.test_fit_and_zero_leakage_calibration`:** Validates seasonal median/MAD calibration strictly on training split without access to validation/test partitions. `[PASSED]`
8. **`test_spatial_consistency.TestSpatialConsistency.test_isolated_downward_drift_detection`:** Asserts an isolated -50% drift generates a massive residual divergence ($d_{s, n, t} > 3.0$) and correctly triggers the anomaly flag. `[PASSED]`
9. **`test_spatial_consistency.TestSpatialConsistency.test_shared_corridor_change_disambiguation`:** Asserts simultaneous -30% drop across primary and neighbor along the same corridor predominantly generates `SHARED_CORRIDOR_CHANGE` classifications, suppressing false hardware alarms. `[PASSED]`
10. **`test_anomaly_baselines.TestAnomalyBaselines.test_zero_leakage_calibration`:** Asserts baseline fit methods only access the training partition. `[PASSED]`
11. **`test_anomaly_baselines.TestAnomalyBaselines.test_rolling_zscore_strictly_causal_no_future_leakage`:** Asserts strictly backward-looking causal rolling windows with zero future data leakage. `[PASSED]`
12. **`test_anomaly_baselines.TestAnomalyBaselines.test_seasonal_mad_score_direction_and_shape`:** Asserts seasonal median and MAD computation across the 168-hour weekly cycle. `[PASSED]`
13. **`test_anomaly_baselines.TestAnomalyBaselines.test_seasonal_mad_nan_handling_and_fallback`:** Asserts robust fallback to global median and global MAD when seasonal bins contain missing data. `[PASSED]`
14. **`test_anomaly_baselines.TestAnomalyBaselines.test_missingness_and_static_baselines`:** Asserts correct flag generation for static threshold and missingness detectors. `[PASSED]`
15. **`test_anomaly_baselines.TestAnomalyBaselines.test_isolation_forest_and_ecod_scoring`:** Tests PyOD ECOD and scikit-learn Isolation Forest model training, continuous score generation, and prediction shape. `[PASSED]`

### 2.3 Resilience Monte Carlo, Observability & Prototype Suites (11 Tests)
16. **`test_resilience_monte_carlo.TestResilienceMonteCarlo.test_seed_reproducibility`:** Verifies identical random seeds produce bitwise-identical Monte Carlo flow draws and identical $\Delta \mathcal{C}$ metrics. `[PASSED]`
17. **`test_resilience_monte_carlo.TestResilienceMonteCarlo.test_sample_convergence`:** Proves empirical Monte Carlo error decay: asserts $\text{SEM}_{500} < \text{SEM}_{50}$ matching theoretical $O(1/\sqrt{N})$ decay. `[PASSED]`
18. **`test_resilience_monte_carlo.TestResilienceMonteCarlo.test_closure_disconnection_penalty`:** Asserts closing M8 Kingston Bridge disconnects directed OD pairs and incorporates the $M = 3,600\text{s}$ penalty cap without infinite divergence. `[PASSED]`
19. **`test_observability_index.TestObservabilityIndex.test_geodetic_distance_formula`:** Verifies Haversine geodetic distance calculation against known Glasgow geographic benchmarks within 1.0 meter precision. `[PASSED]`
20. **`test_observability_index.TestObservabilityIndex.test_observability_index_mathematical_bounds`:** Asserts $\forall e, \quad \Omega_e \in [0.0, 1.0]$. `[PASSED]`
21. **`test_observability_index.TestObservabilityIndex.test_zero_distance_produces_zero_risk`:** Proves an edge with an exactly co-located detector ($\text{dist}_e = 0\text{m}$) has $\Omega_e \equiv 0.0$. `[PASSED]`
22. **`test_observability_index.TestObservabilityIndex.test_distance_monotonicity`:** Asserts for any edge with non-zero criticality, increasing physical sensor distance strictly increases $\Omega_e$. `[PASSED]`
23. **`test_resilience_prototype.TestResiliencePrototype.test_baseline_graph_construction`:** Tests directed NetworkX graph instantiation across 38 nodes, verifying coordinate properties, edge lengths, capacity, and BPR coefficients. `[PASSED]`
24. **`test_resilience_prototype.TestResiliencePrototype.test_disconnection_handling`:** Tests disconnection handling and verifies that disconnected components trigger the $M=3,600\text{s}$ penalty cap. `[PASSED]`
25. **`test_resilience_prototype.TestResiliencePrototype.test_multi_edge_bridge_closure`:** Tests simultaneous multi-edge capacity removal for dual-carriageway river crossings. `[PASSED]`
26. **`test_resilience_prototype.TestResiliencePrototype.test_parameter_sensitivity`:** Evaluates network cost variance under perturbation of free-flow speeds and design capacities. `[PASSED]`

### 2.4 Data Loader, Ingestion & Temporal Splits (13 Tests)
27. **`test_dataset_offline.TestDatasetOffline.test_locations_schema_and_bounds`:** Validates `locations.csv` structure, 470 detector records, 0 null coordinates, Glasgow bounding box. `[PASSED]`
28. **`test_dataset_offline.TestDatasetOffline.test_flow_schema_and_non_negativity`:** Validates time-series schema, 33,644 rows, hour bounds ($0-23$), integer non-negativity. `[PASSED]`
29. **`test_dataset_offline.TestDatasetOffline.test_datetime_reindexing_and_gap_detection`:** Verifies continuous hourly date range construction across 35,064 calendar hours and identifies the 1,420 missing hours. `[PASSED]`
30. **`test_dataset_offline.TestDatasetOffline.test_synthetic_degradation_injection`:** Verifies baseline perturbation generation, MCAR dropout rate bounds, and offset drift. `[PASSED]`
31. **`test_temporal_splits.TestTemporalSplits.test_calendar_hour_counts_and_leap_year`:** Verifies leap year 2020 inclusion (Feb 29 = 24 hrs), exact calendar hours: Train = 17,544 hrs (731 days), Val = 8,760 hrs (365 days), Test = 8,760 hrs (365 days). `[PASSED]`
32. **`test_temporal_splits.TestTemporalSplits.test_split_boundary_non_overlap`:** Proves non-overlapping contiguous boundaries ($\Delta t = 1\text{ hr}$) and zero temporal leakage. `[PASSED]`
33. **`test_temporal_splits.TestTemporalSplits.test_observed_records_vs_calendar_missingness`:** Verifies exact census counts for 33,644-row detectors: 16,639 observed train records, 8,663 observed val records, 8,342 observed test records. `[PASSED]`
34. **`test_temporal_splits.TestTemporalSplits.test_reindex_preserves_zero_flow_as_distinct_from_missing`:** Confirms omitted rows become `NaN` while legitimate zero traffic ($q=0$) is strictly preserved as `0.0`. `[PASSED]`
35. **`test_data_loader.TestDataLoader.test_load_sensor_locations`:** Tests column checks, coordinate bounds, and error handling. `[PASSED]`
36. **`test_data_loader.TestDataLoader.test_load_sensor_flow`:** Tests schema and negative-value assertions. `[PASSED]`
37. **`test_data_loader.TestDataLoader.test_reindex_sensor_flow`:** Tests continuous hourly reindexing, ensuring 35,064 float32 entries and exact gap mapping. `[PASSED]`
38. **`test_data_loader.TestDataLoader.test_compute_missingness_report`:** Tests `MissingnessReport` generation, computing missing and zero-traffic percentages. `[PASSED]`
39. **`test_data_loader.TestDataLoader.test_split_chronological`:** Tests automated partitioning into non-overlapping `SplitName.TRAIN`, `VAL`, and `TEST` series. `[PASSED]`

### 2.5 Corruption Engine, Sensor Matching, Metrics & Reproducibility (17 Tests)
40. **`test_corruption_engine.TestCorruptionEngine.test_mcar_injection`:** Tests stochastic dropout injection and label alignment. `[PASSED]`
41. **`test_corruption_engine.TestCorruptionEngine.test_burst_injection`:** Tests contiguous block outages and label continuity. `[PASSED]`
42. **`test_corruption_engine.TestCorruptionEngine.test_drift_injection`:** Tests multiplicative offset scaling ($\pm 40\%$). `[PASSED]`
43. **`test_corruption_engine.TestCorruptionEngine.test_stuck_value_injection`:** Tests constant freezing at $0.0$ and training mean $\mu_{\text{train}}$. `[PASSED]`
44. **`test_corruption_engine.TestCorruptionEngine.test_reproducibility_with_seed`:** Tests bitwise-identical corrupted data and labels across identical seeds. `[PASSED]`
45. **`test_sensor_matching.TestSensorMatching.test_high_confidence_match`:** Tests unambiguous dominant edge assignment ($d \le 15\text{m}$, confidence $\ge 0.85$). `[PASSED]`
46. **`test_sensor_matching.TestSensorMatching.test_ambiguity_flagging_at_crossroads`:** Tests detector placed equidistant at a crossroad, ensuring `AMBIGUOUS_MULTI_CANDIDATE`. `[PASSED]`
47. **`test_sensor_matching.TestSensorMatching.test_unmatched_distance_exceeded`:** Tests remote detector placed outside search radius, ensuring `UNMATCHED_DISTANCE_EXCEEDED`. `[PASSED]`
48. **`test_sensor_matching.TestSensorMatching.test_multi_sensor_junction_conflict_detection`:** Tests multi-detector approach conflict detection. `[PASSED]`
49. **`test_benchmark_metrics.TestBenchmarkMetrics.test_perfect_classification`:** Verifies metric outputs for perfect classification ($\text{Precision}=1.0, \text{Recall}=1.0, \text{F1}=1.0, \text{MCC}=1.0$). `[PASSED]`
50. **`test_benchmark_metrics.TestBenchmarkMetrics.test_imperfect_classification`:** Verifies exact mathematical evaluation of contingency table metrics. `[PASSED]`
51. **`test_benchmark_metrics.TestBenchmarkMetrics.test_undefined_precision_when_no_positive_predictions`:** Verifies graceful handling and fallback when no positive anomalies are predicted. `[PASSED]`
52. **`test_benchmark_metrics.TestBenchmarkMetrics.test_undefined_recall_when_no_ground_truth_positives`:** Verifies graceful handling and fallback when no ground-truth positives exist. `[PASSED]`
53. **`test_benchmark_metrics.TestBenchmarkMetrics.test_nan_filtering_in_metric_computation`:** Verifies missing or NaN elements in score/label arrays are systematically excluded without distortion. `[PASSED]`
54. **`test_experiment_reproducibility.TestExperimentReproducibility.test_track_a_determinism_across_runs`:** Proves bitwise exact reproduction across multiple runs under identical seeds. `[PASSED]`
55. **`test_experiment_reproducibility.TestExperimentReproducibility.test_track_a_seed_sensitivity`:** Proves changing seeds produces bounded, non-zero variance. `[PASSED]`
56. **`test_experiment_reproducibility.TestExperimentReproducibility.test_track_b_separation_and_disclaimer`:** Enforces strict isolation of Track B statistical anomalies from Track A evaluation. `[PASSED]`

---

## 3. Phase 4.2 Benchmark Execution Commands

The complete empirical workflow for Phase 4.2 was executed with the following reproducible commands:

```powershell
# 1. Download OpenStreetMap XML tiles and generate source manifest
python scripts/download_osm_network.py

# 2. Parse OSM XML, extract junctions, and construct reconstructed graph CSVs
python scripts/build_reconstructed_graph.py

# 3. Validate graph topology, components, and detour paths
python scripts/validate_reconstructed_graph.py

# 4. Execute resilience experiments across cohorts and scenarios
python scripts/run_reconstructed_resilience.py

# 5. Run complete test suite (all 56 offline tests)
python -m unittest discover tests
```

All 56 unit tests pass 100% offline with zero failures and zero network calls, verifying the software architecture and experimental reproducibility.

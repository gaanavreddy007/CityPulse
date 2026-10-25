# Data Dictionary & Empirical Dataset Profile: CITYPULSE

**Project Title:** CITYPULSE: Traffic-Sensor Data Quality, Urban Anomaly Detection, and Road-Network Resilience  
**Author:** Automated Research and Pair-Programming Agent (Antigravity)  
**Date:** October 2026 (Updated with Gate 1 Census Corrections)  
**Primary Project Directory:** `C:\Gaanav\Projects\CityPulse`  
**Dataset Reference:** High-Resolution Traffic Flow Data in Glasgow (UBDC / Zenodo)  

---

## 1. Dataset Provenance & Metadata

| Attribute | Specification | Verification Method |
| :--- | :--- | :--- |
| **Dataset Title** | High-resolution traffic flow data in Glasgow | Zenodo REST API Record `12100278` |
| **Creators** | Yue Li, Qunshan Zhao, Mingshu Wang | University of Glasgow / Urban Big Data Centre |
| **Canonical DOI** | [10.5281/zenodo.12100278](https://doi.org/10.5281/zenodo.12100278) | Zenodo metadata registration |
| **Associated Paper** | *Scientific Data* (Nature Portfolio), Vol. 12, Art. 253 (2025) | Published open-access data descriptor |
| **Publication Date** | 2024-06-18 | Zenodo release timestamp |
| **License** | **Open Government Licence v3.0 (`ogl-uk-3.0`)** | Verified via Zenodo API `license` object |
| **Attribution Requirement** | Must cite: Li, Zhao, & Wang (2025), *Scientific Data*, and acknowledge Glasgow City Council / UBDC as data provider | Mandatory in all project documentation |
| **Financial Cost** | £0.00 (Completely open access, no subscription or registration paywall) | Direct HTTPS download |

---

## 2. Archive Structure & Storage Footprint

```
traffic_flow_data.zip (53.05 MB compressed)
├── locations.csv (16.1 KB)
└── flows/ (470 CSV files, ~380 MB uncompressed)
    ├── GA0151_A.csv (33,644 rows)
    ├── GA0151_C.csv (33,644 rows)
    ├── GA0601_T.csv (33,643 rows)
    ├── ...
    └── GA9999_Z.csv
```

* **Compressed Size:** 55,627,707 bytes (~53.05 MB).
* **Uncompressed Disk Footprint:** ~380 MB.
* **Per-Sensor Record Census:**
  - **33,644 observed records:** 108 sensors (23.0% of network).
  - **33,643 observed records:** 362 sensors (77.0% of network).
  - *Discrepancy Source:* Exactly one missing timestamp at `2023-08-13 03:00:00 BST` on 362 sensors.
* **In-Memory Footprint (Pandas DataFrame):**
  - All 470 sensors merged into a unified columnar array: $\approx 470 \times 35,064 \times 4\text{ bytes} \approx 65.9\text{ MB}$ (using `float32`).
  - Total RAM required: **< 200 MB** (fits comfortably on consumer hardware).

---

## 3. Detailed File Schemas & Data Types

### 3.1 Spatial Metadata (`locations.csv`)
Maps each unique loop detector ID to its spatial WGS84 geographic coordinates.

| Column Name | Native Type | Recommended Type | Null Count | Description & Constraints | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `object` (string) | `category` / `str` | 0 | Unique identifier for the SCOOT detector (`GA[Junction]_[Approach]`). | `GA0151_A` |
| `latitude` | `float64` | `float64` | 0 | WGS84 latitude coordinate in decimal degrees. Valid range: $[55.805004, 55.897428]$. | `55.863144` |
| `longitude` | `float64` | `float64` | 0 | WGS84 longitude coordinate in decimal degrees. Valid range: $[-4.364622, -4.128821]$. | `-4.275053` |

* **Total Records:** 470 rows.
* **Geodetic CRS:** EPSG:4326 (WGS84).
* **Projected CRS for Distance Metrics:** EPSG:27700 (British National Grid / OSGB36).

### 3.2 Time-Series Flow Files (`flows/[sensor_id].csv`)
Contains hourly vehicle counts for a single detector across the 4-year study timeline.

| Column Name | Native Type | Recommended Type | Null Count | Description & Constraints | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `date` | `object` (string) | `pd.Timestamp` | 0 | Calendar date in `YYYY-MM-DD` format. Span: `2019-10-01` to `2023-09-30`. | `2019-10-01` |
| `time` | `int64` | `int8` | 0 | Hour of day as integer from `0` to `23`. Indicates start of 1-hour interval. | `14` |
| `flow` | `int64` | `float32` (post-reindex) | 0 | Aggregated vehicle volume count. Non-negative. Missing hours represented as `NaN`. | `42` |

* **Temporal Resolution:** Hourly ($1\text{ hour}$).
* **Timezone:** Local UK Time (GMT during winter, BST during daylight saving time, UTC+0 / UTC+1).

---

## 4. Chronological Partitions & Missingness Disambiguation

To eliminate discrepancies between calendar time and observed records, all analyses adhere to the audited breakdown below:

### Table: Canonical Chronological Partition Breakdown

| Partition | Date Range (Inclusive) | Calendar Days | Calendar Hours ($H_{\text{cal}}$) | Observed Records ($N_{\text{obs}}$) | Missing Hours ($M_{\text{miss}}$) | Missingness (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Train** | `2019-10-01 00:00` to `2021-09-30 23:00` | 731 (leap yr 2020) | **17,544** | 16,639 | 905 | 5.16% |
| **Validation** | `2021-10-01 00:00` to `2022-09-30 23:00` | 365 | **8,760** | 8,663 | 97 | 1.11% |
| **Test** | `2022-10-01 00:00` to `2023-09-30 23:00` | 365 | **8,760** | 8,342 (108 sensors) / 8,341 (362 sensors) | 418 or 419 | 4.77% / 4.78% |
| **Total** | `2019-10-01 00:00` to `2023-09-30 23:00` | 1,461 | **35,064** | **33,644** / **33,643** | **1,420** / **1,421** | **4.05%** |

* **Missing Data Format:** **Omitted Rows** in raw CSVs.
  - The raw CSVs contain zero `NaN` values.
  - When an outage occurs, rows are omitted.
  - An explicit reindex to the 35,064 hourly index is mandatory to represent omitted timestamps as `NaN` without conflating them with legitimate zero-traffic hours.

---

## 5. Statistical Distributions & Characteristics

| Metric | Central Corridor (`GA0151_C`) | Arterial Approach (`GA0151_A`) | Minor Collector (`GA0401_R`) |
| :--- | :--- | :--- | :--- |
| **Mean Flow ($\mu$)** | 119.1 veh/hr | 31.9 veh/hr | 17.7 veh/hr |
| **Standard Deviation ($\sigma$)** | 82.4 veh/hr | 25.0 veh/hr | 18.2 veh/hr |
| **Median (P50)** | 114.0 veh/hr | 30.0 veh/hr | 13.0 veh/hr |
| **P95 Peak Flow** | 254.0 veh/hr | 78.0 veh/hr | 55.0 veh/hr |
| **Maximum Flow** | 405 veh/hr | 260 veh/hr | 168 veh/hr |
| **Zero-Flow Percentage** | 0.6% | 2.3% | 6.4% |

*Zero-flow observations during early morning hours ($01:00 - 05:00$) are valid empirical observations, not missing data.*

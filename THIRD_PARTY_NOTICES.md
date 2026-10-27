# CITYPULSE -- Third-Party Notices and Attribution

The MIT Licence in LICENSE governs the original CITYPULSE source code
(Python packages in citypulse/, scripts/, and tests/). It does not supersede or
replace the independent licences that govern the third-party datasets and map data.

---

## 1. Glasgow SCOOT Traffic Flow Dataset

**Licence:** Open Government Licence v3.0 (OGL v3.0)

**Source:** Li, Y., Zhao, Q., and Wang, M. (2025). High-resolution traffic flow data
from the urban traffic control system in Glasgow. Scientific Data, 12, 253.
Zenodo: https://doi.org/10.5281/zenodo.12100278

**Data provider:** Urban Big Data Centre (UBDC), University of Glasgow, and Glasgow
City Council.

**Licence terms:** https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/

You are free to copy, publish, distribute, transmit, adapt, and exploit the information
commercially and non-commercially, provided you acknowledge the source:

    Contains public sector information licensed under the Open Government Licence v3.0.

The licence does not permit claiming that the Crown or data provider endorses your use.

**Affected files:**
- data/raw/traffic_flow_data.zip -- raw SCOOT hourly flow archive
- data/sample/locations.csv -- sensor spatial coordinates
- data/sample/flows/ -- per-sensor hourly resampled flow time series

---

## 2. OpenStreetMap Road Network Data

**Licence:** Open Data Commons Open Database License (ODbL 1.0)

**Attribution:** (c) OpenStreetMap contributors

**Licence terms:** https://opendatacommons.org/licenses/odbl/1-0/

You are free to copy, distribute, transmit, and adapt the database.
Attribution: Any public use must credit OpenStreetMap contributors.
Share-Alike: Adapted databases must be released under ODbL.

**Derived datasets in this repository (ODbL notice required on redistribution):**
- data/network/reconstructed_network_nodes.csv -- 1,047 road junctions (WGS84)
- data/network/reconstructed_network_edges.csv -- 1,932 directed road links
- data/network/raw_osm/central_core.osm -- OSM XML extract (source data)
- data/network/raw_osm/clyde_arc_west.osm -- OSM XML extract (source data)

---

## 3. Scientific Libraries

Runtime dependencies are listed in requirements.txt. Each is distributed under its
own permissive licence:

| Package      | Licence          | Project page                     |
|:-------------|:-----------------|:---------------------------------|
| NumPy        | BSD 3-Clause     | https://numpy.org                |
| pandas       | BSD 3-Clause     | https://pandas.pydata.org        |
| SciPy        | BSD 3-Clause     | https://scipy.org                |
| NetworkX     | BSD 3-Clause     | https://networkx.org             |
| scikit-learn | BSD 3-Clause     | https://scikit-learn.org         |
| PyOD         | BSD 2-Clause     | https://pyod.readthedocs.io      |
| Matplotlib   | Matplotlib (PSF) | https://matplotlib.org           |
| Requests     | Apache 2.0       | https://requests.readthedocs.io  |

---

See reports/verified_sources.md for the full citation audit, Zenodo DOI
verification records, and licence compliance notes.

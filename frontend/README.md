# CityPulse Interactive Research Web Application

Interactive data science portfolio and research visualization web application for **CityPulse: Traffic Sensor Data Quality, Spatial Consistency & Road Network Resilience in Glasgow**.

## Features

- **Executive Overview**: Research questions, core metrics, directional couplet mechanics, and methodological constraints.
- **Traffic Flow Explorer**: Interactive diurnal profiles and temporal flow traces for 10 SCOOT inductive loop detectors across Glasgow.
- **Anomaly Detection Lab**: Benchmark tradeoffs comparing seasonal ESD, Isolation Forest, and rolling z-scores across synthetic corruption types, plus spatial cross-consistency tracking under severe weather.
- **Network Resilience Simulator**: Comparative bridge severance scenarios across River Clyde crossings (King George V, Glasgow Bridge, M8 Kingston Bridge, Clyde Arc).
- **Claims & Evidence Audit**: Interactive filterable verification catalog tracing every portfolio claim to saved output artifacts and safe phrasing.
- **Publication Figures**: Full-resolution interactive lightbox viewer for all 6 publication figures.

## Tech Stack

- **Framework**: React 19 + TypeScript + Vite
- **Styling**: Vanilla CSS with modern dark glassmorphism design system
- **Charts**: Recharts
- **Icons**: Lucide React
- **Typography**: Inter & JetBrains Mono

## Local Development

```powershell
cd frontend
npm install
npm run dev
```

## Production Build

```powershell
npm run build
```

Static build outputs are emitted to `frontend/dist/`.

## Deployment

A GitHub Actions workflow is provided in `.github/workflows/deploy-pages.yml` to automatically build and deploy to GitHub Pages upon push to `master`. Enable GitHub Pages under **Repository Settings -> Pages -> Build and deployment: Source -> GitHub Actions**.

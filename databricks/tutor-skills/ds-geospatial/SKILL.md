---
name: ds-geospatial
description: "Geospatial method family: spatial autocorrelation (Moran's I / LISA), CRS and projection traps, spatial joins, spatial CV (spatial-leakage delta), point/raster/polygon data models, and geo feature engineering. Owns the split/validation scheme whenever composed with another family on spatially autocorrelated data…"
---

# ds-geospatial

## Subfields

- **Point/raster/polygon models** — trigger: geospatial data enters the
  task and its representation isn't yet stated. OGC, "Simple Feature
  Access – Part 1: Common Architecture" (ISO 19125) —
  https://www.ogc.org/publications/standard/sfa/ (vector: point/line/
  polygon geometry types and their operations) and GDAL, "Raster Data
  Model" — https://gdal.org/en/stable/user/raster_data_model.html (band,
  geotransform, coordinate system). Vector and raster are not
  interchangeable representations of the same information — converting
  between them is lossy in a specific, statable direction; features
  derived at one representation's resolution/grain don't transfer to the
  other without re-deriving them.
- **CRS/projection traps** — trigger: any distance, area, or join
  computation on geospatial data. Snyder, "Map Projections: A Working
  Manual," USGS Professional Paper 1395, 1987 —
  https://pubs.usgs.gov/pp/1395/report.pdf : no projection preserves area,
  shape, distance, and direction simultaneously — the projection must be
  chosen for the specific computation (equal-area for density, conformal
  for angle-preserving local analysis). Joining or computing distances
  across mismatched CRSs without reprojecting silently produces wrong
  numbers; a geographic CRS (lat/lon in degrees) is not a distance/area
  unit (Gates).
- **Spatial joins** — trigger: combining this geospatial dataset with
  another by location rather than by key. **LITERATURE-THIN**: the
  canonical treatment lives at the implementation level, not a single
  independently-confirmable survey. PostGIS, "Chapter 4. Data Management"
  (spatial predicates §4.8, spatial indexes §4.9) —
  https://postgis.net/docs/using_postgis_dbmanagement.html : a spatial
  join's cost and correctness both depend on the predicate chosen
  (intersects ≠ contains ≠ within) and on a spatial index (GiST/R-tree)
  existing — without one, a spatial join degrades to an all-pairs geometry
  comparison. Cites `ds-gather`'s join gate (same-semantics + cardinality
  check) and `ds-data-models`' grain contract — pointers, not re-derived
  here (Gates).
- **Spatial autocorrelation** — trigger: "is there spatial clustering /
  pattern in this variable," or before choosing a spatial CV block size.
  Esri, "Spatial Autocorrelation (Global Moran's I) (Spatial Statistics
  Tools)" —
  https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-statistics/spatial-autocorrelation.htm
  : practitioner-standard documentation of Global Moran's I and its null
  hypothesis (complete spatial randomness); Moran's 1950 *Biometrika*
  paper and Anselin's 1995 LISA (Local Indicators of Spatial Association)
  paper are the academic origin of the global and local statistics
  respectively — named as the origin, not independently fetched for this
  citation. Moran's I tests only under a *chosen* spatial-weights
  definition (contiguity vs. distance-band vs. k-nearest-neighbor changes
  the result); a non-significant global statistic does not rule out local
  clustering — that's what LISA is for.
- **Spatial CV (spatial-leakage delta)** — trigger: any fold/split touches
  spatially autocorrelated data, or choosing among candidate spatial models.
  Roberts, Bahn, Ciuti, Boyce, Elith, Guillera-Arroita, Hauenstein,
  Lahoz-Monfort, Schröder, Thuiller, Warton, Wintle, Hartig, Dormann,
  "Cross-validation strategies for data with temporal, spatial, hierarchical
  or phylogenetic structure," *Ecography* 40(8), 2017 —
  https://www.ecography.org/appendix/ecog-02881 : standard CV underestimates
  prediction error on spatially structured data because of autocorrelation
  between train/test points, even when residual correlation isn't visible —
  recommends block CV.
- **Geo feature engineering** — trigger: deriving model features from
  spatial structure (spatial lag, distance-to-nearest, spatial-weights
  aggregates). **LITERATURE-THIN**: no single canonical academic reference
  for the practice as a whole; practitioner/tooling-driven. PySAL (Python
  Spatial Analysis Library) project page — https://pysal.org/ : umbrella
  toolkit for spatial-weights construction, spatial-lag features, and
  exploratory spatial statistics underlying most geo feature engineering
  in practice. Don't present this as a settled discipline — any specific
  technique needs its own justification, not a blanket "geospatial
  features" label.

`mandatory` here means: fires whenever `ds-geospatial` composes at all,
same convention as `ds-gather`'s selection-into-the-dataset row — every
geospatial task has a data model and a CRS, whether or not it joins,
diagnoses clustering, cross-validates, or engineers features.

## Selection tree

1. **Data model**: is this task's geospatial data point, raster, or
   polygon (or a mix)? State the representation before anything else —
   **point/raster/polygon models**. A representation switch later is a
   lossy re-derivation, not a free reformat.
2. **CRS**: is every distance/area/join computation ahead stated in a
   projected CRS with named units, or still in a geographic CRS (degrees)?
   Resolve before proceeding — **CRS/projection traps**. Pick the
   projection family for the computation (equal-area vs. conformal), don't
   default to whatever the source shipped in.
3. **Combining with another spatial dataset?** → **spatial joins**: name
   the predicate (intersects/contains/within), confirm a spatial index
   exists, cite `ds-gather`'s join gate and `ds-data-models`' grain
   contract rather than re-deriving either.
4. **Describing or testing spatial pattern?** → **spatial autocorrelation**:
   choose the spatial-weights definition, run Global Moran's I; if
   non-significant, still check LISA before concluding "no pattern" —
   heterogeneous local clustering can hide inside a null global statistic.
5. **Building features for a downstream model?** → **geo feature
   engineering**: spatial lag, distance-to-nearest, spatial-weights
   aggregate — each technique justified on its own.
6. **Any model here will be split/validated?** Is spatial autocorrelation
   in play (diagnosed at step 4, or plausible given the data's spatial
   structure even if step 4 wasn't run)? Yes → **spatial CV**: blocked or
   buffered CV, block size exceeding the diagnosed/plausible
   autocorrelation range. No → state why a standard split is safe here,
   don't default to blocked CV unexamined. Composed with `ds-timeseries` on
   spatiotemporal data → strongest-constraint rule (Edges/Pairings).

## Family-specific pitfalls and evaluation

- **Weights-definition sensitivity**: a spatial autocorrelation result is
  conditional on the chosen spatial-weights definition — report which one
  (contiguity, distance-band, k-NN), don't present the statistic as
  weights-independent.
- **Local clustering masked by a non-significant global statistic**: don't
  conclude "no spatial pattern" from Global Moran's I alone when local
  heterogeneity is plausible — check LISA.
- **Degree-distance conflation**: a distance or area computed in a
  geographic CRS (degrees) is not a real distance/area — this is gate
  material (Gates), not a caveat to mention after the fact.
- **Join predicate/index mismatch**: an unindexed spatial join silently
  degrades to an all-pairs comparison; the wrong predicate silently
  returns the wrong set — both fail quietly, not loudly.
- **Vector/raster conversion treated as free**: rasterization/
  vectorization is lossy in a specific, statable direction — a model
  trained on one representation's derived features doesn't transfer to
  the other without re-deriving them.
- **Evaluation delta on `ds-evaluate`'s generic scorecard**: standard
  (non-spatial) CV underestimates prediction error on spatially structured
  data even when residual correlation isn't visible in-sample (Roberts et
  al., above) — this family's delta is that the *reported* validation
  scheme must be the blocked/buffered spatial CV whenever spatial
  autocorrelation is in play, not a fixed random holdout defended after
  the fact.

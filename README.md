# Sensor contribution audit

A small, portable analytical companion to **Establishing sensor contributions
in multimodal AI**. It reproduces the equation-derived timing-error illustration
and checks declared model-input dimensions. Separately attributed tables retain
a small set of reported values from two source articles. It contains no individual
participant measurements, trained weights, internal clinical predictions or manuscript files.

Repository: [shumao469/sensor-contribution-audit](https://github.com/shumao469/sensor-contribution-audit).
The corresponding contributor is Shumao Xu. An archival identifier and code
licence remain pending. The analytical software and the attributed article
summaries have distinct provenance and licensing scopes.

## Overview and quick navigation

| Capability | Implementation | What it produces |
|---|---|---|
| Timing-error retention | timing.py | Closed-form retained coherent amplitude and expected complex phasor |
| Timing budget | timing.py | Maximum relative jitter SD for a specified retention criterion |
| Reference verification | validation.py | Coordinate/value verification of all 840 retained analytical cells |
| Figure generation | plotting.py | Editable SVG; optional native-vector PDF and 300-dpi PNG |
| Feature-dimension audit | dimensions.py | Affine-score parameter count and declared concatenated-readout dimensions |
| Attributed article values | reported.py and data/reported | Curated aggregate transcriptions with separate source attribution |
| CLI and tests | cli.py and tests | Reproducible commands and analytical/software contracts |

### Download and first run

```bash
git clone https://github.com/shumao469/sensor-contribution-audit.git
cd sensor-contribution-audit
python --version
python run_audit.py --help
python run_audit.py validate --out outputs/validation.json
python run_audit.py generate --out outputs
```

Use Python 3.10 or later. The core calculation, SVG writer and command-line runner require only the Python standard library. No GPU, trained model, participant dataset or Jupyter installation is needed.

### Optional isolated environment

```bash
python -m venv .venv
```

Activate with `.\.venv\Scripts\Activate.ps1` in Windows PowerShell, or `source .venv/bin/activate` on Linux/macOS/WSL. Install the optional rendering lock only if PDF/PNG output is needed. Running directly through run_audit.py avoids requiring an editable installation.

### Typical workflow

1. Run validate and confirm both reference-grid and budget-substitution checks pass.
2. Generate analytical CSV/JSON/SVG outputs into a new output directory.
3. Optionally render PDF/PNG using --with-plots.
4. Run dimensions for the explicitly declared feature/latent sizes of interest.
5. Export reported-values separately; these are literature transcriptions, not outputs of the timing model.
6. Run the tests and retain the command, interpreter version, generated summary and output hashes for provenance.

### Python API

After installation, or with src on the Python path:

```python
from sensor_contribution_audit.timing import coherent_amplitude, jitter_budget_ms
from sensor_contribution_audit.dimensions import dimension_audit

print(coherent_amplitude(20, 3.65))   # frequency in Hz; relative jitter SD in ms
print(jitter_budget_ms(20, 0.9))      # approximately 3.65 ms
print(dimension_audit(12, 8))
```

For editable installation, use python -m pip install -e .; its build backend uses the exact versions declared in pyproject.toml. Analytical API units remain explicit regardless of the command used.

### CLI reference

| Command | Key options | Purpose |
|---|---|---|
| validate | --reference PATH, --out PATH | Verify bundled or supplied reference CSV |
| generate | --out DIR, --with-plots | Write deterministic analytical tables and graphics |
| dimensions | --d-x, --d-z, optional --h-x/--h-z/--quality/--availability, --out | Report declared dimensions and affine parameter counts |
| reported-values | --out PATH | Export attributed article values as JSON |
| --version | Global option | Print package version |

The generate command uses the bundled 1–40 Hz, 0–20 ms grid and 0.9 retention contour. For other frequencies, jitter values or retention requirements, use the timing API; there are no corresponding custom-grid CLI switches.

### Repository layout

```text
run_audit.py                  Checkout runner
pyproject.toml                Package metadata and build pins
requirements-plot-lock.txt    Optional rendering dependencies
src/sensor_contribution_audit/
  timing.py                   Closed-form timing equations
  dimensions.py               Dimension bookkeeping
  validation.py               Retained-reference checks
  plotting.py                 Shared-scene SVG/PDF/PNG generation
  reported.py                 Attributed literature export
  data/                       Analytical reference and literature provenance
examples/generated/           Bundled example tables and figures
tests/                        Analytical and CLI regression tests
MIGRATION.md                  Original repository and pinned source commit
```

### Troubleshooting

| Symptom | Action |
|---|---|
| Command not found | Use python run_audit.py from the repository root, or install the package |
| Module import fails in API use | Install with pip -e . or add src to the Python path |
| PDF/PNG dependencies unavailable | Install requirements-plot-lock.txt, or generate core SVG/CSV/JSON without --with-plots |
| Permission error writing output | Choose a writable output directory |
| Invalid frequency/jitter/dimension | Supply finite values in the documented domain; dimensions are counts |
| Validation differs for custom CSV | Compare complete grid coordinates, units and values against the specified equation |

### Migration and licensing

This repository was extracted from the sensor-contribution-audit directory of shumao469/stroke at commit 265b024086b9cab207704db233da06ea091427ee. See MIGRATION.md. Earlier validation/runtime reports describe that retained source package; a fresh migration test record is stored separately.

The source package reserves code rights pending a licence decision. That policy is preserved; creating this standalone repository does not assign a new code licence. Article-value attribution and CC BY scopes remain separate as described below and in LICENSE_PENDING.md.

## What the calculation establishes

For a unit complex sinusoid of frequency `f` and a relative timing shift
`epsilon_delta ~ Normal(0, sigma_delta^2)`, independent of the underlying phasor:

```text
H(f, sigma_delta)
  = abs(E[exp(i * 2*pi*f*epsilon_delta)])
  = exp(-(2*pi*f*sigma_delta)^2 / 2).
```

`E` denotes expectation, `i` the imaginary unit, `f` frequency in hertz and
`sigma_delta` the standard deviation of residual relative timing error in
**seconds**. The public functions and CSV take milliseconds and perform an
explicit `/1000` conversion. `H` is dimensionless and lies between zero and one.

The retained reference grid has exactly **840 cells**: `f = 1,...,40 Hz` and
`sigma_delta = 0,...,20 ms`, including both endpoints. The contour is sampled
directly from its analytical equation, rather than estimated from heatmap cells:

```text
sigma_delta_max = sqrt(-2*log(eta)) / (2*pi*f), in seconds.
```

For the illustrative requirement `eta = 0.9`, the corresponding budgets round
to **3.65 ms at 20 Hz** and **1.83 ms at 40 Hz**. This retention criterion is an
illustration, not a universal device-acceptance threshold.

The notebook-free implementation uses Python's standard library. Optional
dependencies support native vector PDF and a 300-dpi PNG. SVG retains text and
individual cells as editable objects; PDF also uses native geometry and text.

## Run from a checkout

Requires Python 3.10 or newer; the recorded test environment is CPython 3.12.14.

```bash
python run_audit.py validate
python run_audit.py generate --out outputs
python -m unittest discover -s tests -v
```

For PDF and PNG export, install the explicitly pinned optional environment:

```bash
python -m pip install -r requirements-plot-lock.txt
python run_audit.py generate --out outputs --with-plots
```

An installable command is also supplied:

```bash
python -m pip install -e .
sensor-contribution-audit validate
sensor-contribution-audit generate --out outputs
```

The build-tool pins are in `pyproject.toml`; optional rendering-package pins are
in `requirements-plot-lock.txt`. Core tests and SVG generation require neither
NumPy nor a plotting library. PDF/PNG tests are explicitly skipped when their
optional dependencies are unavailable.

## Reported article values

```bash
python run_audit.py reported-values --out outputs/reported_source_values.json
```

This command exports attributed transcriptions; it performs no inferential test,
pooling or model fit. The original curated CSV tables and the source map are in
`src/sensor_contribution_audit/data/reported/`.

| Source and endpoint | Retained values | Scope |
| --- | --- | --- |
| Ortega-Martinez et al., HbO CNR | Overt 1.20 to 4.73, reported ratio 3.94; covert 0.343 to 1.34, reported ratio 3.91 | Use author-reported ratios, rather than dividing rounded means |
| Same study, concentration-space classification | Reported p = 0.056 overt, 0.17 covert | Author-selected maximum-difference 13-16-s window; within-person trial validation |
| Same study, 730-nm optical-density branch | Reported p = 0.03 overt, 0.15 covert | Separate representation and branch |
| Shin et al., word-generation task | EEG 76.9% at 10 s; NIRS 74.3% at 14 s; hybrid 80.7% at 11 s | Different modality-specific selected 5-s windows in 26 healthy participants |

The times in Shin et al. are window right edges, rather than end-to-end device
latency. These peaks are not an equal-time superiority comparison. The optical
correction and hybrid prediction summaries come from separate studies; their
endpoints remain separate. Numerical transcription tests verify the retained
values and do not establish physiological, predictive or clinical validity.

Sources: Ortega-Martinez, A. et al., *Neurophotonics* **9**, 025003 (2022),
[doi:10.1117/1.NPh.9.2.025003](https://doi.org/10.1117/1.NPh.9.2.025003), Table 2
and sections 3.3-3.4; Shin, J. et al., *Scientific Data* **5**, 180003 (2018),
[doi:10.1038/sdata.2018.3](https://doi.org/10.1038/sdata.2018.3), Dataset C and
Fig. 7. Both source articles state CC BY 4.0. These tables are attributed
transcriptions under that scope, separate from the code's reserved-rights policy.

## Outputs

| File | Meaning |
| --- | --- |
| `gaussian_relative_jitter_heatmap.csv` | Exact 40-by-21 analytical grid |
| `retention_0p9_contour.csv` | 200 directly evaluated contour points |
| `analytical_summary.json` | Equation, units, assumptions, budgets and reference validation |
| `timing_budget.svg` | Editable vector heatmap; no raster image embedded |
| `timing_budget.pdf` | Optional vector PDF of the same shared scene |
| `timing_budget_300dpi.png` | Optional high-resolution render of that PDF |

Generation writes these named files in the requested output folder. Repeated
runs replace those generated files deterministically. It never modifies the
bundled reference table. The PNG is a preview, while SVG and PDF preserve vectors.

## Dimension bookkeeping

```bash
python run_audit.py dimensions --d-x 12 --d-z 8
python run_audit.py dimensions --d-x 12 --d-z 8 --h-x 6 --h-z 4 --quality 2 --availability 2
```

For the affine score `s = w_x.T*x + w_z.T*z + b`, the input dimensions are `d_x`
and `d_z`. The combined feature vector has `d_x + d_z` entries. Coefficient
vectors have matching dimensions and the scalar score has `d_x + d_z + 1`
parameters including its intercept. Its output dimension remains one.

The optional encoder audit reports a **declared concatenated readout input**
of size `h_x + h_z + quality + availability`. This is bookkeeping for that
specified representation, not a universal description of attention or gating.
Encoder and fusion parameter counts remain architecture-dependent. Quality and
availability are observed inputs, rather than trainable parameters. These
checks establish dimensional consistency; they are not empirical model tests.

## Interpretation and limitations

* `H` is `abs(E[Z])`. It is not `E[abs(Z)]`, single-observation power, ERD,
  classification accuracy, measured coherence or magnitude-squared coherence.
* Under a rigid shift of each sinusoid, each observation retains its amplitude
  and power. Phase cancellation affects coherent averaging. The squared
  magnitude of the expected complex amplitude is `H^2`, a distinct quantity.
* A fixed clock offset changes phase. The Gaussian shift model does not model
  clock drift, sensor buffering, interpolation error or sample-by-sample time
  warping. Those effects require appropriate measurements and models.
* The jitter is **relative**. For two timing errors expressed in the same units,
  `Var(epsilon_x - epsilon_z) = Var(epsilon_x) + Var(epsilon_z)
  - 2*Cov(epsilon_x, epsilon_z)`. Treating separate clocks as independent is an
  additional assumption, not an implication of this plot.
* The calculation concerns a specified frequency component. EEG carrier
  frequency, feature-envelope dynamics and haemodynamic dynamics are different
  quantities. It does not estimate HbO, HbR, cerebral oxygen saturation,
  physiological coupling or clinical benefit.
* The model neither specifies a sampling rate nor validates a commercial device.
  A physiological response delay is separate from a clock error.
* The package performs no patient-level analysis, tuning, training or model
  selection. Recovery prediction and new fusion validation remain outside scope.

## Reproducibility and provenance

The reference table in `src/sensor_contribution_audit/data/figure1a_reference.csv`
is a retained analytical reference, not external experimental ground truth.
Its provenance and SHA-256 are recorded beside it. `validate` checks every
coordinate and value against the closed form, using absolute tolerance `1e-14`,
and substitutes the 20/40-Hz budgets back into the retention equation.

The deterministic CSV/JSON/SVG outputs and optional PDF/PNG pair are tested for
bytewise repeatability within the pinned environment. Floating-point round-off,
font substitution and rendering-engine versions can affect bytes across
environments; the numerical reference tolerance remains explicit. Tests cover
the stated analytical identities, units, domain checks, scalar output dimension,
reference coverage and command-line entry points. They do not test a biological
claim or an empirical algorithmic advantage.

The author can select a code licence and add a DOI after an archival service
assigns one. `CITATION.cff` identifies the confirmed contributor and repository;
it omits an unassigned DOI. See `LICENSE_PENDING.md` for the scope of the code
and the separately attributed article values.

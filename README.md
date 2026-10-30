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

Read the [complete formulas and derivations](#technical-derivations-and-interpretation)
on this homepage: [clock and response models](#1-clock-registration-and-response-models),
[Gaussian timing and finite samples](#3-gaussian-characteristic-function-and-coherent-amplitude),
[timing budgets](#5-inverting-a-chosen-retention-criterion), and
[affine/nonlinear model expansion](#6-adding-fixed-features-to-an-affine-score).

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

## Technical derivations and interpretation

All equations, derivations, symbol definitions and assumptions are included
below on this repository homepage. They accompany the v18 revision of
*Establishing sensor contributions in multimodal AI*. The results are mathematical
relations and software checks, separate from the attributed aggregate article
values elsewhere in this repository.

A [standalone Markdown copy](docs/derivations.md) and an
[editable LaTeX source](docs/derivations.tex) are retained for separate use.
The [29 October verification record](docs/verification_2026-10-29.json)
documents the derivation update at that date; its payload hashes are historical.
The homepage presentation was expanded on 30 October 2026 without changing
the equations, implementation, reference data, article values or bundled figures.

### 1. Clock registration and response models

A first-order clock map is

$$
t_{\mathrm{ref}}=a\,t_{\mathrm{device}}+b.
$$

Both times are measured in seconds, the rate factor $a$ is dimensionless, and
the offset $b$ is in seconds. For corresponding measured physical events
$(u_j,v_j)$, a weighted least-squares estimate minimises

$$
\sum_j \lambda_j\left[v_j-(a u_j+b)\right]^2,
\qquad \lambda_j\geq 0.
$$

Here $u_j$ and $v_j$ are device and reference event times, and $\lambda_j$ is a
declared event weight. This fit treats device event times as sufficiently
precise explanatory coordinates. Appreciable errors in both coordinates call
for an errors-in-variables model. At least two distinct event times with positive
weights are needed to identify a rate and offset; timing coverage and event uncertainty determine
the useful precision. Residuals at retained physical events assess the map after
fitting. A fit residual and an independently checked timing error answer
different questions.

Registration places observations on a common timebase. Response operators
describe how a physical process reaches each sensor. In Fig. 1a, $H_x$ and $H_z$
label those response operators; they are distinct from the scalar retention
factor $H$ derived below. For the EEG–fNIRS example, the conceptual models are

$$
e(t)=L j(t)+\varepsilon_e(t),
$$

$$
c(t)=K[h*n](t)+u_s(t)+\varepsilon_c(t).
$$

$e(t)$ is scalp voltage; $j(t)$ is a vector of source currents; and $L$ is the
electrical lead-field operator mapping those sources to electrodes.
$\varepsilon_e(t)$ denotes residual contributions. In the second expression,
$c(t)$ denotes relative haemoglobin estimates, $n(t)$ a conceptual neural drive,
$h$ a haemodynamic response kernel, $*$ convolution, $K$ an effective optical
sensitivity mapping, $u_s(t)$ superficial/systemic contributions, and
$\varepsilon_c(t)$ residual contributions. The optical expression is an
approximate explanatory model under declared pathlength and tissue-sensitivity
assumptions. It supplies neither an absolute cerebral oxygen saturation nor an
identified physiological coupling estimate. Its units depend on the declared
haemoglobin conversion and scaling. Clock correction preserves the physiological
response delay represented by $h$.

These conceptual measurement relations are explained here for the manuscript;
the package implements timing and dimension bookkeeping, rather than an EEG
source model or a haemodynamic inversion.

### 2. Relative timing error

After registration, let $\varepsilon_x$ and $\varepsilon_z$ be residual timing
errors for two observations of a common event, expressed in seconds. Choose the
relative-error convention

$$
\varepsilon_\Delta=\varepsilon_z-\varepsilon_x.
$$

Its variance follows directly from covariance algebra:

$$
\sigma_\Delta^2=\sigma_z^2+\sigma_x^2
 -2\mathrm{Cov}(\varepsilon_x,\varepsilon_z).
$$

$\sigma_x$ and $\sigma_z$ are the device-specific residual standard deviations;
$\sigma_\Delta$ is the standard deviation of their difference. Equal independent
device errors with standard deviation $s$ give $\sigma_\Delta=\sqrt{2}s$.
Identical common-mode errors cancel in the difference. Independence between
device errors is therefore an additional acquisition assumption. It differs
from independence across repeated observations.

### 3. Gaussian characteristic function and coherent amplitude

Consider a unit complex sinusoid at frequency $f$ in hertz. A rigid relative
shift $\varepsilon_\Delta$ changes its phase by $2\pi f\varepsilon_\Delta$.
The timing illustration assumes a Gaussian marginal shift distribution,
independent of the underlying feature:

$$
\varepsilon_\Delta\sim\mathcal N(\mu_\Delta,\sigma_\Delta^2),
\qquad Z=\exp(i2\pi f\varepsilon_\Delta).
$$

$i$ is the imaginary unit, $Z$ the unit phasor induced by a timing shift, and
$\mu_\Delta$ the mean relative shift in seconds. Write
$\varepsilon_\Delta=\mu_\Delta+\sigma_\Delta U$ for a standard Gaussian variable
$U$. For real $v$, define its characteristic function

$$
F(v)=\frac{1}{\sqrt{2\pi}}\int_{-\infty}^{\infty}
 e^{ivu}e^{-u^2/2}\,du.
$$

Differentiation under the integral and integration by parts give
$F'(v)=-vF(v)$, with $F(0)=1$. Thus $F(v)=e^{-v^2/2}$, and substitution of
$v=2\pi f\sigma_\Delta$ yields

$$
\mathbb E[Z]=e^{i2\pi f\mu_\Delta}
 e^{-(2\pi f\sigma_\Delta)^2/2}.
$$

Taking its modulus gives the ensemble coherent-amplitude fraction

$$
H(f,\sigma_\Delta)
 =\left|\mathbb E[e^{i2\pi f\varepsilon_\Delta}]\right|
 =\exp\!\left[-\frac{(2\pi f\sigma_\Delta)^2}{2}\right].
$$

A fixed mean shift rotates the expected phasor; variation across shifts reduces
its modulus. The heatmap uses $\mu_\Delta=0$. Each ideal shifted observation
retains unit amplitude and unit power. Three distinct quantities are

$$
|\mathbb E[Z]|=H,\qquad |\mathbb E[Z]|^2=H^2,
\qquad \mathbb E[|Z|^2]=1.
$$

The characteristic-function identity requires the Gaussian marginal
distribution. Independence across observations supplies the further sampling
assumption used in the next section.

#### Units and implementation

The exponent is dimensionless: frequency is in inverse seconds and
$\sigma_\Delta$ is in seconds. The public API accepts milliseconds and converts
explicitly:

```python
phase_sd = 2 * math.pi * frequency_hz * relative_jitter_sd_ms / 1000
H = math.exp(-0.5 * phase_sd * phase_sd)
```

`timing.coherent_amplitude` evaluates $H$;
`timing.expected_mean_phasor` also includes the mean-offset phase.
The reference grid contains 840 analytical cells: 40 frequencies from 1 to
40 Hz and 21 standard deviations from 0 to 20 ms.

### 4. Finite-sample averages

For $N$ independent, identically distributed unit phasors of any marginal
distribution, write $H=|\mathbb E Z|$ and define

$$
\bar Z_N=\frac{1}{N}\sum_{j=1}^N Z_j.
$$

The $N$ diagonal terms in $\mathbb E|\bar Z_N|^2$ equal one. Each of the
$N(N-1)$ off-diagonal terms equals $|\mathbb E Z|^2=H^2$. Consequently,

$$
\mathbb E|\bar Z_N|^2
 =\frac{N+N(N-1)H^2}{N^2}
 =H^2+\frac{1-H^2}{N}.
$$

This is the expected squared modulus of a finite-sample mean. Its square root
is an RMS quantity, whereas $\mathbb E|\bar Z_N|$ is a different expectation.
Neither should be substituted directly for the ensemble quantity $H$ at finite
$N$. Correlated observation errors change the off-diagonal terms. The general
second-moment expression is

$$
\mathbb E|\bar Z_N|^2
 =\frac{1}{N^2}\sum_{j,k}
 \mathbb E\!\left[e^{i2\pi f(\varepsilon_{\Delta,j}
 -\varepsilon_{\Delta,k})}\right].
$$

For Gaussian marginals the ensemble $H$ remains defined even when shifts are
correlated. Consistency of an empirical mean and its uncertainty additionally
depend on the sampling dependence structure. For measured shifts, a direct
sample summary is $|N^{-1}\sum_j e^{i2\pi f\varepsilon_{\Delta,j}}|$; its
uncertainty and finite-sample behaviour require an appropriate sampling model.

### 5. Inverting a chosen retention criterion

For $f>0$ and $0<\eta\leq1$, require $H\geq\eta$. Taking logarithms and solving
for the non-negative relative standard deviation gives

$$
\sigma_\Delta\leq\sigma_{\max}(f,\eta)
 =\frac{\sqrt{-2\ln\eta}}{2\pi f}.
$$

$\eta$ is a chosen dimensionless amplitude-retention criterion. For $\eta=0.9$,

$$
\sigma_{\max}(20\,{\rm Hz},0.9)=3.65295294\,{\rm ms},
\qquad
\sigma_{\max}(40\,{\rm Hz},0.9)=1.82647647\,{\rm ms}.
$$

The gold contour translates this illustrative 90% coherent-amplitude criterion
into a timing budget. It represents 81% of the corresponding ensemble coherent
power. A 90% coherent-power criterion instead requires $H\geq\sqrt{0.9}$.
At zero frequency every rigid shift retains the constant component, so this
frequency-specific budget places no finite upper bound. At $\eta=1$ and $f>0$
the Gaussian standard-deviation budget is zero.

The contour is evaluated from the equation, separately from the heatmap grid.
Its values are analytical operating examples, rather than universal device
acceptance thresholds. EEG carrier phase, amplitude-envelope dynamics,
haemodynamic responses, finite-window features and task performance each have
their own temporal requirements. The formula quantifies phase averaging under
the stated shift model; those other endpoints require matched evaluations.

### 6. Adding fixed features to an affine score

Let the existing and added feature blocks be $x\in\mathbb R^{d_x}$ and
$z\in\mathbb R^{d_z}$. A scalar affine score is

$$
s=w_x^\top x+w_z^\top z+b
 = [w_x;w_z]^\top[x;z]+b.
$$

The concatenated input dimension is $d_x+d_z$; the coefficient vectors have
dimensions $d_x$ and $d_z$; and $b$ is a scalar intercept. For fixed features
and an unconstrained scalar score, the total parameter count is
$d_x+d_z+1$, compared with $d_x+1$ for the existing-input score. The added block
therefore introduces $d_z$ coefficients. Joint refitting can also change $w_x$
and $b$.

This is affine, rather than strictly linear, when $b$ is included. A logistic
link $p=1/(1+e^{-s})$ makes the probability nonlinear in the features even when
the score is affine. Feature count describes model expansion; the joint
relationship between observations and the target determines predictive value.
The relevant sensor-selection comparison develops both the original-input
system and the augmented system with declared data and selection opportunities.

### 7. Interactions and nonlinear integration

A bilinear interaction makes the mathematical distinction explicit:

$$
r(x,z)=x^\top A z,\qquad A\in\mathbb R^{d_x\times d_z}.
$$

With one input fixed, $r$ is linear in the other. Joint scaling gives
$r(c x,c z)=c^2r(x,z)$, so it is generally nonlinear in the concatenated input.
It is linear in the $d_xd_z$ entries of $A$ after declaring product features
$x_i z_j$. Adding an unconstrained bilinear block and an affine $z$ block to
the original affine score adds $d_xd_z+d_z$ coefficients. Low-rank constraints
or parameter sharing change this count.

A more general encoder/fusion description is

$$
h_x=E_{\phi_x}(x),\qquad h_z=E_{\phi_z}(z),\qquad
s=g_\theta(h_x,h_z,q,m).
$$

$E_{\phi_x}$ and $E_{\phi_z}$ are encoders with trainable parameter blocks
$\phi_x$ and $\phi_z$. Their representations $h_x$ and $h_z$ have declared
dimensions $k_x$ and $k_z$. The fusion function $g_\theta$ has parameter block
$\theta$; $q$ records measured quality variables; and $m$ records stream
availability. An estimated quality score carries its own calibration question.
Gating can make one stream's weight depend on another stream or its quality;
crossmodal attention makes feature selection input-dependent.

An affine head operating on frozen representations remains affine in those
representations. Nonlinear encoders make the complete observation-to-score map
nonlinear. A declared concatenating readout has input dimension
$k_x+k_z+\dim(q)+\dim(m)$; attention architectures can use a different structure.
Encoder and fusion parameter counts require the actual architecture and update
schedule. The package's dimension audit records these declarations without
inferring an architecture-dependent parameter count.

### 8. Learning objectives, input roles and evidence

Architecture describes the mapping. Supervision describes where training
targets originate: external labels, paired-view relationships, masked
observations or a generative objective. A system can combine these stages;
self-supervision is commonly included in the broader unsupervised family.
These choices remain distinct from the evidential role assigned to an added
observation.

An **audit** uses a measurement or intervention to distinguish a named
explanation, outside the declared predictor. Its strength depends on the
reference's sensitivity, uncertainty and shared-error dependencies. A
**correction** uses a reference to estimate interference and receives separate
checks of residual interference and target preservation. A **prediction** input
receives a matched comparison with a comparably developed original-sensor
system at the same decision deadline. Input masking within a fitted model and
redevelopment with fewer inputs address different decisions.

The equations above supply neither causal identification nor evidence of
physiological, clinical or predictive benefit by themselves. The v18 manuscript
connects these analytical distinctions to attributed studies. This repository
retains its mathematical calculations, aggregate-source summaries and software
tests as separate evidence categories. It contains no participant-level
validation, new model training or unpublished clinical results.

### 9. Reproduce the implemented relations

From the repository root:

```bash
python run_audit.py validate
python run_audit.py dimensions --d-x 12 --d-z 8
python -m unittest discover -s tests -v
```

The first command checks every retained analytical reference cell and budget
substitution. The second checks the declared affine dimensions. The test suite
also checks numerical Gaussian integration, relative-error composition,
finite-sample second moments and bilinear identities. These tests evaluate
analytical/software contracts. Conceptual clock fitting, EEG/fNIRS forward
models and nonlinear model training remain explanatory relations, rather than
implemented fitting procedures.

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

The [affine derivation](#6-adding-fixed-features-to-an-affine-score) and
[nonlinear encoder/fusion definitions](#7-interactions-and-nonlinear-integration)
above explain the coefficient counts and declared representation dimensions.
The commands report bookkeeping for the specified model; architecture-dependent
encoder and fusion parameter counts remain explicit declarations.

## Interpretation and limitations

* `H` is `abs(E[Z])`. It is not `E[abs(Z)]`, single-observation power, ERD,
  classification accuracy, measured coherence or magnitude-squared coherence.
* Under a rigid shift of each sinusoid, each observation retains its amplitude
  and power. Phase cancellation affects coherent averaging. The squared
  magnitude of the expected complex amplitude is `H^2`, a distinct quantity.
* A fixed clock offset changes phase. The Gaussian shift model does not model
  clock drift, sensor buffering, interpolation error or sample-by-sample time
  warping. Those effects require appropriate measurements and models.
* The jitter is **relative**. The [covariance derivation](#2-relative-timing-error)
  above specifies how the two device errors combine. Treating separate clocks as
  independent is an additional assumption, not an implication of this plot.
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

# Technical derivations and interpretation

Updated 29 October 2026 for the v18 revision of *Establishing sensor contributions
in multimodal AI*. This document provides the analytical details behind the
timing illustration and model-expansion discussion. The results are mathematical
relations and software checks, separate from the attributed aggregate article
values elsewhere in this repository. The associated [LaTeX source](derivations.tex)
provides an editable equation document.

## 1. Clock registration and response models

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

## 2. Relative timing error

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

## 3. Gaussian characteristic function and coherent amplitude

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

### Units and implementation

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

## 4. Finite-sample averages

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

## 5. Inverting a chosen retention criterion

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

## 6. Adding fixed features to an affine score

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

## 7. Interactions and nonlinear integration

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

## 8. Learning objectives, input roles and evidence

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

## 9. Reproduce the implemented relations

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

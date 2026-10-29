"""Deterministic mathematical contracts for docs/derivations.md.

These tests add no fitted model or participant analysis. Existing timing and
dimension implementations, reference values and bundled figures stay fixed.
"""
import cmath
import itertools
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from sensor_contribution_audit.timing import (
    coherent_amplitude, expected_mean_phasor, jitter_budget_ms,
)
from sensor_contribution_audit.dimensions import dimension_audit


class DerivationContracts(unittest.TestCase):
    def test_frequency_jitter_scaling(self):
        for frequency, sigma in ((1, 2), (20, 5), (40, 20)):
            self.assertAlmostEqual(
                coherent_amplitude(2 * frequency, sigma),
                coherent_amplitude(frequency, 2 * sigma), places=15,
            )

    def test_gaussian_characteristic_function_by_quadrature(self):
        # Composite Simpson integration over nine standard deviations.
        # Gaussian tail probability outside this interval is < 3e-19.
        frequency, sigma_ms, offset_ms = 20, 5, 3
        intervals, lower, upper = 8000, -9.0, 9.0
        step = (upper - lower) / intervals
        total = 0j
        for index in range(intervals + 1):
            u = lower + index * step
            weight = 1 if index in (0, intervals) else (4 if index % 2 else 2)
            density = math.exp(-u * u / 2) / math.sqrt(2 * math.pi)
            shift_seconds = (offset_ms + sigma_ms * u) / 1000
            total += weight * density * cmath.exp(2j * math.pi * frequency * shift_seconds)
        integrated = total * step / 3
        self.assertLess(abs(integrated - expected_mean_phasor(frequency, sigma_ms, offset_ms)), 1e-12)

    def test_independent_device_jitters_compose_as_relative_variance(self):
        frequency, sx, sz, mx, mz = 20, 3, 4, 2, 7
        relative = expected_mean_phasor(frequency, math.hypot(sx, sz), mz - mx)
        product = expected_mean_phasor(frequency, sz, mz) * expected_mean_phasor(frequency, sx, mx).conjugate()
        self.assertLess(abs(relative - product), 1e-14)

    def test_identical_common_mode_timing_errors_cancel(self):
        variance_x = variance_z = covariance = 25.0  # all in ms^2
        variance_relative = variance_x + variance_z - 2 * covariance
        self.assertEqual(variance_relative, 0)
        self.assertEqual(coherent_amplitude(40, math.sqrt(variance_relative)), 1)

    def test_finite_sample_second_moment_for_independent_phasors(self):
        # Exact enumeration for an iid two-point phase distribution; the
        # second-moment identity holds for any iid unit phasors.
        theta, samples = 0.7, 3
        support = (cmath.exp(1j * theta), cmath.exp(-1j * theta))
        second_moment = sum(
            abs(sum(values) / samples) ** 2
            for values in itertools.product(support, repeat=samples)
        ) / (len(support) ** samples)
        h_squared = math.cos(theta) ** 2
        expected = h_squared + (1 - h_squared) / samples
        self.assertAlmostEqual(second_moment, expected, places=14)
        self.assertGreater(second_moment, h_squared)

    def test_correlated_observations_require_different_second_moment(self):
        theta, samples = 0.7, 3
        shared_support = (cmath.exp(1j * theta), cmath.exp(-1j * theta))
        common_shift_moment = sum(abs(value) ** 2 for value in shared_support) / 2
        h_squared = math.cos(theta) ** 2
        independent_formula = h_squared + (1 - h_squared) / samples
        self.assertAlmostEqual(common_shift_moment, 1, places=14)
        self.assertGreater(common_shift_moment, independent_formula)

    def test_amplitude_and_power_criteria_differ(self):
        amplitude_budget = jitter_budget_ms(20, 0.9)
        power_budget = jitter_budget_ms(20, math.sqrt(0.9))
        self.assertAlmostEqual(coherent_amplitude(20, amplitude_budget) ** 2, 0.81, places=14)
        self.assertAlmostEqual(coherent_amplitude(20, power_budget) ** 2, 0.9, places=14)
        self.assertLess(power_budget, amplitude_budget)

    def test_affine_concatenation_and_incremental_parameter_count(self):
        x, z, wx, wz, intercept = (2, -3), (4, 5, -2), (0.5, 2), (1, -1, 3), 0.25
        split = sum(a * b for a, b in zip(x, wx)) + sum(a * b for a, b in zip(z, wz)) + intercept
        concatenated = sum(a * b for a, b in zip(x + z, wx + wz)) + intercept
        self.assertEqual(split, concatenated)
        report = dimension_audit(len(x), len(z))
        self.assertEqual(report['affine_total_parameter_count'] - (len(x) + 1), len(z))

    def test_bilinear_separate_linearity_and_joint_nonlinearity(self):
        matrix = ((1, 2), (-3, 0.5))
        def interaction(x, z):
            return sum(x[i] * matrix[i][j] * z[j] for i in range(2) for j in range(2))
        x, other_x, z = (1, 2), (3, -1), (2, -3)
        added_x = tuple(a + b for a, b in zip(x, other_x))
        self.assertEqual(interaction(added_x, z), interaction(x, z) + interaction(other_x, z))
        jointly_scaled = interaction(tuple(2 * v for v in x), tuple(2 * v for v in z))
        self.assertEqual(jointly_scaled, 4 * interaction(x, z))
        self.assertNotEqual(jointly_scaled, 2 * interaction(x, z))


if __name__ == '__main__':
    unittest.main()

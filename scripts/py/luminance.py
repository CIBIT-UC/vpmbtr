"""Convert 8-bit RGB values to physical luminance (cd/m^2).

The projector/display used in the experiment was characterised with a photometer:
for a set of normalised input levels (0-1), the emitted luminance of the red,
green and blue channels was measured separately. Each channel's response is
non-linear (a gamma-like curve), so here it is approximated with a per-channel
2nd-degree polynomial fit. The luminance of an arbitrary RGB colour is then the
sum of the three channel contributions.

This is used to equate/report the luminance of the visual stimuli (e.g. to check
that conditions are matched in luminance), not in the fMRI GLM itself.

Caveat: summing per-channel polynomials assumes channel additivity and ignores
any interaction/black-level double counting; it is a first-order approximation.
"""

import numpy as np
from numpy.polynomial.polynomial import Polynomial

# Photometer calibration table.
# Columns: normalised input level (0-1), then measured luminance (cd/m^2) for the
# red, green and blue channels at that input level.
calibration_data = np.array(
    [
        [0.000000, 0.148, 0.137, 0.150],
        [0.058824, 0.167, 0.358, 0.190],
        [0.117647, 0.517, 1.740, 0.274],
        [0.176471, 1.450, 5.770, 0.610],
        [0.235294, 2.550, 10.140, 1.000],
        [0.294118, 4.020, 16.230, 1.690],
        [0.352941, 5.840, 22.520, 2.540],
        [0.411765, 7.930, 28.770, 3.620],
        [0.470588, 10.180, 35.330, 4.900],
        [0.529412, 12.700, 41.980, 6.460],
        [0.588235, 15.400, 48.990, 8.210],
        [0.647059, 18.200, 55.950, 10.100],
        [0.705882, 21.300, 63.170, 12.300],
        [0.764706, 24.500, 70.720, 14.600],
        [0.823529, 27.900, 78.370, 17.000],
        [0.882353, 31.400, 85.950, 19.600],
        [0.941176, 34.900, 93.410, 22.400],
        [1.000000, 38.300, 100.000, 25.300],
    ]
)

# Split calibration table into the input axis and the three channel responses.
input_vals = calibration_data[:, 0]
red_lum = calibration_data[:, 1]
green_lum = calibration_data[:, 2]
blue_lum = calibration_data[:, 3]

# Fit a 2nd-degree polynomial per channel (input level -> luminance in cd/m^2).
# .convert() returns coefficients in the ordinary (unscaled) basis so the
# polynomials can be evaluated directly on the 0-1 input domain.
p_red = Polynomial.fit(input_vals, red_lum, deg=2).convert()
p_green = Polynomial.fit(input_vals, green_lum, deg=2).convert()
p_blue = Polynomial.fit(input_vals, blue_lum, deg=2).convert()


def rgb_to_luminance_poly(rgb):
    """Estimate total luminance (cd/m^2) for an 8-bit ``(r, g, b)`` colour.

    Each 0-255 channel value is normalised to 0-1, passed through its fitted
    polynomial, and the three channel luminances are summed.
    """
    # Normalise 8-bit values to the 0-1 domain the polynomials were fit on.
    r, g, b = np.array(rgb) / 255.0
    l_r = p_red(r)
    l_g = p_green(g)
    l_b = p_blue(b)
    luminance = l_r + l_g + l_b
    return float(luminance)


# Example / smoke test: luminance of pure black (the display's black level).
rgb_val = (0, 0, 0)
lum = rgb_to_luminance_poly(rgb_val)
print(f"Estimated luminance (2nd-order fit) for RGB {rgb_val}: {lum:.2f} cd/m²")

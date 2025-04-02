import numpy as np
from scipy.interpolate import interp1d

# Calibration data: input value (0–1) and luminance for R, G, B
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

# Split data into columns
input_vals = calibration_data[:, 0]
red_lum = calibration_data[:, 1]
green_lum = calibration_data[:, 2]
blue_lum = calibration_data[:, 3]

# Create interpolation functions
interp_red = interp1d(input_vals, red_lum, kind="linear", fill_value="extrapolate")
interp_green = interp1d(input_vals, green_lum, kind="linear", fill_value="extrapolate")
interp_blue = interp1d(input_vals, blue_lum, kind="linear", fill_value="extrapolate")


# Function to convert RGB (8-bit) to luminance
def rgb_to_luminance(rgb):
    r, g, b = np.array(rgb) / 255.0  # Normalize to [0, 1]
    l_r = interp_red(r)
    l_g = interp_green(g)
    l_b = interp_blue(b)
    luminance = (
        l_r + l_g + l_b
    )  # the table values are already compensated, otherwise it would be luminance = 0.2126 * l_r + 0.7152 * l_g + 0.0722 * l_b
    return float(luminance)


# Example usage
rgb_value = (130, 130, 130)
luminance = rgb_to_luminance(rgb_value)
print(f"Estimated luminance for RGB {rgb_value}: {luminance:.2f} cd/m²")

# SPDX-FileCopyrightText: 2024 German Aerospace Center
#
# SPDX-License-Identifier: Apache-2.0

import math

import pandas as pd


def auto_scale(data: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """
    Finds and applies a common scaling exponent of 10 for given data columns to minimise leading/trailing digits

    Args:
        data: to be scaled

    Returns:
        rescaled data and scaling factor string (empty if unscaled)
    """
    max_value = abs(pd.DataFrame(data)).max(axis=1).max(axis=0)
    digits = math.floor(math.log10(max_value)) - 1 if max_value > 0 else 0
    exponent = digits

    scaling_factor = 10**exponent
    label_extension = f"{10 ** exponent} " if exponent != 0 else ""
    return data / scaling_factor, label_extension

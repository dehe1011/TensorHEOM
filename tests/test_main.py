import numpy as np
import pytest
from heom.utils import func


@pytest.mark.parametrize(
    "array_a, array_b",
    [
        (np.array([0, np.pi / 2, np.pi]), np.array([0, np.pi / 2, 0])),
        (np.array([1.0, 2.0, 3.0]), np.array([0.5, 1.0, 1.5])),
    ],
)
def test_func(array_a, array_b):
    expected = np.sin(array_a + array_b)
    np.testing.assert_allclose(func(array_a, array_b), expected)
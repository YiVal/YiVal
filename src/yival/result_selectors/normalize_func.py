"""
Normalization functions

"""
import numpy as np


def min_max_normalization(matrix: np.ndarray) -> np.ndarray:
    """normalize matrix in min_max method"""
    matrix_min = matrix.min(axis=0)
    matrix_max = matrix.max(axis=0)
    normalized_matrix = (matrix -
                         matrix_min) / (matrix_max - matrix_min + 1e-10)
    return normalized_matrix


def z_score_normalizatioin(matrix: np.ndarray) -> np.ndarray:
    """normalize matrix in z_score method"""
    matrix_mean = matrix.mean(axis=0)
    matrix_std = matrix.std(axis=0)
    normalized_matrix = (matrix - matrix_mean) / (matrix_std + 1e-10)
    return normalized_matrix


NORMALIZATION_FUNCS = {
    'min-max': min_max_normalization,
    'z-score': z_score_normalizatioin,
}
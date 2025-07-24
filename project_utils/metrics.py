import numpy as np


def tre(t_est: np.ndarray, t_gt: np.ndarray) -> float:
    """
    Calculates the translation error between the transformation matrices.
    In case of an error, returns infinity (`np.inf`).

    The translation error is calculated as:
    \[
    \text{TRE} = \| T_{\text{est}} - T_{\text{gt}} \|
    \]

    Args:
        t_est (np.ndarray): The estimated transformation matrix.
        t_gt (np.ndarray): The ground truth transformation matrix.

    Returns:
        float: The translation error or infinity if an error occurs.
    """
    try:
        return np.linalg.norm(t_est[:3, 3] - t_gt[:3, 3])
    except:
        return np.inf

def rre(t_est: np.ndarray, t_gt: np.ndarray) -> float:
    """
    Calculates the angular error between the rotations of the transformation matrices.
    In case of an error, returns infinity (`np.inf`).

    The angular error is calculated as:
    \[
    \text{RRE} = \arccos\left(\frac{\text{trace}(T_{\text{est}}^{T} \cdot T_{\text{gt}}) - 1}{2}\right)
    \]

    Args:
        t_est (np.ndarray): The estimated transformation matrix.
        t_gt (np.ndarray): The ground truth transformation matrix.

    Returns:
        float: The angular error or infinity if an error occurs.
    """
    try:
        return np.arccos((np.trace(t_est[:3, :3].T @ t_gt[:3, :3]) - 1) / 2)
    except:
        return np.inf
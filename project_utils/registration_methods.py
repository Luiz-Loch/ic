from enum import Enum

import numpy as np

from . import measure_time
from .registration import (deep_global_registration, fast_global_registration,
                           global_registration, maximal_cliques, point_dsc,
                           robust_global_registration)
from .utils_deep_global_registration import DGRModels
from .utils_point_dsc import Snapshot


class RegistrationMethod(Enum):
    RANSAC = (
        'RANSAC',
        global_registration,
    )
    FGR = (
        'Fast Global Registration',
        fast_global_registration,
    )
    TEASER = (
        'TEASER++',
        # robust_global_registration,
    )
    DGR = (
        'Deep Global Registration',
        # deep_global_registration,
    )
    MAC = (
        'Maximal Cliques',
        maximal_cliques,
    )
    POINT_DSC = (
        'PointDSC',
        point_dsc,
    )

    def __init__(self,
                 registration_name: str,
                 function: callable = lambda: None,
                 ):
        self.registration_name: str = registration_name
        self._function: callable = function

    @measure_time
    def run(self, *args, **kwargs) -> np.ndarray:
        return self._function(*args, **kwargs)

    def model(self, dgr_model: DGRModels, point_dsc_snapshot: Snapshot) -> str | None:
    # def model(self, dgr_model, point_dsc_snapshot: Snapshot) -> str | None:
        if self == RegistrationMethod.DGR:
            return dgr_model.value
        elif self == RegistrationMethod.POINT_DSC:
            return point_dsc_snapshot.value
        else:
            return None

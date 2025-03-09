from .fast_global_registration import fast_global_registration
from .global_registration import global_registration
from .icp import fine_alignment_point_to_point, fine_alignment_point_to_plane
# from .teaser import robust_global_registration
from .deep_global_registration import deep_global_registration

__all__ = [
    # .fast_global_registration:
    'fast_global_registration',

    # .global_registration:
    'global_registration',

    # .icp:
    'fine_alignment_point_to_point',
    'fine_alignment_point_to_plane',

    # .teaser:
    # 'robust_global_registration',

    # Deep Global Registration
    'deep_global_registration',
]

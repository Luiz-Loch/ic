from enum import Enum


class Snapshot(Enum):
    """
    Enum class representing the snapshots for Point DSC.
    Each snapshot contains URLs for external and S3 sources, and a local path.
    """
    SNAPSHOT_3DMATCH = "PointDSC_3DMatch_release"

    SNAPSHOT_KITTI = "PointDSC_KITTI_release"

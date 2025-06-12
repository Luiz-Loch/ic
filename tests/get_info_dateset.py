import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import project_utils

if __name__ == '__main__':
    ply_3dmatch_path: str = "./data/3DMatch/7-scenes-office/cloud_bin_0.ply"
    ply_eth_path: str = "./data/ETH/gazebo_summer/Hokuyo_0.ply"
    ply_kitty_path: str = "./data/KITTI/00/velodyne/000000.bin"

    print('3DMatch Dataset Info:')
    print(project_utils.get_dataset_info(ply_3dmatch_path))
    print('ETH Dataset Info:')
    print(project_utils.get_dataset_info(ply_eth_path))
    print('KITTI Dataset Info:')
    print(project_utils.get_dataset_info(ply_kitty_path))

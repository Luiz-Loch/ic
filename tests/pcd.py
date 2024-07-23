import modulos

if __name__ == '__main__':
    source_path = '../data/3DMatch/rgbd-scenes-v2-scene_10/cloud_bin_2.ply'
    target_path = '../data/3DMatch/rgbd-scenes-v2-scene_10/cloud_bin_0.ply'

    source_cloud = modulos.load_point_cloud(source_path)
    target_cloud = modulos.load_point_cloud(target_path)

    # print(f'Tamanho da nuvem de pontos source: {source_cloud}')
    # print(f'Tamanho da nuvem de pontos target: {target_cloud}')

    print('#'*50)

    print(f'`source_cloud.points`: {source_cloud.points}')
    print(f'`target_cloud.points`: {target_cloud.points}')

    print('#'*50)

    print(f'`len(source_cloud.points)`: {len(source_cloud.points)}')
    print(f'`len(source_cloud.points)`: {len(target_cloud.points)}')
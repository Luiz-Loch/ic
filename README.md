# Configuração inicial do *script*

## Dependências

- Python 3.11.9

### Ajustes necessários

Existem algumas linhas dos repositórios em `./external` que precisam ser ajustadas para funcionar com Python 3.11.9:
- linhas com `future_fstrings` podem ser comentadas ou removidas, pois não são mais necessárias.

### Bibliotecas Python

- `open3d==0.19.0`
- `easydict==1.13`
- `boto3`
- [`MinkowskiEngine`](https://github.com/NVIDIA/MinkowskiEngine#requirements)
  - GCC 7.4 
  - OpenBLAS
  - [pytorch 1.7](https://pytorch.org/get-started/previous-versions/) (pip install torch==1.7.1+cu110 torchvision==0.8.2+cu110 torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html)
    - CUDA 11.0 (https://developer.nvidia.com/cuda-11.0-download-archive)
    - Driver da nvidia (https://docs.nvidia.com/deploy/cuda-compatibility/index.html#cuda-11-and-later-defaults-to-minor-version-compatibility)
- (TEASER++)[https://teaser.readthedocs.io/en/latest/installation.html]

## Execução

```bash
python main.py --feature_method FPFH --registration_method RANSAC
python main.py --feature_method FPFH --registration_method FGR
python main.py --feature_method FPFH --registration_method TEASER
python main.py --feature_method FPFH --registration_method DGR       --dgr_model DGR_3DMATCH
python main.py --feature_method FPFH --registration_method DGR       --dgr_model DGR_KITTI
python main.py --feature_method FPFH --registration_method MAC
python main.py --feature_method FPFH --registration_method POINT_DSC --point_dsc_snapshot SNAPSHOT_3DMATCH
python main.py --feature_method FPFH --registration_method POINT_DSC --point_dsc_snapshot SNAPSHOT_KITTI


python main.py --feature_method FCGF --fcgf_model FCGF_3DMATCH --registration_method RANSAC
python main.py --feature_method FCGF --fcgf_model FCGF_3DMATCH --registration_method FGR
python main.py --feature_method FCGF --fcgf_model FCGF_3DMATCH --registration_method TEASER
python main.py --feature_method FCGF --fcgf_model FCGF_3DMATCH --registration_method DGR       --dgr_model DGR_3DMATCH
python main.py --feature_method FCGF --fcgf_model FCGF_3DMATCH --registration_method DGR       --dgr_model DGR_KITTI
python main.py --feature_method FCGF --fcgf_model FCGF_3DMATCH --registration_method MAC
python main.py --feature_method FCGF --fcgf_model FCGF_3DMATCH --registration_method POINT_DSC --point_dsc_snapshot SNAPSHOT_3DMATCH
python main.py --feature_method FCGF --fcgf_model FCGF_3DMATCH --registration_method POINT_DSC --point_dsc_snapshot SNAPSHOT_KITTI

python main.py --feature_method FCGF --fcgf_model FCGF_KITTI --registration_method RANSAC
python main.py --feature_method FCGF --fcgf_model FCGF_KITTI --registration_method FGR
python main.py --feature_method FCGF --fcgf_model FCGF_KITTI --registration_method TEASER
python main.py --feature_method FCGF --fcgf_model FCGF_KITTI --registration_method DGR       --dgr_model DGR_3DMATCH
python main.py --feature_method FCGF --fcgf_model FCGF_KITTI --registration_method DGR       --dgr_model DGR_KITTI
python main.py --feature_method FCGF --fcgf_model FCGF_KITTI --registration_method MAC
python main.py --feature_method FCGF --fcgf_model FCGF_KITTI --registration_method POINT_DSC --point_dsc_snapshot SNAPSHOT_3DMATCH
python main.py --feature_method FCGF --fcgf_model FCGF_KITTI --registration_method POINT_DSC --point_dsc_snapshot SNAPSHOT_KITTI
```
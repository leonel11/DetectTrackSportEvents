# Sport AI System

Program for analysis of videos of sport events based on machine learning

## Prerequisites

* OS: Linux (tested only on Ubuntu >= 16.04) or Windows 10
* NVIDIA videocard with [CUDA capability](https://developer.nvidia.com/cuda-gpus) >= 3.5
* Installed [CUDA](https://developer.nvidia.com/cuda-toolkit) >= 9.0 and [cuDNN 7](https://docs.nvidia.com/deeplearning/sdk/cudnn-install/index.html)

## Requirements

* [Towards-Realtime-MOT](https://github.com/Zhongdao/Towards-Realtime-MOT)
* [Python](https://www.python.org/downloads/) >= 3.6
* [PyTorch](https://pytorch.org) >= 1.2.0
* [opencv-python](https://pypi.org/project/opencv-python)
* [motmetrics](https://pypi.org/project/motmetrics)
* [NumPy](pypi.org/project/numpy)
* [logging](https://pypi.org/project/logging)
* [Cython](https://pypi.org/project/Cython)
* [cython-bbox](https://pypi.org/project/cython-bbox)
* FFmpeg
* [numba](http://numba.pydata.org)
* [matplotlib](https://matplotlib.org/index.html)
* [sklearn](https://scikit-learn.org/stable/)
* [Pillow 6.1.0](https://pypi.org/project/Pillow/6.1.0/)
* [tqdm](https://github.com/tqdm/tqdm)
* [pandas](https://pypi.org/project/pandas)
* [yagmail](https://pypi.org/project/yagmail)
* [SciPy](https://www.scipy.org/install.html)
* [argparse](https://pypi.org/project/argparse)
* [PyQt5](https://pypi.org/project/PyQt5)
* [plotly](https://plotly.com/python/getting-started/)
* your favourite browser

## Installation

1. Clone this repository
    ```bash
    git clone https://github.com/leonel11/DetectTrackSportEvents.git
    ```
    
2. Clone this repository into another directory
    ```bash
    git clone https://github.com/Zhongdao/Towards-Realtime-MOT
    ```
    or download it as a zip file and repack
    
3. Copy all files of repository `Towards-Realtime-MOT` to folder `video_player` without exchanging files of the same name

4. Exchange file `video_player/models.py` to file of the same name from folder `video_player/exchange_files/` with the replacement

5. Install all requirements (you can follow some instructions of installation using [Requirements](https://github.com/Zhongdao/Towards-Realtime-MOT#requirements) or [Issues](https://github.com/Zhongdao/Towards-Realtime-MOT/issues) in case of any problem)

## Advice

1. For Ubuntu:
    * before start of installation type this command:
        ```bash
        sudo apt-get update
        ```
    * After [logging](https://pypi.org/project/logging) installation, before [Cython](https://pypi.org/project/Cython) installation type this command
        ```bash
        sudo apt install libsm6 libxrender-dev
        ```
2. For Windows:

    [FFmpeg installation](https://ru.wikihow.com/установить-программу-FFmpeg-в-Windows)

## Docker

It's also possible to launch this GUI application using Docker container.

1. Install [Docker](https://www.docker.com) on your computer

2. Pull and run container with the support of [CUDA](https://developer.nvidia.com/cuda-toolkit) >=9.0 and [cuDNN 7](https://docs.nvidia.com/deeplearning/sdk/cudnn-install/index.html). For example, [1](https://hub.docker.com/layers/pytorch/pytorch/1.3-cuda10.1-cudnn7-devel/images/sha256-d22bdcc867e24da67947104cce925c9be6544e0e86a10421785f98cfceda718e?context=explore), [2](https://hub.docker.com/layers/nvidia/cuda/9.0-cudnn7-devel-ubuntu16.04/images/sha256-e397c6942183d042fc7c8ee449f233592f26de7509cb833818d90e6fa6de4d81?context=explore) etc.

3. After [PyQt5](https://pypi.org/project/PyQt5) installation, before [plotly](https://plotly.com/python/getting-started/) installation type these commands into container:
    ```bash
    sudo apt-get update
    
    export QT_DEBUG_PLUGUINS=1
    
    sudo apt-get install libxcb-randr0-dev libxcb-xtest0-dev libxcb-xinerama0-dev libxcb-shape0-dev libxcb-xkb-dev
    
    sudo apt install libxkbcommon-x11-0
    ```
4. Install your favourite browser into container

5. For Windows:
    * Use [XLaunch](https://sourceforge.net/projects/vcxsrv/) to implement your own server. Here is some [instructions](https://dev.to/darksmile92/run-gui-app-in-linux-docker-container-on-windows-host-4kde) how to launch it.
    * For volume project don't forget to share needed drive in [Docker settings](https://token2shell.com/howto/docker/sharing-windows-folders-with-containers/)

## Running

* For Windows: double click on `video_player/SportAISystem.lnk` or run `video_player/run_sportaisystem.bat` in `cmd`
* For Linux or Docker container: run `video_player/sportaisystem.sh` in `Terminal`
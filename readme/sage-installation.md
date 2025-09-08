# How to Install SageMath on Windows
1. start wsl
2.  curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"   
3. chmod +x Miniforge3-Linux-x86_64.sh         
4. ~/miniforge3/bin/conda init fish   
5. restart shell
6. conda create -n sage sage python=3.11            
7. conda activate sage
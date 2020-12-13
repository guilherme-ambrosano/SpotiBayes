@echo off
call conda create -y -n SpotiBayes python=3.8
call conda activate SpotiBayes
echo y | call pip install numpy==1.18.5 scipy --upgrade
call conda config --set pip_interop_enabled True
call conda install -y libpython m2w64-toolchain -c msys2

echo.
echo Por favor, verifique se o arquivo 'distutils.cfg' foi criado corretamente na pasta do arquivo abaixo
python -c "import distutils; print(distutils.__file__)"
pause

call conda install -y cython matplotlib pandas pystan -c conda-forge
echo y | call pip install spotipy Flask --upgrade
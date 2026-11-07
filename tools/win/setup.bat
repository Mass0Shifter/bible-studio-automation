@echo off
cd /d "%~dp0"
set FF=C:\Users\USER\AppData\Local\CapCut\Apps\9.5.0.4050\ffmpeg.exe
(
echo === ffmpeg
dir /b "C:\Users\USER\AppData\Local\CapCut\Apps\9.5.0.4050\ff*.exe"
"%FF%" -hide_banner -version
"%FF%" -hide_banner -encoders 2>&1 | findstr /i "x264 aac"
"%FF%" -hide_banner -filters 2>&1 | findstr /i "xfade ebur128 overlay tpad acrossfade alimiter silencedetect"
echo === pip
python -m pip install --user pillow numpy
python -c "import numpy, PIL; print(\"numpy\", numpy.__version__, \"PIL\", PIL.__version__)"
) > setup.txt 2>&1
echo done >> setup.txt

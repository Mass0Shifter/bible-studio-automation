@echo off
rem usage: run_cat.bat <Book>  joins the PI intro section + caption pieces into final\<Book>_PI_final.mp4 (stream copy)
cd /d "C:\Users\USER\Bible Studio\Prophetic Implications\%1\_check\full"
set LOG=..\..\render.log
echo ==== %DATE% %TIME% start CAT %1 >> "%LOG%"
"C:\Users\USER\AppData\Local\CapCut\Apps\9.5.0.4050\ffmpeg.exe" -y -hide_banner -loglevel error -f concat -safe 0 -i all.txt -c copy -movflags +faststart ..\..\final\%1_PI_final_v2.mp4 >> "%LOG%" 2>&1 || goto fail
echo ==== %DATE% %TIME% DONE CAT >> "%LOG%"
exit /b 0
:fail
echo ==== %DATE% %TIME% FAILED CAT >> "%LOG%"
exit /b 1

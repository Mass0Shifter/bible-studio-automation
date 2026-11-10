@echo off
rem usage: run_pi.bat <Book> <plan base name without .json>   (Prophetic Implication films: no character speech -> no speech_fit)
set T=C:\Users\USER\Bible Studio\_tools
cd /d "C:\Users\USER\Bible Studio\Prophetic Implications\%1\plans"
set LOG=..\render.log
echo ==== %DATE% %TIME% start PI render %1 %2 >> "%LOG%"
:fe
python "%T%\win\winrun.py" "%T%\fit_edit.py" %2.json >> "%LOG%" 2>&1
if errorlevel 4 goto fail
if errorlevel 3 goto fe
if errorlevel 1 goto fail
set FIN_BUDGET=100000
:fi
python "%T%\win\winrun.py" "%T%\finish.py" finish.json >> "%LOG%" 2>&1
if errorlevel 4 goto fail
if errorlevel 3 goto fi
if errorlevel 1 goto fail
echo ==== %DATE% %TIME% DONE >> "%LOG%"
exit /b 0
:fail
echo ==== %DATE% %TIME% FAILED >> "%LOG%"
exit /b 1

@echo off
if /i "%~1"=="CAT" call "%~dp0run_cat.bat" %2 & exit /b
if /i "%~1"=="PIS" call "%~dp0run_pistyle.bat" %2 & exit /b
if /i "%~1"=="PI" call "%~dp0run_pi.bat" %2 %3 & exit /b
rem usage: run_chapter.bat <chapter number> <plan base name without .json>
set T=C:\Users\USER\Bible Studio\_tools
cd /d "C:\Users\USER\Bible Studio\Genesis %1\plans"
set LOG=..\rerender_speechcheck.log
echo ==== %DATE% %TIME% start (rerun: speech clips held, never slowed) >> "%LOG%"
python "%T%\win\winrun.py" "%T%\speech_fit.py" %2.json >> "%LOG%" 2>&1 || goto fail
:fe
python "%T%\win\winrun.py" "%T%\fit_edit.py" %2.speechfit.json >> "%LOG%" 2>&1
if errorlevel 4 goto fail
if errorlevel 3 goto fe
if errorlevel 1 goto fail
set FIN_BUDGET=100000
:fi
python "%T%\win\winrun.py" "%T%\finish.py" finish.json >> "%LOG%" 2>&1
if errorlevel 4 goto fail
if errorlevel 3 goto fi
if errorlevel 1 goto fail
python "%T%\win\winrun.py" "%T%\speech_check.py" finish.json >> "%LOG%" 2>&1
python "%T%\win\winrun.py" "%T%\film_check.py" finish.json >> "%LOG%" 2>&1
echo ==== %DATE% %TIME% DONE >> "%LOG%"
exit /b 0
:fail
echo ==== %DATE% %TIME% FAILED >> "%LOG%"
exit /b 1

@echo off
setlocal enabledelayedexpansion
title Bible Studio render watcher
echo Watching %~dp0queue for render jobs. Leave this window open.
:loop
for %%f in ("%~dp0queue\*.job") do (
  set "ARGS="
  set /p ARGS=<"%%f"
  move /y "%%f" "%~dp0queue\started\" >nul
  echo %DATE% %TIME% starting !ARGS!
  start "render !ARGS!" /low cmd /c ""%~dp0run_chapter2.bat" !ARGS!"
)
timeout /t 10 /nobreak >nul
goto loop

@echo off
setlocal
set "HOSTS=%SystemRoot%\System32\drivers\etc\hosts"
findstr /i /c:"creativeos.test" "%HOSTS%" >nul 2>&1
if %errorlevel%==0 (
  echo CreativeOS local name is already configured.
) else (
  >>"%HOSTS%" echo 127.0.0.1 creativeos.test
  if errorlevel 1 (
    echo Could not update the Windows hosts file.
    echo Right-click this file and choose Run as administrator.
    pause
    exit /b 1
  )
  echo Added creativeos.test to the Windows hosts file.
)
echo Open your app at: http://creativeos.test:5000
pause

@echo off
echo Aguardando video.mp4...

:wait
if not exist "%~dp0video.mp4" (
    timeout /t 2 /nobreak >nul
    goto wait
)

echo Arquivo encontrado! Convertendo para GIF...
ffmpeg -y -i "%~dp0video.mp4" -vf "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 "%~dp0video.gif"

echo.
echo Concluido! video.gif gerado.
pause
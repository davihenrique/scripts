@echo off
setlocal enabledelayedexpansion

:: Gera 9 digitos aleatorios
set "cpf="
for /l %%i in (1,1,9) do (
    set /a "digit=!random! %% 10"
    set "cpf=!cpf!!digit!"
)

:: Calcula primeiro digito verificador
set /a "soma=0"
set /a "peso=10"
for /l %%i in (0,1,8) do (
    set "d=!cpf:~%%i,1!"
    set /a "soma+=!d!*!peso!"
    set /a "peso-=1"
)
set /a "resto=!soma! %% 11"
if !resto! lss 2 (
    set "dv1=0"
) else (
    set /a "dv1=11-!resto!"
)
set "cpf=!cpf!!dv1!"

:: Calcula segundo digito verificador
set /a "soma=0"
set /a "peso=11"
for /l %%i in (0,1,9) do (
    set "d=!cpf:~%%i,1!"
    set /a "soma+=!d!*!peso!"
    set /a "peso-=1"
)
set /a "resto=!soma! %% 11"
if !resto! lss 2 (
    set "dv2=0"
) else (
    set /a "dv2=11-!resto!"
)
set "cpf=!cpf!!dv2!"

:: Copia para clipboard e fecha
echo !cpf! | clip
exit
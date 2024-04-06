@echo off

if "%1" == "" (
dotnet clean && nuget restore && dotnet build
)
else
(
git checkout %1 && git pull && dotnet clean && nuget restore && dotnet build
)
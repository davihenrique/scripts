foreach ($fileGame in (Get-ChildItem -Exclude Imgs) )
{
    [bool] $myval = $false
    foreach ($fileImg in (Get-ChildItem -Path '.\Imgs').Basename )
    {
        if($fileGame.Basename.Equals($fileImg))
        {
            $myval = $true
        }       
    }

    if($myval.Equals($false))
    {
        Remove-Item $fileGame
        Write-Host $fileGame.Basename
    }

}
Add-Type -AssemblyName PresentationCore
$music = New-Object System.Windows.Media.MediaPlayer
$music.Open($PWD.Path+".\file\paysandu.mp3")
$music.Play()
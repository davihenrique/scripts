Set oShell = WScript.CreateObject("WScript.Shell")
oShell.run "shutdown -s -t 300"
MsgBox chr(201) + " MEIA NOITE !!!" & vbCrLf & UCase(FormatDateTime(now, 1)) & vbCrLf & vbCrLf &"PC DESLIGANDO EM  5 MIN", vbCritical, "ALERTAR !!!"
<#
    Watch-CopyAndShutdown.ps1

    Monitora o Windows Explorer procurando janelas de progresso de copia/movimentacao
    (classe de janela "OperationStatusWindow") e desliga o computador automaticamente
    assim que TODAS as operacoes de copia detectadas tiverem terminado.

    Uso basico (abre o PowerShell como voce quiser, nao precisa ser admin para monitorar,
    mas o "shutdown" pode pedir confirmacao dependendo das politicas do sistema):

        powershell -ExecutionPolicy Bypass -File .\Watch-CopyAndShutdown.ps1

    Parametros uteis:

        -PollSeconds 5           Intervalo entre verificacoes (padrao: 5s)
        -ConfirmZeroChecks 3     Quantas verificacoes seguidas com 0 copias ativas
                                  sao necessarias para considerar "terminou de verdade"
                                  (evita falso positivo no intervalo entre a 1a e a 2a copia)
        -ShutdownDelaySeconds 60 Tempo de aviso antes do shutdown de fato (cancelavel)
        -DryRun                  Nao desliga o PC, apenas avisa quando terminaria

    Para cancelar um shutdown ja agendado, em outro terminal rode:  shutdown /a
#>

param(
    [int]$PollSeconds = 5,
    [int]$ConfirmZeroChecks = 3,
    [int]$ShutdownDelaySeconds = 60,
    [switch]$DryRun
)

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
using System.Collections.Generic;

public class CopyWatcher {
    [DllImport("user32.dll")]
    private static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll")]
    private static extern int GetClassName(IntPtr hWnd, StringBuilder lpClassName, int nMaxCount);

    [DllImport("user32.dll")]
    private static extern bool IsWindowVisible(IntPtr hWnd);

    private delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    public static int CountCopyWindows() {
        int count = 0;
        EnumWindows(delegate(IntPtr hWnd, IntPtr lParam) {
            if (IsWindowVisible(hWnd)) {
                StringBuilder sb = new StringBuilder(256);
                GetClassName(hWnd, sb, sb.Capacity);
                if (sb.ToString() == "OperationStatusWindow") {
                    count++;
                }
            }
            return true;
        }, IntPtr.Zero);
        return count;
    }
}
"@

function Write-Status {
    param([string]$Message)
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts] $Message"
}

Write-Status "Monitorando janelas de copia do Explorer (classe 'OperationStatusWindow')..."
Write-Status "Aguardando pelo menos uma operacao de copia ser detectada..."

$everDetected = $false
$zeroStreak = 0

while ($true) {
    $count = [CopyWatcher]::CountCopyWindows()

    if ($count -gt 0) {
        if (-not $everDetected) {
            Write-Status "Copia detectada! ($count janela(s) de progresso ativa(s))"
        }
        $everDetected = $true
        $zeroStreak = 0
        Write-Status "Em andamento: $count janela(s) de copia ativa(s)."
    }
    elseif ($everDetected) {
        $zeroStreak++
        Write-Status "Nenhuma janela de copia ativa agora (confirmacao $zeroStreak de $ConfirmZeroChecks)..."
        if ($zeroStreak -ge $ConfirmZeroChecks) {
            break
        }
    }
    else {
        Write-Status "Aguardando inicio de copia... (nenhuma detectada ainda)"
    }

    Start-Sleep -Seconds $PollSeconds
}

Write-Status "Copia(s) finalizada(s) com confianca."

if ($DryRun) {
    Write-Status "[DryRun] O computador seria desligado agora. Nenhuma acao foi executada."
    return
}

Write-Status "Desligando o computador em $ShutdownDelaySeconds segundos. Para cancelar, rode: shutdown /a"
shutdown /s /t $ShutdownDelaySeconds /c "Desligamento automatico: copia de arquivos concluida (Watch-CopyAndShutdown.ps1)"

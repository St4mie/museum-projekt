# rebuild.ps1 – Stoppt, reinigt, baut neu und führt Tests durch.
# Bricht bei >50% Fehlern ab oder wiederholt Cleanup bis MAX_RETRIES erreicht.

# ------------------------------------------------------------------------------
# Parameter
# ------------------------------------------------------------------------------
$MAX_RETRIES = 2            # maximale Anzahl Cleanup-Versuche
$FAIL_PERCENT = 50          # Fehler-Prozent, ab dem erneut gebaut wird
$retry = 0

# Logfile anlegen (wird bei jedem Lauf überschrieben)
$LOGFILE = Join-Path -Path $PSScriptRoot -ChildPath "rebuild.log"
# Datei neu anlegen / leeren
Set-Content -Path $LOGFILE -Value ""

# Hilfsfunktion zum Loggen und Echo
function Log {
    param([string]$message)
    Write-Host $message
    Add-Content -Path $LOGFILE -Value $message
}

# ------------------------------------------------------------------------------
# 1–6: Cleanup + Neubau
# ------------------------------------------------------------------------------
function Cleanup {
    Log "🛑 1) Stoppe **alle** laufenden Container"
    docker ps -q | ForEach-Object { docker stop $_ }

    Log "🗑️ 2) Entferne **alle** Container"
    docker ps -aq | ForEach-Object { docker rm -f $_ }

    Log "🧹 3) Prune ungenutzte Netzwerke"
    docker network prune -f

    Log "🗑️ 4) Entferne ungenutzte Images"
    docker image prune -af

    Log "📦 5) Baue neu und starte im Dev-Profil"
    $env:COMPOSE_PROFILES = "dev"
    docker compose up --build -d

    Log "⏳ 6) Warte, bis die Datenbank den Healthcheck besteht…"
    $DB_CONTAINER = docker compose ps -q db
    while ($true) {
        if ($DB_CONTAINER -and (docker inspect --format='{{.State.Health.Status}}' $DB_CONTAINER) -eq "healthy") {
            break
        }
        Write-Host "." -NoNewline
        Add-Content -Path $LOGFILE -Value "." -NoNewline
        Start-Sleep -Seconds 2
    }
    Log " ✅ Datenbank ist ready"
}

# ------------------------------------------------------------------------------
# 7: Tests ausführen und Fehlerquote ermitteln
# ------------------------------------------------------------------------------
function Run-Tests {
    Log "🧪 7) Führe Tests im Backend-Container aus"
    # Alle Tests laufen lassen, unabhängig von Einzelabbruch
    # Output geht an die Konsole und ins Log
    $output = docker compose exec backend pytest --maxfail=0 --disable-warnings -v
    $output | ForEach-Object { Log $_ }
    $exit_code = $LASTEXITCODE

    if ($exit_code -eq 0) {
        $failed = 0
        $total = [regex]::Match($output, '(\d+) passed').Groups[1].Value
        if (-not $total) { $total = "n/a" }
    } else {
        # fehlgeschlagene Tests zählen
        $failed = [regex]::Match($output, '(\d+) failed').Groups[1].Value
        if (-not $failed) { $failed = 1 }
        $total = [regex]::Match($output, '(\d+) passed').Groups[1].Value
        if (-not $total) { $total = 0 }
    }

    # Prozentuale Fehlerquote berechnen
    if ($total -eq "n/a" -or $total -eq 0) {
        $pct = 100
    } else {
        $pct = [math]::Floor(($failed * 100) / ($total + $failed))
    }

    Log "📊 Tests: $total passed, $failed failed (Fehlerquote: ${pct}%)"
    # Erfolg, wenn Fehlerquote ≤ FAIL_PERCENT
    return ($pct -le $FAIL_PERCENT)
}

# ------------------------------------------------------------------------------
# Hauptablauf
# ------------------------------------------------------------------------------
Log "===== Rebuild gestartet: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ====="
Cleanup

while ($true) {
    if (Run-Tests) {
        Log "🎉 Alle Tests erfolgreich oder unter Schwelle!"
        break
    } else {
        $retry++
        if ($retry -ge $MAX_RETRIES) {
            Log "✘ Zu viele Fehler nach $retry Versuchen – Abbruch."
            break
        }
        Log "⚠ Fehlerquote >$FAIL_PERCENT%. Warte 10s, dann erneut Cleanup… ($retry/$MAX_RETRIES)"
        Start-Sleep -Seconds 10
        Cleanup
    }
}

# ------------------------------------------------------------------------------
# Abschluss & Zusammenfassung
# ------------------------------------------------------------------------------
Log ""
Log "===== Zusammenfassung ====="
if ($failed -eq 0) {
    Log "✓ Rebuild & Tests erfolgreich abgeschlossen"
} else {
    Log "✘ Rebuild beendet mit $failed fehlgeschlagenen Tests"
}
Log "Detail-Log: $LOGFILE"

#!/usr/bin/env bash
# rebuild.sh – Stoppt, reinigt, baut neu und führt Tests durch.
# Bricht bei >50% Fehlern ab oder wiederholt Cleanup bis MAX_RETRIES erreicht.

set -euo pipefail

# ------------------------------------------------------------------------------
# Konfiguration: Welche Services/Container sollen gereinigt werden?
# Kommentiere Zeilen aus, um bestimmte Container nicht zu stoppen/entfernen.
# ------------------------------------------------------------------------------
# Alle:     CLEAN_SERVICES=()
# Nur DB:   CLEAN_SERVICES=(museum-mariadb db-seed)
# Kein DB:  CLEAN_SERVICES=(museum-backend)
CLEAN_SERVICES=(museum-backend)  # z.B. ("museum-mariadb" "museum-backend")

# ------------------------------------------------------------------------------
# Parameter
# ------------------------------------------------------------------------------
MAX_RETRIES=2            # maximale Anzahl Cleanup-Versuche
FAIL_PERCENT=50          # Fehler-Prozent, ab dem erneut gebaut wird
retry=0

# Logfile anlegen (wird bei jedem Lauf überschrieben)
LOGFILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/rebuild.log"
: > "$LOGFILE"  # Datei neu anlegen / leeren

# Hilfsfunktion zum Loggen und Echo
log() {
  echo "$@" | tee -a "$LOGFILE"
}

# ------------------------------------------------------------------------------
# 1–6: Cleanup + Neubau
# ------------------------------------------------------------------------------
cleanup() {
  log "🛑 1) Stoppe Container: ${CLEAN_SERVICES[*]:-alle}"
  if [ ${#CLEAN_SERVICES[@]} -eq 0 ]; then
    docker ps -q | xargs -r docker stop
  else
    for svc in "${CLEAN_SERVICES[@]}"; do
      docker stop "$svc" || true
    done
  fi

  log "🗑️ 2) Entferne Container: ${CLEAN_SERVICES[*]:-alle}"
  if [ ${#CLEAN_SERVICES[@]} -eq 0 ]; then
    docker ps -aq | xargs -r docker rm -f
  else
    for svc in "${CLEAN_SERVICES[@]}"; do
      docker rm -f "$svc" || true
    done
  fi

  log "🧹 3) Prune ungenutzte Netzwerke"
  docker network prune -f

  log "🗑️ 4) Entferne ungenutzte Images"
  docker image prune -af

  log "📦 5) Baue neu und starte im Dev-Profil"
  COMPOSE_PROFILES=dev docker compose up --build -d

  log -n "⏳ 6) Warte, bis die Datenbank den Healthcheck besteht…"
  DB_CONTAINER="$(docker compose ps -q db)"
  until [ -n "$DB_CONTAINER" ] && \
        [ "$(docker inspect --format='{{.State.Health.Status}}' "$DB_CONTAINER")" = "healthy" ]; do
    printf "." | tee -a "$LOGFILE"
    sleep 2
  done
  log " ✅ Datenbank ist ready"
}

# ------------------------------------------------------------------------------
# 7: Tests ausführen und Fehlerquote ermitteln
# ------------------------------------------------------------------------------
run_tests() {
  log "🧪 7) Führe Tests im Backend-Container aus"
  docker compose exec backend pytest --maxfail=0 --disable-warnings -v | tee -a "$LOGFILE"
  exit_code=${PIPESTATUS[0]}

  if [ "$exit_code" -eq 0 ]; then
    failed=0
    total=$(grep -Po '(\d+) passed' "$LOGFILE" | grep -Po '\d+' || echo "n/a")
  else
    failed=$(grep -Po '(\d+) failed' "$LOGFILE" | grep -Po '\d+' || echo 1)
    total=$(grep -Po '(\d+) passed' "$LOGFILE" | grep -Po '\d+' || echo 0)
  fi

  if [[ "$total" == "n/a" ]] || [[ "$total" -eq 0 ]]; then
    pct=100
  else
    pct=$(( failed * 100 / (total + failed) ))
  fi

  log "📊 Tests: $total passed, $failed failed (Fehlerquote: ${pct}%)"
  (( pct > FAIL_PERCENT )) && return 1 || return 0
}

# ------------------------------------------------------------------------------
# Hauptablauf
# ------------------------------------------------------------------------------
log "===== Rebuild gestartet: $(date '+%Y-%m-%d %H:%M:%S') ====="
cleanup

while true; do
  if run_tests; then
    log "🎉 Alle Tests erfolgreich oder unter Schwelle!"
    break
  else
    (( retry++ ))
    if (( retry >= MAX_RETRIES )); then
      log "✘ Zu viele Fehler nach $retry Versuchen – Abbruch."
      break
    fi
    log "⚠ Fehlerquote >${FAIL_PERCENT}%. Warte 10s, dann erneut Cleanup… ($retry/$MAX_RETRIES)"
    sleep 10
    cleanup
  fi
done

# ------------------------------------------------------------------------------
# Abschluss & Zusammenfassung
# ------------------------------------------------------------------------------
log ""
log "===== Zusammenfassung ====="
if (( failed == 0 )); then
  log "✓ Rebuild & Tests erfolgreich abgeschlossen"
else
  log "✘ Rebuild beendet mit $failed fehlgeschlagenen Tests"
fi
log "Detail-Log: $LOGFILE"

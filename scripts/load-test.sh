#!/usr/bin/env bash
# Generates API traffic so the Grafana panels (and the HPA) have something to show.
#   BASE_URL=http://<ingress-host> ./scripts/load-test.sh
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:3000}"
REQUESTS="${REQUESTS:-500}"

echo "Sending ${REQUESTS} rounds of requests to ${BASE_URL}"
for i in $(seq 1 "$REQUESTS"); do
  curl -s -o /dev/null "${BASE_URL}/api/doctors"
  curl -s -o /dev/null "${BASE_URL}/api/appointments"
  curl -s -o /dev/null "${BASE_URL}/api/appointments/stats"
  curl -s -o /dev/null "${BASE_URL}/api/appointments/999999" # a 404, so the status panel shows 4xx too
  if (( i % 50 == 0 )); then echo "  ${i}/${REQUESTS}"; fi
done
echo "Load test completed"

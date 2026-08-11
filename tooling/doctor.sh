#!/usr/bin/env bash
set -euo pipefail

echo 'Deprecated: doctor.sh is now graft-compatibility_install-audit.sh.' >&2
exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/graft-compatibility_install-audit.sh" "$@"

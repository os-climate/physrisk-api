#!/bin/bash

# set -x

status_code="0"

# Process commmand-line arguments
if [ $# -eq 0 ]; then
    TARGET=$(pwd)
elif [ $# -ge 1 ]; then
    TARGET="$*"
fi

cleanup_tmp() {
    # Only clean the temp directory if it was used
    if [ -f /tmp/"${TAPLO_BIN}" ] || [ -f /tmp/"${TAPLO_GZIP}" ]; then
        echo "Cleaning up..."
        rm /tmp/"${TAPLO_BIN}"*
    fi
}

install_pipaudit() {
    pip install --upgrade pip-audit || true
    AUDIT_BIN=$(which pip-audit)
    if [ ! -x "${AUDIT_BIN}" ]; then
        echo "Install failed: pip-audit tool could not be installed [pip-audit]"
        status_code="1"
    else
        # To avoid execution when sourcing this script for testing
        [ "$0" = "${BASH_SOURCE[0]}" ] && pip-audit "$*"
    fi
}

AUDIT_BIN=$(which pip-audit)
if [ ! -x "${AUDIT_BIN}" ]; then
    install_pipaudit "$0"
else
    pip-audit "${TARGET}"
fi

cleanup_tmp
exit $status_code

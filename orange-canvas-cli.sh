#!/bin/sh
# ==============================================================================
#
#          FILE:  orange-canvas-cli.sh
#
#         USAGE:  ---
#
#   DESCRIPTION:  ---
#
#       OPTIONS:  ---
#
#  REQUIREMENTS:  - POSIX shell or better
#                 - timeout (GNU coreutils)
#          BUGS:  ---
#         NOTES:  ---
#       AUTHORS:  Emerson Rocha <rocha[at]ieee.org>
# COLLABORATORS:  ---
#       COMPANY:  EticaAI
#       LICENSE:  Public Domain dedication or Zero-Clause BSD
#                 SPDX-License-Identifier: Unlicense OR 0BSD
#       VERSION:  v1.0.0
#       CREATED:  2022-08-24 21:59 UTC started. Based on orange-via-cli.py
#      REVISION:  ---
# ==============================================================================
set -e

# @see https://github.com/biolab/orange3/issues/1341
# @see https://github.com/biolab/orange3/issues/3874
# @see https://github.com/biolab/orange3/issues/4910
# @see https://github.com/biolab/orange3/pull/4966
# @see https://github.com/biolab/orange3/issues/2525

# @see https://unix.stackexchange.com/questions/483879/stop-kill-a-process-from-the-command-line-after-a-certain-amount-of-time

ORANGE_CLI_RUNTIME="${ORANGE_CLI_RUNTIME-"15"}"
ORANGE_CLI_TIMEOUT="${ORANGE_CLI_TIMEOUT-"300"}"

# We default workflow as first argument and as env variable
ORANGE_CLI_WORKFLOW="${ORANGE_CLI_WORKFLOW-$1}"

print_help() {
    _program="orange-canvas-cli.sh"
    echo "help"
    echo "basic usage"
    echo "   ${_program} path/to/workflow.ows"
    echo "${_program} path/to/workflow.ows"
}

if [ -z "$ORANGE_CLI_WORKFLOW" ] || [ "$ORANGE_CLI_WORKFLOW" = "-h" ] || [ "$ORANGE_CLI_WORKFLOW" = "--help" ]; then
    print_help
    exit 1
fi

set -x
timeout "$ORANGE_CLI_RUNTIME" \
    orange-canvas --no-welcome --no-splash "$ORANGE_CLI_WORKFLOW"
set +x

# ./orange-canvas-cli.sh /workspace/git/EticaAI/lsf-orange-data-mining/orange-simple-test.temp.ows

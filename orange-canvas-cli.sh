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

#### Configurations ____________________________________________________________
# Protip: You can customize this script instead of configure the parameters.

ORANGECLI_DEBUG="${ORANGECLI_DEBUG-""}"
ORANGECLI_RUNTIME="${ORANGECLI_RUNTIME-"15"}"
ORANGECLI_TEARDOWN="${ORANGECLI_TEARDOWN-"5"}"
ORANGECLI_TIMEOUT="${ORANGECLI_TIMEOUT-"300"}"
ORANGECLI_LOGLEVEL="${ORANGECLI_LOGLEVEL-"300"}"

# While not documented, we also default [workflow_file] and [outfile_1] both
# as command line and as envoriment variable
ORANGECLI_WORKFLOW="${ORANGECLI_WORKFLOW-$1}"
ORANGECLI_OUTFILE1="${ORANGECLI_OUTFILE1-$2}"

#### Functions _________________________________________________________________

#######################################
# Print user help
#
# Globals:
#   None
# Arguments:
#   None
# Outputs:
#   None
#######################################
print_help() {
  _program="$0"
  echo "usage: [ENVS=val] ${_program} [workflow_file] [outfile_1]"
  echo ""
  echo "positional arguments:"
  echo "  workflow_file         Path to Orange Workflow file."
  echo "  outfile_1             [Optional] Outfile to watch for changes"
  echo ""
  echo "enviroment variables:"
  echo "  ORANGECLI_TIMEOUT     [Value: '${ORANGECLI_TIMEOUT}'] Maximum runtime."
  echo "                        Used if orange-canvas is taking too long or"
  echo "                        if we fail to detect finished with success"
  echo "  ORANGECLI_TEARDOWN    [Value: '${ORANGECLI_TEARDOWN}'] additional delay"
  echo "                        if [outfile_1] is given and detection may"
  echo "                        fail to consider that the file still being"
  echo "                        written (or there is more outfiles)"
  echo "  ORANGECLI_RUNTIME     [Value: '${ORANGECLI_RUNTIME}'] if [outfile_1]"
  echo "                        is not given, we always stop orange-canvas"
  echo "                        at this exact time."
  echo "  ORANGECLI_DEBUG       [Value: '${ORANGECLI_DEBUG}'] debug/verbose"
  echo ""
  echo "complete examples:"
  echo "   ${_program} path/to/workflow.ows"
  echo ""
  echo "   ${_program} path/to/workflow.ows path/to/result/output_1.xlsx"
  echo ""
  echo "   ORANGECLI_DEBUG=1 path/to/workflow-with-bugs.ows"
  echo ""
  echo "   ORANGECLI_RUNTIME=10 \\"
  echo "     ${_program} path/to/fast-workflow.ows"
  echo ""
  echo "   ORANGECLI_TIMEOUT=10 ORANGECLI_TEARDOWN=2 \\"
  echo "     ${_program} path/to/fast-workflow.ows path/to/result/output_1.xlsx"
}

#######################################
# Print context information
#
# Globals:
#   None
# Arguments:
#   None
# Outputs:
#   None
#######################################
print_debug_context() {
  _program="$0"
  printf "\tprint_debug_context\n"
  echo "ORANGECLI_DEBUG='$ORANGECLI_DEBUG'"
  echo "ORANGECLI_RUNTIME='$ORANGECLI_RUNTIME'"
  echo "ORANGECLI_TEARDOWN='$ORANGECLI_TEARDOWN'"
  echo "ORANGECLI_TIMEOUT='$ORANGECLI_TIMEOUT'"
  echo ""
}

#### Main ______________________________________________________________________

if [ -n "$ORANGECLI_DEBUG" ]; then
  print_debug_context
fi

if [ -z "$ORANGECLI_WORKFLOW" ] || [ "$ORANGECLI_WORKFLOW" = "-h" ] || [ "$ORANGECLI_WORKFLOW" = "--help" ]; then
  print_help
  exit 1
fi

# set -x
# timeout "$ORANGECLI_RUNTIME" \
#   orange-canvas --no-welcome --no-splash "$ORANGECLI_WORKFLOW"
# set +x
set -x
orange-canvas --no-welcome --no-splash "$ORANGECLI_WORKFLOW" &
pid=$!
sleep "$ORANGECLI_RUNTIME"
kill "$pid"
set +x

# ./orange-canvas-cli.sh /workspace/git/EticaAI/lsf-orange-data-mining/orange-simple-test.temp.ows

#### Etc _______________________________________________________________________
# Discussions related to run orange via cli
# @see https://github.com/biolab/orange3/issues/1341
# @see https://github.com/biolab/orange3/issues/3874
# @see https://github.com/biolab/orange3/issues/4910
# @see https://github.com/biolab/orange3/pull/4966
# @see https://github.com/biolab/orange3/issues/2525

# @see https://unix.stackexchange.com/questions/483879/stop-kill-a-process-from-the-command-line-after-a-certain-amount-of-time

# @see https://unix.stackexchange.com/questions/512356/is-there-any-way-to-launch-gui-application-without-gui

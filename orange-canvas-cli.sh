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
#                   - Very portable, Linux, MacOS,  Windows via WSL
#                 - orange-canvas (https://orange3.readthedocs.io/en/latest/)
#                 - Xvfb (if ORANGECLI_USEXVFB=1)
#                   - Does not work on Windows (because Windows do not use X
#                     server). Feel free to customize some alternative
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

# the next line will stop on first error. However we do not use pipefail
# since not availible on POSIX shell
set -e

#### Configurations ____________________________________________________________
# Protip: You can customize this script instead of configure the parameters.

ORANGECLI_DEBUG="${ORANGECLI_DEBUG-""}"
ORANGECLI_RUNTIME="${ORANGECLI_RUNTIME-"15"}"
ORANGECLI_TEARDOWN="${ORANGECLI_TEARDOWN-"5"}"
ORANGECLI_TIMEOUT="${ORANGECLI_TIMEOUT-"300"}"
ORANGECLI_LOGLEVEL="${ORANGECLI_LOGLEVEL-"300"}"
ORANGECLI_USEXVFB="${ORANGECLI_USEXVFB-""}"

# While not documented, we also default [workflow_file] and [outfile_1] both
# as command line and as envoriment variable
ORANGECLI_WORKFLOW="${ORANGECLI_WORKFLOW-$1}"
ORANGECLI_OUTFILE1="${ORANGECLI_OUTFILE1-$2}"
ORANGECLI_OUTFILE2="${ORANGECLI_OUTFILE2-$3}"
ORANGECLI_OUTFILE3="${ORANGECLI_OUTFILE3-$4}"

# green=$(tput setaf 2)
# blue=$(tput setaf 2)
# normal=$(tput sgr0)

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
_print_help() {
  _program="$0"
  echo "usage: [ENVS=val] ${_program} [workflow_file] [outfile_1] [outfile_2] \
[outfile_3]"
  echo ""
  echo "positional arguments:"
  echo "  workflow_file         Path to Orange Workflow file."
  echo "  outfile_1             [Optional] Outfile to watch for changes"
  echo ""
  echo "environment variables:"
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
  echo "  ORANGECLI_USEXVFB     [Value: '${ORANGECLI_USEXVFB}'] Use Xvfb"
  echo "                        (virtual framebuffer X server for X Version 11)"
  echo "                        Hides the QT interface from showing."
  echo "                        Hides the QT interface from showing."
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
# Main event loop
#
# Globals:
#   ORANGECLI_WORKFLOW
#   ORANGECLI_OUTFILE1
#   ORANGECLI_OUTFILE2
#   ORANGECLI_OUTFILE3
#   ORANGECLI_RUNTIME
#   ORANGECLI_TIMEOUT
#   ORANGECLI_USEXVFB
# Arguments:
#   None
# Outputs:
#   Informational messages
#######################################
main_loop() {
  orange_pid=""

  runtime=$(($(date +%s) + ORANGECLI_RUNTIME)) # Calculate end time.
  timeout=$(($(date +%s) + ORANGECLI_TIMEOUT)) # Calculate end time.

  echo "main_loop START"

  status_quo_old=$(main_test_outfiles_status_quo "$ORANGECLI_OUTFILE1" "$ORANGECLI_OUTFILE2" "$ORANGECLI_OUTFILE3")

  if [ -n "$ORANGECLI_USEXVFB" ]; then
    xvfb-run orange-canvas --no-welcome --no-splash "$ORANGECLI_WORKFLOW" &
    orange_pid=$!
  # elif [ -n "$ORANGECLI_USESOMETINGELSE" ]; then
  #   echo "here if needs to run another strategy"
  else
    orange-canvas --no-welcome --no-splash "$ORANGECLI_WORKFLOW" &
    orange_pid=$!
  fi

  status_quo_changes="$((0))"
  # While (current epoch is less than maximum timeout) AND (orange_pid is alive)
  while [ "$(date +%s)" -lt "$timeout" ] && ps -p $orange_pid >/dev/null; do
    now=$(date +%s) # Timenow

    if [ -n "$ORANGECLI_DEBUG" ]; then
      echo "Loop ...now     $now"
      echo "Loop ...runtime $runtime"
      echo "Loop ...timeout $timeout"
      echo "Loop ...ORANGECLI_OUTFILE1 $ORANGECLI_OUTFILE1"
      echo "Loop ...ORANGECLI_OUTFILE2 $ORANGECLI_OUTFILE2"
      echo "Loop ...ORANGECLI_OUTFILE3 $ORANGECLI_OUTFILE3"
    fi

    status_quo=$(main_test_outfiles_status_quo "$ORANGECLI_OUTFILE1" "$ORANGECLI_OUTFILE2" "$ORANGECLI_OUTFILE3")
    # echo "Loop ...status_quo $status_quo"
    if [ "$status_quo_old" != "$status_quo" ]; then
      status_quo_changes="$((status_quo_changes + 1))"
      echo "    outfiles status quo changed [$status_quo_changes] times"
      echo "    status_quo_old $status_quo_old"
      echo "    status_quo $status_quo"
      status_quo_old="$status_quo"
    fi

    if ps -p $orange_pid >/dev/null; then
      echo "$orange_pid is running"
      # Do something knowing the pid exists, i.e. the process with $PID is running
    fi

    # wait # for sleep
    sleep 1
  done

  # echo "waiting for [$ORANGECLI_RUNTIME]"
  # sleep "$ORANGECLI_RUNTIME"

  # Kill if $orange_pid still alive
  if ps -p $orange_pid >/dev/null; then
    kill "$orange_pid"
  fi

  # all strategies would try to kill the $orange_pid
  kill "$orange_pid" || true

  if [ -n "$ORANGECLI_USEXVFB" ]; then
    pkill Xvfb || true
    echo "Tip: previous message like 'Did the X11 server die?' can be ignored"
  fi

  echo "main_loop END"
}

#######################################
# Print user help
#
# Globals:
#   None
# Arguments:
#   outfile_1
#   outfile_2
#   outfile_3
# Outputs:
#   fingerprint
#######################################
main_test_outfiles_status_quo() {
  outfile_1="${1-''}"
  outfile_2="${2-''}"
  outfile_3="${3-''}"

  # stat path/file.ext returns at least modifiation time and size, but syntax
  # varies by operational system. Since we want modifiation time
  # Not just hash of the content, we will just hash the entire result of
  # stat path/file.ext

  fingerprint=""

  if [ -z "$outfile_1" ]; then
    fingerprint="outfile_1:Undefined"
  elif [ -f "$outfile_1" ]; then
    _stat_info=$(stat "$outfile_1" | tr -dc '[:print:]')
    _hashed=$(echo "$_stat_info" | md5sum | cut -d' ' -f1)
    # _size=$(stat -c %s -- "$outfile_1")
    # _mtime=$(stat -c %s -- "$outfile_1")
    fingerprint="outfile_1:${_hashed}"
  else
    fingerprint="outfile_1:NotExist"
  fi

  if [ -z "$outfile_2" ]; then
    fingerprint="${fingerprint}|outfile_2:Undefined"
  elif [ -f "$outfile_2" ]; then
    _stat_info=$(stat "$outfile_2" | tr -dc '[:print:]')
    _hashed=$(echo "$_stat_info" | md5sum | cut -d' ' -f1)
    fingerprint="${fingerprint}|outfile_2:${_hashed}"
  else
    fingerprint="${fingerprint}|outfile_2:NotExist"
  fi

  if [ -z "$outfile_3" ]; then
    fingerprint="${fingerprint}|outfile_2:Undefined"
  elif [ -f "$outfile_3" ]; then
    _stat_info=$(stat "$outfile_3" | tr -dc '[:print:]')
    _hashed=$(echo "$_stat_info" | md5sum | cut -d' ' -f1)
    fingerprint="${fingerprint}|outfile_3:${_hashed}"
  else
    fingerprint="${fingerprint}|outfile_3:NotExist"
  fi
  echo "$fingerprint"
}

#######################################
# Print context information. Likely relevant to know common things that can
# be wrong (like user mixing pip and conda packages), so other can help
# debug.
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

  blue=$(tput setaf 4)
  normal=$(tput sgr0)

  printf "%40s\n" "${blue}"
  printf "\tprint_debug_context START\n"
  echo "ORANGECLI_WORKFLOW='$ORANGECLI_WORKFLOW'"
  echo "ORANGECLI_OUTFILE1='$ORANGECLI_OUTFILE1'"
  echo ""
  echo "ORANGECLI_DEBUG='$ORANGECLI_DEBUG'"
  echo "ORANGECLI_RUNTIME='$ORANGECLI_RUNTIME'"
  echo "ORANGECLI_TEARDOWN='$ORANGECLI_TEARDOWN'"
  echo "ORANGECLI_TIMEOUT='$ORANGECLI_TIMEOUT'"
  echo "ORANGECLI_USEXVFB='$ORANGECLI_USEXVFB'"
  echo ""

  # Things here could be moved to loop or something, but this is mostly
  # copy-and-paste friendly

  if command -v python3 >/dev/null 2>&1; then
    printf "\tpython3 -m pip --version\n"
    python3 -m pip --version
    echo ""
  fi

  if command -v python >/dev/null 2>&1; then
    printf "\tpython -m pip --version\n"
    python -m pip --version
    echo ""
  fi

  # if ! command -v pip &> /dev/null
  if command -v pip >/dev/null 2>&1; then
    printf "\tpip --version\n"
    pip --version
    printf "\tpip list (packages with orange in name)\n"
    pip list | grep -i "orange"
    printf "\tpip list (packages with qt in name)\n"
    pip list | grep -i "qt"
    echo ""
  else
    if command -v pip3 >/dev/null 2>&1; then
      printf "\tpip3 --version\n"
      pip3 --version
      printf "\tpip3 list (packages with orange in name)\n"
      pip3 list | grep -i "orange"
      printf "\tpip3 list (packages with qt in name)\n"
      pip3 list | grep -i "qt"
      echo ""
    fi
    printf "\tpip3 command not found. Ignoring.\n"
  fi

  # @TODO Rocha is not sure if conda list have same output of pip list
  if command -v conda >/dev/null 2>&1; then
    printf "\tconda list (packages with orange in name)\n"
    conda list | grep -i "orange"
    printf "\tconda list  (packages with qt in name)\n"
    conda list | grep -i "qt"
    echo ""
    echo "@TODO maybe add other conda info here."
    echo ""
  else
    printf "\tconda command not found. Ignoring.\n"
  fi
  # printf "\tpip list (packages with orange in name)\n"
  # pip list | grep "orange"
  echo ""
  printf "\tprint_debug_context END\n"
  printf "%40s\n" "${normal}"
  echo ""
  echo ""
}

#### Main ______________________________________________________________________

### Early messages . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
if [ -n "$ORANGECLI_DEBUG" ]; then
  print_debug_context
fi

if [ -z "$ORANGECLI_WORKFLOW" ] || [ "$ORANGECLI_WORKFLOW" = "-h" ] || [ "$ORANGECLI_WORKFLOW" = "--help" ]; then
  _print_help
  exit 1
fi

if [ -z "$ORANGECLI_WORKFLOW" ] || [ ! -f "$ORANGECLI_WORKFLOW" ]; then
  echo "ERROR: ORANGECLI_WORKFLOW [$ORANGECLI_WORKFLOW] is not valid file"
  exit 1
fi

if [ -n "$ORANGECLI_USEXVFB" ] && ! command -v xvfb-run >/dev/null 2>&1; then
  echo "ERROR: ORANGECLI_USEXVFB enabled, but Xvfb not installed"
  exit 1
fi

main_loop

# ./orange-canvas-cli.sh /workspace/git/EticaAI/lsf-orange-data-mining/orange-simple-test.temp.ows

# ORANGECLI_DEBUG=1 ORANGECLI_USEXVFB=1 ./orange-canvas-cli.sh /workspace/git/EticaAI/lsf-orange-data-mining/orange-simple-test.temp.ows
# ORANGECLI_DEBUG=1 ORANGECLI_USEXVFB=1 ./orange-canvas-cli.sh /workspace/git/EticaAI/lsf-orange-data-mining/orange-simple-test.temp.ows /workspace/git/EticaAI/lsf-orange-data-mining/999999/0/iris.csv

#### Etc _______________________________________________________________________
## Discussions related to run orange via cli
# @see https://github.com/biolab/orange3/issues/1341
# @see https://github.com/biolab/orange3/issues/3874
# @see https://github.com/biolab/orange3/issues/4910
# @see https://github.com/biolab/orange3/pull/4966
# @see https://github.com/biolab/orange3/issues/2525

## Kill program after some time

# @see https://unix.stackexchange.com/questions/483879/stop-kill-a-process-from-the-command-line-after-a-certain-amount-of-time

## Xvfb related
# @see https://unix.stackexchange.com/questions/512356/is-there-any-way-to-launch-gui-application-without-gui

# @see https://discourse.nixos.org/t/running-qt-applications-with-xvfb-run/1696
# @see https://stackoverflow.com/questions/13215120/how-do-i-make-python-qt-and-webkit-work-on-a-headless-server

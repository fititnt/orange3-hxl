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

#### Potential To Do's _________________________________________________________
# @TODO implement ORANGECLI_LOGLEVEL to match orange orange-canvas --log-level
# @TODO allow user configure some filepath (or maybe we print to stdout)
#       the actual output of "orange-canvas path/to/workflow.ows"
# @TODO test a bit more outside Linux. However, both Windows and Mac in theory
#       should already work (however, ORANGECLI_USEXVFB=1 to hide the GUI
#       may not work and would be easier to just customize this script to some
#       non Xvfb + xvfb-run dependencies)

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
  echo "summary:"
  echo "  The ${_program} can be used to execute **already working workflows"
  echo "  without user input** fully via command line. If you pass 1 to 3"
  echo "  output files, it will watch for changes (size, modification time,"
  echo "  etc) and use ORANGECLI_TEARDOWN as tolerance for total time without"
  echo "  any new update. However, if you cant pass any output file, then"
  echo "  set harcoded value to ORANGECLI_RUNTIME that will close the"
  echo "  application"
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
  echo "                        fail to consider that the file is still being"
  echo "                        written (or there are more outfiles). "
  echo "                        Even for fast workflows, still recommended"
  echo "                        not set this value lower than 2 (2 seconds)"
  echo "                        to avoid file corruption."
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

  initial_time=$(date +%s)                     # Timenow
  runtime=$(($(date +%s) + ORANGECLI_RUNTIME)) # Calculate end time.
  timeout=$(($(date +%s) + ORANGECLI_TIMEOUT)) # Calculate end time.

  echo "main_loop START"

  # @TODO: maybe mark this variable as empty if we can catch errors. For now
  #        is used only to change the end message of main_loop()
  is_okay="1"
  # is_okay=""

  status_quo_old=$(main_test_outfiles_status_quo \
    "$ORANGECLI_OUTFILE1" "$ORANGECLI_OUTFILE2" "$ORANGECLI_OUTFILE3")

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
  time_since_last_change="$((-1))"

  # while block explained:
  #       (current epoch is less than maximum timeout)
  #          AND
  #       (orange_pid is alive)
  # If orange-canvas fail (example: critical error, or some feature
  # allowing close itself after stop all actions) this code will
  # still work.
  while [ "$(date +%s)" -lt "$timeout" ] && ps -p $orange_pid >/dev/null; do
    diff=$(($(date +%s) - initial_time)) # Calculate end time.
    echo "T${diff}    ${time_since_last_change}"
    now=$(date +%s) # Timenow

    if [ -n "$ORANGECLI_DEBUG" ]; then
      echo "Loop ...now     $now"
      echo "Loop ...runtime $runtime"
      echo "Loop ...timeout $timeout"
      echo "Loop ...ORANGECLI_OUTFILE1 $ORANGECLI_OUTFILE1"
      echo "Loop ...ORANGECLI_OUTFILE2 $ORANGECLI_OUTFILE2"
      echo "Loop ...ORANGECLI_OUTFILE3 $ORANGECLI_OUTFILE3"
    fi

    status_quo=$(main_test_outfiles_status_quo \
      "$ORANGECLI_OUTFILE1" "$ORANGECLI_OUTFILE2" "$ORANGECLI_OUTFILE3")

    # This block only checks for changes on output . . . . . . . . . . . . . . .
    if [ "$status_quo_old" != "$status_quo" ]; then
      status_quo_changes="$((status_quo_changes + 1))"
      echo "    outfiles status quo changed [$status_quo_changes] times"
      echo "    previous time_since_last_change [$time_since_last_change]"
      echo "    status_quo_old [[$status_quo_old]]"
      echo "    status_quo     [[$status_quo]]"
      status_quo_old="$status_quo"
      time_since_last_change="$((0))"
    elif [ "$time_since_last_change" -gt "-1" ]; then
      time_since_last_change="$((time_since_last_change + 1))"
      if [ "$time_since_last_change" -gt "$ORANGECLI_TEARDOWN" ]; then
        echo "INFO: time_since_last_change [$time_since_last_change] > \
ORANGECLI_TEARDOWN [$ORANGECLI_TEARDOWN]"
        echo "      Stoping now..."
        is_okay="1"
        break
      fi
    fi

    # This block only checks for changes on output . . . . . . . . . . . . . . .
    if [ -z "$ORANGECLI_OUTFILE1" ] && [ "$diff" -gt "$ORANGECLI_RUNTIME" ]; then
      echo "INFO: diff [$diff] > \
ORANGECLI_RUNTIME [$ORANGECLI_RUNTIME]"
      echo "      and not output files to check for changes"
      echo "      We will assume it's time to stop without wait for"
      echo "      ORANGECLI_TIMEOUT [$ORANGECLI_TIMEOUT]"

      # This is not really a perfect ok, but whatever. No sufficient context
      # to check.
      is_okay="1"
      break
    fi
    sleep 1
  done

  # Kill if $orange_pid still alive
  if ps -p $orange_pid >/dev/null; then
    echo "INFO: Stoping orange_pid [$orange_pid]"
    kill "$orange_pid"
  else
    echo "INFO: orange_pid [$orange_pid] already was not alive."
    echo "      Not attempting to kill the process"
  fi

  # # all strategies would try to kill the $orange_pid
  # kill "$orange_pid" || true

  if [ -n "$ORANGECLI_USEXVFB" ]; then
    echo ""
    echo "INFO: ORANGECLI_USEXVFB was enabled. Attempting now to stop any"
    echo "      process named Xvfb"
    pkill Xvfb || true
    echo "INFO: previous message like 'Did the X11 server die?' can be ignored"
    echo ""
  fi

  # Lets exist with 0 (to signal ok execution, even if we cannot 100% be sure)
  # However, critical errors would return exit different than 0, so it still
  # likely be usable on CI enviroments

  red=$(tput setaf 1)
  green=$(tput setaf 2)
  normal=$(tput sgr0)

  if [ -n "$is_okay" ]; then
    printf "%40s\n" "${green}main_loop() (likely) successful run ${normal}"
    printf "%40s\n" "${normal}Please check the output to be sure ${normal}"
    exit 0
  else
    printf "%40s\n" "${red}main_loop() failed ${normal}"
    exit 1
  fi
}

#######################################
# Accept 3 arguments (can be empty) and try to create a fingerprint which can
# be compared later for changes. It's like a poor's man inotify, which requires
# an event loop
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

  # md5sum dependency removed. _stat_info without linebreanks already

  fingerprint=""

  if [ -z "$outfile_1" ]; then
    fingerprint="outfile_1:Undefined"
  elif [ -f "$outfile_1" ]; then
    # _stat_info=$(stat "$outfile_1" | tr -dc '[:print:]')
    _stat_info=$(stat "$outfile_1")
    # _hashed=$(echo "$_stat_info" | md5sum | cut -d' ' -f1)
    # fingerprint="outfile_1:${_hashed}"
    fingerprint="outfile_1:${_stat_info}"
  else
    fingerprint="outfile_1:NotExist"
  fi

  if [ -z "$outfile_2" ]; then
    fingerprint="${fingerprint}\n\noutfile_2:Undefined"
  elif [ -f "$outfile_2" ]; then
    # _stat_info=$(stat "$outfile_2" | tr -dc '[:print:]')
    _stat_info=$(stat "$outfile_2")
    # _hashed=$(echo "$_stat_info" | md5sum | cut -d' ' -f1)
    fingerprint="${fingerprint}\n\noutfile_2:${_stat_info}"
  else
    fingerprint="${fingerprint}\n\noutfile_2:NotExist"
  fi

  if [ -z "$outfile_3" ]; then
    fingerprint="${fingerprint}\n\noutfile_2:Undefined"
  elif [ -f "$outfile_3" ]; then
    # _stat_info=$(stat "$outfile_3" | tr -dc '[:print:]')
    _stat_info=$(stat "$outfile_3")
    # _hashed=$(echo "$_stat_info" | md5sum | cut -d' ' -f1)
    fingerprint="${fingerprint}\n\noutfile_3:${_stat_info}"
  else
    fingerprint="${fingerprint}\n\noutfile_3:NotExist"
  fi
  echo "$fingerprint"
}

#######################################
# Print context information. Likely relevant to know common things that can
# be wrong (like user mixing pip and conda packages), so other can help
# debug.
#
# Globals:
#   ORANGECLI_DEBUG
#   ORANGECLI_RUNTIME
#   ORANGECLI_TEARDOWN
#   ORANGECLI_TIMEOUT
#   ORANGECLI_LOGLEVEL
#   ORANGECLI_USEXVFB
#   ORANGECLI_WORKFLOW
#   ORANGECLI_OUTFILE1
#   ORANGECLI_OUTFILE2
#   ORANGECLI_OUTFILE3
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

# Here we start the main loop
main_loop

# main_loop() will (hopefully) already return correct exit status,
# so this script could be used as quick reference for Continuous Integration
# (Or use Orange3 via GitHub Actions use workflows files to make
# data conversions, without require end users know too much about
# Python scripting)

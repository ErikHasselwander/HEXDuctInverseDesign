#!/usr/bin/env bash
set -euo pipefail

SESSION="starccm_server"
WORKDIR="$PWD"   # change to the folder containing basecase.sim if needed
LOG="$WORKDIR/${SESSION}.log"

CMD='starccm+ -server -np 14 -assignport 47830 refFiles/basecase_2D_kwcc_200k.sim'

if tmux has-session -t "$SESSION" 2>/dev/null; then
  tmux kill-session -t "$SESSION"
  echo "Stopped tmux session: $SESSION"
  exit 0
fi

# Start in detached tmux. Use a login shell to pick up your normal env,
# log output, and keep the session open if the command exits.
tmux new-session -d -s "$SESSION" -c "$WORKDIR" \
  "bash -lc '
    echo \"[$(date)] starting: $CMD\" | tee -a \"$LOG\"
    ($CMD) >> \"$LOG\" 2>&1
    rc=\$?
    echo \"[$(date)] command exited with status \$rc\" | tee -a \"$LOG\"
    echo \"Log: $LOG\"
    exec bash
  '"

echo "Started tmux session: $SESSION"
echo "Attach with: tmux attach -t $SESSION"
echo "Log file: $LOG"

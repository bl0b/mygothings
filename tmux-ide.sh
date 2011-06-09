#!/bin/sh
tmux start-server
tmux new-session -n vim -s mygothings "while true; do vim -u mygothings.vimrc -i mygothings.viminfo -S mygothings.vim; done" ';' detach
tmux split-window -h -p 30 -t mygothings:vim "cd py && while true; do PYHISTORY=mygothings.pyhistory python -i sandbox.py; done"
tmux split-window -v -p 30 "while true; do HISTFILE=shell1.history bash -i; done"
tmux set-option mouse-mode on
tmux set-option mouse-select-pane on

tmux bind-key -n C-q kill-session



tmux attach-session -t mygothings

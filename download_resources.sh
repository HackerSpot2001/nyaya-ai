#!/bin/bash

# Run indefinitely (or until manually stopped)
while true
do
    echo "⚙ Fetching documents..."
    
    python3 manage.py acts
    python3 manage.py lawmin
    ./clear_ram.sh

    echo "✔ Completed one cycle..."
    echo "-----------------------------------"

    sleep 4
done

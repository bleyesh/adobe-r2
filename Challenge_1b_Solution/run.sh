#!/bin/bash

# Default to Collection 1 if no argument is provided
INPUT_DIR="${1:-Challenge_1b/Collection 1}"

echo "🔄 Running analysis on $INPUT_DIR..."
python3 src/main.py --input_dir "$INPUT_DIR"

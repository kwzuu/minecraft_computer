#!/bin/bash

error() {
  echo "An error occurred: $1"
  exit 1
}

cd "$(dirname -- "$0")" || error "Directory does not exist"

cargo build --release

# shellcheck disable=SC1073
find tests -type f | while read -r file; do
  base_name="$(basename "$file")"
  echo "building $base_name"
  target/release/schematic_assembler "$file" "schematics/${base_name%.*}.schematic"
done

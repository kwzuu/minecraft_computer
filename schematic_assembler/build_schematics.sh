#!/bin/bash

error() {
  echo "An error occurred: $1"
  exit 1
}

if [ -n "$1" ]; then
  dir="$(realpath "$1")"
else
  cd "$(basename "$0")" || exit
  dir="schematic_assembly"
fi

if ! [ -h schematics ]; then
  echo 'You should symlink `schematics'\'' to where you want to drop the schematics for testing.' >&2
  if ! [ -d schematics ]; then
    echo 'Creating it as a directory as fallback.' >&2
    mkdir schematics
  fi
fi

cargo build --release

# shellcheck disable=SC1073
find "$dir" -type f | while read -r file; do
  base_name="$(basename "$file")"
  echo "building $base_name"
  target/release/schematic_assembler "$file" "schematics/${base_name%.*}.schematic"
done

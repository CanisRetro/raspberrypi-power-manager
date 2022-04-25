#!/bin/bash

power_manager_root="$PWD"
config_dir="$power_manager_root/config"
log_dir="$power_manager_root/log"

python3 ./src/__main__.py "$config_dir" "$log_dir"

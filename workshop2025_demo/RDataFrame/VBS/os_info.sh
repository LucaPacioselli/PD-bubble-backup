#!/bin/bash

# Display operating system details
echo "Operating System Details:"

# Print Linux kernel version
echo "Kernel version: $(uname -r)"

# Print OS distribution info (Ubuntu, CentOS, etc.)
if [ -f /etc/os-release ]; then
    echo "OS Distribution Info:"
    cat /etc/os-release
else
    echo "/etc/os-release file not found. Unable to determine OS distribution."
fi


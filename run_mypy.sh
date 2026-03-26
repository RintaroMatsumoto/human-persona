#!/bin/bash
# Run mypy strict type checking on core/ modules

set -e

echo "Running mypy strict type checking on core/ modules..."
echo "======================================================="

python -m mypy core/ \
    --strict \
    --show-error-codes \
    --show-error-context \
    --no-implicit-reexport

echo ""
echo "Type checking complete!"

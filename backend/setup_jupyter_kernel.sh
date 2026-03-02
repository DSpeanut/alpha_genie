#!/bin/bash

# Script to create a Jupyter kernel using the backend's virtual environment

echo "Setting up Jupyter kernel for Alpha Genie backend..."

# Activate the virtual environment
source venv/bin/activate

# Install ipykernel if not already installed
pip install ipykernel

# Register the kernel
python -m ipykernel install --user --name=alpha_genie --display-name="alpha_genie"

echo ""
echo "✅ Jupyter kernel 'alpha_genie' has been created!"
echo ""
echo "You can now:"
echo "  1. Open Jupyter: jupyter notebook"
echo "  2. Select kernel: 'alpha_genie'"
echo ""

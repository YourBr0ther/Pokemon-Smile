#!/bin/bash

# Add current directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run pytest with coverage
pytest tests/ -v --cov=app --cov-report=term-missing 
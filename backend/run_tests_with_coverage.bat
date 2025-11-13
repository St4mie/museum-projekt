@echo off
echo Running tests with coverage...
cd %~dp0
python -m pytest --cov=app --cov-report=term --cov-report=html tests/
echo.
echo Coverage report generated in htmlcov/ directory
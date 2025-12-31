#!/bin/bash
open "http://127.0.0.1:8502" || xdg-open "http://127.0.0.1:8502"

# Run the app
.venv/bin/python web.py
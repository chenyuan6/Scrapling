#!/bin/bash
cd /opt/scrapling
DATE=$(date +%Y-%m-%d)
.venv/bin/python lamose_leads/scraper.py \
  --source file \
  --file lamose_leads/targets.txt \
  --output lamose_leads/results/leads_$DATE.csv

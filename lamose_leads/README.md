# Lamose Lead Scraper

Finds business emails from public websites for B2B outreach. Built on [Scrapling](https://github.com/D4Vinci/Scrapling).

## Quick Start (local)

```bash
git clone https://github.com/chenyuan6/Scrapling
cd Scrapling
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"
playwright install chromium
```

## Usage

```bash
# Scrape specific URLs
python lamose_leads/scraper.py --source website \
  --urls https://brand1.com https://brand2.com \
  --output leads.csv

# Bulk from a .txt file (one URL per line)
python lamose_leads/scraper.py --source file \
  --file lamose_leads/targets.txt \
  --output leads.csv

# Google search → auto-scrape results
python lamose_leads/scraper.py --source google \
  --query "coffee shop Calgary" --limit 50 \
  --output leads.csv
```

## VPS (31.220.49.110)

Installed at `/opt/scrapling`. Runs daily at 8am UTC via cron.

```bash
# SSH in
ssh -i ~/.ssh/lamose_vps root@31.220.49.110

# Add targets
nano /opt/scrapling/lamose_leads/targets.txt

# View today's results
ls /opt/scrapling/lamose_leads/results/

# Check cron log
tail -f /opt/scrapling/lamose_leads/cron.log
```

### Re-setup SSH key on a new machine

Generate a new key and add it to the VPS:
```bash
ssh-keygen -t ed25519 -C "lamose-vps" -f ~/.ssh/lamose_vps
ssh-copy-id -i ~/.ssh/lamose_vps.pub root@31.220.49.110
```

## Target Segments (proven customer fit)

| Priority | Segment | Search Query |
|---|---|---|
| 1 | Coffee shops | `"coffee shop" site:google.com/maps` |
| 2 | Dental clinics | `"dental clinic" Alberta` |
| 3 | Fitness studios | `"CrossFit" OR "yoga studio" Canada` |
| 4 | Golf clubs | `"golf club" Canada` |
| 5 | Real estate brokerages | `"Royal LePage" OR "RE/MAX" brokerage` |
| 6 | Hotels | `"hotel" Alberta BC` |

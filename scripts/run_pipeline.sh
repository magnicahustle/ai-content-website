#!/bin/bash
cd /home/miki/AI
source /home/miki/AI/venv/bin/activate
python3 /home/miki/AI/agents/content_creator.py
git add .
git commit -m "feat: Add new article (automated)"
git push origin main

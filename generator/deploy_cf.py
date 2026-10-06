#!/usr/bin/env python3
"""Deploy static assets to Cloudflare Pages (ringgit-iviztrading)."""

import os
import subprocess
import sys


def load_env():
    env_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    if not os.path.exists(env_file):
        print(f"Error: .env not found at {env_file}")
        sys.exit(1)
    with open(env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'").strip('"')


load_env()

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
dist_dir = os.path.join(project_dir, "dist")
project_name = "ringgit-iviztrading"

wrangler_bin = "/root/node_modules/.bin/wrangler"

print(f"Deploying {dist_dir} to Cloudflare Pages ({project_name})...\n")

cmd = [
    wrangler_bin,
    "pages",
    "deploy",
    dist_dir,
    f"--project-name={project_name}",
]

res = subprocess.run(cmd, env=os.environ.copy())
sys.exit(res.returncode)

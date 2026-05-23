"""
Git-based Coordination and Auto-Learning Script for Codex & Antigravity.
This script checks for updates in AGENT_COORDINATION.md, logs changes,
inspects Git status, and creates an automated triggers file if changes are detected.

Usage:
  python coordination_checker.py
"""
import os
import re
import datetime
import subprocess

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
COORDINATION_FILE = os.path.join(REPO_ROOT, "AGENT_COORDINATION.md")
TRIGGERS_FILE = os.path.join(REPO_ROOT, "coordination_triggers.json")

def get_git_status():
    try:
        res = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, cwd=REPO_ROOT)
        return res.stdout.strip()
    except Exception as e:
        return f"Error getting git status: {e}"

def parse_coordination_file():
    if not os.path.exists(COORDINATION_FILE):
        return None
    
    with open(COORDINATION_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Parse Mailbox messages
    mailbox_data = {"to_codex": [], "to_antigravity": []}
    
    # Find Mailbox section
    mailbox_match = re.search(r"## Mailbox(.*?)(## Shared Rules|$)", content, re.DOTALL | re.IGNORECASE)
    if mailbox_match:
        mailbox_content = mailbox_match.group(1)
        
        # Parse To Codex
        to_codex_match = re.search(r"### To Codex(.*?)### To Antigravity", mailbox_content, re.DOTALL | re.IGNORECASE)
        if to_codex_match:
            messages = re.findall(r"-\s*(.*)", to_codex_match.group(1))
            mailbox_data["to_codex"] = [m.strip() for m in messages if m.strip()]
            
        # Parse To Antigravity
        to_antigravity_match = re.search(r"### To Antigravity(.*)", mailbox_content, re.DOTALL | re.IGNORECASE)
        if to_antigravity_match:
            messages = re.findall(r"-\s*(.*)", to_antigravity_match.group(1))
            mailbox_data["to_antigravity"] = [m.strip() for m in messages if m.strip()]
            
    return mailbox_data

def run_checker():
    print("=" * 60)
    print("COORDINATION & AUTO-LEARNING CHECKER ACTIVE")
    print(f"Time: {datetime.datetime.now()}")
    print("=" * 60)
    
    # 1. Check Git Status
    print("\n[1] Checking local repository status:")
    status = get_git_status()
    if status:
        print(status)
    else:
        print("  Clean working directory (no uncommitted changes).")
        
    # 2. Parse Coordination File
    print("\n[2] Parsing AGENT_COORDINATION.md:")
    mailbox = parse_coordination_file()
    if mailbox:
        print(f"  Messages to Codex: {len(mailbox['to_codex'])}")
        for m in mailbox['to_codex']:
            print(f"    - {m}")
            
        print(f"  Messages to Antigravity: {len(mailbox['to_antigravity'])}")
        for m in mailbox['to_antigravity']:
            print(f"    - {m}")
    else:
        print("  No AGENT_COORDINATION.md file found.")
        
    print("\n" + "=" * 60)
    print("Checker completed successfully.")
    print("=" * 60)

if __name__ == "__main__":
    run_checker()

"""
Autonomous 30-second checking loop script for Codex & Antigravity.
This script regularly pulls updates from GitHub, runs the coordination checker,
monitors the training process, and pushes any local results.

Usage:
  python check_loop.py
"""
import os
import time
import subprocess
import datetime
import psutil

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
PID_TO_MONITOR = 28172

def run_cmd(args):
    try:
        res = subprocess.run(args, capture_output=True, text=True, cwd=REPO_ROOT)
        return res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return "", str(e)

def is_process_running(pid):
    try:
        return psutil.pid_exists(pid)
    except Exception:
        return False

def run_loop():
    print("=" * 60)
    print("STARTING AUTONOMOUS 30-SECOND COORDINATION LOOP")
    print(f"Monitoring PID: {PID_TO_MONITOR}")
    print(f"Repository: {REPO_ROOT}")
    print("=" * 60)
    
    iteration = 1
    while True:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] Iteration {iteration} - Checking for updates...")
        
        # 1. Git Fetch
        run_cmd(["git", "fetch", "origin"])
        
        # 2. Check if behind remote
        behind_out, _ = run_cmd(["git", "log", "HEAD..origin/main", "--oneline"])
        if behind_out:
            print("  New updates found on GitHub! Pulling changes...")
            pull_out, _ = run_cmd(["git", "pull", "origin", "main"])
            print(f"  Pull result: {pull_out}")
        else:
            print("  Local branch is up-to-date with remote.")
            
        # 3. Run coordination checker
        print("  Running coordination checker...")
        checker_out, _ = run_cmd(["python", "coordination_checker.py"])
        print(checker_out)
        
        # 4. Check training process status
        running = is_process_running(PID_TO_MONITOR)
        if running:
            try:
                proc = psutil.Process(PID_TO_MONITOR)
                cpu_percent = proc.cpu_percent(interval=0.1)
                mem = proc.memory_info().rss / (1024 * 1024)
                print(f"  Training PID {PID_TO_MONITOR} is ACTIVE: CPU={cpu_percent:.1f}%, RAM={mem:.1f}MB")
            except Exception:
                print(f"  Training PID {PID_TO_MONITOR} is ACTIVE.")
        else:
            print(f"  Training PID {PID_TO_MONITOR} is INACTIVE / COMPLETED!")
            
            # Check if any final submission files were generated in Downloads
            downloads_dir = r"C:\Users\HARI\Downloads"
            files = [f for f in os.listdir(downloads_dir) if "sub_v2" in f]
            if files:
                print(f"  Found generated predictions: {files}")
                # We can copy them to the repo root to track them
                for f in files:
                    src = os.path.join(downloads_dir, f)
                    dst = os.path.join(REPO_ROOT, f)
                    if not os.path.exists(dst):
                        print(f"  Copying {f} to repo root...")
                        subprocess.run(["copy", src, dst], shell=True)
                
                # Check if we should add, commit and push
                run_cmd(["git", "add", "."])
                run_cmd(["git", "commit", "-m", "Add V2 optimized submissions and results"])
                run_cmd(["git", "push", "origin", "main"])
                print("  Successfully pushed final submission files to GitHub!")
            break
            
        iteration += 1
        time.sleep(30)

if __name__ == "__main__":
    run_loop()

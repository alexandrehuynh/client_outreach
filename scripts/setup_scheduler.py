#!/usr/bin/env python3
"""
Setup script for automated scheduling of the outreach automation system.
Supports both cron (macOS/Linux) and Windows Task Scheduler.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

def get_project_path():
    """Get the absolute path to the project directory."""
    return Path(__file__).parent.parent.absolute()

def get_python_path():
    """Get the path to the current Python executable."""
    return sys.executable

def setup_cron_jobs():
    """Set up cron jobs for macOS/Linux."""
    project_path = get_project_path()
    python_path = get_python_path()
    
    cron_jobs = [
        # Run outreach automation every 4 hours during business days (9 AM, 1 PM, 5 PM)
        f"0 9,13,17 * * 1-5 cd {project_path} && {python_path} main.py --mode both",
        
        # Check responses every 2 hours
        f"0 */2 * * * cd {project_path} && {python_path} main.py --mode check-responses",
        
        # Daily status check at 8 AM
        f"0 8 * * 1-5 cd {project_path} && {python_path} main.py --mode status"
    ]
    
    print("Setting up cron jobs...")
    print("\nCron jobs to be added:")
    for job in cron_jobs:
        print(f"  {job}")
    
    # Get current crontab
    try:
        current_crontab = subprocess.run(
            ['crontab', '-l'], 
            capture_output=True, 
            text=True, 
            check=False
        ).stdout
    except FileNotFoundError:
        print("Error: crontab command not found. Please ensure cron is installed.")
        return False
    
    # Add new jobs
    new_crontab = current_crontab + "\n# Outreach Automation Jobs\n"
    for job in cron_jobs:
        new_crontab += job + "\n"
    
    # Install new crontab
    try:
        process = subprocess.Popen(
            ['crontab', '-'],
            stdin=subprocess.PIPE,
            text=True
        )
        process.communicate(input=new_crontab)
        
        if process.returncode == 0:
            print("\n✅ Cron jobs installed successfully!")
            print("\nTo view your crontab: crontab -l")
            print("To edit your crontab: crontab -e")
            return True
        else:
            print("❌ Failed to install cron jobs")
            return False
            
    except Exception as e:
        print(f"❌ Error installing cron jobs: {e}")
        return False

def create_windows_batch_file():
    """Create batch files for Windows Task Scheduler."""
    project_path = get_project_path()
    python_path = get_python_path()
    
    batch_content = f"""@echo off
cd /d "{project_path}"
"{python_path}" main.py --mode both
"""
    
    batch_file = project_path / "run_outreach.bat"
    
    try:
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        
        print(f"✅ Created batch file: {batch_file}")
        return batch_file
        
    except Exception as e:
        print(f"❌ Error creating batch file: {e}")
        return None

def setup_windows_tasks():
    """Provide instructions for Windows Task Scheduler setup."""
    batch_file = create_windows_batch_file()
    
    if not batch_file:
        return False
    
    print("\n" + "="*60)
    print("WINDOWS TASK SCHEDULER SETUP INSTRUCTIONS")
    print("="*60)
    
    print(f"""
1. Open Task Scheduler (taskschd.msc)

2. Click "Create Basic Task..." in the right panel

3. Name: "Outreach Automation - Main"
   Description: "Run cold outreach automation system"

4. Trigger: Select "Daily"
   Start date: Today
   Start time: 09:00:00
   Recur every: 1 days

5. Action: Select "Start a program"
   Program/script: {batch_file}
   Start in: {get_project_path()}

6. Click "Finish"

7. Right-click the new task and select "Properties"

8. In the "Triggers" tab, click "Edit" and then "Advanced settings"
   Check "Repeat task every: 4 hours"
   For a duration of: 1 day

9. In the "Conditions" tab:
   Uncheck "Start the task only if the computer is on AC power"
   
10. Click "OK" to save

REPEAT steps 2-10 for checking responses:
- Name: "Outreach Automation - Check Responses"  
- Change the batch file content to: "{get_python_path()}" main.py --mode check-responses
- Set to repeat every 2 hours instead of 4
""")
    
    print("\n✅ Windows setup instructions provided above")
    return True

def main():
    """Main setup function."""
    print("Outreach Automation Scheduler Setup")
    print("="*40)
    
    system = platform.system().lower()
    
    if system in ['linux', 'darwin']:  # Linux or macOS
        print(f"Detected system: {system.capitalize()}")
        print("Setting up cron jobs...")
        
        if setup_cron_jobs():
            print("\n🎉 Automation scheduling setup complete!")
            print("\nYour outreach automation will now run:")
            print("  - Every 4 hours during business days (9 AM, 1 PM, 5 PM)")
            print("  - Response checking every 2 hours")
            print("  - Daily status report at 8 AM")
        else:
            print("\n❌ Failed to set up automated scheduling")
            
    elif system == 'windows':
        print("Detected system: Windows")
        print("Setting up Windows Task Scheduler...")
        
        if setup_windows_tasks():
            print("\n🎉 Windows setup instructions provided!")
            print("Please follow the instructions above to complete the setup.")
        else:
            print("\n❌ Failed to create Windows setup files")
            
    else:
        print(f"❌ Unsupported system: {system}")
        print("Please set up automation manually using your system's scheduler.")
    
    print(f"\nProject location: {get_project_path()}")
    print(f"Python executable: {get_python_path()}")

if __name__ == "__main__":
    main() 
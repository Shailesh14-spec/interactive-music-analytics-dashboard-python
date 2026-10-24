"""Run every portfolio analysis and fail if any project fails."""
from pathlib import Path
import subprocess
import sys
for script in sorted(Path(__file__).resolve().parent.glob('*/analysis.py')):
    print(f'Running {script.parent.name}', flush=True)
    subprocess.run([sys.executable, str(script)], check=True)

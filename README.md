# Cache Organization and Policy Simulation

This project simulates cache behavior and compares policies using various access patterns.

## Setup

1. Create and activate a Python virtual environment (recommended):
   ```sh
   python -m venv .venv
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   ```

2. Install required packages:
   ```sh
   pip install -r requirements.txt
   ```

## Running

- **Main analysis:**
  ```sh
  python main.py
  ```
  This will print statistics and ensure a `results/` directory is created for outputs.

- **Detailed plotting:**
  ```sh
  python analysis.py
  ```
  The script creates `results/simulation_results.csv` and saves plots under `results/`.

- **Web Dashboard:**
  ```sh
  python backend/app.py
  ```
  Open `http://localhost:5000` in your browser to access the interactive dashboard.

## Notes

- A `results` folder is automatically created if missing.
- Ensure the virtual environment is selected in VS Code to avoid import errors with pandas, numpy, and matplotlib.

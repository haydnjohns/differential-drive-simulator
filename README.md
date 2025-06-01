**Author:** Haydn Johns  
**Date:** 2025-05-31

A Python-based simulator for visualizing and debugging differential drive robot movements.  
This tool provides a real-time visual interface to test movement instructions using left, right, or both wheels, and includes a variety of interactive features for inspection and control.

---

## Features

- Forward and backward movement with left, right, or both wheels
- Visual display of:
  - Robot path
  - Heading direction
  - Axle location
  - Turn points
  - Initial position and global origin
- Interactive controls:
  - `Space`: Play / Pause
  - `[` and `]`: Scrub back and forward one frame at a time (hold for faster scrubbing)
  - Arrow keys: Pan the view
  - `+` / `-`: Zoom in and out
  - `0`: Reset view to fit path
  - `Esc`: Exit simulator

---

## Project Structure

```
differential-drive-simulator/
│
├── src/
│   ├── run_simulator.py           # Entry point for running the simulation (user inputs go here)
│   └── simulator.py               # Simulation engine and rendering logic
├── assets/
│   └── example_simulation.gif     # Animated gif of simulation features
│
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## Getting Started

### 1. Clone the repository:

```bash
git clone https://github.com/haydnjohns/differential-drive-simulator.git ~/differential-drive-simulator/
```

### 2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

### 3. Install dependencies:

```bash
pip install -r requirements.txt
```

### 4. Run the simulator:

```bash
python src/run_simulator.py
```

---

## Requirements

- Python 3.7+
- Pygame

(Install via `requirements.txt`)

---

## Notes

- All simulation parameters (initial position, movement commands, display options) are defined in `run_simulator.py`.
- The rendering and logic code is abstracted into `simulator.py` to keep user inputs separate from backend logic.

---

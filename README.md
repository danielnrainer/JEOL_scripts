# TEM Scripts Collection

A collection of Python scripts/apps/utilities designed for automating and enhancing workflows with Rigaku Synergy-ED instruments and JEOL TEMs. This repository contains various standalone utilities designed to simplify common tasks in electron microscopy.

## Requirements

- Python 3.8 (higher not tested)
- PyJEM (not included - should be present on JEOL TEM PCs and Rigaku Synergy-ED PCs)
- Additional requirements per script (see individual .py files); global requirements.txt contains _all_ packages

## Installation

1. Clone this repository:
```bash
git clone https://github.com/danielnrainer/TEM-scripts.git
cd TEM-scripts
```

2. Install common dependencies:
```bash
pip install -r requirements.txt
```

Note: PyJEM must be installed separately as it comes with JEOL TEM systems.

## Scripts

- `beam_blank.py` - Control beam blanking on JEOL microscopes and Synergy-ED diffractometers
- `stage_loggr.py` - Logging script (CLI only) for stage positions of JEOL TEMs and Synergy-ED diffractometers

## Usage

Each script is standalone and can be run independently. Navigate to the script's directory and run it using Python:

```bash
python script_name.py
```

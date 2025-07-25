# Thesis Defense Scheduler

Automatic scheduling system for thesis defense sessions with GUI interface.

## Features

- Automatic defense scheduling with conflict detection
- Chairman assignment optimization
- Multiple export formats (CSV, JSON, PDF)
- User-friendly GUI interface

## Installation

1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   source .venv/bin/activate  # On Linux/Mac
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

## Project Structure

```
thesis-defense-scheduler/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore file
├── README.md              # This file
├── src/                   # Source code
│   ├── __init__.py
│   ├── models/            # Data models
│   │   ├── __init__.py
│   │   ├── person.py      # Person class
│   │   ├── defense.py     # Defense class
│   │   ├── room.py        # Room class
│   │   ├── time_slot.py   # TimeSlot class
│   │   └── session_parameters.py
│   ├── gui/               # GUI components
│   │   ├── __init__.py
│   │   ├── main_window.py # Main application window
│   │   ├── dialogs.py     # Dialog windows
│   │   ├── availability_dialog.py
│   │   └── parameters_dialog.py
│   ├── algorithm/         # Scheduling algorithms
│   │   ├── __init__.py
│   │   └── scheduler.py   # Main scheduling algorithm
│   └── utils/             # Utilities
│       ├── __init__.py
│       ├── validators.py  # Input validators
│       └── exporters.py   # Export functionality
├── tests/                 # Unit tests
│   └── __init__.py
├── data/                  # Data files
│   └── examples/          # Example data
└── docs/                  # Documentation
```

## Requirements

- **Defense duration**: 30 minutes
- **Max parallel defenses**: 2 (two rooms)
- **Chairman**: Selected automatically from available persons
- **Supervisor/Reviewer**: Assigned to each defense
- **Breaks**: User-defined only

## Development

### Running tests
```bash
pytest
```

### Git workflow
1. Create feature branch from `development`
2. Make changes and commit
3. Create Pull Request to `development`
4. After review, merge to `development`
5. Final release: merge `development` to `master`

## Authors

2-person student team project

## License

MIT
# TADA
Technology Engineering Computation Expansion Automated Data Annotation process


# ⚙️ Universal Mechanical Engineering Auto-Annotator

A production-grade, multi-modal automated data annotation pipeline built specifically for solo engineers. This framework completely eliminates manual labeling by programmatically analyzing mechanical engineering data structures and exporting AI-ready JSON notations.

---

## 🚀 Modality Infrastructure Coverage
The system auto-labels datasets across five core engineering domains:
1. **3D CAD Geometry**: Parses `.stl`, `.obj`, and `.ply` meshes to extract spatial profiles (e.g., shafts, brackets, plates).
2. **1D Sensor Telemetry**: Processes industrial vibration/pressure time-series `.csv` data using wave signal processing.
3. **2D Thermal Vision**: Segments gradient pixel intensities from infrared matrices to track structural hotspots.
4. **2D Technical Blueprints**: Automatically parses engineering drawings and extracts metadata markers (e.g., GD&T notes).
5. **Kinematic Robotics**: Tracks path coordinate variances to verify trajectory alignment and jitter errors.

---

## 🛠️ Installation & Setup

1. Clone this repository structure into your local development workspace.
2. Install the necessary system and engineering packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the default directory trees automatically by executing the program runner:
   ```bash
   python main.py
   ```

---

## 📂 Expected Directory Layout
Ensure your assets match the following repository structure:

```text
⚙️ mechanical-universal-auto-annotator/
│
├── 📁 config/
│   ├── 📄 taxonomy.json           # Unified master AI labels
│   └── 📄 threshold_rules.yaml    # Adjust design tolerances here
│
├── 📁 data/
│   ├── 📁 raw_ingest/             # Place raw engineering assets here
│   └── 📁 unified_labels/         # Output location for auto-generated JSONs
│
├── 📁 src/                        # Modular processing engines
│   ├── 📜 cad_parser.py
│   ├── 📜 telemetry_annotator.py
│   ├── 📜 thermal_vision.py
│   ├── 📜 blueprint_parser.py
│   └── 📜 kinematic_tracker.py
│
└── 📄 main.py                     # Main execution entry point
```

---

## 🎛️ Modifying Engineering Thresholds
To adjust the criteria for how parts are labeled without modifying any code, open `config/threshold_rules.yaml` and modify the parameters:

* Increase `min_aspect_ratio` if your shafts require tighter slender constraints.
* Tweak `brightness_threshold` to isolate hotspots at different thermal sensor limits.
* Modify `max_rms_vibration` to flag bearing faults at lower structural tolerances.

---

## 🏃 Execution Workflow
1. Place your engineering files into their respective subfolders within `data/raw_ingest/`.
2. Ensure file names follow standard naming rules:
   * Kinematic files must contain the word **"kinematic"** (e.g., `robot_kinematic_log.csv`).
   * Thermal images must contain the word **"thermal"** (e.g., `bearing_thermal.jpg`).
3. Run the master pipeline manager:
   ```bash
   python main.py
   ```
4. Find your individual file pairs and the global dataset index ledger (`master_five_modality_manifest.json`) ready inside `data/unified_labels/`.




   
# Pipeline setup and cross-modality execution documentation

# Documentation on rules, dependencies, and execution

# GitHub Repository Architecture

To scale an automated data annotation pipeline as a solo engineer, your GitHub repository must be structured like a production-grade data engineering application. It separates data assets, configuration logic, core geometric parsing, and export handlers.

```
⚙️ mechanical-cad-auto-annotator/
│
├── 📁 .github/
│   └── 📁 workflows/
│       └── 📄 data_validation.yml      # CI/CD pipeline to check annotation integrity
│
├── 📁 config/
│   ├── 📄 taxonomy.json                # Master engineering class names and IDs
│   └── 📄 threshold_rules.yaml         # Mathematical criteria for the rule engine
│
├── 📁 data/
│   ├── 📁 raw_cad/                     # Raw input 3D meshes (.stl, .obj, .ply)
│   └── 📁 annotated_outputs/           # Auto-generated JSON notations & COCO manifests
│
├── 📁 src/
│   ├── 📜 __init__.py
│   ├── 📜 geometry_extractor.py       # Mesh parsing, features, and inertial calculation
│   ├── 📜 rule_engine.py             # Classification logic using metadata thresholds
│   └── 📜 export_formatter.py          # Converts local JSON into AI-ready structures
│
├── 📄 .gitignore                       # Ensures large raw CAD files are not pushed to Git
├── 📄 main.py                          # Application entry point to execute bulk pipelines
├── 📄 README.md                        # Documentation on rules, dependencies, and execution
└── 📄 requirements.txt                 # Software library versions
```

Architectural Defense: Core Structural Design Choices

1. Decoupled Architecture (src/ Modularization)Defense: Separating geometry_extractor.py from rule_engine.py allows you to scale the pipeline independently. If you transition from 3D meshes (.stl) to Boundary Representation models (.step), you only rewrite the extractor module. The downstream rules evaluating structural traits remain untouched.

2.Declarative Rule Configurations (config/)Defense: Hardcoding geometric thresholds (e.g., volume < 5000) inside Python scripts creates technical debt. Moving thresholds to threshold_rules.yaml lets you tweak dimensions, tolerances, or aspect ratios instantly without altering code.

3. Strict Data Exclusion via .gitignoreDefense: CAD data catalogs can grow to gigabytes or terabytes. Storing large binary blobs directly in a standard Git repository degrades version control performance. The .gitignore file enforces that only script infrastructure is tracked, while massive datasets stay stored locally or within dedicated cloud object storage (e.g., AWS S3).

4. Automated CI/CD Data Checkers (.github/workflows/)Defense: As a solo engineer, you need automated unit testing. GitHub Actions run whenever you change a rule, automatically ensuring that newly generated annotation schemas do not violate your master taxonomy.json indexing file.
#

 To automate data annotation across the entire mechanical engineering lifecycle as a solo engineer, your architecture must scale beyond CAD models. It must ingest, process, and label sensor telemetry, thermal camera feeds, and 2D engineering drawings simultaneously.Here is the complete production-grade GitHub architecture and the multi-modal automation code to execute it without a team.


 # Complete Multi-Modal GitHub Architecture
 ```
⚙️ mechanical-universal-auto-annotator/
│
├── 📁 .github/workflows/
│   └── 📄 integration_data_check.yml    # Validates data sync across sensors/images
│
├── 📁 config/
│   ├── 📄 mechanical_taxonomy.json       # Master IDs for parts, faults, and anomalies
│   └── 📄 engineering_thresholds.yaml    # Signal rules, stress tolerances, and temperature limits
│
├── 📁 data/
│   ├── 📁 raw_ingest/
│   │   ├── 📁 cad_geometry/             # .STL, .OBJ mesh designs
│   │   ├── 📁 sensor_telemetry/          # .CSV vibration, pressure, tachometer logs
│   │   ├── 📁 thermal_vision/            # .TIFF, .JPG infrared captures
│   │   └── └── 📁 technical_blueprints/    # .PDF, .DXF 2D design layouts
│   └── 📁 unified_labels/               # Automated multi-modal JSON/COCO outputs
│
├── 📁 src/
│   ├── 📜 __init__.py
│   ├── 📜 pipeline_coordinator.py       # Master entry engine mapping multi-modal streams
│   ├── 📜 cad_segmenter.py              # Extends 3D geometry features and mass properties
│   ├── 📜 telemetry_annotator.py        # Processes frequency bands and isolates faults
│   ├── 📜 thermal_computer_vision.py    # Detects heat patterns and gradient hotspots
│   └── 📜 blueprint_parser.py           # Extracts bounding vectors from 2D engineering sheets
│
├── 📄 main.py                           # Single command-line trigger to parse all data
├── 📄 README.md                         # Pipeline setup and cross-modality execution documentation
└── 📄 requirements.txt                  # Package dependencies (opencv, trimesh, scipy, pandas)

```
Architectural Defense: Multi-Modal Design Choices

Centralized Taxonomy Engine (config/mechanical_taxonomy.json)Defense: An anomaly must mean the same thing across all data domains. For example, if a bearing fails, the 3D model identifies the part location, the sensor log flags high-frequency acceleration, and the thermal image detects a heat spike. A unified taxonomy ensures all three distinct data pipelines map to the exact same label ID, allowing you to train multi-modal AI models later.

Streaming Pipeline Isolation (src/)Defense: Separating the processing code into modules prevents a failure in one data type from breaking the others. If a 2D blueprint file is corrupted, the sensor telemetry and 3D CAD loops continue running uninterrupted.

Decoupled Data Pipeline WorkflowsDefense: Time-series files (sensors) require statistical wave transformations, while thermal images require color-gradient spatial matrices. Isolating these parsers ensures your codebase remains lightweight and easy to maintain by a single developer.

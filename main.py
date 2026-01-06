import FreeCAD as App
import FreeCADGui as Gui
import os, csv, yaml, subprocess
from glob import glob
import ImportGui

# -----------------------------
# 1. Detect project folder
# -----------------------------
def find_project_yaml(doc_path=None):
    if doc_path is None:
        doc_path = App.ActiveDocument.FileName
    project_root = os.path.dirname(doc_path)
    yaml_path = os.path.join(project_root, "project.yaml")
    if os.path.exists(yaml_path):
        return project_root, yaml_path
    else:
        raise FileNotFoundError("project.yaml not found in project folder")

# -----------------------------
# 2. Load YAML config
# -----------------------------
def load_project_config(yaml_path):
    with open(yaml_path) as f:
        return yaml.safe_load(f)

# -----------------------------
# 3. Load CSVs into `data`
# -----------------------------
def load_csvs(data_dir, default_row=0):
    data = {}
    for root, dirs, files in os.walk(data_dir):
        for f in files:
            if f.endswith('.csv'):
                fname = os.path.splitext(f)[0]
                fpath = os.path.join(root, f)
                with open(fpath) as csvfile:
                    reader = list(csv.DictReader(csvfile))
                    data[fname] = reader
    return data, default_row

# -----------------------------
# 4. Access CSV parameter
# -----------------------------
def get_param(data, name, default_row=0):
    import re
    m = re.match(r"(\w+)\.(\w+)(?:\[(\d+)\])?", name)
    if not m:
        raise ValueError(f"Invalid param {name}")
    file, col, row = m.groups()
    row = int(row) if row else default_row
    return float(data[file][row][col])

# -----------------------------
# 5. Git info
# -----------------------------
def get_git_info(path):
    try:
        branch = subprocess.check_output(
            ['git', '-C', path, 'rev-parse', '--abbrev-ref', 'HEAD']
        ).decode().strip()
        commit = subprocess.check_output(
            ['git', '-C', path, 'rev-parse', '--short', 'HEAD']
        ).decode().strip()
        return branch, commit
    except:
        return None, None

# -----------------------------
# 6. Load subparts
# -----------------------------
def load_subparts(parts_dir):
    fcstd_files = glob(os.path.join(parts_dir, '**', '*.fcstd'), recursive=True)
    for f in fcstd_files:
        App.open(f)  # opens subpart as separate doc; optionally use ShapeBinder in main

# -----------------------------
# 7. Export STEP to meshes/
# -----------------------------
def export_meshes(meshes_dir):
    doc = App.ActiveDocument
    if not os.path.exists(meshes_dir):
        os.makedirs(meshes_dir)
    for obj in doc.Objects:
        if obj.TypeId.startswith("Part::") or obj.TypeId.startswith("PartDesign::Body"):
            step_path = os.path.join(meshes_dir, f"{obj.Name}.STEP")
            ImportGui.export([obj], step_path)

# -----------------------------
# 8. Main project loader
# -----------------------------
def load_project():
    doc_path = App.ActiveDocument.FileName
    project_root, yaml_path = find_project_yaml(doc_path)
    cfg = load_project_config(yaml_path)

    # CSVs
    data_dir = os.path.join(project_root, cfg['data_dir'])
    data, default_row = load_csvs(data_dir, cfg.get('default_row', 0))

    # Git info
    branch, commit = get_git_info(project_root)
    print(f"Project: {cfg['project_name']} Branch: {branch} Commit: {commit}")

    # Subparts
    parts_dir = os.path.join(project_root, cfg['parts_dir'])
    load_subparts(parts_dir)

    # Mesh export
    meshes_dir = os.path.join(project_root, cfg['meshes_dir'])
    export_meshes(meshes_dir)

    return data, default_row

# -----------------------------
# Example usage
# -----------------------------
data, default_row = load_project()

# Access param like OpenSCAD
wheelbase = get_param(data, "chassis.Wheelbase")
arm_len = get_param(data, "suspension.ArmLength[2]")

print(f"Wheelbase: {wheelbase}, Arm length: {arm_len}")
import FreeCAD, FreeCADGui
from PySide2 import QtGui
import os

# Import main module
import ProjectManager

# -----------------------------
# Command wrappers
# -----------------------------
class LoadProjectCommand:
    """Load project YAML, CSVs, subparts, update spreadsheet"""
    def Activated(self):
        ProjectManager.load_project()
        FreeCAD.Console.PrintMessage("Project loaded.\n")

    def GetResources(self):
        return {
            'Pixmap': os.path.join(os.path.dirname(__file__), 'resources/load_icon.svg'),
            'MenuText': 'Load Project',
            'ToolTip': 'Load project YAML, CSVs, subparts, update spreadsheet'
        }

class RefreshCSVCommand:
    """Reload CSV files and update spreadsheet"""
    def Activated(self):
        doc = FreeCAD.ActiveDocument
        if doc is None:
            FreeCAD.Console.PrintError("No active document.\n")
            return
        # Reload project to refresh CSVs
        ProjectManager.load_project()
        FreeCAD.Console.PrintMessage("CSV data refreshed.\n")

    def GetResources(self):
        return {
            'Pixmap': os.path.join(os.path.dirname(__file__), 'resources/refresh_icon.svg'),
            'MenuText': 'Refresh CSV',
            'ToolTip': 'Reload CSV files and update spreadsheet parameters'
        }

class ExportMeshesCommand:
    """Export all parts to meshes folder"""
    def Activated(self):
        doc_path = FreeCAD.ActiveDocument.FileName
        project_root, yaml_path = ProjectManager.find_project_yaml(doc_path)
        cfg = ProjectManager.load_project_config(yaml_path)
        meshes_dir = os.path.join(project_root, cfg['meshes_dir'])
        ProjectManager.export_meshes(meshes_dir)
        FreeCAD.Console.PrintMessage(f"Meshes exported to {meshes_dir}\n")

    def GetResources(self):
        return {
            'Pixmap': os.path.join(os.path.dirname(__file__), 'resources/export_icon.svg'),
            'MenuText': 'Export Meshes',
            'ToolTip': 'Export all parts to meshes folder (STEP/STL)'
        }

# -----------------------------
# Workbench class
# -----------------------------
class ProjectManagerWorkbench(FreeCADGui.Workbench):
    MenuText = "ProjectManager"
    ToolTip = "Manage FreeCAD projects with YAML/CSV and Git integration"
    Icon = os.path.join(os.path.dirname(__file__), 'resources/pm_icon.svg')

    def Initialize(self):
        # Add commands
        self.appendToolbar("ProjectManager", ["LoadProject", "RefreshCSV", "ExportMeshes"])
        self.appendMenu("ProjectManager", ["LoadProject", "RefreshCSV", "ExportMeshes"])
        FreeCAD.Console.PrintMessage("ProjectManager Workbench loaded.\n")

    def Activated(self):
        pass

    def Deactivated(self):
        pass

# -----------------------------
# Register Workbench and commands
# -----------------------------
FreeCADGui.addCommand('LoadProject', LoadProjectCommand())
FreeCADGui.addCommand('RefreshCSV', RefreshCSVCommand())
FreeCADGui.addCommand('ExportMeshes', ExportMeshesCommand())
FreeCADGui.addWorkbench(ProjectManagerWorkbench())

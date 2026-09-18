import json
import os
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
from collections import Counter


class ManifestLogger:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.start_time = datetime.now()
        self.records: List[Dict[str, Any]] = []
 
#  TODO should refactor this function in to this -- 
#       def record_file(self, **kwargs):
#           self.records.append(kwargs)
    def record_file(
        self,
        final_filename: str,
        file_path: str,
        extension: str,
        source_template: str,
        corruption_label: str,
        character_corruption_label: str,
        extension_scrambled: bool = False,
        original_extension: str = "none",
        is_duplicate: bool = False,
        original_file: str = "none"
    ) -> None:
        """Logs metadata for an individual generated file."""
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

        entry = {
            "filename": final_filename,
            "extension": extension,
            "size_bytes": file_size,
            "source_template": os.path.basename(source_template),
            "is_structure_corrupted": corruption_label != "none",
            "structure_corruption_label": corruption_label,
            "is_character_corrupted": character_corruption_label != "none",
            "character_corruption_label": character_corruption_label,
            "extension_scrambled": extension_scrambled,
            "original_extension": original_extension,
            "is_duplicate": is_duplicate,
            "copied_from": os.path.basename(original_file) if original_file else None,
            "generated_at": datetime.now().isoformat()
        }
        self.records.append(entry)

    def _get_file_profile(self, record: dict) -> tuple:
        """Determines active modifications for a single file record."""
        active_mods = []
        
        if record.get("extension_scrambled"):
            active_mods.append("extension_scrambled")
            
        if record.get("structure_corruption_label") not in (None, "none", ""):
            active_mods.append("structure_corrupted")
            
        if record.get("character_corruption_label") not in (None, "none", ""):
            active_mods.append("character_corrupted")
            
        if record.get("is_duplicate"):
            active_mods.append("is_duplicate")
            
        return tuple(sorted(active_mods)) if active_mods else ("clean",)

    def generate_summary_metrics(self) -> dict:
        """Computes counts and combination stats from recorded files."""
        end_time = datetime.now()
        combo_counts = Counter(self._get_file_profile(r) for r in self.records)
        combo_summary = {" + ".join(combo): count for combo, count in combo_counts.items()}
        structural_corrupted_count = sum(1 for r in self.records if r["is_structure_corrupted"])
        character_corrupted_count = sum(1 for r in self.records if r["is_character_corrupted"])
        extension_scrambled = sum(1 for r in self.records if r["extension_scrambled"])
        duplicates = sum(1 for r in self.records if r["is_duplicate"])

        total_files = len(self.records)        # end_time = datetime.now()

        clean_files = combo_summary.get("clean", 0)
        
        file_type_counts = {}
        for record in self.records:
            extension = record["extension"]
            file_type_counts[extension] = file_type_counts.get(extension, 0) + 1

        return {
            "generated_at": self.start_time.isoformat(),
            "execution_duration_seconds": round((end_time - self.start_time).total_seconds(), 3),
            "total_records": total_files,
            "clean_records": clean_files,
            "total_modified_records": total_files - clean_files,
            "single_modification_records": sum(
                c for k, c in combo_summary.items()
                if k != "clean" and " + " not in k
            ),
            "multi_modification_records": sum(
                c for k, c in combo_summary.items() if " + " in k
            ),
            "individual_counts": {
                "character_corrupted_count": character_corrupted_count,
                "character_corruption_rate": round(character_corrupted_count / total_files, 2) if total_files > 0 else 0.0,
                "structure_corrupted_count": structural_corrupted_count,
                "structural_corruption_rate": round(structural_corrupted_count / total_files, 2) if total_files > 0 else 0.0,
                "extension_scrambled_count": extension_scrambled,
                "extension_scrambled_rate": round(extension_scrambled / total_files, 2) if total_files > 0 else 0.0,
                "duplicate_count": duplicates,
                "duplicate_rate": round(duplicates / total_files, 2) if total_files > 0 else 0.0,
                "file_type_counts": file_type_counts
            },
            "combinations_breakdown": combo_summary,
        }



    def save_manifest(self, manifest_name: str = "manifest.json") -> str:
        """Calculates batch stats and writes the JSON manifest to the output directory."""

        summary_metrics = self.generate_summary_metrics()
        manifest_data = {
            "title": "Dirty Dataset Manifest",
            "description": ("Metadata for a batch of synthetic dirty files.",
                            "File type counts reflect the original type, before",
                            "the scrambled extension modification is applied"
                            ),
            "batch_metadata": summary_metrics,
            "files": self.records
        }

        manifest_path = os.path.join(self.output_dir, "metadata", manifest_name)
        manifest = Path(manifest_path) 
 
        if not manifest.exists():
            manifest.parent.mkdir(parents=True, exist_ok=True)
            
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=4)
            
        return manifest_path
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path


class ManifestLogger:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.start_time = datetime.now()
        self.records: List[Dict[str, Any]] = []

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

    def save_manifest(self, manifest_name: str = "manifest.json") -> str:
        """Calculates batch stats and writes the JSON manifest to the output directory."""
        end_time = datetime.now()
        total_files = len(self.records)
        structural_corrupted_count = sum(1 for r in self.records if r["is_structure_corrupted"])
        character_corrupted_count = sum(1 for r in self.records if r["is_character_corrupted"])
        corrupted_count = structural_corrupted_count + character_corrupted_count
        clean_count = total_files - corrupted_count
        duplicated_count = sum(1 for r in self.records if r["is_duplicate"])
        scrambled_count = sum(1 for r in self.records if r["extension_scrambled"])
        
        file_type_counts = {}
        for record in self.records:
            extension = record["extension"]
            file_type_counts[extension] = file_type_counts.get(extension, 0) + 1

        manifest_data = {
            "title": "Dirty Dataset Manifest",
            "description": ("Metadata for a batch of synthetic dirty files.",
                            "File type counts reflect the original type, before",
                            "the scrambled extension modification is applied"
                            ),
            "batch_metadata": {
                "generated_at": self.start_time.isoformat(),
                "execution_duration_seconds": round((end_time - self.start_time).total_seconds(), 3),
                "total": total_files,
                "clean_count": clean_count,
                "scrambled_extensions": scrambled_count,
                "scrambled_rate": round(scrambled_count / total_files, 2) if total_files > 0 else 0.0,
                "structural_corrupted_count": corrupted_count,
                "structural_corruption_rate": round(corrupted_count / total_files, 2) if total_files > 0 else 0.0,
                "character_corrupted_count": corrupted_count,
                "character_corruption_rate": round(corrupted_count / total_files, 2) if total_files > 0 else 0.0,
                "duplicated_count": duplicated_count,
                "duplicated_rate": round(duplicated_count / total_files, 2) if total_files > 0 else 0.0,
                "file_type_counts": file_type_counts
            },
            "files": self.records
        }

        manifest_path = os.path.join(self.output_dir, "metadata", manifest_name)
        manifest = Path(manifest_path) 
        
        if not manifest.exists():
            manifest.parent.mkdir(parents=True, exist_ok=True)
            
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=4)
            
        return manifest_path
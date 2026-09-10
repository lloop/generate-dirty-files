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
        mutation_label: str,
        is_duplicate: bool = False,
        original_file: str = "none"
    ) -> None:
        """Logs metadata for an individual generated file."""
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

        entry = {
            "filename": final_filename,
            # "relative_path": os.path.relpath(file_path, self.output_dir),
            "extension": extension,
            "size_bytes": file_size,
            "source_template": os.path.basename(source_template),
            "is_corrupted": mutation_label != "none",
            "mutation_label": mutation_label,
            "is_duplicate": is_duplicate,
            "copied_from": os.path.basename(original_file) if original_file else None,
            "generated_at": datetime.now().isoformat()
        }
        self.records.append(entry)

    def save_manifest(self, manifest_name: str = "manifest.json") -> str:
        """Calculates batch stats and writes the JSON manifest to the output directory."""
        end_time = datetime.now()
        total_files = len(self.records)
        corrupted_count = sum(1 for r in self.records if r["is_corrupted"])
        clean_count = total_files - corrupted_count
        duplicated_count = sum(1 for r in self.records if r["is_duplicate"])

        manifest_data = {
            "batch_metadata": {
                "generated_at": self.start_time.isoformat(),
                "execution_duration_seconds": round((end_time - self.start_time).total_seconds(), 3),
                "total_files": total_files,
                "clean_files_count": clean_count,
                "corrupted_files_count": corrupted_count,
                "corruption_rate": round(corrupted_count / total_files, 2) if total_files > 0 else 0.0,
                "duplicated_files_count": duplicated_count,
                "duplicated_rate": round(duplicated_count / total_files, 2) if total_files > 0 else 0.0
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
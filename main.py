import os
import random
import shutil
from pathlib import Path
from data_modifiers.generate_title import generate_title
from data_modifiers.alter_content import alter_content
from manifest_builder import ManifestLogger

from config import OUT_DIRECTORY, TEMPLATES_DIRECTORY, AMOUNT_OF_FILES

PERCENT_DUPLICATE = 0.05

class MasterDataGenerator:
    def __init__(self, templates_dir: str = "base_templates"):

        self.templates_dir = templates_dir
        self.title_generator = generate_title
        self.content_modifier = alter_content 

        # Map available extensions to their template source file path
        self.template_map = self._load_templates()

    def _load_templates(self) -> dict:
        """
        Scans base_templates directory and maps each unique extension
        to its template path (e.g., {'.txt': 'base_templates/base_txt.txt'}).
        """
        if not os.path.exists(self.templates_dir):
            raise FileNotFoundError(
                f"Templates directory '{self.templates_dir}' not found."
            )

        template_map = {}
        for filename in os.listdir(self.templates_dir):
            full_path = os.path.join(self.templates_dir, filename)
            if os.path.isfile(full_path):
                _, ext = os.path.splitext(filename)
                ext = ext.lower()
                if ext:
                    template_map[ext] = full_path

        if not template_map:
            raise ValueError(
                f"No valid template files found in '{self.templates_dir}'."
            )

        print(
            f"[*] Found templates for extensions: {list(template_map.keys())}"
        )
        return template_map

    def generate_batch(
        self,
        output_dir: str = "output", 
        total_files: int = 20
    ):
        """
        Generates a batch of synthetic files by randomly picking extensions
        from available base templates, altering titles, mutating content,
        and optionally creating duplicates.
        """
        
        # Create the output directory. delete previous output if it exists
        files = Path(output_dir)
        if files.exists():
            shutil.rmtree(output_dir)
        files.mkdir()

        available_extensions = list(self.template_map.keys())

        generated_count = 0
        duplicate_count = 0
        
        # Initialize manifest logger
        manifest = ManifestLogger(output_dir=output_dir)

        print(f"[*] Generating {total_files} synthetic files in '{output_dir}'...")
        
        generated_paths = []

        # for i in range(1, total_files + 1):
        while generated_count < total_files:
            # 1. Randomly choose an extension from discovered base templates
            chosen_ext = random.choice(available_extensions)
            template_path = self.template_map[chosen_ext]

            # 2. Generate a title with random alterations
            final_filename = self.title_generator(
                available_extensions=[chosen_ext]
            )

            # 3. Copy base template content to destination output file
            dest_path = os.path.join(output_dir, final_filename)
            shutil.copyfile(template_path, dest_path)

            # 4. Apply content corruption in-placemodifiers
            mutation_label = self.content_modifier(
                dest_path
            )

            generated_count += 1

            # 6. Duplicate (optionally creates duplicate files)
            if generated_count < total_files and random.random() < PERCENT_DUPLICATE:
                stem, ext = os.path.splitext(final_filename)
                dup_suffix = random.choice(["_copy", " (1)", "_v2", "_backup"])
                dup_filename = f"{stem}{dup_suffix}{ext}"
                dup_path = os.path.join(output_dir, dup_filename)

                # Copy already mutated or clean file as duplicate
                shutil.copyfile(dest_path, dup_path)

                # Not sure I want this.
                # 50% chance duplicate content gets additional corruption
                # if random.random() < 0.5:
                #     self.content_modifier(
                #         dup_path
                #     )
                
                generated_count += 1
                duplicate_count += 1
                print(f"    [++] Created duplicate: {dup_filename}")
                
                # Log the duplicate to manifest
                manifest.record_file(
                    final_filename=dup_filename,
                    file_path=dup_path,
                    extension=chosen_ext,
                    source_template=template_path,
                    mutation_label=mutation_label,
                    is_duplicate=True,
                    original_file=dest_path
                )
                
            # 7. Log to manifest
            manifest.record_file(
                final_filename=final_filename,
                file_path=dest_path,
                extension=chosen_ext,
                source_template=template_path,
                mutation_label=mutation_label,
                is_duplicate=False,
                original_file="none"
            )
        
            generated_paths.append(dest_path)
            
        # Save manifest.json to the output folder
        manifest_file = manifest.save_manifest()

        print(
            f"[✔] Batch generation complete: {generated_count} files generated, "
            f"{duplicate_count} duplicates created."
            f"Manifest written to: {manifest_file}"
        )


if __name__ == "__main__":
    corruptor = MasterDataGenerator(templates_dir=TEMPLATES_DIRECTORY)

    corruptor.generate_batch(
        output_dir=OUT_DIRECTORY,
        total_files=AMOUNT_OF_FILES
    )
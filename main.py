import argparse
import os
import random
import shutil
import uuid
from pathlib import Path

from config import (
    AMOUNT_OF_FILES,
    OUT_DIRECTORY,
    PERCENT_CHAR_CORRUPT,
    PERCENT_CORRUPTION,
    PERCENT_DUPLICATE,
    PERCENT_EXTENSION_SCRAMBLE,
    TEMPLATES_DIRECTORY,
)
from data_modifiers.character_modifier import CharacterModifier
from data_modifiers.extension_scrambler import scramble_extension
from data_modifiers.generate_title import generate_title
from data_modifiers.handlers.registry import HandlerRegistry
from manifest_builder import ManifestLogger
from models.file_record import FileRecord


class MasterDataGenerator:

    def __init__(self, templates_dir: str = TEMPLATES_DIRECTORY):
        self.templates_dir = templates_dir
        self.title_generator = generate_title
        self.registry = HandlerRegistry()
        self.char_modifier = CharacterModifier()
        self.template_map = self._load_templates()

    def _load_templates(self) -> dict:
        """Scans base_templates directory and maps each unique extension

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
        self, output_dir: str = "output", total_files: int = 20
    ):
        """Generates a batch of synthetic files by randomly picking extensions

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
        extension_scrambled_count = 0
        corrupted_count = 0
        character_corrupted_count = 0
        duplicate_count = 0

        # Initialize manifest logger
        manifest = ManifestLogger(output_dir=output_dir)

        print(
            f"[*] Generating {total_files} synthetic files in"
            f" '{output_dir}'..."
        )

        generated_paths = []

        while generated_count < total_files:
            # Randomly choose an extension from discovered base templates
            chosen_ext = random.choice(available_extensions)
            template_path = self.template_map[chosen_ext]

            # Generate a title with random alterations
            final_filename = self.title_generator(
                available_extensions=[chosen_ext]
            )

            # Resolve unique destination path before writing
            raw_dest_path = os.path.join(output_dir, final_filename)
            dest_path = self._get_unique_path(raw_dest_path)

            # Check extension mode before reading
            is_binary = chosen_ext.lower() in [
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".ico",
            ]
            read_mode = "rb" if is_binary else "r"
            write_mode = "wb" if is_binary else "w"
            encoding = None if is_binary else "utf-8"

            # Read base template content
            with open(
                template_path,
                read_mode,
                encoding=encoding,
                errors=None if is_binary else "ignore",
            ) as f:
                template_content = f.read()

            # Instantiate the state-tracking model
            file_record = FileRecord(
                unique_token=uuid.uuid4().hex[:8],
                original_filename=os.path.basename(dest_path),
                original_extension=chosen_ext,
                content=template_content,
                is_binary=is_binary,
            )

            # Random extension scrambler
            extension_scrambled = False
            if random.random() < PERCENT_EXTENSION_SCRAMBLE:
                extension_scrambled = True
                dest_path = scramble_extension(Path(dest_path))
                final_filename = os.path.basename(dest_path)
                extension_scrambled_count += 1

            file_record.output_filename = final_filename
            file_record.extension_scrambled = extension_scrambled

            # Fetch the dedicated handler for this format
            handler = self.registry.get_handler(chosen_ext, is_binary=is_binary)

            # Add Unique Entropy
            file_record.content = handler.add_unique_entropy(
                file_record.content, token=file_record.unique_token
            )

            # Structural Corruption Pass
            mutation = (
                "auto" if random.random() < PERCENT_CORRUPTION else "none"
            )
            if mutation == "auto":
                corrupted_count += 1

            file_record.content, corruption_label = handler.corrupt_structure(
                file_record.content, mutation_type=mutation
            )
            file_record.structural_mutation = corruption_label

            # Character Corruption Pass
            char_label = "none"
            if not is_binary and isinstance(file_record.content, str):
                if random.random() < PERCENT_CHAR_CORRUPT:
                    file_record.content, char_label = self.char_modifier.corrupt_character_encoding(
                        file_record.content
                    )   
                    character_corrupted_count += 1
            file_record.character_mutation = char_label

            # Finalize SHA-256 and byte sizes before disk write
            file_record.finalize_content(file_record.content)

            # Write final content to disk ONCE
            with open(dest_path, write_mode, encoding=encoding) as f:
                f.write(file_record.content)

            str_dest_path = str(dest_path)

            generated_count += 1

            # Duplicate file creation
            if (
                generated_count < total_files
                and random.random() < PERCENT_DUPLICATE
            ):
                stem, ext = os.path.splitext(final_filename)
                dup_suffix = random.choice(["_copy", " (1)", "_v2", "_backup"])
                dup_filename = f"{stem}{dup_suffix}{ext}"

                # Resolve unique duplicate destination path before copying
                raw_dup_path = os.path.join(output_dir, dup_filename)
                dup_path = self._get_unique_path(raw_dup_path)
                dup_filename = os.path.basename(dup_path)

                # Copy already mutated or clean file as duplicate
                shutil.copyfile(dest_path, dup_path)

                generated_count += 1
                duplicate_count += 1
                print(f"    [++] Created duplicate: {dup_filename}")

                # Log the duplicate to manifest
                manifest.record_file(
                    final_filename=dup_filename,
                    file_path=dup_path,
                    extension=chosen_ext,
                    source_template=template_path,
                    corruption_label=corruption_label,
                    character_corruption_label=char_label,
                    extension_scrambled=extension_scrambled,
                    original_extension=(
                        chosen_ext if extension_scrambled else "none"
                    ),
                    is_duplicate=True,
                    original_file=str_dest_path,
                )

            # Log to manifest
            manifest.record_file(
                final_filename=final_filename,
                file_path=str_dest_path,
                extension=chosen_ext,
                source_template=template_path,
                corruption_label=corruption_label,
                character_corruption_label=char_label,
                extension_scrambled=extension_scrambled,
                original_extension=(
                    chosen_ext if extension_scrambled else "none"
                ),
                is_duplicate=False,
                original_file="none",
            )

            generated_paths.append(dest_path)

        # Save manifest.json to the output folder
        manifest_file = manifest.save_manifest()

        print(
            f"--------------------------------------------------"
            f"\nBatch generation complete: {generated_count} files generated, "
            f"\n{extension_scrambled_count} scrambled extensions created."
            f"\n{corrupted_count} corrupted structures created."
            f"\n{character_corrupted_count} corrupted characters created."
            f"\n{duplicate_count} duplicates created."
            f"\nManifest written to: {manifest_file}"
        )

    def _get_unique_path(self, dest_path: str) -> str:
        """Ensures file writes never overwrite existing generated files."""
        path = Path(dest_path)
        if not path.exists():
            return str(path)

        stem, ext = path.stem, path.suffix
        counter = 1
        while path.exists():
            path = path.with_name(f"{stem}_{counter}{ext}")
            counter += 1
        return str(path)


if __name__ == "__main__":

    # Add command line arguments for output_directory and amount_of_files
    parser = argparse.ArgumentParser(
        description="Generate synthetic dirty dataset batches."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=OUT_DIRECTORY,
        help="Path to output directory (default: defined in config.py)",
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=AMOUNT_OF_FILES,
        help="Number of synthetic files to generate",
    )
    args = parser.parse_args()

    corruptor = MasterDataGenerator()
    corruptor.generate_batch(output_dir=args.output, total_files=args.count)
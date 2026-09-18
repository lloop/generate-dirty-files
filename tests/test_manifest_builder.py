# tests/test_manifest_logger.py
import json
import os
from pathlib import Path

import pytest

from manifest_logger import ManifestLogger  # adjust import to actual module path


@pytest.fixture
def logger(tmp_path):
    return ManifestLogger(output_dir=str(tmp_path))


class TestRecordFile:
    def test_appends_one_record(self, logger, tmp_path):
        f = tmp_path / "invoice.txt"
        f.write_text("hello")
        logger.record_file(
            final_filename="invoice.txt",
            file_path=str(f),
            extension=".txt",
            source_template="templates/invoice_template.txt",
            corruption_label="none",
            character_corruption_label="none",
        )
        assert len(logger.records) == 1

    def test_computes_real_file_size(self, logger, tmp_path):
        f = tmp_path / "data.csv"
        f.write_text("a,b,c\n1,2,3\n")
        logger.record_file(
            final_filename="data.csv",
            file_path=str(f),
            extension=".csv",
            source_template="template.csv",
            corruption_label="none",
            character_corruption_label="none",
        )
        assert logger.records[0]["size_bytes"] == os.path.getsize(f)
        assert logger.records[0]["size_bytes"] > 0

    def test_missing_file_reports_zero_size(self, logger):
        logger.record_file(
            final_filename="ghost.txt",
            file_path="/nonexistent/path/ghost.txt",
            extension=".txt",
            source_template="template.txt",
            corruption_label="none",
            character_corruption_label="none",
        )
        assert logger.records[0]["size_bytes"] == 0

    def test_source_template_is_basenamed(self, logger, tmp_path):
        f = tmp_path / "a.txt"
        f.write_text("x")
        logger.record_file(
            final_filename="a.txt",
            file_path=str(f),
            extension=".txt",
            source_template="/deep/nested/path/template.txt",
            corruption_label="none",
            character_corruption_label="none",
        )
        assert logger.records[0]["source_template"] == "template.txt"

    def test_structure_corruption_flag_true_when_label_not_none(self, logger, tmp_path):
        f = tmp_path / "a.txt"
        f.write_text("x")
        logger.record_file(
            final_filename="a.txt",
            file_path=str(f),
            extension=".txt",
            source_template="t.txt",
            corruption_label="row_shuffle",
            character_corruption_label="none",
        )
        record = logger.records[0]
        assert record["is_structure_corrupted"] is True
        assert record["structure_corruption_label"] == "row_shuffle"

    def test_structure_corruption_flag_false_when_label_none(self, logger, tmp_path):
        f = tmp_path / "a.txt"
        f.write_text("x")
        logger.record_file(
            final_filename="a.txt",
            file_path=str(f),
            extension=".txt",
            source_template="t.txt",
            corruption_label="none",
            character_corruption_label="none",
        )
        assert logger.records[0]["is_structure_corrupted"] is False

    def test_character_corruption_flag_true_when_label_not_none(self, logger, tmp_path):
        f = tmp_path / "a.txt"
        f.write_text("x")
        logger.record_file(
            final_filename="a.txt",
            file_path=str(f),
            extension=".txt",
            source_template="t.txt",
            corruption_label="none",
            character_corruption_label="mojibake",
        )
        record = logger.records[0]
        assert record["is_character_corrupted"] is True
        assert record["character_corruption_label"] == "mojibake"

    def test_defaults_for_optional_params(self, logger, tmp_path):
        f = tmp_path / "a.txt"
        f.write_text("x")
        logger.record_file(
            final_filename="a.txt",
            file_path=str(f),
            extension=".txt",
            source_template="t.txt",
            corruption_label="none",
            character_corruption_label="none",
        )
        record = logger.records[0]
        assert record["extension_scrambled"] is False
        assert record["original_extension"] == "none"
        assert record["is_duplicate"] is False
        assert record["copied_from"] is "none"

    def test_copied_from_is_basenamed_when_provided(self, logger, tmp_path):
        f = tmp_path / "a.txt"
        f.write_text("x")
        logger.record_file(
            final_filename="a.txt",
            file_path=str(f),
            extension=".txt",
            source_template="t.txt",
            corruption_label="none",
            character_corruption_label="none",
            is_duplicate=True,
            original_file="/some/dir/original.txt",
        )
        assert logger.records[0]["copied_from"] == "original.txt"
        assert logger.records[0]["is_duplicate"] is True

    def test_copied_from_none_when_original_file_is_literal_string_none(self, logger, tmp_path):
        # Default sentinel is the string "none", which is truthy, so
        # `os.path.basename("none")` runs and returns "none" -- it does NOT
        # collapse to Python None unless original_file is falsy (e.g. "").
        f = tmp_path / "a.txt"
        f.write_text("x")
        logger.record_file(
            final_filename="a.txt",
            file_path=str(f),
            extension=".txt",
            source_template="t.txt",
            corruption_label="none",
            character_corruption_label="none",
        )
        assert logger.records[0]["copied_from"] == "none"

    def test_generated_at_is_present_and_iso_formatted(self, logger, tmp_path):
        f = tmp_path / "a.txt"
        f.write_text("x")
        logger.record_file(
            final_filename="a.txt",
            file_path=str(f),
            extension=".txt",
            source_template="t.txt",
            corruption_label="none",
            character_corruption_label="none",
        )
        from datetime import datetime
        # Should not raise
        datetime.fromisoformat(logger.records[0]["generated_at"])

    def test_multiple_records_accumulate_in_order(self, logger, tmp_path):
        for name in ["a.txt", "b.txt", "c.txt"]:
            f = tmp_path / name
            f.write_text("x")
            logger.record_file(
                final_filename=name,
                file_path=str(f),
                extension=".txt",
                source_template="t.txt",
                corruption_label="none",
                character_corruption_label="none",
            )
        assert [r["filename"] for r in logger.records] == ["a.txt", "b.txt", "c.txt"]


class TestSaveManifest:
    def _add_record(self, logger, tmp_path, name, corruption="none", char_corruption="none",
                     scrambled=False, duplicate=False, ext=".txt"):
        f = tmp_path / name
        f.write_text("x")
        logger.record_file(
            final_filename=name,
            file_path=str(f),
            extension=ext,
            source_template="t" + ext,
            corruption_label=corruption,
            character_corruption_label=char_corruption,
            extension_scrambled=scrambled,
            is_duplicate=duplicate,
        )

    def test_creates_metadata_directory_and_file(self, logger, tmp_path):
        self._add_record(logger, tmp_path, "a.txt")
        manifest_path = logger.save_manifest()
        assert Path(manifest_path).exists()
        assert Path(manifest_path).parent.name == "metadata"

    def test_default_filename_is_manifest_json(self, logger, tmp_path):
        self._add_record(logger, tmp_path, "a.txt")
        manifest_path = logger.save_manifest()
        assert Path(manifest_path).name == "manifest.json"

    def test_custom_filename_is_respected(self, logger, tmp_path):
        self._add_record(logger, tmp_path, "a.txt")
        manifest_path = logger.save_manifest(manifest_name="batch_007.json")
        assert Path(manifest_path).name == "batch_007.json"

    def test_written_file_is_valid_json_with_expected_top_level_keys(self, logger, tmp_path):
        self._add_record(logger, tmp_path, "a.txt")
        manifest_path = logger.save_manifest()
        data = json.loads(Path(manifest_path).read_text())
        assert set(data.keys()) == {"title", "description", "batch_metadata", "files"}
        assert data["title"] == "Dirty Dataset Manifest"

    def test_total_and_files_match_records(self, logger, tmp_path):
        self._add_record(logger, tmp_path, "a.txt")
        self._add_record(logger, tmp_path, "b.csv", ext=".csv")
        manifest_path = logger.save_manifest()
        data = json.loads(Path(manifest_path).read_text())
        assert data["batch_metadata"]["total"] == 2
        assert len(data["files"]) == 2

    def test_file_type_counts_grouped_by_extension(self, logger, tmp_path):
        self._add_record(logger, tmp_path, "a.txt")
        self._add_record(logger, tmp_path, "b.txt")
        self._add_record(logger, tmp_path, "c.csv", ext=".csv")
        manifest_path = logger.save_manifest()
        data = json.loads(Path(manifest_path).read_text())
        assert data["batch_metadata"]["file_type_counts"] == {".txt": 2, ".csv": 1}

    def test_scrambled_and_duplicated_counts(self, logger, tmp_path):
        self._add_record(logger, tmp_path, "a.txt", scrambled=True)
        self._add_record(logger, tmp_path, "b.txt", duplicate=True)
        self._add_record(logger, tmp_path, "c.txt")
        manifest_path = logger.save_manifest()
        data = json.loads(Path(manifest_path).read_text())
        assert data["batch_metadata"]["scrambled_extensions"] == 1
        assert data["batch_metadata"]["duplicated_count"] == 1
        assert data["batch_metadata"]["scrambled_rate"] == round(1 / 3, 2)
        assert data["batch_metadata"]["duplicated_rate"] == round(1 / 3, 2)

    def test_zero_records_does_not_divide_by_zero(self, logger):
        manifest_path = logger.save_manifest()
        data = json.loads(Path(manifest_path).read_text())
        meta = data["batch_metadata"]
        assert meta["total"] == 0
        assert meta["scrambled_rate"] == 0.0
        assert meta["structural_corruption_rate"] == 0.0
        assert meta["character_corruption_rate"] == 0.0
        assert meta["duplicated_rate"] == 0.0

    def test_execution_duration_is_a_non_negative_number(self, logger, tmp_path):
        self._add_record(logger, tmp_path, "a.txt")
        manifest_path = logger.save_manifest()
        data = json.loads(Path(manifest_path).read_text())
        assert data["batch_metadata"]["execution_duration_seconds"] >= 0

    def test_clean_count_bug_double_counts_files_corrupted_both_ways(self, logger, tmp_path):
        # BUG: `corrupted_count = structural_corrupted_count + character_corrupted_count`
        # is a sum of two counts, not a count of distinct corrupted files.
        # A single file that is BOTH structurally and character corrupted
        # gets counted twice, which can make clean_count wrong (even negative
        # in extreme cases) instead of reflecting actual distinct clean files.
        self._add_record(logger, tmp_path, "a.txt", corruption="row_shuffle", char_corruption="mojibake")
        self._add_record(logger, tmp_path, "b.txt")  # genuinely clean
        manifest_path = logger.save_manifest()
        data = json.loads(Path(manifest_path).read_text())
        meta = data["batch_metadata"]
        # Documents current (buggy) behavior: 2 total, 1 file double-counted
        # as corrupted -> clean_count comes out as 2 - 2 = 0, even though
        # exactly one file ("b.txt") is actually clean.
        assert meta["total"] == 2
        assert meta["clean_count"] == 0  # should arguably be 1

    def test_character_corrupted_count_bug_reports_combined_sum(self, logger, tmp_path):
        # BUG: manifest_data["character_corrupted_count"] is assigned
        # `corrupted_count` (structural + character combined), not the
        # `character_corrupted_count` variable actually computed above it.
        # Same bug affects "structural_corrupted_count" in the output dict.
        self._add_record(logger, tmp_path, "a.txt", corruption="row_shuffle", char_corruption="none")
        self._add_record(logger, tmp_path, "b.txt", corruption="none", char_corruption="mojibake")
        manifest_path = logger.save_manifest()
        data = json.loads(Path(manifest_path).read_text())
        meta = data["batch_metadata"]
        # There is exactly 1 structurally-corrupted file and 1
        # character-corrupted file, but both output fields report 2
        # (the sum), documenting the current mislabeling.
        assert meta["structural_corrupted_count"] == 2
        assert meta["character_corrupted_count"] == 2


    def test_calling_twice_overwrites_manifest_file(self, logger, tmp_path):
        self._add_record(logger, tmp_path, "a.txt")
        path1 = logger.save_manifest()
        self._add_record(logger, tmp_path, "b.txt")
        path2 = logger.save_manifest()
        assert path1 == path2
        data = json.loads(Path(path2).read_text())
        assert data["batch_metadata"]["total"] == 2
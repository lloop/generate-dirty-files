# tests/test_master_data_generator.py
import json
import os
from pathlib import Path

import pytest

import main as mdg  # adjust import to actual module path
from main import MasterDataGenerator


class FakeHandler:
    """Stand-in for whatever HandlerRegistry.get_handler() normally returns."""

    def corrupt_structure(self, content, mutation_type="none"):
        # No-op corruption; return content and label unchanged so tests
        # can assert on exact byte/text output deterministically.
        return content, mutation_type

    def add_unique_entropy(self, content, token):
        # Identity, so output is predictable in assertions.
        return content


@pytest.fixture
def templates_dir(tmp_path):
    d = tmp_path / "templates"
    d.mkdir()
    (d / "base_txt.txt").write_text("hello template content")
    (d / "base_csv.csv").write_text("a,b,c\n1,2,3")
    return d


@pytest.fixture
def generator(templates_dir, monkeypatch):
    gen = MasterDataGenerator(templates_dir=str(templates_dir))
    # Replace the real handler registry with a deterministic fake so tests
    # aren't coupled to handler-specific corruption behavior.
    monkeypatch.setattr(gen.registry, "get_handler", lambda ext, is_binary=False: FakeHandler())
    return gen


def force_probability(monkeypatch, name, value):
    """Patch a PERCENT_* constant as imported into the module under test."""
    monkeypatch.setattr(mdg, name, value)


class TestLoadTemplates:
    def test_raises_if_templates_dir_missing(self, tmp_path):
        missing = tmp_path / "does_not_exist"
        with pytest.raises(FileNotFoundError):
            MasterDataGenerator(templates_dir=str(missing))

    def test_raises_if_no_valid_template_files(self, tmp_path):
        empty_dir = tmp_path / "empty_templates"
        empty_dir.mkdir()
        with pytest.raises(ValueError):
            MasterDataGenerator(templates_dir=str(empty_dir))

    def test_maps_extensions_case_insensitively(self, tmp_path):
        d = tmp_path / "templates"
        d.mkdir()
        (d / "BASE.TXT").write_text("x")
        gen = MasterDataGenerator(templates_dir=str(d))
        assert ".txt" in gen.template_map

    def test_ignores_extensionless_files(self, tmp_path):
        d = tmp_path / "templates"
        d.mkdir()
        (d / "no_extension_file").write_text("x")
        (d / "valid.txt").write_text("x")
        gen = MasterDataGenerator(templates_dir=str(d))
        assert list(gen.template_map.keys()) == [".txt"]

    def test_ignores_subdirectories(self, tmp_path):
        d = tmp_path / "templates"
        d.mkdir()
        (d / "valid.txt").write_text("x")
        (d / "subdir").mkdir()
        gen = MasterDataGenerator(templates_dir=str(d))
        assert list(gen.template_map.keys()) == [".txt"]


class TestGetUniquePath:
    def test_returns_same_path_when_no_collision(self, generator, tmp_path):
        target = tmp_path / "fresh.txt"
        result = generator._get_unique_path(str(target))
        assert result == str(target)

    def test_appends_counter_on_collision(self, generator, tmp_path):
        existing = tmp_path / "taken.txt"
        existing.write_text("x")
        result = generator._get_unique_path(str(existing))
        assert result == str(tmp_path / "taken_1.txt")

    def test_increments_past_multiple_collisions(self, generator, tmp_path):
        (tmp_path / "taken.txt").write_text("x")
        (tmp_path / "taken_1.txt").write_text("x")
        (tmp_path / "taken_2.txt").write_text("x")
        result = generator._get_unique_path(str(tmp_path / "taken.txt"))
        assert result == str(tmp_path / "taken_3.txt")

    def test_preserves_extension(self, generator, tmp_path):
        (tmp_path / "data.csv").write_text("x")
        result = generator._get_unique_path(str(tmp_path / "data.csv"))
        assert result.endswith(".csv")


class TestGenerateBatch:
    def test_creates_output_directory(self, generator, tmp_path, monkeypatch):
        force_probability(monkeypatch, "PERCENT_STRUCT_CORRUPTION", 0.0)
        force_probability(monkeypatch, "PERCENT_CHAR_CORRUPT", 0.0)
        force_probability(monkeypatch, "PERCENT_DUPLICATE", 0.0)
        force_probability(monkeypatch, "PERCENT_EXTENSION_SCRAMBLE", 0.0)

        out_dir = tmp_path / "output"
        generator.generate_batch(output_dir=str(out_dir), total_files=3)
        assert out_dir.exists()

    def test_wipes_previous_output_directory(self, generator, tmp_path, monkeypatch):
        force_probability(monkeypatch, "PERCENT_STRUCT_CORRUPTION", 0.0)
        force_probability(monkeypatch, "PERCENT_CHAR_CORRUPT", 0.0)
        force_probability(monkeypatch, "PERCENT_DUPLICATE", 0.0)
        force_probability(monkeypatch, "PERCENT_EXTENSION_SCRAMBLE", 0.0)

        out_dir = tmp_path / "output"
        out_dir.mkdir()
        stale_file = out_dir / "leftover_from_previous_run.txt"
        stale_file.write_text("stale")

        generator.generate_batch(output_dir=str(out_dir), total_files=2)
        assert not stale_file.exists()

    def test_generates_exact_requested_count_with_no_duplicates(self, generator, tmp_path, monkeypatch):
        force_probability(monkeypatch, "PERCENT_STRUCT_CORRUPTION", 0.0)
        force_probability(monkeypatch, "PERCENT_CHAR_CORRUPT", 0.0)
        force_probability(monkeypatch, "PERCENT_DUPLICATE", 0.0)
        force_probability(monkeypatch, "PERCENT_EXTENSION_SCRAMBLE", 0.0)

        out_dir = tmp_path / "output"
        generator.generate_batch(output_dir=str(out_dir), total_files=5)

        produced = [p for p in out_dir.iterdir() if p.is_file() and p.name != "metadata"]
        # metadata/ is a subdirectory, not a file, so this filters correctly
        assert len(produced) == 5

    def test_writes_manifest_json_with_matching_total(self, generator, tmp_path, monkeypatch):
        force_probability(monkeypatch, "PERCENT_STRUCT_CORRUPTION", 0.0)
        force_probability(monkeypatch, "PERCENT_CHAR_CORRUPT", 0.0)
        force_probability(monkeypatch, "PERCENT_DUPLICATE", 0.0)
        force_probability(monkeypatch, "PERCENT_EXTENSION_SCRAMBLE", 0.0)

        out_dir = tmp_path / "output"
        generator.generate_batch(output_dir=str(out_dir), total_files=4)

        manifest_path = out_dir / "metadata" / "manifest.json"
        assert manifest_path.exists()
        data = json.loads(manifest_path.read_text())
        assert data["batch_metadata"]["total"] == 4
        assert len(data["files"]) == 4

    def test_forced_duplicate_creation_still_stops_at_total_files(self, generator, tmp_path, monkeypatch):
        # PERCENT_DUPLICATE=1.0 means every eligible file triggers a duplicate,
        # but the loop guards with `generated_count < total_files` before
        # attempting one -- so the final count should never exceed the request.
        force_probability(monkeypatch, "PERCENT_STRUCT_CORRUPTION", 0.0)
        force_probability(monkeypatch, "PERCENT_CHAR_CORRUPT", 0.0)
        force_probability(monkeypatch, "PERCENT_DUPLICATE", 1.0)
        force_probability(monkeypatch, "PERCENT_EXTENSION_SCRAMBLE", 0.0)

        out_dir = tmp_path / "output"
        generator.generate_batch(output_dir=str(out_dir), total_files=6)

        produced = [p for p in out_dir.iterdir() if p.is_file()]
        assert len(produced) == 6

        manifest_path = out_dir / "metadata" / "manifest.json"
        data = json.loads(manifest_path.read_text())
        assert data["batch_metadata"]["total"] == 6
        assert data["batch_metadata"]["duplicated_count"] >= 1

    def test_forced_extension_scramble_logs_original_extension(self, generator, tmp_path, monkeypatch):
        force_probability(monkeypatch, "PERCENT_STRUCT_CORRUPTION", 0.0)
        force_probability(monkeypatch, "PERCENT_CHAR_CORRUPT", 0.0)
        force_probability(monkeypatch, "PERCENT_DUPLICATE", 0.0)
        force_probability(monkeypatch, "PERCENT_EXTENSION_SCRAMBLE", 1.0)

        out_dir = tmp_path / "output"
        generator.generate_batch(output_dir=str(out_dir), total_files=2)

        manifest_path = out_dir / "metadata" / "manifest.json"
        data = json.loads(manifest_path.read_text())
        for entry in data["files"]:
            assert entry["extension_scrambled"] is True
            # original_extension should be recorded, not "none", when scrambled
            assert entry["original_extension"] != "none"

    def test_forced_character_corruption_is_reflected_in_manifest(self, generator, tmp_path, monkeypatch):
        force_probability(monkeypatch, "PERCENT_STRUCT_CORRUPTION", 0.0)
        force_probability(monkeypatch, "PERCENT_CHAR_CORRUPT", 1.0)
        force_probability(monkeypatch, "PERCENT_DUPLICATE", 0.0)
        force_probability(monkeypatch, "PERCENT_EXTENSION_SCRAMBLE", 0.0)

        out_dir = tmp_path / "output"
        generator.generate_batch(output_dir=str(out_dir), total_files=3)

        manifest_path = out_dir / "metadata" / "manifest.json"
        data = json.loads(manifest_path.read_text())
        for entry in data["files"]:
            assert entry["is_character_corrupted"] is True
            assert entry["character_corruption_label"] != "none"

    def test_duplicate_skipped_for_intended_zero_byte_file(self, generator, tmp_path, monkeypatch, capsys):
        # If corrupt_structure produces empty content, the duplicate pass
        # should be skipped even when PERCENT_DUPLICATE forces an attempt.
        class ZeroByteHandler(FakeHandler):
            def corrupt_structure(self, content, mutation_type="none"):
                return "", "zero_byte_corruption"

        monkeypatch.setattr(generator.registry, "get_handler", lambda ext, is_binary=False: ZeroByteHandler())
        force_probability(monkeypatch, "PERCENT_STRUCT_CORRUPTION", 1.0)
        force_probability(monkeypatch, "PERCENT_CHAR_CORRUPT", 0.0)
        force_probability(monkeypatch, "PERCENT_DUPLICATE", 1.0)
        force_probability(monkeypatch, "PERCENT_EXTENSION_SCRAMBLE", 0.0)

        out_dir = tmp_path / "output"
        generator.generate_batch(output_dir=str(out_dir), total_files=2)

        captured = capsys.readouterr()
        assert "Skipping duplicate pass" in captured.out

    def test_binary_extension_written_and_read_in_binary_mode(self, tmp_path, monkeypatch):
        d = tmp_path / "templates"
        d.mkdir()
        (d / "base.png").write_bytes(b"\x89PNG\r\n\x1a\nBINARYDATA")
        gen = MasterDataGenerator(templates_dir=str(d))
        monkeypatch.setattr(gen.registry, "get_handler", lambda ext, is_binary=False: FakeHandler())

        force_probability(monkeypatch, "PERCENT_STRUCT_CORRUPTION", 0.0)
        force_probability(monkeypatch, "PERCENT_CHAR_CORRUPT", 0.0)
        force_probability(monkeypatch, "PERCENT_DUPLICATE", 0.0)
        force_probability(monkeypatch, "PERCENT_EXTENSION_SCRAMBLE", 0.0)

        out_dir = tmp_path / "output"
        gen.generate_batch(output_dir=str(out_dir), total_files=1)

        produced = [p for p in out_dir.iterdir() if p.is_file()]
        assert len(produced) == 1
        assert produced[0].read_bytes() == b"\x89PNG\r\n\x1a\nBINARYDATA"
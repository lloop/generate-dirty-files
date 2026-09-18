# data_modifiers/test_extension_scrambler.py
import random
from pathlib import Path

import pytest

from data_modifiers.extension_scrambler import scramble_extension


class TestScrambleExtension:
    def test_returns_a_path_object(self):
        result = scramble_extension(Path("invoice.txt"), [".txt", ".csv", ".json"])
        assert isinstance(result, Path)

    def test_new_extension_differs_from_original(self):
        result = scramble_extension(Path("invoice.txt"), [".txt", ".csv", ".json"])
        assert result.suffix != ".txt"

    def test_new_extension_is_from_provided_list(self):
        extensions = [".txt", ".csv", ".json", ".xml"]
        result = scramble_extension(Path("invoice.txt"), extensions)
        assert result.suffix in extensions

    def test_stem_is_preserved(self):
        result = scramble_extension(Path("invoice.txt"), [".txt", ".csv", ".json"])
        assert result.stem == "invoice"

    def test_directory_is_preserved(self):
        result = scramble_extension(Path("/some/nested/dir/invoice.txt"), [".txt", ".csv"])
        assert result.parent == Path("/some/nested/dir")

    def test_current_extension_matching_is_case_insensitive(self):
        # current_ext is lowercased before filtering, so an uppercase
        # extension on the file should still be excluded from candidates
        random.seed(0)
        for _ in range(20):
            result = scramble_extension(Path("invoice.TXT"), [".txt", ".csv"])
            assert result.suffix == ".csv"

    def test_extensions_list_is_not_lowercased_for_comparison(self):
        # NOTE: only current_ext is .lower()'d, not the entries in `extensions`.
        # If the list contains an uppercase variant of the current extension,
        # it will NOT be filtered out and could be chosen as the "new" one,
        # producing a no-op scramble. This test documents that behavior.
        random.seed(0)
        result = scramble_extension(Path("invoice.txt"), [".TXT", ".csv"])
        assert result.suffix in {".TXT", ".csv"}

    def test_only_one_possible_extension_besides_current(self):
        result = scramble_extension(Path("invoice.txt"), [".txt", ".csv"])
        assert result.suffix == ".csv"

    def test_no_alternative_extensions_raises(self):
        # possible_exts becomes empty -> random.choice([]) raises IndexError
        with pytest.raises(IndexError):
            scramble_extension(Path("invoice.txt"), [".txt"])

    def test_empty_extensions_list_raises(self):
        with pytest.raises(IndexError):
            scramble_extension(Path("invoice.txt"), [])

    def test_file_with_no_original_extension(self):
        # suffix is "" for an extensionless file; "" won't match any real
        # extension in the list, so all of them remain candidates
        result = scramble_extension(Path("invoice"), [".txt", ".csv"])
        assert result.suffix in {".txt", ".csv"}

    def test_multiple_dots_in_filename_only_affects_final_suffix(self):
        result = scramble_extension(Path("archive.tar.gz"), [".gz", ".zip"])
        assert result.stem == "archive.tar"
        assert result.suffix == ".zip"

    def test_deterministic_with_seeded_random(self):
        random.seed(123)
        result1 = scramble_extension(Path("invoice.txt"), [".txt", ".csv", ".json"])
        random.seed(123)
        result2 = scramble_extension(Path("invoice.txt"), [".txt", ".csv", ".json"])
        assert result1 == result2

    def test_uses_random_choice_from_filtered_candidates(self, monkeypatch):
        captured = {}

        def fake_choice(seq):
            captured["seq"] = list(seq)
            return seq[0]

        monkeypatch.setattr(random, "choice", fake_choice)
        scramble_extension(Path("invoice.txt"), [".txt", ".csv", ".json"])
        assert ".txt" not in captured["seq"]
        assert set(captured["seq"]) == {".csv", ".json"}
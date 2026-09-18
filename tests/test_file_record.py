# tests/test_file_record.py
import hashlib

import pytest

from models.file_record import FileRecord  # adjust import to actual module path


def make_record(**overrides) -> FileRecord:
    defaults = dict(
        unique_token="abc123",
        original_filename="invoice.txt",
        original_extension=".txt",
    )
    defaults.update(overrides)
    return FileRecord(**defaults)


class TestDefaults:
    def test_required_fields_are_set(self):
        record = make_record()
        assert record.unique_token == "abc123"
        assert record.original_filename == "invoice.txt"
        assert record.original_extension == ".txt"

    def test_optional_fields_have_expected_defaults(self):
        record = make_record()
        assert record.output_filename == ""
        assert record.output_extension == ""
        assert record.content == ""
        assert record.is_binary is False
        assert record.structural_mutation == "none"
        assert record.character_mutation == "none"
        assert record.extension_scrambled is False
        assert record.is_duplicate is False

    def test_computed_fields_default_before_finalize(self):
        record = make_record()
        assert record.sha256_hash == ""
        assert record.byte_size == 0

    def test_computed_fields_are_not_settable_via_init(self):
        # sha256_hash and byte_size use field(init=False), so passing them
        # to the constructor should raise a TypeError
        with pytest.raises(TypeError):
            FileRecord(
                unique_token="x",
                original_filename="a.txt",
                original_extension=".txt",
                sha256_hash="deadbeef",
            )

    def test_mutable_fields_are_independent_across_instances(self):
        # Guard against accidental shared mutable default state (not present
        # here, but worth locking in since these are dataclass fields)
        r1 = make_record()
        r2 = make_record()
        r1.structural_mutation = "reordered"
        assert r2.structural_mutation == "none"


class TestFinalizeContentWithStringPayload:
    def test_sets_content(self):
        record = make_record()
        record.finalize_content("hello world")
        assert record.content == "hello world"

    def test_computes_correct_byte_size_for_ascii(self):
        record = make_record()
        record.finalize_content("hello")
        assert record.byte_size == 5

    def test_computes_correct_byte_size_for_multibyte_utf8(self):
        record = make_record()
        text = "café"  # é is 2 bytes in UTF-8
        record.finalize_content(text)
        assert record.byte_size == len(text.encode("utf-8"))

    def test_computes_correct_sha256_hash(self):
        record = make_record()
        content = "hello world"
        record.finalize_content(content)
        expected = hashlib.sha256(content.encode("utf-8", errors="surrogateescape")).hexdigest()
        assert record.sha256_hash == expected

    def test_empty_string_content(self):
        record = make_record()
        record.finalize_content("")
        assert record.byte_size == 0
        assert record.sha256_hash == hashlib.sha256(b"").hexdigest()

    def test_handles_unpaired_surrogates_without_raising(self):
        # errors="surrogateescape" specifically exists to survive content
        # produced by earlier corruption steps (e.g. mojibake/null-byte
        # injection) that may contain invalid/lone surrogate code points.
        record = make_record()
        # A lone surrogate, which plain .encode("utf-8") would reject
        surrogate_content = "abc\udcffdef"
        record.finalize_content(surrogate_content)
        assert record.byte_size > 0
        assert len(record.sha256_hash) == 64


class TestFinalizeContentWithBytesPayload:
    def test_sets_content(self):
        record = make_record()
        payload = b"\x89PNG\r\n\x1a\n"
        record.finalize_content(payload)
        assert record.content == payload

    def test_computes_correct_byte_size(self):
        record = make_record()
        payload = b"\x00\x01\x02\x03"
        record.finalize_content(payload)
        assert record.byte_size == 4

    def test_computes_correct_sha256_hash(self):
        record = make_record()
        payload = b"binary data here"
        record.finalize_content(payload)
        assert record.sha256_hash == hashlib.sha256(payload).hexdigest()

    def test_empty_bytes_content(self):
        record = make_record()
        record.finalize_content(b"")
        assert record.byte_size == 0
        assert record.sha256_hash == hashlib.sha256(b"").hexdigest()

    def test_does_not_reencode_bytes_as_utf8(self):
        # Bytes that are NOT valid UTF-8 should pass straight through to
        # hashlib without any decode/encode roundtrip attempt.
        record = make_record()
        invalid_utf8 = b"\xff\xfe\xfd"
        record.finalize_content(invalid_utf8)
        assert record.byte_size == 3
        assert record.sha256_hash == hashlib.sha256(invalid_utf8).hexdigest()


class TestFinalizeContentOverwriting:
    def test_calling_twice_updates_hash_and_size_to_latest_call(self):
        record = make_record()
        record.finalize_content("first")
        first_hash = record.sha256_hash
        record.finalize_content("second, and longer")
        assert record.content == "second, and longer"
        assert record.sha256_hash != first_hash
        assert record.byte_size == len("second, and longer".encode("utf-8"))


class TestToManifestDict:
    def test_contains_all_expected_keys(self):
        record = make_record()
        manifest = record.to_manifest_dict()
        expected_keys = {
            "unique_token",
            "original_filename",
            "output_filename",
            "original_extension",
            "output_extension",
            "extension_mismatch",
            "is_duplicate",
            "mutations",
            "file_size_bytes",
            "sha256",
        }
        assert set(manifest.keys()) == expected_keys

    def test_maps_fields_to_correct_manifest_keys(self):
        record = make_record(
            output_filename="invoice_final.csv",
            output_extension=".csv",
            extension_scrambled=True,
            is_duplicate=True,
            structural_mutation="row_shuffle",
            character_mutation="mojibake",
        )
        record.finalize_content("some,csv,content")
        manifest = record.to_manifest_dict()

        assert manifest["unique_token"] == "abc123"
        assert manifest["original_filename"] == "invoice.txt"
        assert manifest["output_filename"] == "invoice_final.csv"
        assert manifest["original_extension"] == ".txt"
        assert manifest["output_extension"] == ".csv"
        assert manifest["extension_mismatch"] is True
        assert manifest["is_duplicate"] is True
        assert manifest["mutations"] == {
            "structural": "row_shuffle",
            "character_encoding": "mojibake",
        }
        assert manifest["file_size_bytes"] == len(b"some,csv,content")
        assert manifest["sha256"] == hashlib.sha256(b"some,csv,content").hexdigest()

    def test_reflects_defaults_before_finalize_content_is_called(self):
        record = make_record()
        manifest = record.to_manifest_dict()
        assert manifest["file_size_bytes"] == 0
        assert manifest["sha256"] == ""
        assert manifest["mutations"] == {"structural": "none", "character_encoding": "none"}

    def test_does_not_leak_raw_content_field(self):
        # The manifest is meant for a dataset JSON -- it should not include
        # the (potentially large or binary) raw content payload.
        record = make_record()
        record.finalize_content("some content that should not appear directly")
        manifest = record.to_manifest_dict()
        assert "content" not in manifest
import pytest
from data_modifiers.character_modifier import CharacterModifier


@pytest.fixture
def modifier():
    return CharacterModifier()


class TestCorruptCharacterEncoding:
    def test_empty_string_returns_unchanged(self, modifier):
        result, label = modifier.corrupt_character_encoding("")
        assert result == ""
        assert label == "none"

    def test_non_string_input_returns_unchanged(self, modifier):
        for bad_input in [None, 123, 3.14, [], {}, b"bytes"]:
            result, label = modifier.corrupt_character_encoding(bad_input)
            assert result == bad_input
            assert label == "none"

    def test_returns_tuple_of_str_and_label(self, modifier):
        result, label = modifier.corrupt_character_encoding("hello world")
        assert isinstance(result, str)
        assert isinstance(label, str)
        assert label in {"mojibake", "null_byte_injection", "unicode_replacement_char"}

    def test_dispatches_to_one_of_three_strategies(self, modifier, monkeypatch):
        # Force each branch and confirm the right label comes back
        content = "hello world"

        monkeypatch.setattr(random, "choice", lambda _: modifier._corrupt_mojibake) if False else None
        # simpler: call each private method directly (covered below), and
        # separately confirm corrupt_character_encoding always returns one of them
        seen_labels = set()
        for _ in range(50):  # sample enough calls to likely hit all branches
            _, label = modifier.corrupt_character_encoding(content)
            seen_labels.add(label)
        assert seen_labels.issubset({"mojibake", "null_byte_injection", "unicode_replacement_char"})


class TestCorruptMojibake:
    def test_ascii_content_roundtrips_without_error(self, modifier):
        result, label = modifier._corrupt_mojibake("hello")
        assert label == "mojibake"
        assert isinstance(result, str)

    def test_non_ascii_content_gets_corrupted(self, modifier):
        original = "café résumé"
        result, label = modifier._corrupt_mojibake(original)
        assert label == "mojibake"
        # UTF-8 bytes of accented chars decoded as cp1252 should differ from original
        assert result != original

    def test_handles_encode_failure_gracefully(self, modifier, monkeypatch):
        class Unencodable(str):
            def encode(self, *args, **kwargs):
                raise UnicodeEncodeError("utf-8", "x", 0, 1, "boom")

        bad_content = Unencodable("test")
        result, label = modifier._corrupt_mojibake(bad_content)
        assert result == bad_content
        assert label == "none"


class TestCorruptNullBytes:
    def test_inserts_exactly_one_null_byte(self, modifier):
        content = "hello world"
        result, label = modifier._corrupt_null_bytes(content)
        assert label == "null_byte_injection"
        assert result.count("\x00") == 1
        # length should grow by exactly one character
        assert len(result) == len(content) + 1

    def test_preserves_original_characters(self, modifier):
        content = "hello"
        result, _ = modifier._corrupt_null_bytes(content)
        assert result.replace("\x00", "") == content

    def test_single_character_content(self, modifier):
        # pos = random.randint(0, len(content)-1) -> randint(0, 0) is valid
        result, label = modifier._corrupt_null_bytes("a")
        assert label == "null_byte_injection"
        assert "\x00" in result
        assert result.replace("\x00", "") == "a"

    def test_empty_content_raises(self, modifier):
        # randint(0, -1) raises ValueError -- documents current (fragile) behavior
        with pytest.raises(ValueError):
            modifier._corrupt_null_bytes("")


class TestCorruptReplacementChars:
    def test_label_is_correct(self, modifier):
        _, label = modifier._corrupt_replacement_chars("hello world this is a test")
        assert label == "unicode_replacement_char"

    def test_length_is_unchanged(self, modifier):
        content = "hello world this is a longer test string"
        result, _ = modifier._corrupt_replacement_chars(content)
        assert len(result) == len(content)

    def test_contains_at_least_one_replacement_char(self, modifier):
        content = "a" * 100
        result, _ = modifier._corrupt_replacement_chars(content)
        assert "\ufffd" in result

    def test_short_content_still_replaces_at_least_one(self, modifier):
        # len // 20 == 0 for short strings, but max(1, ...) guards it
        result, label = modifier._corrupt_replacement_chars("hi")
        assert label == "unicode_replacement_char"
        assert len(result) == 2
        assert "\ufffd" in result

    def test_single_character_content(self, modifier):
        result, label = modifier._corrupt_replacement_chars("x")
        assert result == "\ufffd"
        assert label == "unicode_replacement_char"

    def test_empty_content_raises(self, modifier):
        # randint(0, len(content_list)-1) with empty list raises ValueError
        with pytest.raises(ValueError):
            modifier._corrupt_replacement_chars("")


class TestDeterminismWithSeededRandom:
    def test_seeded_random_is_reproducible(self, modifier):
        random.seed(42)
        result1 = modifier.corrupt_character_encoding("hello world")
        random.seed(42)
        result2 = modifier.corrupt_character_encoding("hello world")
        assert result1 == result2


# needed for the seeded-random test and the dispatch sampling test
import random  # noqa: E402
import random
import pytest

import data_modifiers.generate_title as ftg  # adjust import to actual module path
from data_modifiers.generate_title import (
    generate_title,
    mistake_punctuation,
    cap_first,
    capitalized,
    FILE_NAMES,
    FILE_EXTENSIONS,
    ADDED,
    MISTAKES,
)


class TestCapFirst:
    def test_capitalizes_first_letter_only(self):
        assert cap_first("hello") == "Hello"

    def test_lowercases_rest_of_string(self):
        assert cap_first("hELLO") == "Hello"

    def test_empty_string(self):
        assert cap_first("") == ""

    def test_already_capitalized(self):
        assert cap_first("Hello") == "Hello"


class TestCapitalized:
    def test_uppercases_entire_string(self):
        assert capitalized("hello") == "HELLO"

    def test_mixed_case_input(self):
        assert capitalized("HeLLo") == "HELLO"

    def test_empty_string(self):
        assert capitalized("") == ""


class TestMistakePunctuation:
    def test_returns_string_one_char_longer(self):
        word = "invoice"
        result = mistake_punctuation(word)
        assert len(result) == len(word) + 1

    def test_inserted_char_is_a_known_mistake(self):
        word = "invoice"
        result = mistake_punctuation(word)
        inserted_chars = set(result) - set(word)
        # The only new character introduced should be one of MISTAKES
        assert inserted_chars.issubset(set(MISTAKES))

    def test_removing_any_mistake_char_once_recovers_original_length(self):
        word = "report"
        result = mistake_punctuation(word)
        # Whatever got inserted, stripping exactly one occurrence of it
        # should reconstruct a string equal in length to the original
        for m in MISTAKES:
            if result.count(m) > word.count(m):
                idx = result.index(m)
                rebuilt = result[:idx] + result[idx + 1:]
                assert rebuilt == word
                return
        pytest.fail("No inserted mistake character found in result")

    def test_empty_word_still_inserts_a_character(self):
        # insert_pos = randint(0, 0) = 0, so this should not raise
        result = mistake_punctuation("")
        assert len(result) == 1
        assert result in MISTAKES

    def test_insertion_can_occur_at_start_or_end(self, monkeypatch):
        monkeypatch.setattr(random, "choice", lambda seq: "_")
        monkeypatch.setattr(random, "randint", lambda a, b: 0)
        assert mistake_punctuation("abc") == "_abc"

        monkeypatch.setattr(random, "randint", lambda a, b: 3)
        assert mistake_punctuation("abc") == "abc_"


class TestGenerateTitle:
    def test_returns_a_string(self):
        result = generate_title()
        assert isinstance(result, str)

    def test_ends_with_a_known_extension_by_default(self):
        result = generate_title()
        assert any(result.endswith(ext) for ext in FILE_EXTENSIONS)

    def test_uses_provided_extension_list_when_given(self):
        custom_exts = [".pdf"]
        result = generate_title(available_extensions=custom_exts)
        assert result.endswith(".pdf")

    def test_empty_extension_list_falls_back_to_default(self):
        # `available_extensions or FILE_EXTENSIONS` means [] is falsy and
        # falls back to the default list, not to "no extension"
        result = generate_title(available_extensions=[])
        assert any(result.endswith(ext) for ext in FILE_EXTENSIONS)

    def test_base_name_always_traceable_to_known_name(self, monkeypatch):
        # Disable all random modifications so we can check the base name cleanly
        monkeypatch.setattr(random, "random", lambda: 1.0)  # fails every "< PERCENT_x" check
        monkeypatch.setattr(random, "choice", lambda seq: seq[0])

        result = generate_title(available_extensions=[".txt"])
        assert result == f"{FILE_NAMES[0]}.txt"

    def test_name_addition_applied_when_forced(self, monkeypatch):
        calls = {"n": 0}

        def fake_random():
            # First call: PERCENT_ADDED check -> force True
            # Second call: PERCENT_MODIFIED check -> force False
            # Third call: PERCENT_MISTAKEN_PUNCTUATION check -> force False
            calls["n"] += 1
            return 0.0 if calls["n"] == 1 else 1.0

        monkeypatch.setattr(random, "random", fake_random)
        monkeypatch.setattr(random, "choice", lambda seq: seq[0])

        result = generate_title(available_extensions=[".txt"])
        assert result == f"{FILE_NAMES[0]}{ADDED[0]}.txt"

    def test_modifier_applied_when_forced(self, monkeypatch):
        calls = {"n": 0}

        def fake_random():
            calls["n"] += 1
            # PERCENT_ADDED -> False, PERCENT_MODIFIED -> True, PERCENT_MISTAKEN -> False
            return 1.0 if calls["n"] == 1 else (0.0 if calls["n"] == 2 else 1.0)

        def fake_choice(seq):
            # First choice call is FILE_NAMES, second is MODIFIERS
            if seq is ftg.MODIFIERS:
                return capitalized
            return seq[0]

        monkeypatch.setattr(random, "random", fake_random)
        monkeypatch.setattr(random, "choice", fake_choice)

        result = generate_title(available_extensions=[".txt"])
        assert result == f"{FILE_NAMES[0].upper()}.txt"

    def test_mistaken_punctuation_applied_when_forced(self, monkeypatch):
        calls = {"n": 0}

        def fake_random():
            calls["n"] += 1
            # PERCENT_ADDED -> False, PERCENT_MODIFIED -> False, PERCENT_MISTAKEN -> True
            return 1.0 if calls["n"] in (1, 2) else 0.0

        monkeypatch.setattr(random, "random", fake_random)
        monkeypatch.setattr(random, "choice", lambda seq: seq[0])
        monkeypatch.setattr(random, "randint", lambda a, b: 0)

        result = generate_title(available_extensions=[".txt"])
        assert result == f"{MISTAKES[0]}{FILE_NAMES[0]}.txt"

    def test_many_calls_produce_only_valid_extensions(self):
        # Statistical smoke test across the probabilistic branches
        for _ in range(200):
            result = generate_title()
            assert any(result.endswith(ext) for ext in FILE_EXTENSIONS)

    def test_many_calls_never_crash(self):
        for _ in range(200):
            generate_title()
            generate_title(available_extensions=[".pdf", ".docx"])
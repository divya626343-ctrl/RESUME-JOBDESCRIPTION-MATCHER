# ============================================================
# tests/test_matcher.py
# Basic tests for the matcher pipeline
# ============================================================

import pytest
from match import clean_text, is_allowed_file, score_label


def test_clean_text_strips_whitespace():
    result = clean_text("  hello   world  ")
    assert result == "hello world"


def test_clean_text_removes_control_chars():
    result = clean_text("hello\x00world")
    assert "\x00" not in result


def test_is_allowed_file_pdf():
    assert is_allowed_file("resume.pdf") is True


def test_is_allowed_file_docx():
    assert is_allowed_file("resume.docx") is True


def test_is_allowed_file_txt():
    assert is_allowed_file("resume.txt") is True


def test_is_allowed_file_rejects_png():
    assert is_allowed_file("photo.png") is False


def test_is_allowed_file_rejects_exe():
    assert is_allowed_file("virus.exe") is False


def test_score_label_excellent():
    assert score_label(80) == "Excellent"


def test_score_label_good():
    assert score_label(60) == "Good"


def test_score_label_fair():
    assert score_label(40) == "Fair"


def test_score_label_low():
    assert score_label(20) == "Low"
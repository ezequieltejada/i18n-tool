import json
import os
import pytest
from core import (load_all, save_all, get_by_path, set_by_path, delete_by_path,
                  flatten_keys, search_keys, search_values)


# --- load_all ---

def test_load_all_discovers_json_files(tmp_path):
    (tmp_path / "es.json").write_text('{"A": "1"}')
    (tmp_path / "eu.json").write_text('{"B": "2"}')
    result = load_all(str(tmp_path))
    assert set(result.keys()) == {"es", "eu"}
    assert result["es"] == {"A": "1"}
    assert result["eu"] == {"B": "2"}


def test_load_all_ignores_non_json(tmp_path):
    (tmp_path / "es.json").write_text('{"A": "1"}')
    (tmp_path / "notes.txt").write_text("not json")
    result = load_all(str(tmp_path))
    assert set(result.keys()) == {"es"}


def test_load_all_empty_dir(tmp_path):
    result = load_all(str(tmp_path))
    assert result == {}


def test_load_all_nested_json(tmp_path):
    (tmp_path / "es.json").write_text('{"EMPLEO": {"TITULO": "empleo"}}')
    result = load_all(str(tmp_path))
    assert result["es"]["EMPLEO"]["TITULO"] == "empleo"


# --- save_all ---

def test_save_all_writes_with_2_space_indent(tmp_path):
    files = {"es": {"A": "1"}}
    save_all(str(tmp_path), files)
    content = (tmp_path / "es.json").read_text()
    expected = json.dumps({"A": "1"}, indent=2, ensure_ascii=False)
    assert content == expected
    assert not content.endswith("\n")


def test_save_all_multiple_files(tmp_path):
    files = {"es": {"A": "1"}, "eu": {"B": "2"}}
    save_all(str(tmp_path), files)
    assert (tmp_path / "es.json").exists()
    assert (tmp_path / "eu.json").exists()


def test_save_all_overwrites_existing(tmp_path):
    (tmp_path / "es.json").write_text('{"OLD": "data"}')
    save_all(str(tmp_path), {"es": {"NEW": "data"}})
    result = json.loads((tmp_path / "es.json").read_text())
    assert result == {"NEW": "data"}


# --- get_by_path ---

def test_get_by_path_simple():
    assert get_by_path({"A": "1"}, "A") == "1"


def test_get_by_path_nested():
    data = {"EMPLEO": {"DETALLE": {"TIPO": "tipo"}}}
    assert get_by_path(data, "EMPLEO.DETALLE.TIPO") == "tipo"


def test_get_by_path_missing_returns_none():
    assert get_by_path({"A": "1"}, "B") is None


def test_get_by_path_partial_missing():
    assert get_by_path({"A": {"B": "1"}}, "A.C") is None


def test_get_by_path_returns_dict_for_intermediate():
    data = {"A": {"B": "1"}}
    assert get_by_path(data, "A") == {"B": "1"}


# --- set_by_path ---

def test_set_by_path_simple():
    data = {}
    set_by_path(data, "A", "1")
    assert data == {"A": "1"}


def test_set_by_path_nested_creates_intermediates():
    data = {}
    set_by_path(data, "A.B.C", "val")
    assert data == {"A": {"B": {"C": "val"}}}


def test_set_by_path_overwrites_existing():
    data = {"A": "old"}
    set_by_path(data, "A", "new")
    assert data["A"] == "new"


def test_set_by_path_preserves_siblings():
    data = {"A": {"B": "1", "C": "2"}}
    set_by_path(data, "A.B", "updated")
    assert data == {"A": {"B": "updated", "C": "2"}}


# --- delete_by_path ---

def test_delete_by_path_simple():
    data = {"A": "1", "B": "2"}
    parent_empty = delete_by_path(data, "A")
    assert "A" not in data
    assert not parent_empty


def test_delete_by_path_nested():
    data = {"A": {"B": "1", "C": "2"}}
    parent_empty = delete_by_path(data, "A.B")
    assert data == {"A": {"C": "2"}}
    assert not parent_empty


def test_delete_by_path_returns_true_when_parent_empty():
    data = {"A": {"B": "1"}}
    parent_empty = delete_by_path(data, "A.B")
    assert data == {"A": {}}
    assert parent_empty


def test_delete_by_path_missing_key():
    data = {"A": "1"}
    parent_empty = delete_by_path(data, "B")
    assert data == {"A": "1"}
    assert not parent_empty


def test_delete_by_path_missing_nested():
    data = {"A": {"B": "1"}}
    parent_empty = delete_by_path(data, "A.C")
    assert data == {"A": {"B": "1"}}
    assert not parent_empty


# --- flatten_keys ---

def test_flatten_keys_simple():
    assert flatten_keys({"A": "1", "B": "2"}) == {"A": "1", "B": "2"}


def test_flatten_keys_nested():
    data = {"EMPLEO": {"DETALLE": {"TIPO": "tipo"}, "TITULO": "empleo"}}
    result = flatten_keys(data)
    assert result == {
        "EMPLEO.DETALLE.TIPO": "tipo",
        "EMPLEO.TITULO": "empleo",
    }


def test_flatten_keys_empty():
    assert flatten_keys({}) == {}


# --- search_keys ---

def test_search_keys_substring_match():
    data = {"EMPLEO": {"DETALLE": {"TIPO": "tipo"}, "TITULO": "empleo"}}
    assert search_keys(data, "DETALLE") == ["EMPLEO.DETALLE.TIPO"]


def test_search_keys_case_insensitive():
    data = {"EMPLEO": {"TITULO": "empleo"}}
    assert search_keys(data, "empleo") == ["EMPLEO.TITULO"]


def test_search_keys_no_match():
    data = {"A": "1"}
    assert search_keys(data, "ZZZZZ") == []


def test_search_keys_multiple_matches():
    data = {"A": {"B": "1"}, "AB": "2"}
    results = search_keys(data, "A")
    assert "A.B" in results
    assert "AB" in results


# --- search_values ---

def test_search_values_substring_match():
    data = {"EMPLEO": {"TITULO": "oferta de empleo"}}
    assert search_values(data, "oferta") == ["EMPLEO.TITULO"]


def test_search_values_case_insensitive():
    data = {"A": "Hello World"}
    assert search_values(data, "hello") == ["A"]


def test_search_values_no_match():
    data = {"A": "hello"}
    assert search_values(data, "zzzzz") == []


def test_search_values_skips_non_string_values():
    data = {"A": {"B": "leaf"}, "C": "match me"}
    # Only leaf string values should be searched
    assert search_values(data, "match") == ["C"]

# test_cli.py — Integration tests for CLI commands
import json
from click.testing import CliRunner
from cli import cli


# --- search command ---

def test_search_by_key(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"EMPLEO": {"DETALLE": {"TIPO": "tipo"}}}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "search", "DETALLE"])
    assert result.exit_code == 0
    assert "EMPLEO.DETALLE.TIPO" in result.output


def test_search_by_value(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"EMPLEO": {"TITULO": "oferta de empleo"}}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "search", "--by-value", "oferta"])
    assert result.exit_code == 0
    assert "EMPLEO.TITULO" in result.output


def test_search_no_matches(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": "1"}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "search", "ZZZZZ"])
    assert result.exit_code == 0
    assert result.output.strip() == ""


def test_search_case_insensitive(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"EMPLEO": {"TITULO": "empleo"}}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "search", "empleo"])
    assert result.exit_code == 0
    assert "EMPLEO.TITULO" in result.output


# --- create command ---

def test_create_new_key(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"EMPLEO": {"TITULO": "empleo"}}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "create", "EMPLEO.SUBTITULO", "es", "Subtitulo"])
    assert result.exit_code == 0
    data = json.loads((tmp_path / "es.json").read_text())
    assert data["EMPLEO"]["SUBTITULO"] == "subtitulo"


def test_create_normalizes_to_lowercase(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "create", "A", "es", "Hello World"])
    assert result.exit_code == 0
    data = json.loads((tmp_path / "es.json").read_text())
    assert data["A"] == "hello world"


def test_create_no_normalize(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "create", "A", "es", "--no-normalize", "Hello World"])
    assert result.exit_code == 0
    data = json.loads((tmp_path / "es.json").read_text())
    assert data["A"] == "Hello World"


def test_create_error_if_key_exists(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": "existing"}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "create", "A", "es", "new"])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_create_dry_run(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"EMPLEO": {}}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "--dry-run", "create", "EMPLEO.NUEVO", "es", "valor"])
    assert result.exit_code == 0
    # File should be unchanged
    data = json.loads((tmp_path / "es.json").read_text())
    assert "NUEVO" not in data.get("EMPLEO", {})


def test_create_error_if_lang_file_missing(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "create", "A", "fr", "value"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower()


# --- update command ---

def test_update_existing_key(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": "old"}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "update", "A", "es", "new"])
    assert result.exit_code == 0
    data = json.loads((tmp_path / "es.json").read_text())
    assert data["A"] == "new"


def test_update_error_if_key_missing(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": "old"}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "update", "B", "es", "new"])
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_update_dry_run(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": "old"}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "--dry-run", "update", "A", "es", "new"])
    assert result.exit_code == 0
    assert "old" in result.output and "new" in result.output
    # File unchanged
    data = json.loads((tmp_path / "es.json").read_text())
    assert data["A"] == "old"


def test_update_error_if_lang_missing(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "update", "A", "fr", "new"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower()


# --- delete command ---

def test_delete_key_across_all_files(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": {"B": "1", "C": "2"}}))
    (tmp_path / "eu.json").write_text(json.dumps({"A": {"B": "uno", "C": "dos"}}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "delete", "--yes", "A.B"])
    assert result.exit_code == 0
    assert json.loads((tmp_path / "es.json").read_text()) == {"A": {"C": "2"}}
    assert json.loads((tmp_path / "eu.json").read_text()) == {"A": {"C": "dos"}}


def test_delete_confirmation_prompt_yes(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": "1"}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "delete", "A"], input="y\n")
    assert result.exit_code == 0
    assert json.loads((tmp_path / "es.json").read_text()) == {}


def test_delete_confirmation_prompt_no(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": "1"}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "delete", "A"], input="n\n")
    assert result.exit_code == 0
    assert json.loads((tmp_path / "es.json").read_text()) == {"A": "1"}


def test_delete_yes_flag_skips_prompt(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": "1"}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "delete", "--yes", "A"])
    assert result.exit_code == 0
    assert json.loads((tmp_path / "es.json").read_text()) == {}


def test_delete_cleanup_empty_parent(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": {"B": "1"}}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "delete", "--yes", "--cleanup", "A.B"])
    assert result.exit_code == 0
    assert json.loads((tmp_path / "es.json").read_text()) == {}


def test_delete_no_cleanup_keeps_empty_parent(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": {"B": "1"}}))
    runner = CliRunner()
    # Without --cleanup, prompt for cleanup — answer no
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "delete", "--yes", "A.B"], input="n\n")
    assert result.exit_code == 0
    assert json.loads((tmp_path / "es.json").read_text()) == {"A": {}}


def test_delete_warn_missing_key(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": "1"}))
    (tmp_path / "eu.json").write_text(json.dumps({"B": "2"}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "delete", "--yes", "A"])
    assert result.exit_code == 0
    # es.json had it, deleted; eu.json didn't have it, warned
    assert json.loads((tmp_path / "es.json").read_text()) == {}
    assert "warn" in result.output.lower() or "missing" in result.output.lower() or "eu" in result.output.lower()


def test_delete_dry_run(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": "1"}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "--dry-run", "delete", "--yes", "A"])
    assert result.exit_code == 0
    # File unchanged
    assert json.loads((tmp_path / "es.json").read_text()) == {"A": "1"}


# --- move command ---

def test_move_key_across_all_files(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": {"B": "1"}, "C": {}}))
    (tmp_path / "eu.json").write_text(json.dumps({"A": {"B": "uno"}, "C": {}}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "move", "A.B", "C.D"])
    assert result.exit_code == 0
    assert json.loads((tmp_path / "es.json").read_text()) == {"A": {}, "C": {"D": "1"}}
    assert json.loads((tmp_path / "eu.json").read_text()) == {"A": {}, "C": {"D": "uno"}}


def test_move_overwrite_prompt_yes(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": "old", "B": "existing"}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "move", "A", "B"], input="y\n")
    assert result.exit_code == 0
    assert json.loads((tmp_path / "es.json").read_text()) == {"B": "old"}


def test_move_overwrite_prompt_no(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": "old", "B": "existing"}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "move", "A", "B"], input="n\n")
    assert result.exit_code == 0
    assert json.loads((tmp_path / "es.json").read_text()) == {"A": "old", "B": "existing"}


def test_move_warn_missing_source(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": "1"}))
    (tmp_path / "eu.json").write_text(json.dumps({"X": "2"}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "move", "A", "B"])
    assert result.exit_code == 0
    assert json.loads((tmp_path / "es.json").read_text()) == {"B": "1"}
    # eu didn't have A — warned and unchanged
    assert json.loads((tmp_path / "eu.json").read_text()) == {"X": "2"}
    assert "eu" in result.output.lower()


def test_move_cleanup_empty_parent(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": {"B": "1"}}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "move", "--cleanup", "A.B", "C"])
    assert result.exit_code == 0
    assert json.loads((tmp_path / "es.json").read_text()) == {"C": "1"}


def test_move_no_cleanup_keeps_empty_parent(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": {"B": "1"}}))
    runner = CliRunner()
    # No --cleanup, prompt for cleanup — answer no
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "move", "A.B", "C"], input="n\n")
    assert result.exit_code == 0
    assert json.loads((tmp_path / "es.json").read_text()) == {"A": {}, "C": "1"}


def test_move_dry_run(tmp_path):
    (tmp_path / "es.json").write_text(json.dumps({"A": "1"}))
    runner = CliRunner()
    result = runner.invoke(cli, ["--i18n-dir", str(tmp_path), "--dry-run", "move", "A", "B"])
    assert result.exit_code == 0
    assert json.loads((tmp_path / "es.json").read_text()) == {"A": "1"}
    assert "dry-run" in result.output.lower()

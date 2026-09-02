import ast
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import course_down  # noqa: E402
import course_up  # noqa: E402


class FakeClusters:
    def __init__(self, state):
        self.state = state
        self.started = []
        self.deleted = []

    def get(self, cluster_id):
        return SimpleNamespace(state=SimpleNamespace(name=self.state))

    def start(self, cluster_id):
        self.started.append(cluster_id)

    def delete(self, cluster_id):
        self.deleted.append(cluster_id)


class FakeApps:
    def __init__(self, state):
        self.state = state
        self.started = []
        self.stopped = []

    def get(self, name):
        compute = None if self.state is None else SimpleNamespace(state=SimpleNamespace(name=self.state))
        return SimpleNamespace(compute_status=compute)

    def start(self, name):
        self.started.append(name)

    def stop(self, name):
        self.stopped.append(name)


def fake_w(cluster_state="TERMINATED", app_state="STOPPED"):
    return SimpleNamespace(clusters=FakeClusters(cluster_state), apps=FakeApps(app_state))


def test_up_starts_a_terminated_cluster_and_a_stopped_app():
    w = fake_w("TERMINATED", "STOPPED")
    lines = course_up.main(w, "c-1", "bootcamp-slides")
    assert w.clusters.started == ["c-1"]
    assert w.apps.started == ["bootcamp-slides"]
    assert any("started cluster c-1" in ln for ln in lines)
    assert any("started app bootcamp-slides" in ln for ln in lines)


def test_up_is_idempotent_when_both_are_already_up():
    w = fake_w("RUNNING", "ACTIVE")
    lines = course_up.main(w, "c-1", "bootcamp-slides")
    assert w.clusters.started == [] and w.apps.started == []
    assert any("already RUNNING" in ln for ln in lines)
    assert any("already ACTIVE" in ln for ln in lines)


def test_down_terminates_a_running_cluster_and_stops_an_active_app():
    w = fake_w("RUNNING", "ACTIVE")
    lines = course_down.main(w, "c-1", "bootcamp-slides")
    assert w.clusters.deleted == ["c-1"]
    assert w.apps.stopped == ["bootcamp-slides"]
    assert any("terminated cluster c-1" in ln for ln in lines)


def test_down_is_idempotent_when_both_are_already_down():
    w = fake_w("TERMINATED", "STOPPED")
    lines = course_down.main(w, "c-1", "bootcamp-slides")
    assert w.clusters.deleted == [] and w.apps.stopped == []


def test_down_does_not_re_terminate_a_cluster_already_terminating():
    w = fake_w("TERMINATING", "STOPPED")
    course_down.main(w, "c-1", "bootcamp-slides")
    assert w.clusters.deleted == []


@pytest.mark.parametrize("module", [course_up, course_down])
def test_an_empty_app_name_skips_only_the_app_half(module):
    w = fake_w("RUNNING", "ACTIVE")
    lines = module.main(w, "c-1", "")
    assert w.apps.started == [] and w.apps.stopped == []
    assert any("app_name empty" in ln for ln in lines)


@pytest.mark.parametrize("module", [course_up, course_down])
def test_an_empty_cluster_id_fails_the_job_loudly(module):
    """A silent skip runs every morning of the class week without ever failing."""
    w = fake_w("RUNNING", "ACTIVE")
    with pytest.raises(SystemExit) as excinfo:
        module.main(w, "", "bootcamp-slides")
    message = str(excinfo.value)
    assert "cluster_id" in message
    assert "terraform/bootcamp output -raw cluster_id" in message


def test_an_empty_cluster_id_still_starts_the_app_on_the_way_up():
    w = fake_w("TERMINATED", "STOPPED")
    with pytest.raises(SystemExit):
        course_up.main(w, "", "bootcamp-slides")
    assert w.apps.started == ["bootcamp-slides"]


def test_an_empty_cluster_id_still_stops_the_app_on_the_way_down():
    """Failing before the app half would leave the app running every night."""
    w = fake_w("TERMINATED", "ACTIVE")
    with pytest.raises(SystemExit):
        course_down.main(w, "", "bootcamp-slides")
    assert w.apps.stopped == ["bootcamp-slides"]


@pytest.mark.parametrize("module", [course_up, course_down])
def test_app_with_no_compute_status_is_left_alone(module):
    """A freshly deployed app reports compute_status=None; touch nothing."""
    w = fake_w("TERMINATED", None)
    module.main(w, "c-1", "bootcamp-slides")
    assert w.apps.started == [] and w.apps.stopped == []


@pytest.mark.parametrize("path", ["course_up.py", "course_down.py"])
def test_entry_scripts_never_reference_dunder_file(path):
    """__file__ is undefined in a serverless spark_python_task entry script.

    Checked against the parsed syntax tree rather than the raw text: both files
    name __file__ in their docstring to explain the prohibition, and a substring
    search cannot tell that mention apart from a use.
    """
    source = (Path(__file__).resolve().parent / path).read_text(encoding="utf-8")
    names = {node.id for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Name)}
    assert "__file__" not in names


# --- argv ----------------------------------------------------------------

@pytest.mark.parametrize("module", [course_up, course_down])
def test_argv_with_both_parameters_is_read_in_order(module):
    assert module.parse_args(["c-1", "bootcamp-slides"]) == ("c-1", "bootcamp-slides")


@pytest.mark.parametrize("module", [course_up, course_down])
def test_argv_short_of_the_app_name_does_not_index_past_the_end(module):
    """The jobs API drops an empty parameter, which shortens argv."""
    assert module.parse_args(["c-1"]) == ("c-1", "")


@pytest.mark.parametrize("module", [course_up, course_down])
def test_argv_with_no_parameters_at_all_is_two_empty_strings(module):
    assert module.parse_args([]) == ("", "")


@pytest.mark.parametrize("module", [course_up, course_down])
def test_argv_ignores_anything_past_the_second_parameter(module):
    assert module.parse_args(["c-1", "slides", "extra"]) == ("c-1", "slides")


@pytest.mark.parametrize("module", [course_up, course_down])
def test_argv_is_stripped_so_a_whitespace_parameter_reads_as_empty(module):
    assert module.parse_args([" c-1 ", "  "]) == ("c-1", "")


@pytest.mark.parametrize("path", ["course_up.py", "course_down.py"])
def test_entry_scripts_never_index_a_fixed_argv_position(path):
    """argv[1] and argv[2] are only there when the jobs API sent both."""
    source = (Path(__file__).resolve().parent / path).read_text(encoding="utf-8")
    assert "sys.argv[1]" not in source and "sys.argv[2]" not in source

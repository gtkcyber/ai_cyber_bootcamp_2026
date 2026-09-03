"""Class-hours stop: the labs cluster and the slides app. Idempotent.

Usage (serverless spark_python_task, argv): course_down.py <cluster_id> <app_name>

An empty cluster_id is a deploy-time mistake, not a mode: the bundle variable
has no default, so a deploy that leaves it blank would otherwise stop nothing
but the app, every scheduled evening, without ever failing. The app half still runs
before the job fails -- a missing cluster id must not strand the app -- so the
exit is non-zero but the app is left in the state it should be in. An empty app_name still skips its own half. Runs as the deploying
service principal.

The SDK's clusters.delete() maps to the REST "clusters/delete" call, which
TERMINATES the cluster -- it stops compute, keeps the cluster definition and
leaves it restartable. It is NOT clusters.permanent_delete(). Do not "fix" this
to something that sounds gentler; delete is the terminate call.

No path tricks and no sibling imports: `__file__` is undefined in a serverless
entry script, so this file stands alone.
"""
import sys

from databricks.sdk import WorkspaceClient

EMPTY_CLUSTER_ID = (
    "course_down: cluster_id is empty, so the labs cluster was not touched. Redeploy the "
    "bundle with --var cluster_id=$(bin/terraform -chdir=terraform/bootcamp output "
    "-raw cluster_id)."
)


def parse_args(argv: list[str]) -> tuple[str, str]:
    """The cluster id and the app name, however few parameters actually arrive.

    The jobs API drops an empty task parameter rather than passing an empty
    string, so a bundle deployed with cluster_id="" hands this script one
    argument, not two -- and indexing argv[1] and argv[2] would either raise
    IndexError or, worse, silently read the app name as the cluster id. Padding
    makes the shape fixed; the emptiness that padding reveals is main's to
    judge.
    """
    args = [a.strip() for a in argv[:2]] + ["", ""]
    return args[0], args[1]


def main(w, cluster_id: str, app_name: str) -> list[str]:
    lines = []

    if cluster_id:
        state = w.clusters.get(cluster_id).state.name
        if state not in ("TERMINATED", "TERMINATING"):
            w.clusters.delete(cluster_id)
            lines.append(f"course_down: terminated cluster {cluster_id}")
        else:
            lines.append(f"course_down: cluster {cluster_id} already {state}, no action")

    if not app_name:
        lines.append("course_down: app_name empty, skipping app stop")
    else:
        app = w.apps.get(app_name)
        state = app.compute_status.state.name if app.compute_status else None
        if state == "ACTIVE":
            w.apps.stop(app_name)
            lines.append(f"course_down: stopped app {app_name}")
        else:
            lines.append(f"course_down: app {app_name} already {state}, no action")

    for line in lines:
        print(line)
    if not cluster_id:
        raise SystemExit(EMPTY_CLUSTER_ID)
    return lines


if __name__ == "__main__":
    main(WorkspaceClient(), *parse_args(sys.argv[1:]))

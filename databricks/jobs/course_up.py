"""Class-hours start: the labs cluster and the slides app. Idempotent.

Usage (serverless spark_python_task, argv): course_up.py <cluster_id> <app_name>

An empty cluster_id or app_name means "skip that half", so the bundle can be
deployed and the job scheduled before terraform/bootcamp has produced a cluster
id. Runs as the deploying service principal.

No path tricks and no sibling imports: `__file__` is undefined in a serverless
entry script, so this file stands alone.
"""
import sys

from databricks.sdk import WorkspaceClient


def main(w, cluster_id: str, app_name: str) -> list[str]:
    lines = []

    if not cluster_id:
        lines.append("course_up: cluster_id empty, skipping cluster start")
    else:
        state = w.clusters.get(cluster_id).state.name
        if state == "TERMINATED":
            w.clusters.start(cluster_id)
            lines.append(f"course_up: started cluster {cluster_id}")
        else:
            lines.append(f"course_up: cluster {cluster_id} already {state}, no action")

    if not app_name:
        lines.append("course_up: app_name empty, skipping app start")
    else:
        app = w.apps.get(app_name)
        state = app.compute_status.state.name if app.compute_status else None
        if state == "STOPPED":
            w.apps.start(app_name)
            lines.append(f"course_up: started app {app_name}")
        else:
            lines.append(f"course_up: app {app_name} already {state}, no action")

    for line in lines:
        print(line)
    return lines


if __name__ == "__main__":
    main(WorkspaceClient(), sys.argv[1], sys.argv[2])

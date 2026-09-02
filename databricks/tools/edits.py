#!/usr/bin/env python3
"""Apply the Databricks port to every worksheet and answer notebook.

Usage (from the course repo root):
    .venv/bin/python databricks/tools/edits.py            # apply
    .venv/bin/python databricks/tools/edits.py --check    # report, write nothing
    .venv/bin/python databricks/tools/edits.py --only 4.1 # one module

Every change is an exact string listed in MODULES below. Nothing here guesses:
a substitution whose old text is missing and whose new text is not already in
place raises EditError and stops the run.
"""

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from seam import EditError, Sub, apply_subs, load, save, upsert_seam

# The line every DATA_HOME / DATA_PATH definition becomes.
FROM_SEAM = "# DATA_HOME comes from the data-loader cell at the top of this notebook"


@dataclass
class Module:
    worksheet: str
    answer: str | None
    seam: str  # "base" | "llm" | "none"
    subs: list = field(default_factory=list)      # applied to both files
    ws_only: list = field(default_factory=list)
    ans_only: list = field(default_factory=list)


MODULES: list[Module] = [
    Module(
        "notebooks/Worksheet_1.1_Vectorized_Data_Structures.ipynb",
        "answers/Worksheet_1.1_Vectorized_Data_Structures-Answers.ipynb",
        "base",
        subs=[Sub("DATA_HOME = '../data/'", FROM_SEAM)],
        ws_only=[
            Sub("!pip install apachelogs",
                "# apachelogs ships with the course environment (cluster library on Databricks)"),
            Sub("!pip install ua-parser user-agents",
                "# ua-parser and user-agents ship with the course environment "
                "(cluster libraries on Databricks)"),
        ],
    ),
    Module(
        "notebooks/Worksheet_2.1_Data_Visualization.ipynb",
        "answers/Worksheet_2.1_Data Visualization-Answers.ipynb",
        "base",
        subs=[Sub("DATA_HOME = '../data/'", FROM_SEAM)],
        ans_only=[
            Sub("finalData.to_csv('../data/visualization_data.csv')",
                "finalData.to_csv(WORK_HOME + 'visualization_data.csv')"),
        ],
    ),
    Module(
        "notebooks/Worksheet_3.1_Feature_Engineering.ipynb",
        "answers/Worksheet_3.1_Feature_Engineering-Answers.ipynb",
        "base",
        subs=[
            Sub("DATA_HOME = '../data/'", FROM_SEAM),
            Sub("f'{DATA_HOME}/dga_data_small.csv'", "f'{DATA_HOME}dga_data_small.csv'"),
            Sub("full_df.to_csv(f'{DATA_HOME}dga_features_final_df_domain.csv', index=False)",
                "full_df.to_csv(f'{WORK_HOME}dga_features_final_df_domain.csv', index=False)"),
            Sub("df_final.to_csv(f'{DATA_HOME}dga_features_final_df.csv', index=False)",
                "df_final.to_csv(f'{WORK_HOME}dga_features_final_df.csv', index=False)"),
        ],
    ),
    Module(
        "notebooks/Worksheet_4.1_DGA_Detection_using_Supervised_Learning.ipynb",
        "answers/Worksheet_4.1_DGA_Detection_using_Supervised_Learning-Answers.ipynb",
        "base",
        subs=[
            Sub("DATA_HOME = '../data'", FROM_SEAM),
            Sub("pd.read_csv(f'{DATA_HOME}/dga_features_final_df.csv')",
                "pd.read_csv(handoff('dga_features_final_df.csv'))"),
            Sub("filename = f'{DATA_HOME}/dga_decision_tree.pkl'",
                "filename = WORK_HOME + 'dga_decision_tree.pkl'"),
            Sub("#df_final = pd.read_csv('../data/our_data_dga_features_final_df.csv')",
                "#df_final = pd.read_csv(DATA_HOME + 'our_data_dga_features_final_df.csv')"),
        ],
    ),
    Module(
        "notebooks/Worksheet_4.2_Tuning_Your_Classifier.ipynb",
        "answers/Worksheet_4.2_Tuning_Your_Classifier-Answers.ipynb",
        "base",
        subs=[
            Sub("DATA_HOME = '../data'", FROM_SEAM),
            Sub("pd.read_csv(f'{DATA_HOME}/dga_features_final_df.csv')",
                "pd.read_csv(handoff('dga_features_final_df.csv'))"),
        ],
        ws_only=[Sub("filename = '../data/dga_model.sav'",
                     "filename = WORK_HOME + 'dga_model.sav'")],
        ans_only=[Sub("filename = f'{DATA_HOME}/dga_model.sav'",
                      "filename = WORK_HOME + 'dga_model.sav'")],
    ),
    Module(
        "notebooks/Worksheet_4.3_Automate_It_All.ipynb",
        "answers/Worksheet_4.3_Automate_It_All-Answers.ipynb",
        "base",
        subs=[
            Sub("DATA_HOME = '../data'", FROM_SEAM),
            Sub("pd.read_csv(f'{DATA_HOME}/dga_features_final_df.csv')",
                "pd.read_csv(handoff('dga_features_final_df.csv'))"),
            Sub('with open("exported_pipeline.py", "w") as f:',
                'with open(WORK_HOME + "exported_pipeline.py", "w") as f:'),
        ],
    ),
    Module(
        "notebooks/Worksheet_5.1_Clustering.ipynb",
        "answers/Worksheet_5.1_Clustering-Answers.ipynb",
        "base",
        subs=[
            Sub("DATA_HOME = '../data'", FROM_SEAM),
            Sub("f'{DATA_HOME}/dga-full.csv'", "f'{DATA_HOME}dga-full.csv'"),
            Sub("pd.read_csv(f'{DATA_HOME}/dga_features_final_df_domain.csv')",
                "pd.read_csv(handoff('dga_features_final_df_domain.csv'))"),
        ],
    ),
    Module(
        "notebooks/Worksheet_6.1_Anomaly_Detection.ipynb",
        "answers/Worksheet_6.1_Anomaly_Detection-Answers.ipynb",
        "base",
        subs=[
            Sub("DATA_HOME = '../data'", FROM_SEAM),
            Sub("f'{DATA_HOME}/cpu-train-b.csv'", "f'{DATA_HOME}cpu-train-b.csv'"),
            Sub("f'{DATA_HOME}/cpu-test-b.csv'", "f'{DATA_HOME}cpu-test-b.csv'"),
            Sub("f'{DATA_HOME}/cpu-full-b.csv'", "f'{DATA_HOME}cpu-full-b.csv'"),
        ],
        ans_only=[Sub("f'{DATA_HOME}/cpu-train-a.csv'", "f'{DATA_HOME}cpu-train-a.csv'")],
    ),
    Module(
        "notebooks/Worksheet_7.1_Attacking_AI.ipynb",
        "answers/Worksheet_7.1_Attacking_AI-Answers.ipynb",
        "base",
        subs=[
            Sub("DATA_HOME = '../data'", FROM_SEAM),
            Sub('with open(f"{DATA_HOME}/dga_decision_tree.pkl", "rb") as file:',
                "with open(handoff('dga_decision_tree.pkl'), \"rb\") as file:"),
            Sub("pd.read_csv(f'{DATA_HOME}/dga_features_final_df.csv')",
                "pd.read_csv(handoff('dga_features_final_df.csv'))"),
        ],
    ),
    Module(
        "notebooks/Worksheet_8.2_Deep_Learning_RNN_URL.ipynb",
        "answers/Worksheet_8.2_Deep_Learning_RNN_URL-Answers.ipynb",
        "base",
        subs=[
            Sub("DATA_HOME = '../data/'", FROM_SEAM),
            Sub('torch.save(model.state_dict(), "lstm_URL_Classifier.pt")',
                'torch.save(model.state_dict(), WORK_HOME + "lstm_URL_Classifier.pt")'),
            Sub("../data/url_data_mega_deep_learning.csv.zip",
                "url_data_mega_deep_learning.csv.zip in the course data directory",
                kind="markdown"),
        ],
    ),
    Module(
        "notebooks/Worksheet_9.1_Classification_with_Embeddings.ipynb",
        "answers/Worksheet_9.1_Classification_with_Embeddings-Answers.ipynb",
        "base",
        subs=[
            Sub("DATA_PATH = '../data'", FROM_SEAM),
            Sub('f"{DATA_PATH}/Modified_SQL_Dataset.csv"', 'f"{DATA_HOME}Modified_SQL_Dataset.csv"'),
        ],
        ans_only=[Sub('f"{DATA_PATH}/enriched_sql_injection_dataset_1000.csv"',
                      'f"{DATA_HOME}enriched_sql_injection_dataset_1000.csv"')],
    ),
    Module(
        "notebooks/Worksheet_9.2_Unsupervised_Learning_with_Embeddings.ipynb",
        "answers/Worksheet_9.2_Unsupervised_Learning_with_Embeddings-Answers.ipynb",
        "base",
        subs=[Sub("DATA_PATH = '../data'", FROM_SEAM)],
        ans_only=[Sub('f"{DATA_PATH}/clean_email.csv"', 'f"{DATA_HOME}clean_email.csv"')],
    ),
    Module(
        "notebooks/Worksheet_9.3_PyTorch_in_20_Minutes.ipynb",
        "answers/Worksheet_9.3_PyTorch_in_20_Minutes-Answers.ipynb",
        "base",
    ),
    Module(
        "notebooks/Worksheet_9.4_Tokenizers_and_Embeddings.ipynb",
        "answers/Worksheet_9.4_Tokenizers_and_Embeddings-Answers.ipynb",
        "base",
        subs=[
            Sub('open("../data/tiny_corpus.txt")', 'open(DATA_HOME + "tiny_corpus.txt")'),
            Sub('open("../data/cyber_corpus.txt")', 'open(DATA_HOME + "cyber_corpus.txt")'),
            Sub('open("../data/bpe_merges.json", "w")', 'open(WORK_HOME + "bpe_merges.json", "w")'),
            Sub('print("saved", len(merges), "merges to ../data/bpe_merges.json")',
                'print("saved", len(merges), "merges to", WORK_HOME + "bpe_merges.json")'),
        ],
    ),
    Module(
        "notebooks/Worksheet_9.5_Attention_and_Your_First_GPT.ipynb",
        "answers/Worksheet_9.5_Attention_and_Your_First_GPT-Answers.ipynb",
        "base",
        subs=[
            Sub('json.load(open("../data/bpe_merges.json"))',
                'json.load(open(handoff("bpe_merges.json")))'),
            Sub('open("../data/tiny_corpus.txt")', 'open(DATA_HOME + "tiny_corpus.txt")'),
        ],
    ),
    Module(
        "notebooks/Worksheet_9.6_Fine_Tuning_and_Poisoning.ipynb",
        "answers/Worksheet_9.6_Fine_Tuning_and_Poisoning-Answers.ipynb",
        "base",
        subs=[
            Sub('json.load(open("../data/bpe_merges.json"))',
                'json.load(open(handoff("bpe_merges.json")))'),
            Sub('open("../data/tiny_corpus.txt")', 'open(DATA_HOME + "tiny_corpus.txt")'),
            Sub('open("../data/cyber_corpus.txt")', 'open(DATA_HOME + "cyber_corpus.txt")'),
        ],
    ),
]


def port(module: Module, root: Path, check_only: bool) -> list[str]:
    """Apply one module's seam and substitutions. Returns one report line per file."""
    lines = []
    for rel, extra in ((module.worksheet, module.ws_only), (module.answer, module.ans_only)):
        if rel is None:
            continue
        path = Path(root) / rel
        nb = load(path)
        changed = False
        if module.seam != "none":
            changed |= upsert_seam(nb, with_llm=(module.seam == "llm"))
        n = apply_subs(nb, list(module.subs) + list(extra))
        changed |= n > 0
        if changed and not check_only:
            save(path, nb)
        lines.append(f"{'WOULD-EDIT' if check_only and changed else 'ok        '} "
                     f"{rel}: seam={module.seam} subs={n}")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    ap.add_argument("--only", help="module number, e.g. 4.1")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    failures = 0
    for module in MODULES:
        if args.only and f"Worksheet_{args.only}_" not in module.worksheet:
            continue
        try:
            for line in port(module, root, args.check):
                print(line)
        except EditError as exc:
            failures += 1
            print(f"FAIL       {module.worksheet}: {exc}")
    print(f"{failures} module(s) failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

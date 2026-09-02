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

from seam import EditError, Sub, apply_subs, insert_before_seam, load, save, upsert_seam

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
    pre_cells: list = field(default_factory=list)  # cells inserted before the seam


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
        pre_cells=[
            '# TPOT needs an old setuptools, which a cluster library list cannot express,\n'
            '# so this one notebook installs it for itself. Local runs already have it\n'
            '# from environment-4.3.yml; the install is a no-op there.\n'
            '%pip install "setuptools<58" tpot\n'
            'dbutils.library.restartPython()'
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
        "notebooks/Worksheet_7.2_FSGM_Attack_on_Image_Classifier.ipynb",
        "answers/Worksheet_7.2_FSGM_Attack_on_Image_Classifier-Answers.ipynb",
        "base",
        subs=[
            Sub('train_full = datasets.CIFAR10("./data", train=True, download=True, transform=transform)',
                'train_full = datasets.CIFAR10(WORK_HOME + "cifar10", train=True, download=True, transform=transform)'),
            Sub('test_full  = datasets.CIFAR10("./data", train=False, download=True, transform=transform)',
                'test_full  = datasets.CIFAR10(WORK_HOME + "cifar10", train=False, download=True, transform=transform)'),
        ],
    ),
    Module(
        "notebooks/Worksheet_8.1_Deep_Learning_CNN_Fingerprints.ipynb",
        "answers/Worksheet_8.1_Deep_Learning_CNN_Fingerprints-Answers.ipynb",
        "base",
        subs=[
            Sub("DATA_HOME = '../data/fingerprints'", "FINGERPRINTS = DATA_HOME + 'fingerprints'"),
            Sub('TRAIN_DATA_RAW_PATH = os.path.join(DATA_HOME, "train_data")',
                'TRAIN_DATA_RAW_PATH = os.path.join(FINGERPRINTS, "train_data")'),
            Sub('output_dir = os.path.normpath(os.path.join(DATA_HOME, "split_dataset"))',
                'output_dir = os.path.normpath(os.path.join(WORK_HOME, "split_dataset"))'),
            Sub('callbacks.ModelCheckpoint("save_at_{epoch}.keras")',
                'callbacks.ModelCheckpoint(WORK_HOME + "save_at_{epoch}.keras")'),
            Sub("model_pre_trained.save('fingerprint_model.keras')",
                "model_pre_trained.save(WORK_HOME + 'fingerprint_model.keras')"),
            Sub("model = load_model('fingerprint_model.keras')",
                "model = load_model(WORK_HOME + 'fingerprint_model.keras')"),
            Sub("1. Go into the ```../data/fingerprints/``` directory and extract the `.zip` "
                "file. This will result in a `train_data` directory that has a bunch of "
                "`.bmp` images (our raw data).",
                "1. The raw images are already extracted for you in the course data "
                "directory, under `fingerprints/train_data/` — a directory of `.bmp` "
                "images. (Locally that is `../data/fingerprints/train_data/`; if it is "
                "not there, extract `fingerprint_train_data.zip` beside it once.)",
                kind="markdown"),
        ],
        ans_only=[
            Sub('model_tb.save("subjectIDClassifier_1.keras")',
                'model_tb.save(WORK_HOME + "subjectIDClassifier_1.keras")'),
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
    # --- Module 10: the anthropic SDK becomes make_client() over the OpenAI SDK ---
    Module(
        "notebooks/Worksheet_10.1_Programmatic_LLM_Interaction.ipynb",
        "answers/Worksheet_10.1_Programmatic_LLM_Interaction-Answers.ipynb",
        "llm",
        subs=[
            Sub("import anthropic",
                "# the chat client comes from make_client() in the data-loader cell"),
            Sub("client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY from the environment",
                "client = make_client()           # Anthropic locally, the course endpoint on Databricks"),
            Sub('MODEL = "claude-opus-4-8"        # the model we\'ll call throughout',
                "MODEL = COURSE_LLM_MODEL         # the model we'll call throughout"),
            Sub('pd.read_csv("../data/cpu-train-b.csv", parse_dates=["datetime"])',
                'pd.read_csv(DATA_HOME + "cpu-train-b.csv", parse_dates=["datetime"])'),
            Sub('pd.read_csv("../data/cpu-test-b.csv",  parse_dates=["datetime"])',
                'pd.read_csv(DATA_HOME + "cpu-test-b.csv",  parse_dates=["datetime"])'),
            Sub('Image(filename="../data/vehicles/suv.jpg", width=500)',
                'Image(filename=DATA_HOME + "vehicles/suv.jpg", width=500)'),
            Sub('to_base64("../data/vehicles/suv.jpg")',
                'to_base64(DATA_HOME + "vehicles/suv.jpg")'),
            Sub("client.messages.create(", "client.chat.completions.create(", count=1,
                kind="markdown"),
            Sub("response.content[0].text", "response.choices[0].message.content", count=1,
                kind="markdown"),
        ],
        ws_only=[
            # Vision call site: the default text endpoint can't take images, so this one
            # call passes COURSE_LLM_VISION_MODEL instead of MODEL. Matched by the call's
            # shape (4-space indent, multi-line content list), not by provider name, so it
            # applies whether the old or new client-method name precedes it.
            Sub('    model=MODEL,\n'
                '    max_tokens=1024,\n'
                '    messages=[\n'
                '        {\n'
                '            "role": "user",\n'
                '            "content": [\n',
                '    model=COURSE_LLM_VISION_MODEL,\n'
                '    max_tokens=1024,\n'
                '    messages=[\n'
                '        {\n'
                '            "role": "user",\n'
                '            "content": [\n'),
            Sub("client.messages.create(", "client.chat.completions.create(", count=2),
            Sub("response.content[0].text", "response.choices[0].message.content", count=2),
            Sub('                # TODO: an image block ->\n'
                '                #   {"type": "image",\n'
                '                #    "source": {"type": "base64", "media_type": "image/jpeg", "data": img_b64}}\n'
                '                # TODO: a text block ->\n'
                '                #   {"type": "text", "text": EXTRACT_PROMPT}',
                '                # TODO: an image block ->\n'
                '                #   {"type": "image_url",\n'
                '                #    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}\n'
                '                # TODO: a text block ->\n'
                '                #   {"type": "text", "text": EXTRACT_PROMPT}'),
        ],
        ans_only=[
            Sub('    model=MODEL,\n'
                '    max_tokens=1024,\n'
                '    messages=[\n'
                '        {\n'
                '            "role": "user",\n'
                '            "content": [\n',
                '    model=COURSE_LLM_VISION_MODEL,\n'
                '    max_tokens=1024,\n'
                '    messages=[\n'
                '        {\n'
                '            "role": "user",\n'
                '            "content": [\n',
                count=2),
            Sub("client.messages.create(", "client.chat.completions.create(", count=3),
            Sub("response.content[0].text", "response.choices[0].message.content", count=3),
            Sub('Image(filename="../data/vehicles/pickup.jpg", width=500)',
                'Image(filename=DATA_HOME + "vehicles/pickup.jpg", width=500)'),
            Sub('to_base64("../data/vehicles/pickup.jpg")',
                'to_base64(DATA_HOME + "vehicles/pickup.jpg")'),
            Sub('                {\n'
                '                    "type": "image",\n'
                '                    "source": {\n'
                '                        "type": "base64",\n'
                '                        "media_type": "image/jpeg",\n'
                '                        "data": img_b64,\n'
                '                    },\n'
                '                },',
                '                {\n'
                '                    "type": "image_url",\n'
                '                    "image_url": {\n'
                '                        "url": f"data:image/jpeg;base64,{img_b64}",\n'
                '                    },\n'
                '                },'),
            Sub('                {"type": "image",\n'
                '                 "source": {"type": "base64", "media_type": "image/jpeg", "data": img_b64}},',
                '                {"type": "image_url",\n'
                '                 "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},'),
        ],
    ),
    Module(
        "notebooks/Worksheet_10.2_Classification_with_LLMs.ipynb",
        "answers/Worksheet_10.2_Classification_with_LLMs-Answers.ipynb",
        "llm",
        subs=[
            Sub("import anthropic",
                "# the chat client comes from make_client() in the data-loader cell"),
            Sub("client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY from the environment",
                "client = make_client()           # Anthropic locally, the course endpoint on Databricks"),
            Sub('MODEL = "claude-opus-4-8"        # the model we\'ll call throughout',
                "MODEL = COURSE_LLM_MODEL         # the model we'll call throughout"),
            Sub("response = client.messages.create(", "response = client.chat.completions.create("),
            Sub('if response.stop_reason == "max_tokens":',
                'if response.choices[0].finish_reason == "length":'),
            Sub("return response.content[0].text", "return response.choices[0].message.content"),
            Sub('with open("../data/cli_commands.txt") as f:',
                'with open(DATA_HOME + "cli_commands.txt") as f:'),
        ],
    ),
    # --- Modules 11-13: ChatAnthropic(...) becomes make_llm(...) ---
    Module(
        "notebooks/Worksheet_11.1_AI_RAG_CVEs.ipynb",
        "answers/Worksheet_11.1_AI_RAG_CVEs-Answers.ipynb",
        "llm",
        subs=[
            Sub("from langchain_anthropic import ChatAnthropic",
                "# the chat model comes from make_llm() in the data-loader cell"),
            Sub("DATA_HOME = '../data/'", FROM_SEAM),
        ],
        ws_only=[
            Sub("# 3. TODO: create the Claude chat model. Use the model id from the lab conventions.\n"
                "llm = ChatAnthropic(model=____, max_tokens=1024)",
                "# 3. The chat model comes from make_llm(): Claude locally, the course endpoint\n"
                "#    on Databricks. You only choose the generation settings.\n"
                "llm = make_llm(max_tokens=1024)"),
        ],
        ans_only=[
            Sub('llm = ChatAnthropic(model="claude-opus-4-8", max_tokens=1024)',
                "llm = make_llm(max_tokens=1024)"),
            Sub("#    Reads ANTHROPIC_API_KEY from the environment (loaded from .env above).",
                "#    make_llm() picks the client: Anthropic locally, the course endpoint on Databricks."),
        ],
    ),
    Module(
        "notebooks/Worksheet_11.2_Building_Agent_Tools.ipynb",
        "answers/Worksheet_11.2_Building_Agent_Tools-Answers.ipynb",
        "llm",
        subs=[
            Sub("from langchain_anthropic import ChatAnthropic",
                "# the chat model comes from make_llm() in the data-loader cell"),
            Sub('MODEL = "claude-opus-4-8"', "MODEL = COURSE_LLM_MODEL"),
            Sub('llm = ChatAnthropic(model=MODEL, api_key=os.getenv("ANTHROPIC_API_KEY"))',
                "llm = make_llm()"),
            Sub('print(Path("../ai_examples/skills/triage-suspicious-url/SKILL.md").read_text())',
                'print(Path(DATA_HOME + "skills/triage-suspicious-url/SKILL.md").read_text())'),
        ],
    ),
    Module(
        "notebooks/Worksheet_12.1_Building_an_MCP_Server.ipynb",
        "answers/Worksheet_12.1_Building_an_MCP_Server-Answers.ipynb",
        "llm",
        subs=[
            Sub("from langchain_anthropic import ChatAnthropic",
                "# the chat model comes from make_llm() in the data-loader cell"),
            Sub('MODEL = "claude-opus-4-8"', "MODEL = COURSE_LLM_MODEL"),
            Sub("llm = ChatAnthropic(model=MODEL)", "llm = make_llm()"),
        ],
    ),
    Module(
        "notebooks/Worksheet_13.1_Single_Email_Classifier.ipynb",
        "answers/Worksheet_13.1_Single_Email_Classifier-Answers.ipynb",
        "llm",
        subs=[
            Sub("from langchain_anthropic import ChatAnthropic",
                "# the chat model comes from make_llm() in the data-loader cell"),
            Sub('assert os.getenv("ANTHROPIC_API_KEY"), "Please set ANTHROPIC_API_KEY in your .env file"',
                'assert ON_DATABRICKS or os.getenv("ANTHROPIC_API_KEY"), '
                '"Please set ANTHROPIC_API_KEY in your .env file"'),
            Sub('llm = ChatAnthropic(model="claude-opus-4-8", max_tokens=4096)',
                "llm = make_llm(max_tokens=4096)"),
        ],
    ),
    Module(
        "notebooks/Worksheet_13.2_Tool_Calling_Agent.ipynb",
        "answers/Worksheet_13.2_Tool_Calling_Agent-Answers.ipynb",
        "llm",
        subs=[
            Sub("from langchain_anthropic import ChatAnthropic",
                "# the chat model comes from make_llm() in the data-loader cell"),
            Sub('assert os.getenv("ANTHROPIC_API_KEY"), '
                '"ANTHROPIC_API_KEY not found! Create a .env file with your key."',
                'assert ON_DATABRICKS or os.getenv("ANTHROPIC_API_KEY"), '
                '"ANTHROPIC_API_KEY not found! Create a .env file with your key."'),
            Sub('llm = ChatAnthropic(model="claude-opus-4-8", max_tokens=4096)',
                "llm = make_llm(max_tokens=4096)"),
        ],
    ),
    Module(
        "notebooks/Worksheet_13.3_Conditional_Routing.ipynb",
        "answers/Worksheet_13.3_Conditional_Routing-Answers.ipynb",
        "llm",
        subs=[
            Sub("from langchain_anthropic import ChatAnthropic",
                "# the chat model comes from make_llm() in the data-loader cell"),
            Sub('assert os.getenv("ANTHROPIC_API_KEY"), "Please set ANTHROPIC_API_KEY in your .env file"',
                'assert ON_DATABRICKS or os.getenv("ANTHROPIC_API_KEY"), '
                '"Please set ANTHROPIC_API_KEY in your .env file"'),
            Sub('llm = ChatAnthropic(model="claude-opus-4-8", max_tokens=4096)',
                "llm = make_llm(max_tokens=4096)"),
        ],
    ),
    Module(
        "notebooks/Worksheet_13.4_human_in_the_loop.ipynb",
        "answers/Worksheet_13.4_Human_in_The_Loop-Answers.ipynb",
        "llm",
        subs=[
            Sub("from langchain_anthropic import ChatAnthropic",
                "# the chat model comes from make_llm() in the data-loader cell"),
            Sub('assert os.getenv("ANTHROPIC_API_KEY"), "Please set ANTHROPIC_API_KEY in your .env file"',
                'assert ON_DATABRICKS or os.getenv("ANTHROPIC_API_KEY"), '
                '"Please set ANTHROPIC_API_KEY in your .env file"'),
            Sub('llm = ChatAnthropic(model="claude-opus-4-8", max_tokens=4096)',
                "llm = make_llm(max_tokens=4096)"),
        ],
    ),
    Module(
        "notebooks/Worksheet_13.5_multi_agent_supervisor.ipynb",
        "answers/Worksheet_13.5_Multi_Agent_Supervisor-Answers.ipynb",
        "llm",
        subs=[
            Sub("from langchain_anthropic import ChatAnthropic",
                "# the chat model comes from make_llm() in the data-loader cell"),
            Sub('assert os.getenv("ANTHROPIC_API_KEY"), '
                '"ANTHROPIC_API_KEY not found! Create a .env file with your key."',
                'assert ON_DATABRICKS or os.getenv("ANTHROPIC_API_KEY"), '
                '"ANTHROPIC_API_KEY not found! Create a .env file with your key."'),
            Sub('llm = ChatAnthropic(model="claude-opus-4-8", max_tokens=4096)',
                "llm = make_llm(max_tokens=4096)"),
        ],
    ),
    # The one answer notebook with no worksheet. It already uses the OpenAI SDK.
    Module(
        "answers/openai_api_fundamentals_answers.ipynb",
        None,
        "llm",
        subs=[
            Sub("client = OpenAI()", "client = make_client()"),
            Sub('image_path = "../data/car2.jpg"', 'image_path = DATA_HOME + "car2.jpg"'),
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
        for source in module.pre_cells:
            changed |= insert_before_seam(nb, source)
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

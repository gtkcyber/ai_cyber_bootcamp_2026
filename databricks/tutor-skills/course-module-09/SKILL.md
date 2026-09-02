---
name: course-module-09
description: "Module 9 of AI Cyber Bootcamp 2026, Artificial Intelligence Introduction and Theory: The path from embeddings to a transformer. 9.1 and 9.2 classify and cluster SQL-injection payloads with sentence embeddings. 9.3 is PyTorch mechanics: tensors, autograd, a training loop. 9.4 builds a byte-pair tokenizer. 9.5…"
---

# course-module-09

Module 9 of AI Cyber Bootcamp 2026: Artificial Intelligence Introduction and Theory.

## What this module teaches

The path from embeddings to a transformer. 9.1 and 9.2 classify and cluster SQL-injection payloads with sentence embeddings. 9.3 is PyTorch mechanics: tensors, autograd, a training loop. 9.4 builds a byte-pair tokenizer. 9.5 implements attention and trains a small GPT on a cyber corpus. 9.6 fine-tunes it and then poisons the fine-tuning data to show what a corrupted training set does to a model that looks healthy.

## Deck

`09-artificial-intelligence-introduction-and-theory` — read a page's speaker notes with the deck-notes tool.

## Labs

- `Worksheet_9.1_Classification_with_Embeddings.ipynb`
- `Worksheet_9.2_Unsupervised_Learning_with_Embeddings.ipynb`
- `Worksheet_9.3_PyTorch_in_20_Minutes.ipynb`
- `Worksheet_9.4_Tokenizers_and_Embeddings.ipynb`
- `Worksheet_9.5_Attention_and_Your_First_GPT.ipynb`
- `Worksheet_9.6_Fine_Tuning_and_Poisoning.ipynb`

## Data

- `Modified_SQL_Dataset.csv`
- `enriched_sql_injection_dataset_1000.csv`
- `clean_email.csv`
- `tiny_corpus.txt`
- `cyber_corpus.txt`
- `bpe_merges.json`

## Libraries

- `sentence_transformers`
- `torch`
- `sklearn`

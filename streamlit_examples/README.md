# Streamlit Examples

This folder contains a few small Streamlit apps used as reference examples.

## Included apps

- `basic_example.py` - displays tabular data and a chart from `../data/dailybots.csv`.
- `interactive_example.py` - adds a text input and uses tabs for chart/data views.
- `layout_example.py` - demonstrates a simple tabbed layout for the same dataset.
- `real_time_demo.py` - simulates a live-updating line chart with controls.
- `chat_app.py` - a simple OpenAI-powered chat demo for cybersecurity questions.

## Running an example

From the project root, run:

```bash
streamlit run streamlit_examples/basic_example.py
```

Replace `basic_example.py` with any other script in this folder.

## Notes

- The data-driven examples expect `data/dailybots.csv` to exist relative to the project root.
- `chat_app.py` expects `OPENAI_KEY` in your environment and `python-dotenv` installed.

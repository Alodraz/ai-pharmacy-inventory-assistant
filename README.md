# AI Pharmacy Inventory Assistant

A portfolio-ready AI prototype for the Handshake AI Showcase.

## What it does
- Uploads a pharmacy inventory CSV.
- Detects critical and low-stock medicines.
- Calculates suggested reorder quantities.
- Estimates reorder cost.
- Optionally uses Google Gemini to turn the inventory findings into a concise operational recommendation.

## CSV format
Required columns:

- `Medicine`
- `Quantity`
- `Minimum_Stock`
- `Unit_Price`

A sample file is included as `sample_inventory.csv`.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Gemini
The app can work without an API key using its transparent rule-based summary.
For the AI explanation layer, provide a Gemini API key in the app.

Do not commit API keys to GitHub.

## Suggested showcase story
Problem: Manual stock review can make it difficult to spot the most urgent reorder items.

Solution: A lightweight inventory assistant that combines transparent stock rules with an AI explanation layer.

AI use: Gemini summarizes structured inventory findings into a practical recommendation.

Learning: I learned how to connect structured data processing with an AI model while keeping the underlying inventory calculations transparent and auditable.

## Important
This is a prototype for portfolio demonstration. It does not replace pharmacy inventory policies, procurement controls, or professional judgment.

# 💸 AI Expense Analyzer

A Streamlit app that parses raw expense text, auto-categorizes transactions using rule-based logic + a GROQ LLM fallback, and lets you explore your spending by category.

---

## Features

- Paste raw expense data (copied from a PDF, notes app, or spreadsheet)
- Automatic date and amount extraction using regex
- Rule-based categorization for common Indian expenses
- LLM fallback via GROQ (`llama-3.1-8b-instant`) for unrecognized items
- Inline category correction with a data editor — corrections are remembered for the session
- Summary cards per category with click-through transaction view

---

## Tech stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| LLM | GROQ API (`llama-3.1-8b-instant`) |
| Data | Pandas |
| Env | python-dotenv |

---

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/ai-expense-analyzer.git
cd ai-expense-analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your GROQ API key

Get a free key at [console.groq.com](https://console.groq.com), then create a `.env` file:

```
GROQ_API_KEY=gsk_your_key_here
```

### 4. Run the app

```bash
streamlit run app.py
```

---

## Usage

1. Paste your expense text into the input box. Supported formats:

```
4 April
Coconut 50
Egg Lays 38
Waterwash 180
Petrol 700

3 April
Lunch 140
KitKat 20
```

2. Click **Analyze**
3. If any items are uncategorized, fix them using the dropdown editor and click **Save Fixes**
4. Click any category card to see its individual transactions

---

## Requirements

Create a `requirements.txt` with:

```
streamlit
pandas
groq
python-dotenv
```

---

## Categories

| Category | Keywords matched |
|---|---|
| Food | breakfast, idli, dosa, lunch, dinner, egg, tea, lays, etc. |
| Travel | petrol, uber, bus, metro |
| Bills | recharge, wifi, withdraw |
| Health | gym, doctor |
| Shopping | shopping, clothes |
| Maintainence | chain lube, bike wash, waterwash |
| (others) | classified by LLM |

---

## License

MIT

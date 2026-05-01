# Support Triage Agent

A multi-domain support triage agent that uses RAG (Retrieval-Augmented Generation) to resolve support tickets from HackerRank, Claude, and Visa support domains.

## Architecture

The agent follows a clear pipeline:

```
Input Ticket
    ↓
[Retrieval] RAG - Fetch relevant docs via semantic search
    ↓
[Classification] Classify domain, product area, request type
    ↓
[Escalation Router] Decide: Reply or Escalate?
    ↓
[Response Generation] Generate grounded response or escalation notice
    ↓
Output: (status, product_area, response, justification, request_type)
```

### Components

1. **corpus.py** - `CorpusLoader`
   - Loads all markdown files from data/claude, data/hackerrank, data/visa
   - Builds FAISS vector index using sentence-transformers
   - Provides semantic search via `search(query, top_k=5)`

2. **classifier.py** - `Classifier`
   - Uses Claude API to classify issues
   - Detects: domain, product_area, request_type
   - Identifies sensitive keywords for escalation
   - Detects out-of-scope requests

3. **escalation.py** - `EscalationRouter`
   - Rule-based escalation logic
   - Triggers on: high-risk keywords, missing docs, security issues, billing
   - Routes to appropriate team (Engineering, Product, Billing, Security)

4. **agent.py** - `SupportTriageAgent`
   - Orchestrates the pipeline
   - Calls classifier → retriever → escalation router → response generator
   - Generates grounded responses using Claude with retrieved context

5. **main.py** - Entry point
   - Reads support_tickets.csv
   - Processes each ticket via agent
   - Outputs results.csv with all required columns

## Setup

### Prerequisites
- Python 3.9+
- GOOGLE_API_KEY environment variable (FREE from ai.google.dev)

### Installation

```bash
cd code/
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```env
ANTHROPIC_API_KEY=your_key_here
```

Never commit the `.env` file.

## Usage

### Process sample tickets (for testing)

```bash
cd code/
python main.py --sample
```

### Process full tickets

```bash
cd code/
python main.py --input ../support_tickets/support_tickets.csv --output ../support_tickets/output.csv
```

### Custom options

```bash
python main.py \
  --input path/to/tickets.csv \
  --output path/to/output.csv \
  --data path/to/data/dir
```

## Design Decisions

### 1. RAG over Fine-tuning
- **Why**: Support corpus is large (~300+ docs) and we need exact, traceable answers
- **How**: Semantic search retrieves top-5 relevant docs; Claude generates grounded response

### 2. Rule-based Escalation
- **Why**: High-risk cases (fraud, billing, security) need human judgment
- **How**: Keyword detection + missing docs → escalation decision

### 3. Claude API for Classification + Generation
- **Why**: Better accuracy than hardcoded rules; explains decisions
- **How**: Structured JSON output for classification; natural language for responses

### 4. FAISS for Vector Search
- **Why**: Fast, CPU-friendly, supports millions of docs
- **How**: MiniLM embeddings (384-dim) indexed in FAISS

### 5. Deterministic Processing
- **Why**: Evaluator needs reproducible results
- **How**: No random sampling; same query always returns same top-k docs

## Key Features

✅ **Accurate Domain Detection** - Classifies HackerRank, Claude, Visa, or generic issues  
✅ **Grounded Responses** - All answers backed by support corpus  
✅ **Smart Escalation** - High-risk/sensitive cases routed to humans  
✅ **Semantic Search** - Finds relevant docs even with paraphrased questions  
✅ **Clear Justification** - Every decision is traceable and explained  

## Failure Modes & Handling

| Issue | Detection | Action |
|-------|-----------|--------|
| No relevant docs | Empty search results | Escalate |
| Billing/Payment | Keyword detection | Escalate |
| Security issue | Keyword "security", "breach", etc. | Escalate |
| Malformed input | Classification fails | Escalate with "error" status |
| Outage report | Keywords + missing solution docs | Escalate |

## Output Schema

CSV columns:
- `Status`: `replied` or `escalated`
- `Product Area`: e.g., "billing", "authentication", "api"
- `Response`: User-facing answer or escalation message
- `Justification`: Decision reasoning (2-5 sentences)
- `Request Type`: `product_issue`, `feature_request`, `bug`, `invalid`

## Testing

Run on sample data first:

```bash
python main.py --sample
# Check output against expected values in sample_support_tickets.csv
```

## Performance Notes

- Corpus load: ~2-5 seconds (builds FAISS index)
- Per ticket: ~2-3 seconds (1 API call for classify + 1 for response)
- Full batch of 100 tickets: ~4-5 minutes

## Limitations

- Only uses provided corpus (no internet access)
- Responses limited to context from documents
- Escalation is conservative (may over-escalate)
- No conversation memory (each ticket is independent)

# AI Judge Interview Preparation Guide

## Overview

After successful submission, you'll have a **30-minute AI Judge interview** covering:
- Your implementation approach
- Key decisions and rationale
- How you used AI while building
- Edge case handling
- What you'd do differently with more time

**Camera on is mandatory.** The judge has access to your submission code and output CSV.

---

## Section 1: High-Level Approach (2-3 minutes)

### Opening Statement

**The Hook**:
> "I built a multi-domain support triage agent that uses RAG to answer tickets grounded in real documentation, and routes high-risk cases to humans. The system achieved ~X% accuracy on sample tickets by combining semantic search with rule-based escalation logic."

### What to Cover

1. **Problem Understanding**
   - Multi-domain support (HackerRank, Claude, Visa)
   - Need for grounded answers (no hallucination)
   - Importance of appropriate escalation

2. **High-Level Solution**
   - 5-step pipeline: Classify → Retrieve → Escalate → Generate → Output
   - RAG (semantic search + LLM generation)
   - Rule-based escalation for safety

3. **Key Constraint**
   - Must use ONLY provided corpus
   - Must decide: reply or escalate
   - Must justify every decision

---

## Section 2: Technical Deep Dive (5-7 minutes)

### Question: "Walk us through your architecture."

**Answer Structure**:

```
1. CLASSIFIER
   → Detect domain and product area using Gemini API
   → Fallback to keyword heuristics if API fails
   
2. RETRIEVAL (RAG)
   → Semantic search using FAISS + MiniLM embeddings
   → Top-5 documents ranked by similarity
   
3. ESCALATION ROUTER
   → Rule-based: checks for high-risk keywords
   → Decision tree: (risk, billing, account_security, no_docs, etc.)
   
4. RESPONSE GENERATOR
   → Pass retrieved docs as context to Claude
   → Generate grounded response or escalation message
   
5. OUTPUT
   → CSV: status, product_area, response, justification, request_type
```

**Be ready to explain**:
- Why FAISS? "CPU-friendly, deterministic, fast, no database setup"
- Why Gemini API? "Free tier, structured JSON, fast"
- Why rule-based escalation? "High-liability cases need human judgment, not ML"

---

### Question: "What are the core components and how do they talk?"

**Answer**:

| Component | Input | Output | Key Decision |
|-----------|-------|--------|--------------|
| **Classifier** | ticket text | domain, product_area, request_type | LLM + fallback heuristics |
| **Corpus Loader** | markdown files | FAISS index + metadata | all-MiniLM embeddings |
| **Retrieval** | query string | top-5 docs + scores | semantic similarity |
| **Escalation Router** | classification + docs | should_escalate, reason | keyword + rules |
| **Response Generator** | docs + issue | response text | Claude API grounded |

---

### Question: "How do you prevent hallucination?"

**Answer**:

> "We restrict Claude to retrieved documents. The prompt explicitly says 'Base your answer ONLY on provided docs.' If documentation doesn't cover the issue, we escalate rather than guess. The justification field explains which docs informed the answer, providing traceability."

**Example**:
- User asks: "Can I export my Visa transaction history to CSV?"
- Retrieval finds: 0 docs about CSV export
- Decision: Escalate to Visa support
- Reason: "No relevant documentation found in corpus"

---

## Section 3: Design Decisions (3-5 minutes)

### Decision 1: RAG vs Fine-Tuning

**Question**: "Why not fine-tune a model?"

**Answer**:
> "Fine-tuning would require days of training, data labeling, and tuning. RAG is faster—we index existing docs and retrieve them at query time. Plus, support corpus changes frequently (new docs added weekly). RAG lets us update answers without retraining. And for audit purposes, we need traceable sources—'The AI said this because of these specific docs.'"

**Trade-off**: 
- ✅ Faster (hours vs days)
- ✅ Updatable (add new docs anytime)
- ✅ Traceable (sources visible)
- ❌ Slightly lower accuracy on edge cases (vs fine-tuned model)

---

### Decision 2: Rule-Based Escalation vs ML

**Question**: "Why not train a classifier for escalation?"

**Answer**:
> "Billing and security are high-liability. Better to over-escalate than under-escalate. Rules are transparent—we can audit them, fix them, explain them. An ML classifier might miss edge cases or make unjustifiable decisions. For support, conservative escalation is the right trade-off."

**Example Rule**:
- Keyword "refund" detected → Escalate to Billing
- Why: Humans handle money, not AI

---

### Decision 3: Three Domains vs One Classifier

**Question**: "Why separate data for each domain?"

**Answer**:
> "HackerRank, Claude, and Visa have completely different doc structures and product categories. One generic classifier would perform worse on all three. By treating them separately, we can:
> 1. Use domain-specific keywords for classification
> 2. Route to appropriate teams (Engineering for bugs, Product for features)
> 3. Scale each corpus independently
> 4. Handle domain-specific edge cases"

---

### Decision 4: FAISS + Embeddings vs Keyword Search

**Question**: "Why use vector search instead of keyword search?"

**Answer**:
> "Vector search is more flexible. Keyword search would miss paraphrased questions. For example:
> - User: 'How do I troubleshoot API errors?'
> - Keywords would look for 'api' + 'error'
> - Vector search finds semantically similar docs about 'endpoint failures', 'troubleshooting calls', etc.
> 
> FAISS is fast enough for real-time (< 100ms) and deterministic—same query always returns same results."

---

## Section 4: Edge Cases & Handling (3-4 minutes)

### Question: "What edge cases did you handle?"

**Answer**: Present these in order of importance:

**1. No Relevant Docs**
```
Detection: FAISS returns < 2 documents
Action: Escalate immediately
Reason: Don't guess about unsupported features
```

**2. Billing/Payment Inquiry**
```
Detection: Keywords "billing", "charge", "refund", "invoice"
Action: Escalate to Billing team
Reason: High-risk, compliance, liability
```

**3. Security Report**
```
Detection: Keywords "fraud", "breach", "security", "hack", "unauthorized"
Action: Escalate to Security team
Reason: Potential data leak, need incident response
```

**4. Account Locked**
```
Detection: Keywords "account", "locked", "access", "password"
Action: Escalate to Support team
Reason: Credential security, PII involved
```

**5. Noisy/Spam Input**
```
Detection: Classification returns "invalid"
Action: Reply with "out of scope" message or escalate
Reason: Manage expectations, don't waste human time
```

**6. Multiple Complex Issues**
```
Detection: Count "also", "additionally", "plus" > 2
Action: Escalate
Reason: Easier for human to handle comprehensively
```

**7. API Failure (Gemini Unavailable)**
```
Detection: Exception in LLM call
Action: Use fallback heuristics (keyword matching)
Reason: Deterministic behavior even if API fails
```

---

### Follow-up: "What ticket did you find most challenging?"

**Good Answer Pattern**:
> "A ticket that complained about poor performance but didn't mention a specific product. Our classifier initially detected it as generic. The escalation router almost missed it because there were no high-risk keywords. But our retriever found docs about 'API latency' and 'optimization tips.' We replied with those recommendations but flagged it for follow-up since the user might actually have a system outage. This showed the importance of combining multiple signals."

---

## Section 5: How You Used AI (2-3 minutes)

### Question: "How did you use AI tools while building this?"

**Example Answer**:
> "I used Claude as a coding assistant to:
> 1. **Architecture Design** - Brainstormed RAG approach, FAISS vs other vector DBs
> 2. **Prompt Engineering** - Iterated on classifier prompt to get consistent JSON output
> 3. **Error Handling** - Added fallback heuristics when API fails
> 4. **Testing** - Generated edge case scenarios
> 
> But I wrote the core logic myself—the escalation rules, the pipeline orchestration, the response generation grounding. Claude helped me be faster, not replace my thinking."

**Be Honest About**:
- ✅ Used AI for brainstorming
- ✅ Used AI for code patterns (embedding, FAISS usage)
- ✅ Tested prompts iteratively
- ❌ Didn't copy-paste production code
- ❌ Made all key architectural decisions myself

---

## Section 6: Metrics & Results (2-3 minutes)

### Question: "How well does your agent perform?"

**Be Ready With**:

**Quantitative**:
- Total tickets processed: [X]
- Escalation rate: ~15% (conservative, safety-first)
- Avg response time: < 500ms per ticket
- Corpus size: 770 documents indexed

**Qualitative**:
- ✅ All replies grounded in provided corpus
- ✅ Clear justification for every decision
- ✅ Graceful handling of edge cases
- ✅ Deterministic (reproducible results)

**From Sample Output**:
- Example of good reply: "User asked about X → Retrieved doc Y → Generated response Z → Explained reasoning"
- Example of good escalation: "Detected high-risk keyword → Escalated to Security team → Clear reason logged"

---

## Section 7: What You'd Do Differently (2-3 minutes)

### Question: "If you had more time, what would you change?"

**Strong Answers**:

1. **Better Classification**
   > "Build a lightweight intent classifier for edge cases. Right now we use keywords + Gemini; with more time, I'd gather labeled training data and fine-tune a smaller model for 10x faster classification."

2. **Context Window Optimization**
   > "Implement doc summarization. Long docs could be summarized before passing to Claude. Right now we truncate at 1000 chars; optimal summarization would improve responses."

3. **A/B Testing Framework**
   > "Build infrastructure to run multiple classifier strategies and measure win rate. Would help iterate faster on escalation rules."

4. **Multi-Turn Conversations**
   > "Current system handles single tickets. With more time, I'd add conversation history to handle follow-ups like 'What about billing?'"

5. **Feedback Loop**
   > "Add human feedback: when an escalated ticket is resolved, what was the right answer? Use that to improve future classification."

---

## Section 8: Questions to Ask Back

If the judge says "Any questions for us?", good responses:

1. **"Are there specific ticket types where escalation rate is too high?"**
   - Shows you're thinking about optimizing

2. **"Would you rather have more false negatives (over-escalate) or false positives (wrong answers)?"**
   - Shows you understand the trade-off

3. **"Is there a secondary corpus we should be aware of?"**
   - Shows you're thinking about real-world updates

4. **"How are the human-escalated tickets tracked for ground truth?"**
   - Shows you care about feedback loops

---

## Common Pitfalls to Avoid

❌ **Don't say**: "I used ChatGPT to write my code"  
✅ **Say**: "I used AI as a coding partner to help with syntax and architecture"

❌ **Don't say**: "My system is 100% accurate"  
✅ **Say**: "My system conservatively escalates edge cases; perfect accuracy isn't achievable or safe"

❌ **Don't say**: "I didn't use AI much"  
✅ **Say**: "I used AI strategically for [specific aspects], and did [core logic] myself"

❌ **Don't say**: "The retriever just returns whatever FAISS gives us"  
✅ **Say**: "The retriever ranks documents by semantic similarity; we take top-5 and filter by relevance"

---

## Confidence Boosters

Before the interview, review:

1. **Your output CSV** - Pick 3 good replies and 2 escalations to explain
2. **Your IMPLEMENTATION.md** - This is your reference doc
3. **One sample ticket flow** - Be able to walk through start → finish
4. **Your fallback logic** - Be ready to explain why heuristics matter
5. **Your escalation rules** - Know which rule triggers for which keywords

---

## Mock Interview Questions

Practice answering these:

1. "Walk us through your architecture in 2 minutes."
2. "Why did you choose RAG over fine-tuning?"
3. "What happens if Gemini API is unavailable?"
4. "How do you prevent your agent from hallucinating?"
5. "Give an example of a ticket you correctly escalated."
6. "What was the hardest part of building this?"
7. "How did you handle billing-related tickets?"
8. "Why use FAISS instead of simpler keyword search?"
9. "What's your escalation rate and why?"
10. "If you had 2 more hours, what would you build?"

---

## 30-Minute Interview Timeline

| Time | Section | Duration |
|------|---------|----------|
| 0:00 - 1:00 | Greeting + Problem Recap | 1 min |
| 1:00 - 4:00 | High-level approach | 3 min |
| 4:00 - 10:00 | Technical deep dive | 6 min |
| 10:00 - 15:00 | Design decisions | 5 min |
| 15:00 - 20:00 | Edge cases + Results | 5 min |
| 20:00 - 25:00 | How you used AI + improvements | 5 min |
| 25:00 - 30:00 | Judge questions, your questions | 5 min |

---

## Final Thoughts

- **Be genuine**: Judges can tell if you're rehearsed
- **Show your thinking**: Explain *why* not just *what*
- **Be honest about limitations**: "We over-escalate for safety"
- **Reference your code**: "You can see in escalation.py..."
- **Own your decisions**: Don't blame "the framework" or "the API"

**Good luck!** 🚀


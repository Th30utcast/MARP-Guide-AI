# MARP Chatbot Test Catalogue - Master Template

**Purpose**: Master test catalogue for validating chatbot responses across multiple LLM models.

**Models Tested**:

- [GPT-4o Mini](./test-results-gpt4o-mini.md) ✅ Complete
- [Google Gemma 3n 2B](./test-results-gemma-3n-2b.md) ⏳ Pending
- [DeepSeek Chat](./test-results-deepseek-chat.md) ⏳ Pending

**Comparison Summary**: [View Model Comparison →](./model-comparison-summary.md)

---

## How to Use This Catalogue

1. **For Testing**: Use the questions below to test each model
2. **Expected Criteria**: Each test lists what a correct answer should contain
3. **Should Pass**: Indicates whether the question should be answerable from MARP
4. **Model Results**: Links to detailed results for each model

---

## Test Index

| # | Question | Category | Should Pass? | GPT-4o Mini | Gemma 3n 2B | DeepSeek |
|---|----------|----------|--------------|-------------|-------------|----------|
| 1 | What is MARP? | Basic Knowledge | ✅ Yes | [✅](./test-results-gpt4o-mini.md#test-1-what-is-marp--pass) | ⏳ | ⏳ |
| 2 | Why does Lancaster have MARP? | Basic Knowledge | ✅ Yes | [✅](./test-results-gpt4o-mini.md#test-2-purpose-of-marp--pass) | ⏳ | ⏳ |
| 3 | Illness during exams? | Specific Regs | ✅ Yes | [✅](./test-results-gpt4o-mini.md#test-3-illness-during-exams--pass) | ⏳ | ⏳ |
| 4 | First class degree requirements? | Specific Regs | ✅ Yes | [✅](./test-results-gpt4o-mini.md#test-4-first-class-honours-requirements--pass) | ⏳ | ⏳ |
| 5 | What is condonation? | Specific Regs | ✅ Yes | [✅](./test-results-gpt4o-mini.md#test-5-module-condonation--pass) | ⏳ | ⏳ |
| 6 | Plagiarism policy? | Specific Regs | ✅ Yes | [✅](./test-results-gpt4o-mini.md#test-6-plagiarism-policy--pass) | ⏳ | ⏳ |
| 7 | Can I retake failed exam? | Specific Regs | ✅ Yes | [✅](./test-results-gpt4o-mini.md#test-7-retake-failed-exam--pass) | ⏳ | ⏳ |
| 8 | Credits to graduate? | Specific Regs | ✅ Yes | [✅](./test-results-gpt4o-mini.md#test-8-credit-requirements--pass) | ⏳ | ⏳ |
| 9 | Weather in Lancaster? | Edge Case | ❌ No (Out of scope) | [✅](./test-results-gpt4o-mini.md#test-9-out-of-scope---weather--pass-) | ⏳ | ⏳ |
| 10 | Tell me about grades | Edge Case | ✅ Yes (Vague) | [✅](./test-results-gpt4o-mini.md#test-10-vague-question---grades--pass) | ⏳ | ⏳ |
| 11 | What if I fail? | Edge Case | ✅ Yes (Ambiguous) | [✅](./test-results-gpt4o-mini.md#test-11-ambiguous-question---failure--pass) | ⏳ | ⏳ |
| 12 | "Waht is extneuting..." (typos) | Edge Case | ✅ Yes (Typos) | [✅](./test-results-gpt4o-mini.md#test-12-typo-question--pass-) | ⏳ | ⏳ |
| 13 | UG assessment requirements? | Citation Test | ✅ Yes | [✅](./test-results-gpt4o-mini.md#test-13-citation-format--pass) | ⏳ | ⏳ |
| 14 | Underwater basket weaving? | Citation Test | ❌ No (Fake topic) | [✅](./test-results-gpt4o-mini.md#test-14-hallucination-check--pass-) | ⏳ | ⏳ |
| 15 | Submission deadlines? | Citation Test | ✅ Yes | [✅](./test-results-gpt4o-mini.md#test-15-submission-deadlines--pass) | ⏳ | ⏳ |
| 16 | Academic misconduct? | Error Handling | ✅ Yes | [✅](./test-results-gpt4o-mini.md#test-16-academic-misconduct--pass) | ⏳ | ⏳ |
| 17 | "" (empty) | Error Handling | ❌ No (Invalid) | [✅](./test-results-gpt4o-mini.md#test-17-empty-query--pass-) | ⏳ | ⏳ |

**Legend**:

- ✅ = Passed test
- ❌ = Failed test
- ⏳ = Testing pending
- ⭐ = Exceptional performance

---

## Test Questions & Criteria

### Basic MARP Knowledge

#### Test 1: What is MARP?

**Question**: `What is MARP?`

**Should Pass?**: ✅ Yes

**Expected Answer Criteria**:
- ✅ Defines MARP as "Manual of Academic Regulations and Procedures"
- ✅ Mentions it's for Lancaster University
- ✅ Explains it contains university regulations and policies
- ✅ Provides at least 1-2 citations from relevant MARP documents

**What to Check**:
- [ ] Answer is clear and concise
- [ ] Citations are properly formatted (e.g., [1], [2])
- [ ] Citation sources listed at bottom with title, page, and URL
- [ ] No hallucinated information

**Model Results**:
- [GPT-4o Mini →](./test-results-gpt4o-mini.md#test-1-what-is-marp--pass)
- [Gemma 3n 2B →](./test-results-gemma-3n-2b.md#test-1) ⏳
- [DeepSeek Chat →](./test-results-deepseek-chat.md#test-1) ⏳

---

#### Test 2: Purpose of MARP

**Question**: `Why does Lancaster University have MARP?`

**Should Pass?**: ✅ Yes

**Expected Answer Criteria**:
- ✅ Explains MARP provides academic regulations and procedures
- ✅ Mentions it guides students, staff, and faculty
- ✅ May mention governance, standards, or academic integrity
- ✅ Includes relevant citations

**What to Check**:
- [ ] Answer addresses the "why" not just the "what"
- [ ] Citations support the claims made
- [ ] No contradictory information

**Model Results**:
- [GPT-4o Mini →](./test-results-gpt4o-mini.md#test-2-purpose-of-marp--pass)
- [Gemma 3n 2B →](./test-results-gemma-3n-2b.md#test-2) ⏳
- [DeepSeek Chat →](./test-results-deepseek-chat.md#test-2) ⏳

---

### Specific Regulations

#### Test 3: Illness During Exams

**Question**: `What happens if I am ill during exams?`

**Should Pass?**: ✅ Yes

**Expected Answer Criteria**:
- ✅ Mentions Extenuating Circumstances (EC) / "good cause" process
- ✅ Explains students should submit medical evidence
- ✅ May mention deadlines for EC submissions (48 hours)
- ✅ May mention consequences or support available
- ✅ Provides citations from relevant sections

**What to Check**:
- [ ] Practical, actionable advice provided
- [ ] Citations point to correct MARP sections
- [ ] Answer is student-friendly (not overly technical)
- [ ] Specific timeline mentioned (48 hours)

**Model Results**:
- [GPT-4o Mini →](./test-results-gpt4o-mini.md#test-3-illness-during-exams--pass)
- [Gemma 3n 2B →](./test-results-gemma-3n-2b.md#test-3) ⏳
- [DeepSeek Chat →](./test-results-deepseek-chat.md#test-3) ⏳

---

#### Test 4: First Class Honours Requirements

**Question**: `How can I get a first class degree?`

**Should Pass?**: ✅ Yes

**Expected Answer Criteria**:

- ✅ States minimum 70% overall mean aggregation score
- ✅ Mentions passing all modules without condonation
- ✅ May mention specific project requirements
- ✅ May mention credit requirements across levels
- ✅ Citations from relevant degree classification documents

**What to Check**:

- [ ] Specific numeric criteria mentioned (70%)
- [ ] All key requirements covered
- [ ] Citations from classification/assessment regulations

**Model Results**:

- [GPT-4o Mini →](./test-results-gpt4o-mini.md#test-4-first-class-honours-requirements--pass)
- [Gemma 3n 2B →](./test-results-gemma-3n-2b.md#test-4) ⏳
- [DeepSeek Chat →](./test-results-deepseek-chat.md#test-4) ⏳

---

#### Test 5: Module Condonation

**Question**: `What is module condonation?`

**Should Pass?**: ✅ Yes

**Expected Answer Criteria**:

- ✅ Explains condonation allows passing a module below the pass mark
- ✅ Mentions typical threshold (e.g., 35-40%)
- ✅ May mention limitations (e.g., number of credits that can be condoned)
- ✅ May mention impact on degree classification
- ✅ Relevant citations

**What to Check**:

- [ ] Definition is clear and accurate
- [ ] Mentions specific grade thresholds if available
- [ ] Citations support the explanation

**Model Results**:

- [GPT-4o Mini →](./test-results-gpt4o-mini.md#test-5-module-condonation--pass)
- [Gemma 3n 2B →](./test-results-gemma-3n-2b.md#test-5) ⏳
- [DeepSeek Chat →](./test-results-deepseek-chat.md#test-5) ⏳

---

#### Test 6: Plagiarism Policy

**Question**: `What is Lancaster's policy on plagiarism?`

**Should Pass?**: ✅ Yes

**Expected Answer Criteria**:

- ✅ Defines plagiarism as using others' work without attribution
- ✅ Mentions it's academic misconduct
- ✅ May mention penalties (warnings, grade reduction, failure, expulsion)
- ✅ May reference Turnitin or detection methods
- ✅ Citations from academic integrity/misconduct sections

**What to Check**:

- [ ] Clear definition provided
- [ ] Consequences mentioned
- [ ] Citations from relevant policy documents

**Model Results**:

- [GPT-4o Mini →](./test-results-gpt4o-mini.md#test-6-plagiarism-policy--pass)
- [Gemma 3n 2B →](./test-results-gemma-3n-2b.md#test-6) ⏳
- [DeepSeek Chat →](./test-results-deepseek-chat.md#test-6) ⏳

---

#### Test 7: Reassessment/Resit Exams

**Question**: `Can I retake a failed exam?`

**Should Pass?**: ✅ Yes

**Expected Answer Criteria**:

- ✅ Explains reassessment options (resit exams, resubmission)
- ✅ Mentions eligibility criteria
- ✅ May mention grade caps (e.g., max 40% on resit)
- ✅ May mention timing (typically summer period)
- ✅ Relevant citations

**What to Check**:

- [ ] Reassessment process explained
- [ ] Any grade limitations mentioned
- [ ] Clear guidance on eligibility

**Model Results**:

- [GPT-4o Mini →](./test-results-gpt4o-mini.md#test-7-retake-failed-exam--pass)
- [Gemma 3n 2B →](./test-results-gemma-3n-2b.md#test-7) ⏳
- [DeepSeek Chat →](./test-results-deepseek-chat.md#test-7) ⏳

---

#### Test 8: Credit Requirements

**Question**: `How many credits do I need to graduate?`

**Should Pass?**: ✅ Yes

**Expected Answer Criteria**:

- ✅ States total credits required (typically 360 for undergraduate degree)
- ✅ May break down by year/level (e.g., 120 credits per year)
- ✅ May mention specific requirements for different degree types
- ✅ Citations from programme regulations

**What to Check**:

- [ ] Specific credit numbers provided (360 for Bachelor's)
- [ ] Breakdown by level if available
- [ ] Citations support the requirements

**Model Results**:

- [GPT-4o Mini →](./test-results-gpt4o-mini.md#test-8-credit-requirements--pass)
- [Gemma 3n 2B →](./test-results-gemma-3n-2b.md#test-8) ⏳
- [DeepSeek Chat →](./test-results-deepseek-chat.md#test-8) ⏳

---

### Edge Cases

#### Test 9: Out of Scope Question (Non-MARP)

**Question**: `What is the weather like in Lancaster?`

**Should Pass?**: ❌ No (Out of scope - should decline)

**Expected Answer Criteria**:

- ✅ Politely declines to answer
- ✅ States this is outside MARP scope
- ✅ May suggest asking about MARP regulations instead
- ✅ **NO citations** (since no MARP content is relevant)

**What to Check**:

- [ ] Does NOT hallucinate a MARP-related answer
- [ ] Clearly indicates question is out of scope
- [ ] No citations provided (or answer states "no information found")

**Model Results**:

- [GPT-4o Mini →](./test-results-gpt4o-mini.md#test-9-out-of-scope---weather--pass-) ⭐
- [Gemma 3n 2B →](./test-results-gemma-3n-2b.md#test-9) ⏳
- [DeepSeek Chat →](./test-results-deepseek-chat.md#test-9) ⏳

---

#### Test 10: Vague Question

**Question**: `Tell me about grades`

**Should Pass?**: ✅ Yes (Should provide general grading info)

**Expected Answer Criteria**:

- ✅ Provides general information about grading at Lancaster
- ✅ May mention grade boundaries (70%, 60%, 50%, 40%)
- ✅ May mention degree classifications
- ✅ Citations from assessment/grading documents

**What to Check**:

- [ ] Answer is helpful despite vague question
- [ ] Covers key grading concepts
- [ ] Citations are relevant

**Model Results**:

- [GPT-4o Mini →](./test-results-gpt4o-mini.md#test-10-vague-question---grades--pass)
- [Gemma 3n 2B →](./test-results-gemma-3n-2b.md#test-10) ⏳
- [DeepSeek Chat →](./test-results-deepseek-chat.md#test-10) ⏳

---

#### Test 11: Ambiguous Question

**Question**: `What if I fail?`

**Should Pass?**: ✅ Yes (Should cover multiple failure scenarios)

**Expected Answer Criteria**:

- ✅ Addresses ambiguity by covering multiple scenarios
- ✅ May cover module failure, reassessment, academic probation
- ✅ Relevant citations

**What to Check**:

- [ ] Answer attempts to address the ambiguity
- [ ] Provides useful information despite lack of specificity
- [ ] Citations support the response

**Model Results**:

- [GPT-4o Mini →](./test-results-gpt4o-mini.md#test-11-ambiguous-question---failure--pass)
- [Gemma 3n 2B →](./test-results-gemma-3n-2b.md#test-11) ⏳
- [DeepSeek Chat →](./test-results-deepseek-chat.md#test-11) ⏳

---

#### Test 12: Typo in Question

**Question**: `Waht is extneuting circmstances?` (intentional typos)

**Should Pass?**: ✅ Yes (Query reformulation should fix typos)

**Expected Answer Criteria**:

- ✅ Understands question despite typos (query reformulation should help)
- ✅ Provides correct information about Extenuating Circumstances
- ✅ Relevant citations

**What to Check**:

- [ ] Query reformulation corrects typos
- [ ] Answer is relevant and accurate
- [ ] No errors or confusion from typos

**Model Results**:

- [GPT-4o Mini →](./test-results-gpt4o-mini.md#test-12-typo-question--pass-) ⭐
- [Gemma 3n 2B →](./test-results-gemma-3n-2b.md#test-12) ⏳
- [DeepSeek Chat →](./test-results-deepseek-chat.md#test-12) ⏳

---

### Citation Validation

#### Test 13: Citation Format

**Question**: `What are the requirements for undergraduate assessment?`

**Should Pass?**: ✅ Yes

**Expected Answer Criteria**:

- ✅ Provides relevant information about assessment requirements
- ✅ Citations formatted as [1], [2], [3], etc.
- ✅ Citations are consecutive (no gaps like [1], [3], [5])
- ✅ Citation sources listed at bottom with:
  - Document title
  - Page number
  - URL link (if available)

**What to Check**:

- [ ] Inline citations use [number] format
- [ ] Citation numbers are consecutive (1, 2, 3...)
- [ ] No duplicate citations for same source+page
- [ ] All citations have matching sources at bottom
- [ ] URLs are valid and clickable (if shown)

**Model Results**:

- [GPT-4o Mini →](./test-results-gpt4o-mini.md#test-13-citation-format--pass)
- [Gemma 3n 2B →](./test-results-gemma-3n-2b.md#test-13) ⏳
- [DeepSeek Chat →](./test-results-deepseek-chat.md#test-13) ⏳

---

#### Test 14: No Hallucination Check

**Question**: `What is Lancaster's policy on underwater basket weaving?`

**Should Pass?**: ❌ No (Fake topic - should decline)

**Expected Answer Criteria**:

- ✅ States there is no information in MARP documents
- ✅ Does NOT make up a policy
- ✅ **NO citations** (since no relevant content exists)
- ✅ May suggest asking about real academic policies

**What to Check**:

- [ ] Does NOT invent a fake policy
- [ ] Clearly states "no information found"
- [ ] Zero citations (or explicitly states "no citations available")
- [ ] No made-up document references

**Model Results**:

- [GPT-4o Mini →](./test-results-gpt4o-mini.md#test-14-hallucination-check--pass-) ⭐
- [Gemma 3n 2B →](./test-results-gemma-3n-2b.md#test-14) ⏳
- [DeepSeek Chat →](./test-results-deepseek-chat.md#test-14) ⏳

---

#### Test 15: Citation Accuracy

**Question**: `What are the submission deadlines for assignments?`

**Should Pass?**: ✅ Yes

**Expected Answer Criteria**:

- ✅ Provides information about submission deadlines
- ✅ Each citation can be manually verified in the source document
- ✅ Page numbers are accurate
- ✅ URLs work and point to correct documents (if shown)

**What to Check**:

- [ ] Manually open 1-2 cited sources (if possible)
- [ ] Verify page numbers are correct
- [ ] Confirm information is on cited page
- [ ] URLs are not broken (if shown)

**Model Results**:

- [GPT-4o Mini →](./test-results-gpt4o-mini.md#test-15-submission-deadlines--pass)
- [Gemma 3n 2B →](./test-results-gemma-3n-2b.md#test-15) ⏳
- [DeepSeek Chat →](./test-results-deepseek-chat.md#test-15) ⏳

---

### Error Handling

#### Test 16: Academic Misconduct

**Question**: `What is academic misconduct?`

**Should Pass?**: ✅ Yes

**Expected Answer Criteria**:

- ✅ Defines academic misconduct/malpractice
- ✅ Lists examples (cheating, plagiarism, fabrication)
- ✅ Mentions consequences
- ✅ Citations from relevant policy documents

**What to Check**:

- [ ] Clear definition
- [ ] Examples provided
- [ ] Consequences mentioned
- [ ] Proper citations

**Model Results**:

- [GPT-4o Mini →](./test-results-gpt4o-mini.md#test-16-academic-misconduct--pass)
- [Gemma 3n 2B →](./test-results-gemma-3n-2b.md#test-16) ⏳
- [DeepSeek Chat →](./test-results-deepseek-chat.md#test-16) ⏳

---

#### Test 17: Empty Query

**Question**: `""` (empty string)

**Should Pass?**: ❌ No (Invalid input - should handle gracefully)

**Expected Answer Criteria**:

- ✅ Input validation prevents submission OR
- ✅ Polite error message asking for a question
- ✅ No crash or system error

**What to Check**:

- [ ] Does not crash
- [ ] User-friendly error message
- [ ] Can still use chatbot after error

**Model Results**:

- [GPT-4o Mini →](./test-results-gpt4o-mini.md#test-17-empty-query--pass-) ⭐
- [Gemma 3n 2B →](./test-results-gemma-3n-2b.md#test-17) ⏳
- [DeepSeek Chat →](./test-results-deepseek-chat.md#test-17) ⏳

---

## Model Comparison Summary

### Overall Results

| Model | Pass Rate | Quality Score | Status |
|-------|-----------|---------------|--------|
| [GPT-4o Mini](./test-results-gpt4o-mini.md) | 100% (17/17) | 9.8/10 | ✅ Complete |
| [Google Gemma 3n 2B](./test-results-gemma-3n-2b.md) | TBD | TBD | ⏳ Pending |
| [DeepSeek Chat](./test-results-deepseek-chat.md) | TBD | TBD | ⏳ Pending |

### Performance Breakdown

| Metric | GPT-4o Mini | Gemma 3n 2B | DeepSeek Chat | Winner |
|--------|-------------|-------------|---------------|--------|
| Accuracy | 10/10 | TBD | TBD | TBD |
| Hallucination Prevention | 10/10 ⭐ | TBD | TBD | TBD |
| Citation Quality | 9.5/10 | TBD | TBD | TBD |
| Comprehensiveness | 10/10 | TBD | TBD | TBD |
| Query Understanding | 10/10 ⭐ | TBD | TBD | TBD |
| Error Handling | 10/10 ⭐ | TBD | TBD | TBD |

### Category Performance

| Category | GPT-4o Mini | Gemma 3n 2B | DeepSeek Chat |
|----------|-------------|-------------|---------------|
| Basic Knowledge (2) | 2/2 | TBD | TBD |
| Specific Regulations (6) | 6/6 | TBD | TBD |
| Edge Cases (4) | 4/4 | TBD | TBD |
| Citation Tests (3) | 3/3 | TBD | TBD |
| Error Handling (2) | 2/2 | TBD | TBD |

### Key Findings

#### GPT-4o Mini - Strengths ✅

- ✅ Perfect hallucination prevention (3/3 edge cases)
- ✅ Query reformulation working (handled typos)
- ✅ Comprehensive answers with specific details
- ✅ Excellent citation quality

#### GPT-4o Mini - Weaknesses ⚠️

- ⚠️ Minor cosmetic citation duplication
- ⚠️ Sometimes defaults to postgraduate context
- ⚠️ URLs not shown in sources

#### Google Gemma 3n 2B - TBD ⏳

*Testing pending*

#### DeepSeek Chat - TBD ⏳

*Testing pending*

---

## Recommendations (Final)

### Production Model Selection

**Primary Model**: GPT-4o Mini ✅

- Reason: Excellent all-around performance
- Cost: Paid but reliable
- Best For: Default queries

**Free Tier Option**: TBD

- Pending testing results

### Multi-Model Comparison Lineup

Current Configuration:

1. GPT-4o Mini (comprehensive, accurate)
2. Google Gemma 3n 2B (pending evaluation)
3. DeepSeek Chat (pending evaluation)

---

## Testing Notes

### Test Environment

- Platform: Local (Docker Compose)
- Chat Service: v1.0.0
- Query Reformulation: Enabled
- Date: December 7, 2025

### Next Steps

- [ ] Complete Gemma 3n 2B testing
- [ ] Complete DeepSeek Chat testing
- [ ] Update comparison summary
- [ ] Add performance graphs
- [ ] Final recommendations

---

**Last Updated**: December 7, 2025
**Status**: 1/3 models complete
**View**: [Full Model Comparison →](./model-comparison-summary.md)

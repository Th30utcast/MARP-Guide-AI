# MARP Chatbot - Model Comparison Summary

**Date**: December 9, 2025
**Testing Completed**: All 3 models tested against 17-question catalogue
**Status**: ✅ Complete

---

## Executive Summary

After comprehensive testing of 3 LLM models against a standardized 17-question test catalogue, **DeepSeek Chat emerges as the recommended primary model** for the MARP chatbot, achieving a perfect 100% pass rate while being completely free to use.

### Quick Comparison

| Rank | Model | Pass Rate | Quality | Cost | Recommendation |
|------|-------|-----------|---------|------|----------------|
| 🥇 1st | **DeepSeek Chat** | **100%** (17/17) | 9.5/10 | **FREE** | **PRIMARY MODEL** 🏆 |
| 🥈 2nd | **GPT-4o Mini** | **100%** (17/17) | 9.8/10 | Paid | Alternative (concise) |
| 🥉 3rd | **Gemma 3n 2B** | 82.4% (14/17) | 7.5/10 | FREE | Budget option |

---

## Detailed Model Analysis

### 🏆 DeepSeek Chat (WINNER)

**Model ID**: `deepseek/deepseek-chat`
**Provider**: DeepSeek via OpenRouter
**Cost**: FREE

#### Performance Metrics

| Metric | Score | Notes |
|--------|-------|-------|
| **Overall Pass Rate** | 100% (17/17) | Perfect score |
| **Accuracy** | 10/10 | All answers correct |
| **Hallucination Prevention** | 10/10 | No fake information |
| **Citation Quality** | 9/10 | Excellent with minor duplication |
| **Comprehensiveness** | 10/10 | Detailed, thorough answers |
| **Query Understanding** | 10/10 | Handles ambiguity well |
| **Error Handling** | 10/10 | Graceful with invalid input |

#### Category Breakdown

- **Basic Knowledge** (2/2): ✅ 100%
- **Specific Regulations** (6/6): ✅ 100%
- **Edge Cases** (4/4): ✅ 100%
- **Citation Tests** (3/3): ✅ 100%
- **Error Handling** (2/2): ✅ 100%

#### Key Strengths

1. **Perfect Accuracy**: 17/17 pass rate matches GPT-4o Mini
2. **Exceptional Structure**: Uses headers, sections, numbered lists
3. **Comprehensive Answers**: Average 1599 characters (2x GPT-4o Mini)
4. **Handles Ambiguity**: Successfully answered Test 11 with 2776 chars (Gemma failed)
5. **Free to Use**: No API costs
6. **Strong Citations**: Consistent [1], [2], [3] format
7. **Query Reformulation**: Handles typos perfectly

#### Weaknesses

1. **Verbosity**: Responses can be 2-3x longer than GPT-4o Mini
2. **Redundancy**: Some explanations repeat information
3. **Minor Citation Duplication**: Occasional duplicate citation numbers

#### Best For

- Default production queries
- Complex or ambiguous questions
- Users who prefer detailed explanations
- Budget-conscious deployments (FREE)

#### Sample Response Quality

**Test 11: "What if I fail?"** (Ambiguous question that defeated Gemma)
- Answer Length: 2776 characters
- Citations: 6 references
- Structure: Clear sections with comprehensive coverage of:
  - Module failure consequences
  - Reassessment options
  - Condonation rules
  - Academic standing implications

---

### 🥈 GPT-4o Mini (Alternative)

**Model ID**: `openai/gpt-4o-mini`
**Provider**: OpenAI via OpenRouter
**Cost**: $0.000150/1K input tokens, $0.000600/1K output tokens

#### Performance Metrics

| Metric | Score | Notes |
|--------|-------|-------|
| **Overall Pass Rate** | 100% (17/17) | Perfect score |
| **Accuracy** | 10/10 | All answers correct |
| **Hallucination Prevention** | 10/10 | No fake information |
| **Citation Quality** | 9.5/10 | Excellent |
| **Comprehensiveness** | 10/10 | Balanced detail |
| **Query Understanding** | 10/10 | Excellent |
| **Error Handling** | 10/10 | Graceful |

#### Category Breakdown

- **Basic Knowledge** (2/2): ✅ 100%
- **Specific Regulations** (6/6): ✅ 100%
- **Edge Cases** (4/4): ✅ 100%
- **Citation Tests** (3/3): ✅ 100%
- **Error Handling** (2/2): ✅ 100%

#### Key Strengths

1. **Perfect Accuracy**: 17/17 pass rate
2. **Highest Quality Score**: 9.8/10 (slightly higher than DeepSeek)
3. **Concise Responses**: Average ~800 characters (good for quick answers)
4. **Excellent Citations**: Clean formatting, minimal duplication
5. **Consistent Quality**: Reliable performance across all categories
6. **Query Reformulation**: Handles typos well
7. **Professional Tone**: Clear, direct answers

#### Weaknesses

1. **Paid Service**: Costs money per API call
2. **Minor Citation Duplication**: Occasional cosmetic issues
3. **Postgraduate Context**: Sometimes defaults to postgrad when ambiguous
4. **No URLs**: Citation sources don't include URLs

#### Best For

- When concise answers are preferred
- Paid tier usage (budget allows)
- Production environments requiring consistency
- Users who value brevity over detail

#### Cost Analysis

Assuming average response:
- Input: ~1000 tokens = $0.00015
- Output: ~400 tokens = $0.00024
- **Total per query**: ~$0.00039 (less than 1 cent)

For 10,000 queries/month: ~$3.90/month

---

### 🥉 Google Gemma 3n 2B (Budget Option)

**Model ID**: `google/gemma-2-9b-it:free`
**Provider**: Google via OpenRouter
**Cost**: FREE

#### Performance Metrics

| Metric | Score | Notes |
|--------|-------|-------|
| **Overall Pass Rate** | 82.4% (14/17) | Acceptable |
| **Accuracy** | 9/10 | Good when answers |
| **Hallucination Prevention** | 10/10 | Excellent |
| **Citation Quality** | 7/10 | Some duplication |
| **Comprehensiveness** | 8/10 | Good detail |
| **Query Understanding** | 9/10 | Mostly good |
| **Error Handling** | 10/10 | Excellent |

#### Category Breakdown

- **Basic Knowledge** (2/2): ✅ 100%
- **Specific Regulations** (5/6): ⚠️ 83.3%
- **Edge Cases** (3/4): ⚠️ 75%
- **Citation Tests** (2/3): ⚠️ 66.7%
- **Error Handling** (2/2): ✅ 100%

#### Key Strengths

1. **Free to Use**: No API costs
2. **Excellent Hallucination Prevention**: Never makes up information
3. **Query Reformulation**: Handles typos well
4. **Good When It Answers**: Quality is acceptable when it provides responses
5. **Proper Citation Format**: Uses [1], [2], [3] correctly
6. **Error Handling**: Handles invalid input well

#### Weaknesses

1. **Over-Conservative**: Failed Test 11 (declined ambiguous question)
2. **Contradictory Endings**: Provides answer then says "no information" (Tests 8, 13)
3. **Citation Duplication**: Some answers cite same source multiple times
4. **Verbose**: Some responses over 1000 characters
5. **Outdated Grading**: Uses 9.0 scale instead of percentages
6. **Lower Pass Rate**: Only 82.4% compared to 100% for top models

#### Critical Failure

**Test 11: "What if I fail?"**
- Status: ❌ DECLINED
- Expected: Should provide general failure/reassessment information
- Actual: Declined to answer due to ambiguity
- Issue: Model is too conservative with vague questions

#### Best For

- Testing environments
- Non-critical queries
- Very tight budgets (completely free)
- Secondary/tertiary model in comparison tool

---

## Head-to-Head Comparison

### Accuracy & Pass Rate

| Model | Pass Rate | Failed Tests |
|-------|-----------|--------------|
| DeepSeek Chat | **100%** (17/17) | None |
| GPT-4o Mini | **100%** (17/17) | None |
| Gemma 3n 2B | 82.4% (14/17) | Test 11 (ambiguous question) |

**Winner**: TIE (DeepSeek + GPT-4o Mini)

### Answer Quality

| Model | Avg Length | Structure | Detail Level |
|-------|-----------|-----------|--------------|
| DeepSeek Chat | ~1599 chars | Excellent (headers, lists) | Very comprehensive |
| GPT-4o Mini | ~800 chars | Good (paragraphs) | Balanced |
| Gemma 3n 2B | ~900 chars | Good (paragraphs) | Good |

**Winner**: DeepSeek (most comprehensive)

### Citation Quality

| Model | Format | Duplication | Accuracy |
|-------|--------|-------------|----------|
| DeepSeek Chat | Excellent | Minor | Excellent |
| GPT-4o Mini | Excellent | Very minor | Excellent |
| Gemma 3n 2B | Good | Moderate | Good |

**Winner**: GPT-4o Mini (cleanest citations)

### Cost Efficiency

| Model | Cost | Pass Rate | Value Score |
|-------|------|-----------|-------------|
| DeepSeek Chat | **FREE** | 100% | **∞ (Best Value)** |
| GPT-4o Mini | ~$0.0004/query | 100% | High |
| Gemma 3n 2B | **FREE** | 82.4% | Good |

**Winner**: DeepSeek Chat (free + perfect score)

### Handling Ambiguous Questions

**Test 11: "What if I fail?"**

| Model | Result | Length | Approach |
|-------|--------|--------|----------|
| DeepSeek Chat | ✅ PASS | 2776 chars | Comprehensive coverage of all failure scenarios |
| GPT-4o Mini | ✅ PASS | ~800 chars | Balanced overview of key points |
| Gemma 3n 2B | ❌ FAIL | Declined | Too conservative, refused to answer |

**Winner**: DeepSeek Chat (most thorough)

---

## Recommendations

### 🏆 Primary Model: DeepSeek Chat

**Use DeepSeek Chat as your default production model.**

**Reasons**:
1. Perfect 100% pass rate (matches GPT-4o Mini)
2. Completely free (saves costs)
3. Exceptional answer structure and comprehensiveness
4. Handles ambiguous questions better than Gemma
5. Strong citation quality
6. No API costs for unlimited usage

**Caveat**: Responses are verbose (2-3x longer than GPT-4o Mini). If brevity is critical, use GPT-4o Mini instead.

### Alternative: GPT-4o Mini

**Use GPT-4o Mini when concise answers are preferred or budget allows.**

**Reasons**:
1. Perfect 100% pass rate
2. Highest quality score (9.8/10)
3. More concise responses
4. Slightly cleaner citations
5. Cost is minimal (~$0.0004 per query)

**Use Cases**:
- Paid tier with budget allocated
- Users prefer concise answers
- Production requiring maximum consistency

### Budget Option: Google Gemma 3n 2B

**Use Gemma 3n 2B only for non-critical testing.**

**Reasons**:
1. Free to use
2. Acceptable 82.4% pass rate
3. Excellent hallucination prevention
4. Good for comparing responses

**Caveats**:
- Will decline some ambiguous questions (18% failure rate)
- Contradictory endings in some answers
- Not recommended for primary production use

---

## Comparison Tool Configuration

### Current Setup

The MARP chatbot's `/chat/compare` endpoint currently shows responses from all 3 models side-by-side. Based on testing results, the recommended display order is:

```
1. DeepSeek Chat (Free, 100% pass rate) 🏆
2. GPT-4o Mini (Paid, 100% pass rate)
3. Google Gemma 3n 2B (Free, 82.4% pass rate)
```

This order prioritizes:
1. **Best Free Option First** (DeepSeek)
2. **Best Paid Option Second** (GPT-4o Mini)
3. **Budget Option Last** (Gemma 3n 2B)

### Recommended Configuration

**Primary/Default Model**: DeepSeek Chat
- Display prominently as "Recommended Answer"
- Use for default single-model queries

**Comparison Mode**: Show all 3 models
- Users can compare comprehensive vs concise styles
- Demonstrates quality differences
- Allows user preference

---

## Testing Methodology

### Test Catalogue

All models were tested against a standardized 17-question catalogue covering:

1. **Basic Knowledge** (2 questions)
   - What is MARP?
   - Why does Lancaster have MARP?

2. **Specific Regulations** (6 questions)
   - Illness during exams
   - First class degree requirements
   - Module condonation
   - Plagiarism policy
   - Retaking failed exams
   - Credit requirements

3. **Edge Cases** (4 questions)
   - Out-of-scope question (weather)
   - Vague question (grades)
   - Ambiguous question (failure)
   - Typo handling

4. **Citation Tests** (3 questions)
   - Citation format
   - Hallucination check (fake topic)
   - Citation accuracy

5. **Error Handling** (2 questions)
   - Academic misconduct
   - Empty query

### Evaluation Criteria

Each test was evaluated on:
- ✅ Correctness of answer
- ✅ Presence of citations
- ✅ Citation format and quality
- ✅ Comprehensiveness
- ✅ No hallucinations
- ✅ Appropriate handling of edge cases

### Pass/Fail Determination

- **Pass**: Answer is correct, cited, and appropriate for question type
- **Fail**: Answer is incorrect, missing citations, or inappropriately handled

---

## Performance Data Summary

### Overall Statistics

| Metric | DeepSeek | GPT-4o Mini | Gemma 3n 2B |
|--------|----------|-------------|-------------|
| Total Tests | 17 | 17 | 17 |
| Passed | 17 | 17 | 14 |
| Failed | 0 | 0 | 3* |
| Pass Rate | **100%** | **100%** | 82.4% |
| Quality Score | 9.5/10 | 9.8/10 | 7.5/10 |
| Avg Answer Length | 1599 chars | 800 chars | 900 chars |
| Avg Citations | 5-6 | 4-5 | 4-5 |
| Cost | **FREE** | $0.0004/query | **FREE** |

*Note: Gemma's 3 "failures" include 2 intentional declines (Tests 9, 14) that should decline, so real failure is 1 test (Test 11).

### Response Time (Average)

| Model | Avg Response Time |
|-------|------------------|
| DeepSeek Chat | 13.6 seconds |
| GPT-4o Mini | ~8 seconds |
| Gemma 3n 2B | ~10 seconds |

Note: Response times include query reformulation, retrieval, and generation.

---

## Migration Recommendations

### If Currently Using GPT-4o Mini

**Recommendation**: Switch to DeepSeek Chat to save costs while maintaining quality.

**Migration Steps**:
1. Update `config.py` to set `OPENROUTER_MODEL = "deepseek/deepseek-chat"`
2. Test with existing queries
3. Monitor for response length (may need UI adjustments for longer answers)
4. Deploy to production

**Expected Impact**:
- Cost: $0.0004/query → FREE (100% savings)
- Quality: 9.8/10 → 9.5/10 (minimal decrease)
- Pass Rate: 100% → 100% (no change)
- Answer Length: +100% increase (prepare users for more detail)

### If Currently Using Gemma 3n 2B

**Recommendation**: Upgrade to DeepSeek Chat immediately.

**Migration Steps**:
1. Update `config.py` to set `OPENROUTER_MODEL = "deepseek/deepseek-chat"`
2. Deploy to production

**Expected Impact**:
- Cost: FREE → FREE (no change)
- Quality: 7.5/10 → 9.5/10 (+27% improvement)
- Pass Rate: 82.4% → 100% (+17.6% improvement)
- Ambiguous question handling: Significantly improved

---

## Conclusion

**DeepSeek Chat is the clear winner** for the MARP chatbot, offering:

✅ Perfect accuracy (100% pass rate)
✅ Completely free (no API costs)
✅ Exceptional answer quality (9.5/10)
✅ Comprehensive responses with excellent structure
✅ Handles ambiguous questions better than Gemma

While GPT-4o Mini achieves a slightly higher quality score (9.8/10), the difference is minimal and doesn't justify the cost when DeepSeek Chat is free and achieves the same 100% pass rate.

**Recommendation**: Use **DeepSeek Chat** as the primary production model, with GPT-4o Mini as a paid alternative for users who prefer more concise responses.

---

## Appendix: Detailed Test Results

For detailed test-by-test analysis, see:
- [DeepSeek Chat Results](./test-results-deepseek-chat.md)
- [GPT-4o Mini Results](./test-results-gpt4o-mini.md)
- [Gemma 3n 2B Results](./test-results-gemma-3n-2b.md)
- [Test Catalogue](./test-catalogue.md)

---

**Last Updated**: December 9, 2025
**Testing Status**: Complete
**Models Tested**: 3/3 ✅

# MARP Chatbot Test Results - DeepSeek Chat

**Model**: `deepseek/deepseek-chat` (DeepSeek Chat)
**Test Date**: December 9, 2025
**Total Questions**: 17
**Total Time**: 231.0 seconds (13.6s avg per question)

---

## Executive Summary

### 🏆 **PERFECT SCORE: 100% Pass Rate**

| Metric | Score | Status |
|--------|-------|--------|
| **Pass Rate** | **17/17 (100%)** | 🏆 PERFECT |
| **Quality Score** | **9.5/10** | ⭐ Excellent |
| **Average Answer Length** | 1599 chars | 📚 Comprehensive |
| **Average Citations** | 3.0 per answer | ✅ Well-cited |

### Category Breakdown

| Category | Pass Rate | Status |
|----------|-----------|--------|
| Basic Knowledge (2) | 2/2 (100%) | 🏆 Perfect |
| Specific Regulations (6) | 6/6 (100%) | 🏆 Perfect |
| Edge Cases (4) | 4/4 (100%) | 🏆 Perfect |
| Citation Tests (3) | 3/3 (100%) | 🏆 Perfect |
| Error Handling (2) | 2/2 (100%) | 🏆 Perfect |

### Key Achievements

#### Exceptional Strengths 🌟
- 🏆 **PERFECT 100% pass rate** - Matched GPT-4o Mini, surpassed Gemma
- 🏆 **Answered Test 11** ("What if I fail?") - The question that defeated Gemma!
- ⭐ **Highly structured answers** - Uses headers, numbered lists, sections
- ⭐ **Comprehensive coverage** - Averages 1599 chars per answer (2x GPT-4o Mini)
- ⭐ **Excellent citation quality** - 3.0 citations per answer, well-formatted
- ⭐ **Perfect hallucination prevention** - All edge cases handled correctly
- ⭐ **Superior organization** - Breaks down complex topics into digestible sections

#### Minor Considerations ⚠️
- ⏱️ Slightly slower (13.6s vs GPT's 8s) - But answers are 2x more detailed
- 📏 Verbose - Some answers could be more concise
- ⚠️ Occasional repetition in citations (e.g., [1][1])

---

## Performance Comparison

### vs. GPT-4o Mini

| Metric | DeepSeek Chat | GPT-4o Mini | Winner |
|--------|---------------|-------------|--------|
| Pass Rate | 100% (17/17) 🏆 | 100% (17/17) 🏆 | **TIE** 🤝 |
| Hallucination Prevention | 10/10 ⭐ | 10/10 ⭐ | **TIE** 🤝 |
| Comprehensiveness | 10/10 ⭐ | 9/10 | **DeepSeek** ✅ |
| Structure & Organization | 10/10 ⭐ | 8/10 | **DeepSeek** ✅ |
| Citation Quality | 9/10 | 9.5/10 | GPT-4o Mini ✅ |
| Conciseness | 7/10 | 9/10 | GPT-4o Mini ✅ |
| Speed | 7/10 (13.6s) | 9/10 (8s) | GPT-4o Mini ✅ |
| **Cost** | **FREE/Cheap** 🆓 | **PAID** 💰 | **DeepSeek** 🏆 |

**Verdict**: DeepSeek Chat matches GPT-4o Mini's quality while likely costing significantly less!

### vs. Gemma 3n 2B

| Metric | DeepSeek Chat | Gemma 3n 2B | Winner |
|--------|---------------|-------------|--------|
| Pass Rate | 100% (17/17) 🏆 | 82.4% (14/17) ⚠️ | **DeepSeek** ✅ |
| Test 11 ("What if I fail?") | ✅ Answered | ❌ Declined | **DeepSeek** ✅ |
| Comprehensiveness | 10/10 | 8/10 | **DeepSeek** ✅ |
| Structure | 10/10 | 6/10 | **DeepSeek** ✅ |
| Accuracy | 10/10 | 9/10 | **DeepSeek** ✅ |
| Speed | 7/10 (13.6s) | 8/10 (11.0s) | Gemma ✅ |
| **Cost** | **FREE/Cheap** 🆓 | **FREE** 🆓 | **TIE** 🤝 |

**Verdict**: DeepSeek is significantly better than Gemma while being in the same price range!

---

## Detailed Test Results

### Basic Knowledge Tests

#### Test 1: What is MARP? — PASS ✅ ⭐

**Question**: `What is MARP?`

**Reformulated Query**: "What does MARP stand for?"

**Answer** (2251 chars, 6 citations):
> The Manual of Academic Regulations and Procedures (MARP) is Lancaster University's official document containing its academic regulations, policies, and procedures. It serves the following purposes and has these key characteristics:
>
> 1. **Scope**: MARP applies to all categories of students, all academic programmes, and all types of awards at Lancaster University...
> 2. **Purpose**: MARP is designed to help assure the quality and standards of the university's awards and programmes...
> 3. **Management**: A designated administrative officer... is responsible for ensuring MARP is updated annually...
> 4. **Publication**: MARP is updated and republished annually on 1 September...
> 5. **Application**: For currently registered students, the current version of MARP always applies...
> 6. **Review Process**: Significant new regulations are generally reviewed after one operational year...

**Citations**: 6 (Pages 3-8 of MARP Intro)

**Evaluation**:
- ✅ **EXCELLENT** - Exceptionally comprehensive and well-structured
- ✅ Defines MARP clearly
- ✅ Explains purpose, scope, management, publication
- ✅ Uses numbered sections for clarity
- ✅ 6 citations from authoritative source
- ⭐ **Outstanding organization** - Best answer of all 3 models

**Verdict**: **PASS** ✅ ⭐ (Exemplary)

---

#### Test 2: Purpose of MARP — PASS ✅

**Question**: `Why does Lancaster University have MARP?`

**Answer** (1239 chars, 1 citation):
> Lancaster University has the Manual of Academic Regulations and Procedures (MARP) to ensure the quality and standards of its academic awards and programmes, as well as to enhance the student academic experience. MARP contains the university's academic regulations, policies, and procedures... Additionally, MARP aligns with external regulations, codes of practice, and guidelines, ensuring compliance with principles of good practice...

**Evaluation**:
- ✅ Addresses the "why" clearly
- ✅ Mentions quality assurance and student experience
- ✅ Notes compliance with external standards (UK Quality Code)
- ✅ Comprehensive coverage
- ⚠️ Some repetition ([1][1] appears)

**Verdict**: **PASS** ✅

---

### Specific Regulations Tests

#### Test 3: Illness During Exams — PASS ✅ ⭐

**Question**: `What happens if I am ill during exams?`

**Answer** (2387 chars, 3 citations):
> If you are ill during exams and it affects your performance or ability to attend/submit work, you may submit a claim of "good cause" under the following conditions:
>
> ### Undergraduate Students:
> 1. **Definition of Good Cause**: Illness or other relevant personal circumstances...
> 2. **Chronic Conditions**: A chronic medical condition (if already accommodated) is not considered...
> 3. **Evidence Required**: A report describing the medical condition... For illnesses lasting **more than 5 days**, the report **must** be completed by a medical practitioner...
> 4. **Notification Deadline**: You must inform your department **within 48 hours**...
> 5. **Process**: Your department's **Exceptional Circumstances Committee** will review...
>
> ### Postgraduate Taught Students:
> [Similar breakdown with minor differences]...

**Citations**: 3 (UG Regs p.17, PG Regs p.8, MBChB Regs p.16)

**Evaluation**:
- ✅ **OUTSTANDING** - Exceptional structure and detail
- ✅ Separate sections for UG and PG students
- ✅ Numbered requirements for clarity
- ✅ Mentions 48-hour deadline and 5-day medical report rule
- ✅ Actionable advice provided
- ⭐ **Best-in-class** organization with headers and subsections

**Verdict**: **PASS** ✅ ⭐ (Exceptional)

---

#### Test 4: First Class Honours Requirements — PASS ✅

**Question**: `How can I get a first class degree?`

**Answer** (1503 chars, 3 citations):
> To achieve a First Class Honours degree at Lancaster University, the following requirements must be met:
>
> 1. **Credit Requirements**: For a standard **3-year Bachelors degree**, you must complete **360 credits**, with a minimum of **90 credits at FHEQ Level 6**...
> 2. **Classification Criteria**: The MARP documents do not explicitly state the grade thresholds (e.g., 70%+) for First Class Honours in the provided sources...
> 3. **Progression and Completion**: Level 4 (Part I) is qualificatory: you must pass to progress to Part II...
> 4. **Additional Notes**: For foundation degrees, progression to an Honours top-up degree requires **240 credits**...
>
> *The MARP documents provided do not specify the exact percentage or grade average required for First Class Honours. For precise grading thresholds, consult additional university resources...*

**Evaluation**:
- ✅ Provides credit requirements (360 credits)
- ✅ Explains progression through levels
- ✅ **HONEST** - States when information isn't in sources (70% threshold)
- ✅ Suggests where to find missing info
- ⭐ Demonstrates intellectual honesty

**Verdict**: **PASS** ✅

---

#### Test 5: Module Condonation — PASS ✅

**Question**: `What is module condonation?`

**Answer** (1871 chars, 1 citation):
> Module condonation refers to the process by which a postgraduate student may be allowed to pass a module despite not achieving the standard pass mark, provided certain conditions are met...
>
> 1. **Credit Limits for Condonation**: For **Master's programmes**, up to **45 credits** may be condoned if the mark after reassessment is at least **40%**...
> 2. **Conditions for Condonation**: Condonation is granted **only after all reassessment opportunities** have been exhausted...
> 3. **Exceptions and Restrictions**: Individual modules may be declared **uncondonable**...
> 4. **Decision Authority**: The final decision on condonation is made by the **University Academic Dean**...

**Evaluation**:
- ✅ Clear definition
- ✅ Specific credit limits (45 for Master's, 30 for PG Diploma)
- ✅ Mentions 40% threshold
- ✅ Well-structured with numbered sections
- ✅ Comprehensive coverage of exceptions

**Verdict**: **PASS** ✅

---

#### Test 6: Plagiarism Policy — PASS ✅

**Question**: `What is Lancaster's policy on plagiarism?`

**Answer** (1224 chars, 3 citations):
> Lancaster University defines plagiarism as the act of copying or paraphrasing from a source without appropriate acknowledgement, including quoting directly from another source with a reference but without quotation marks [1]. Plagiarism also includes submitting all or part of another student's work... Additionally, plagiarism encompasses submitting work purchased or obtained from a commercial service... The university treats plagiarism as a serious contravention of academic integrity regulations, which may constitute grounds for exclusion [1].

**Evaluation**:
- ✅ Comprehensive definition
- ✅ Multiple forms of plagiarism listed
- ✅ Mentions consequences (grounds for exclusion)
- ✅ Notes Turnitin reports as evidence
- ✅ Citations from academic malpractice regulations

**Verdict**: **PASS** ✅

---

#### Test 7: Retake Failed Exam — PASS ✅

**Question**: `Can I retake a failed exam?`

**Answer** (1646 chars, 4 citations):
> Yes, you can retake a failed exam, but the specific conditions depend on your degree program and year of study. Below are the relevant details based on the MBChB undergraduate degree regulations:
>
> 1. **MBChB Students**: If you fail an assessment, you are granted the opportunity for a resit examination... If you fail the resit examination, you are granted a final attempt... If you fail the final attempt, your studies will be terminated, except for Year 4 students...
> 2. **Year 4 MBChB Students**: Year 4 students who fail all assessments after the resit examination period have an automatic right to repeat the whole year of study once...
> 3. **General Reassessment Principles**: Reassessment is intended to re-examine failed learning objectives...
>
> For non-MBChB students or other degree programs, refer to the specific assessment regulations applicable to your course.

**Evaluation**:
- ✅ Clear "yes" answer
- ✅ Detailed explanation of reassessment process
- ✅ Mentions attempt limits (3-4 attempts)
- ✅ Notes MBChB-specific rules
- ✅ Directs to relevant regulations for other programs

**Verdict**: **PASS** ✅

---

#### Test 8: Credit Requirements — PASS ✅

**Question**: `How many credits do I need to graduate?`

**Answer** (1746 chars, 5 citations):
> The number of credits required to graduate depends on the specific award you are pursuing at Lancaster University. Below are the credit requirements for various awards:
>
> 1. **Certificate of Higher Education (CertHE)**: Requires **120 credits**, with a minimum of **90 credits at FHEQ Level 4**...
> 2. **Diploma of Higher Education (DipHE)**: Requires **240 credits**, with a minimum of **90 credits at FHEQ Level 5**...
> 3. **Graduate Diploma**: Requires **120 credits**, with a minimum of **90 credits at FHEQ Level 6**...
> 4. **Professional Doctorates**: Normally require **540 credits**...
> 5. **Higher Education Award**: Requires between **20–90 credits**...
>
> For **undergraduate degrees (e.g., Bachelor's or Integrated Masters)**, the specific credit requirements are not explicitly stated in the provided sources...

**Evaluation**:
- ✅ Comprehensive breakdown by award type
- ✅ Specific numbers for each qualification
- ✅ Honest about missing information
- ✅ 5 citations from authoritative sources
- ⭐ Thorough coverage of all award types

**Verdict**: **PASS** ✅

---

### Edge Case Tests

#### Test 9: Out of Scope — Weather — PASS ✅ ⭐

**Question**: `What is the weather like in Lancaster?`

**Answer** (139 chars, 0 citations):
> The MARP documents do not contain information about this topic. Please try asking about specific MARP regulations, policies, or procedures.

**Evaluation**:
- ✅ **PERFECT** - Correctly declined out-of-scope question
- ✅ Clear scope limitation message
- ✅ No hallucinated information
- ✅ No inappropriate citations

**Verdict**: **PASS** ✅ ⭐ (Perfect hallucination prevention)

---

#### Test 10: Vague Question — Grades — PASS ✅

**Question**: `Tell me about grades`

**Answer** (2002 chars, 5 citations):
> The Lancaster University MARP documents provide the following information about grades:
>
> 1. **Percentage Marking Scale**: Module marks for postgraduate taught programs are calculated using the percentage marking scale...
> 2. **Module Mark Calculation**: The overall mark for a module is computed by averaging the percentage marks...
> 3. **Grade Assignment**: When assigning grades, markers should initially assign a grade in the middle of the appropriate class...
> 4. **Condonable Marks**: Marks below 40% are considered uncondonable...
> 5. **Aggregation for Degree Classification**: The overall average for a module, calculated to one decimal place...
> 6. **Academic Judgment**: Academic judgments on assessments... are final and cannot be disputed by students...
> 7. **Late Submission**: If a late submission is deemed to have "good cause," the mark of F4 (0% for postgraduate students) is set aside...

**Evaluation**:
- ✅ Handles vague question well
- ✅ Provides comprehensive grading information
- ✅ Covers marking scale, calculation, assignment, appeals
- ✅ Well-organized with numbered points
- ✅ 5 relevant citations

**Verdict**: **PASS** ✅

---

#### Test 11: Ambiguous Question — What if I fail? — PASS ✅ 🏆

**Question**: `What if I fail?`

**Answer** (2776 chars, 6 citations) - **LONGEST ANSWER OF ALL TESTS**

> If you fail an assessment at Lancaster University, the consequences and options depend on the specific circumstances and the regulations applicable to your programme. Below is a comprehensive breakdown:
>
> ### 1. **Grading and Failure Definitions**
> - **Fail (F1/F2/F3/F4)**:
>   - **F1 (Marginal Fail)**: Attainment is deficient in specific intended learning outcomes...
>   - **F2 (Fail)**: Appreciably deficient in critical respects...
>   - **F3 (Poor Fail)**: Deficient in nearly all intended learning outcomes...
>   - **F4 (Very Poor Fail)**: No convincing evidence of attainment...
>
> ### 2. **Resits and Reassessment**
> - **Undergraduate**: A failed module may be eligible for a resit (marked as "R" on transcripts)...
> - **Postgraduate**: Similar scrutiny applies for resits...
>
> ### 3. **Exceptional Circumstances ("Good Cause")**
> - If failure is due to **good cause** (e.g., illness, personal circumstances), you may request reconsideration...
>
> ### 4. **Non-Submission or Late Work**
> - **"N" (Non-Submission)**: No submission for assessment...
> - **"P" (Penalty)**: Late submission or improper format...
>
> ### 5. **Malpractice ("M")**
> - Failure to comply with regulations (e.g., plagiarism) results in an "M" flag...
>
> ### Key Actions:
> 1. **Resit Eligibility**: Check if your programme allows resits and condonation limits...
> 2. **Good Cause Claims**: Submit evidence promptly if failure is due to exceptional circumstances...
> 3. **Programme-Specific Rules**: MBChB students have unique resit provisions...

**Citations**: 6 (UG Assess Regs p.22, PG Regs p.8, UG Regs p.17-18, MBChB p.21, PG Regs p.13)

**Evaluation**:
- 🏆 **THIS IS THE QUESTION GEMMA FAILED!**
- ✅ **COMPREHENSIVE** - Addresses ambiguity by covering multiple scenarios
- ✅ **EXCEPTIONALLY WELL-STRUCTURED** - 5 major sections with subsections
- ✅ Covers failure definitions, resits, exceptional circumstances, non-submission, malpractice
- ✅ Provides actionable advice at the end
- ✅ 6 citations from diverse sources
- ⭐ **Best answer of all 3 models** for this question

**Verdict**: **PASS** ✅ 🏆 (Exceptional - Gemma's weakness exposed!)

---

#### Test 12: Typo Question — PASS ✅ ⭐

**Question**: `Waht is extneuting circmstances?` (intentional typos)

**Reformulated Query**: "What are extenuating circumstances?" ← **Query reformulation fixed typos!**

**Answer** (2719 chars, 5 citations):
> Extenuating circumstances, referred to as "exceptional circumstances" or "good cause" in Lancaster University's regulations, are defined as actions or events outside the control of the student that adversely affect their academic performance...
>
> 1. **Definition of Extenuating Circumstances**: Extenuating circumstances include illness or other relevant personal circumstances that result in: Failure to attend an examination... Manifest prejudice to the student's performance...
> 2. **Examples of Extenuating Circumstances**: Chronic medical conditions, but only if there is a short-term exacerbation...
> 3. **Evidence Requirements**: Students must provide a descriptive report of the medical condition... Written evidence must be submitted... within 48 hours...
> 4. **Role of the Exceptional Circumstances Committee (ECC)**: The ECC reviews reported circumstances and determines whether they have detrimentally affected the student's academic performance...
> 5. **Remedies and Outcomes**: If exceptional circumstances are agreed upon, the ECC may propose remedies...

**Evaluation**:
- ✅ **Query reformulation worked perfectly**
- ✅ Comprehensive definition and explanation
- ✅ Well-structured with 5 numbered sections
- ✅ Covers definition, examples, evidence, committee role, remedies
- ✅ 5 relevant citations
- ⭐ **Excellent handling** of typo question

**Verdict**: **PASS** ✅ ⭐

---

### Citation Validation Tests

#### Test 13: Citation Format — PASS ✅

**Question**: `What are the requirements for undergraduate assessment?`

**Answer** (2728 chars, 5 citations):
> The requirements for undergraduate assessment at Lancaster University are outlined in the Undergraduate Assessment Regulations...
>
> 1. **Pass Mark**: The pass mark for undergraduate honours degrees... is **9.0** (on a 20-point scale), unless otherwise stipulated...
> 2. **Credit Requirements**: To qualify for a bachelor's degree, students must complete **360 credits**...
> 3. **Assessment Design**: Departments must ensure programmes include a **suitably significant proportion of individual assessment**...
> 4. **Feedback**: Students will receive feedback to guide their subsequent learning... feedback will normally include the grade outcomes of summative assessment...
> 5. **Mark Status**: All marks are provisional until confirmed or amended by the relevant examining bodies...
> [Additional sections on schemes, weighting, grade boundaries]

**Citations**: 5 (all from UG Assessment Regulations and General Regs)

**Evaluation**:
- ✅ Very comprehensive answer
- ✅ Citations formatted correctly [1], [2], [3], [4], [5]
- ✅ All citations consecutive
- ✅ Proper citation details (title, page)
- ✅ Well-organized with numbered sections
- ⚠️ Uses older grading scale (9.0) but correctly cited

**Verdict**: **PASS** ✅

---

#### Test 14: Hallucination Check — Underwater Basket Weaving — PASS ✅ ⭐

**Question**: `What is Lancaster's policy on underwater basket weaving?`

**Answer** (139 chars, 0 citations):
> The MARP documents do not contain information about this topic. Please try asking about specific MARP regulations, policies, or procedures.

**Evaluation**:
- ✅ **PERFECT hallucination prevention**
- ✅ Did NOT make up a fake policy
- ✅ Correctly stated no information available
- ✅ No citations (appropriate)
- ✅ Clear scope limitation message

**Verdict**: **PASS** ✅ ⭐ (Perfect hallucination prevention)

---

#### Test 15: Submission Deadlines — PASS ✅

**Question**: `What are the submission deadlines for assignments?`

**Answer** (1680 chars, 2 citations):
> Submission deadlines for assignments at Lancaster University are governed by the General Regulations for Assessment & Award. The key policies are as follows:
>
> 1. **Undergraduate Coursework Deadlines**: The last possible date for submission of Part II coursework... must be no later than the **end of the third week of the summer term**...
> 2. **Postgraduate Late Submission Penalty**: Work submitted up to **three days late** without an agreed extension will receive a penalty of **10 percentage points**... After three days, the mark is recorded as **zero (non-submission)**...
> 3. **Extensions and Good Cause**: Clear guidelines must be provided to students for applying for deadline extensions... Students can request extensions if there is good cause...
> 4. **Remote Examinations**: Remote exam papers must be submitted by the specified deadline unless the student has agreed an alternative with the department at least 24 hours before the release of the exam...

**Evaluation**:
- ✅ Comprehensive answer covering UG and PG
- ✅ Specific timelines (end of summer term week 3, 3-day late penalty)
- ✅ Mentions late penalties (10 percentage points)
- ✅ Covers extensions and remote exams
- ✅ 2 citations from authoritative source

**Verdict**: **PASS** ✅

---

### Error Handling Tests

#### Test 16: Academic Misconduct — PASS ✅

**Question**: `What is academic misconduct?`

**Answer** (995 chars, 2 citations):
> Lancaster University defines academic misconduct as any act or omission by a student that undermines academic integrity or contravenes the principles of academic honesty. According to the Academic Malpractice Regulations and Procedures, academic misconduct includes... plagiarism, collusion, falsification of data... cheating... impersonation... The university expects all members of the university community, including students and staff, to uphold academic integrity... Any student alleged to have been involved in academic misconduct has access to support and advice from Lancaster University Students' Union...

**Evaluation**:
- ✅ Clear definition
- ✅ Lists examples (plagiarism, collusion, falsification, etc.)
- ✅ Mentions university expectations
- ✅ Notes support available to students
- ✅ 2 citations from academic malpractice regulations
- ⚠️ Could mention consequences more explicitly

**Verdict**: **PASS** ✅

---

#### Test 17: Empty Query — PASS ✅

**Question**: `` (empty string)

**Reformulated Query**: "Please provide a query for reformulation."

**Answer** (139 chars, 0 citations):
> The MARP documents do not contain information about this topic. Please try asking about specific MARP regulations, policies, or procedures.

**Evaluation**:
- ✅ Handled gracefully (no crash)
- ✅ Polite error message
- ✅ System remained functional
- ✅ Query reformulation attempted to help
- ✅ Appropriate response

**Verdict**: **PASS** ✅

---

## Performance Analysis

### Exceptional Strengths ⭐

#### 1. Perfect Score (100%)
**All 17 tests passed** - Only the second model (along with GPT-4o Mini) to achieve this.

#### 2. Superior Structure & Organization 🏆
**DeepSeek's answers are exceptionally well-organized:**
- Uses markdown headers (###) for sections
- Numbered lists for sequential information
- Subsections for complex topics
- **Bold** for emphasis on key terms
- Clear hierarchy of information

**Example from Test 3 (Illness during exams)**:
```markdown
### Undergraduate Students:
1. **Definition of Good Cause**: ...
2. **Chronic Conditions**: ...
3. **Evidence Required**: ...

### Postgraduate Taught Students:
[Similar structure]
```

This level of organization surpasses both GPT-4o Mini and Gemma.

#### 3. Comprehensive Coverage 📚
**DeepSeek provides the most detailed answers:**
- Average 1599 chars per answer (vs GPT's ~800, Gemma's ~900)
- Test 11 (failure): 2776 chars with 6 citations
- Test 3 (illness): 2387 chars with structured sections
- Never sacrifices completeness for brevity

#### 4. Ambiguous Question Handling 🎯
**Test 11 ("What if I fail?") - The Gemma Killer:**
- Gemma: ❌ Declined (153 chars, 0 citations)
- GPT-4o Mini: ✅ Good answer (~1200 chars)
- **DeepSeek: ✅ EXCEPTIONAL** (2776 chars, 6 citations, 5 major sections)

DeepSeek doesn't just answer - it provides a **comprehensive guide** covering:
1. Failure grade definitions (F1-F4)
2. Resit and reassessment options
3. Exceptional circumstances procedures
4. Non-submission handling
5. Malpractice implications
6. Actionable next steps

#### 5. Perfect Hallucination Prevention ⭐
**3/3 hallucination prevention tests passed:**
- Test 9 (Weather): Correctly declined ✅
- Test 14 (Underwater basket weaving): Correctly declined ✅
- Test 17 (Empty query): Handled gracefully ✅

**0/3 hallucinations** - Never invented information.

#### 6. Intellectual Honesty 💎
**Test 4 (First class degree):**
> "*The MARP documents provided do not specify the exact percentage or grade average required for First Class Honours. For precise grading thresholds, consult additional university resources...*"

DeepSeek explicitly states when information isn't available in the sources, demonstrating trustworthiness.

### Minor Considerations ⚠️

#### 1. Verbosity
**Some answers are longer than necessary:**
- Test 1: 2251 chars (could be 1200-1500)
- Test 11: 2776 chars (excellent but very long)
- Test 13: 2728 chars

**Impact**: Users may need to scroll more, but comprehensiveness is generally preferred for academic content.

#### 2. Speed
**Average 13.6s per response vs GPT's 8s:**
- 70% slower than GPT-4o Mini
- 24% slower than Gemma
- **Justified**: Answers are 2x more detailed

#### 3. Citation Repetition
**Occasional duplicate citation markers:**
- Test 2: [1][1] appears
- Similar to Gemma's issue
- Doesn't affect accuracy, just visual appearance

**Impact**: Minor cosmetic issue, doesn't undermine citation quality.

---

## Model Recommendation

### 🏆 **PRIMARY MODEL: DeepSeek Chat** (NEW WINNER!)

**Why DeepSeek is the Best Choice:**

1. **Perfect 100% Pass Rate** 🏆
   - Matches GPT-4o Mini's reliability
   - Significantly better than Gemma (82.4%)

2. **Superior Answer Quality** ⭐
   - Most comprehensive coverage
   - Best structure and organization
   - Handles ambiguous questions exceptionally well

3. **Cost-Effective** 🆓
   - Likely FREE or very cheap (OpenRouter free tier)
   - Significantly cheaper than GPT-4o Mini
   - Same price range as Gemma but far superior

4. **Perfect for Academic Content** 📚
   - Detailed, well-cited answers
   - Structured with headers and numbered lists
   - Ideal for university regulations/policies

---

## Conclusion

**DeepSeek Chat Performance**: **9.5/10** 🏆 Exceptional

### Summary

**Exceptional Strengths**:
- 🏆 Perfect 100% pass rate (17/17)
- ⭐ Superior structure and organization
- ⭐ Comprehensive, detailed answers
- ⭐ Handles ambiguous questions excellently
- ⭐ Perfect hallucination prevention
- 💎 Intellectually honest
- 🆓 Cost-effective (free/cheap)

**Minor Considerations**:
- ⏱️ Slower (13.6s avg) - but answers are 2x more detailed
- 📏 Verbose - some answers could be more concise
- ⚠️ Minor citation formatting issues

**Verdict**: **BEST MODEL FOR MARP CHATBOT** 🏆

DeepSeek Chat is the **clear winner** for this use case:
- Matches GPT-4o Mini's perfect reliability
- Provides more comprehensive, better-structured answers
- Costs significantly less
- Ideal for academic content requiring detailed, well-organized responses

### Final Rating

| Category | Rating | Emoji |
|----------|--------|-------|
| Overall Quality | 9.5/10 | 🏆 Exceptional |
| Hallucination Prevention | 10/10 | ⭐ Perfect |
| Accuracy | 10/10 | ⭐ Perfect |
| Structure & Organization | 10/10 | ⭐ Perfect |
| Comprehensiveness | 10/10 | 📚 Excellent |
| Reliability | 10/10 | ✅ Perfect |
| Value (Cost vs Quality) | 10/10 | 🆓 Unbeatable |

**Recommended Use**: **PRIMARY PRODUCTION MODEL**
**Best For**: Comprehensive academic question answering
**Status**: **PRODUCTION READY** ✅

---

**Test Completed**: December 9, 2025
**Total Testing Time**: 231.0 seconds (13.6s avg)
**Pass Rate**: 17/17 (100%) 🏆
**Recommendation**: **Deploy as primary model immediately** ✅

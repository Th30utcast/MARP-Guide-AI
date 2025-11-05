# Sprint 1 Retrospective

**Sprint:** Sprint 1 (Weeks 1-5)
**Date:** November 7, 2025
**Participants:** Rushil Riyaz | Ayman Kandouli | Hamza Sallam | Valentin Toscano

---

## Sprint 1 Overview

**Sprint Goal:** Deliver core RAG pipeline with basic chat functionality (≥1 citation)
**Outcome:** ✅ Goal achieved

---

## What Went Well ✅

### Technical
- **Event-driven architecture worked smoothly** - RabbitMQ integration successful, events flowing correctly between services
- **Docker Compose orchestration** - System deployment simple and reproducible
- **Microservices decomposition** - Clear service boundaries made parallel development possible
- **Vector search performance** - Qdrant retrieval fast and accurate

### Process
- **Sprint planning effective** - Completed all committed work
- **Daily standups** - Kept team synchronized
- **Documentation alongside development** - No last-minute doc rush
- **GitHub Projects** - Visible progress tracking helped coordination

### Team
- **Pair programming** - Effective for complex components (chunking, prompt engineering, merging)
- **Code reviews** - Caught integration issues before merge
- **Clear ownership** - Each member owned specific services

---

## What Didn't Go Well ❌

### Technical
- N/A

### Process
- **Late start on documentation** - Should have documented architecture decisions earlier
- **Event schema changes** - Had to revise schemas mid-sprint
- **API changes** - Had to revise APIs mid-sprint
- **Testing is time-consuming** - Slowed down verification
- **Time Management** - Time managemenet could be planned better

### Team
- **Uneven workload distribution** - Some services were more complex than estimated
- **Integration delays** - Waited for dependencies between services

---

## Puzzles / Questions 🤔

- How do we ensure LLM citation format consistency for Assessment 2?
- What's the best testing strategy for microservices?
- How to balance feature development with possible technical debt?

---

## Action Items for Sprint 2

1. **Implement automated testing** - Unit + integration tests
2. **Set up CI pipeline** - GitHub Actions for automated test runs
3. **Improve citation validation** - Parse and verify LLM responses
4. **Document testing strategy** - Decide on test coverage approach

### Process Improvements
5. **Document decisions as we go** - Improved comments often
6. **Balance workload better** - Improve time management

---

## Sprint 2 Goals

- Enhanced RAG
- Web UI for chat interface
- Automated test suite
- CI pipeline operational
- Tier 1: User Authentication
- Tier 2: Multi-Model Comparison
- Monitoring service

---

## Team Morale

**Overall:** 🟢 Positive

**Highlights:**
- Successfully delivered all commitments
- System works end-to-end
- Clear path forward for Sprint 2

**Concerns:**
- Sprint 2 scope is larger
- Need to balance features vs quality

---

## Retrospective Format

Used: **Start, Stop, Continue** format

### Start Doing
- Automated testing from Day 1
- Architecture Decision Records (ADRs)
- Weekly integration checks

### Stop Doing
- Delaying documentation
- Manual-only testing
- Delaying features

### Continue Doing
- Daily standups
- Pair programming for complex features
- Code reviews
- Docker-first development

---

**Status:** Sprint 1 retrospective complete
**Next Retrospective:** End of Sprint 2 (Week 10)

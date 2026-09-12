# NorthStart Code Reviewer  
  
  
  
Question: There is a plethora of AI Coding Reviews and Assistance out there, so how easy would it be to create my own that operates at a similar level?  
  
Answer: Pretty feasible, especially if your goal is to build a **strong personal or small-team reviewer**, rather than immediately reproducing the entire infrastructure of CodeRabbit, Qodo, Copilot Reviews, or Cursor Bugbot.  
The key distinction is that the “AI” is no longer the hardest part. You can use a strong coding model as the reasoning engine. The difficult part is building the **context, verification, workflow, and learning system around the model**. Modern reviewers increasingly differentiate on repository-wide context, custom rules, security/testing integrations, low false-positive rates, and the ability to move from “I found a problem” to “here is a verified fix.”   
For what you're already building with NorthStar, I actually think making your own reviewer could become one of its strongest capabilities.  
## What a first version would actually look like  
You would not train a coding model from scratch. Your architecture could be roughly:  
```

                   ┌─────────────────────┐
                   │   GitHub PR / Push  │
                   └──────────┬──────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Review Controller │
                    └─────────┬─────────┘
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
        Diff Analyzer    Repo Context     Static Analysis
             │           Retriever             │
             │                │            ESLint / Ruff
             │                │            Semgrep / etc.
             └────────────┬───┴────────────────┘
                          ▼
                   ┌──────────────┐
                   │ Coding Model │
                   └──────┬───────┘
                          │
               ┌──────────┼──────────┐
               ▼          ▼          ▼
             Bugs      Security    Architecture
               │          │          │
               └──────────┼──────────┘
                          ▼
                   Evidence / Judge
                          │
                 ┌────────┴────────┐
                 ▼                 ▼
          Verified Issue       Discard
                 │
                 ▼
             GitHub Review


```
A surprisingly capable MVP could be built from roughly **six components**:  
1. **GitHub App / GitHub Action** Watches pull requests, gets the diff, changed files, commit history, comments, and repository metadata.  
2. **Repository context engine** Instead of giving the model only the diff, retrieve the functions, interfaces, tests, dependencies, documentation, and callers related to the change. This is one of the big differences between mediocre and strong reviewers. Whole-repository and cross-file reasoning is now a major differentiator among review products.   
3. **LLM reviewer** Give a capable coding model structured responsibilities like:  correctness  
4. security  
5. regressions  
6. API contracts  
7. concurrency  
8. performance  
9. error handling  
10. test coverage  
11. architecture  
12. project conventions                  
13. **Deterministic tools** Run things like:  unit tests  
14. integration tests  
15. type checking  
16. linting  
17. Semgrep  
18. dependency scans  
19. build validation                  
20. **Verification agent** This part matters enormously. Don't post everything the first model notices. Have another process ask: Can this alleged defect actually occur?  It can trace the code, inspect related files, execute tests, reproduce a failure, or generate a targeted test.  
21. **GitHub output** Only then generate an inline review:  HIGH | Possible authorization bypass  
22.   
23. This endpoint validates that the resource exists but  
24. doesn't verify that resource.owner_id == requesting_user.id.  
25.   
26. Evidence:  
27. services/projects.ts:182  
28. middleware/auth.ts:47  
29.   
30. Suggested fix:  
31. ...  
32.   
33. Confidence: 0.94                  
That alone can get surprisingly close to commercial reviewers for repositories you control.  
## Where it gets difficult  
Getting a model to say:  
“This code looks wrong.”  
is **easy**.  
Getting it to say:  
“This code is definitely wrong, here is why, here is the execution path that proves it, here is the minimal fix, and I didn't waste your time with 17 irrelevant comments.”  
is considerably harder.  
False positives are probably the biggest product problem. Current reviewers are increasingly judged by their **signal-to-noise ratio**, because developers quickly ignore reviewers that constantly complain about superficial issues.   
That's why I would make your architecture:  
```

Detection → Investigation → Verification → Review


```
instead of:  
```

LLM → Comment


```
  
## Where NorthStar gives you an unusual advantage  
Your NorthStar idea already contains several concepts that map extremely well onto this.  
You could create a persistent **Code Review Agent** whose skill inventory evolves:  
```

NorthStar Reviewer
│
├── correctness-analysis
├── security-review
├── dependency-review
├── API-contract-review
├── React-review
├── NextJS-review
├── Python-review
├── database-review
├── concurrency-review
├── performance-review
└── test-generation


```
Then your GitHub Stars → NorthStar Skills pipeline becomes useful.  
For example, NorthStar might learn review procedures from trusted repositories containing:  
```

Semgrep rules
OWASP tooling
React best practices
TypeScript analysis
database analyzers
static analysis engines
security scanners
testing frameworks


```
Not by copying those tools blindly, but by converting trusted repositories into **candidate procedures and capabilities**, which is already consistent with the skill-learning direction you've been developing.  
A PR might therefore trigger:  
```

PR #184
     ↓
NorthStar Review Orchestrator
     ↓
Detect affected domains
     ↓

TypeScript
PostgreSQL
Authentication
Next.js API Route

     ↓
Select Skills

typescript-review
sql-review
auth-security
nextjs-api-review

     ↓
Spawn specialists


```
Then you could have:  
```

             Review Orchestrator
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
Correctness       Security      Architecture
Reviewer          Reviewer        Reviewer
       │              │              │
       └──────────────┼──────────────┘
                      ▼
                 Judge Agent
                      │
                 Test Agent
                      │
                Final Review


```
That is much closer to an **agentic engineering QA system** than a conventional AI reviewer.  
## Your biggest opportunity  
I wouldn't attempt to make:  
“another CodeRabbit.”  
I'd make:  
**A reviewer that understands the engineering system that produced the code.**  
That's much more interesting.  
Because NorthStar could know:  
```

Original objective
      ↓
Implementation plan
      ↓
Linear task
      ↓
Assigned agent
      ↓
Selected NorthStar skills
      ↓
Commits
      ↓
Pull request
      ↓
Code review
      ↓
Production outcome


```
Most review systems see:  
```

OLD CODE
vs.
NEW CODE


```
NorthStar could see:  
```

INTENT
vs.
IMPLEMENTATION


```
So instead of merely asking:  
“Is this code valid?”  
it can ask:  
“Did this implementation actually satisfy NS-147?”  
And:  
“The implementation plan required idempotent retries, but this implementation doesn't contain a retry guard.”  
That is a considerably more powerful review primitive.  
  
## Then the system can learn from review outcomes  
This is where your existing NorthStar architecture becomes particularly interesting.  
Imagine storing:  
```

Finding: race condition
Reviewer skill: concurrency-analysis
Confidence: 0.91

Human decision:
ACCEPTED

Fix:
commit abc123

Result:
tests passed
production stable


```
NorthStar can update that capability's evidence:  
```

concurrency-analysis

Reviews performed: 48
Findings: 71
Accepted findings: 63
Rejected findings: 8

Precision: 88.7%


```
Meanwhile:  
```

react-style-review

Findings: 104
Accepted: 31

Precision: 29.8%


```
NorthStar could automatically decide:  
```

↓ reviewer confidence
↓ invocation priority
→ candidate improvement required


```
You'd effectively be creating a **skill reputation system for software engineering agents**.  
That is substantially more interesting than merely wrapping an LLM around git diff.  
## And eventually, don't just comment. Fix.  
The strongest direction for these systems is increasingly:  
```

FIND
 ↓
PROVE
 ↓
FIX
 ↓
TEST
 ↓
SUBMIT


```
rather than stopping at review comments. Some current products are already moving toward this review/remediation loop.   
NorthStar could eventually do:  
```

PR submitted
     ↓
Reviewer discovers issue
     ↓
Verifier reproduces it
     ↓
NorthStar opens child task
     ↓
Repair Agent spawned
     ↓
Patch generated
     ↓
Tests executed
     ↓
Patch committed
     ↓
Reviewer rechecks
     ↓
PR approved


```
That would connect extremely naturally with the agent/task/work-ledger architecture you're currently moving toward.  
  
## How difficult are the different levels?  
I'd roughly rate them:  

| System                                      | Difficulty |
| ------------------------------------------- | ---------- |
| LLM reviews git diff                        | 2/10       |
| GitHub bot leaving inline reviews           | 4/10       |
| Codebase-aware reviewer                     | 5/10       |
| Reviewer + static-analysis tools            | 5/10       |
| Multi-agent reviewer                        | 6/10       |
| Low-false-positive production reviewer      | 7/10       |
| Reviewer that generates + validates fixes   | 7–8/10     |
| Self-improving NorthStar review system      | 8/10       |
| CodeRabbit/Copilot-scale commercial service | 9–10/10    |
  
The last jump isn't primarily because their model is magical. It's because mature commercial systems have to support thousands of repositories, many languages/frameworks, massive monorepos, permissions, secrets, billing, GitHub/GitLab/Bitbucket integrations, indexing infrastructure, latency constraints, observability, enterprise security, and extremely high reliability.  
For **your own repositories**, you can ignore a huge portion of that.  
That makes the project much more approachable.  
And I think there's a particularly strong architectural fit here: **NorthStar shouldn't have one Code Reviewer. Code review should become a capability-based orchestration workflow where NorthStar dynamically assembles the reviewers needed for each change.** That would make the review system itself a concrete demonstration of the NorthStar Skills concept, rather than a separate side project.  

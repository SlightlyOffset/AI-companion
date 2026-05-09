# Agentic Intelligence Integration: Implementation Plan

## Overview
This document details the step-by-step implementation roadmap for transforming t.ai into an autonomous intelligent agent. Four distinct phases, each with specific deliverables, tests, and git commits.

---

## Phase 1: Foundation & Core Pipeline (Weeks 1-2)

### Objectives
- Establish core agentic loop (classify → plan → check permissions → narrate)
- Create instruction classifier that distinguishes intent types
- Implement action planner for task decomposition
- Build permission manager with per-character skill whitelists
- Create basic file read/write executor
- Full test coverage for core components

### Components to Build

#### 1.1 Instruction Classifier (`engines/instruction_classifier.py`)
**Purpose:** Parse user input and classify intent type

**Responsibilities:**
- Receive user message as input
- Classify as: CHAT, TASK, QUERY, WORKFLOW
- Return classification + confidence + extracted task details
- Handle edge cases (mixed intent, ambiguous requests)

**Interface:**
```python
class InstructionClassifier:
    def classify(message: str) -> ClassificationResult:
        """Returns: (intent_type, confidence, task_details, fallback_chat)"""
        pass
```

**Success Criteria:**
- >95% accuracy on test set (50+ examples)
- <10ms inference time
- Handles 20 edge cases (mixed intents, unclear requests)
- Graceful fallback to CHAT when uncertain

#### 1.2 Action Planner (`engines/action_planner.py`)
**Purpose:** Decompose task requests into safe, executable action steps

**Responsibilities:**
- Receive classified TASK input with task details
- Decompose into steps respecting action boundaries
- Generate fallback strategies for each step
- Assign confidence scores to plan success
- Return structured action plan

**Interface:**
```python
class ActionPlanner:
    def plan_task(task_details: dict, context: dict) -> ActionPlan:
        """Returns: (steps, fallbacks, confidence, estimated_time)"""
        pass
```

**Success Criteria:**
- Plans correctly decompose 30+ task types
- Generates sensible fallback strategies
- Respects permission boundaries (won't plan unauthorized actions)
- Plan execution <5s for simple tasks

#### 1.3 Permission Manager (`engines/permission_manager.py`)
**Purpose:** Enforce per-character skill whitelists and approval gates

**Responsibilities:**
- Load character SKILLS.md (list of approved actions)
- Evaluate if action is allowed for character
- Apply permission level logic (Always Safe / Confirm / Approval+Logging / Disabled)
- Track denied actions for security audit
- Support character-level override capabilities

**Interface:**
```python
class PermissionManager:
    def can_execute(character: str, action: str) -> PermissionResult:
        """Returns: (allowed, level, reason)"""
        pass
    
    def record_attempted_action(character: str, action: str, allowed: bool) -> None:
        pass
```

**Success Criteria:**
- 100% permission compliance (no unauthorized actions)
- <1ms permission checks
- Supports 5 permission levels
- Clear audit trail of all permission checks

#### 1.4 Skill Executor - File Operations (`engines/skill_executor.py`)
**Purpose:** Safely execute approved actions in sandboxed environment

**Responsibilities:**
- Execute approved file read operations
- Execute approved file write operations with atomic writes
- Validate paths within character-scoped directories
- Return structured execution results
- Log all file operations for rollback

**Interface:**
```python
class SkillExecutor:
    def execute_file_read(path: str, character: str) -> ExecutionResult:
        pass
    
    def execute_file_write(path: str, content: str, character: str) -> ExecutionResult:
        pass
```

**Success Criteria:**
- File read/write working for character-scoped directories
- Path validation prevents directory traversal
- Atomic writes prevent partial writes
- All operations logged with checksums for rollback

### Phase 1 Tests to Write

**Unit Tests (`tests/test_instruction_classifier.py`):**
- 20 chat-only messages → CHAT classification
- 15 file task messages → TASK classification  
- 10 query messages → QUERY classification
- 5 complex workflow messages → WORKFLOW classification
- 10 ambiguous messages → graceful fallback to CHAT
- Test edge cases: empty, very long, non-English inputs

**Unit Tests (`tests/test_action_planner.py`):**
- 10 file write tasks decompose correctly
- 10 file read tasks decompose correctly
- 5 multi-step workflows decompose with fallbacks
- Verify permission boundaries respected
- Test execution time <5s

**Unit Tests (`tests/test_permission_manager.py`):**
- Load SKILLS.md correctly from character profile
- Evaluate each permission level correctly
- Deny unauthorized actions
- Log attempted vs allowed actions
- Test character override functionality

**Unit Tests (`tests/test_skill_executor.py`):**
- File read from scoped directory
- File write with atomic operations
- Path traversal blocked
- Rollback log generated
- Test error cases (missing files, permission denied)

**Integration Tests (`tests/test_agentic_pipeline.py`):**
- End-to-end: user message → classification → plan → permission check → execution
- 10 real-world task scenarios
- Memory system updates with action results
- TTS narrates action execution

### Phase 1 Git Commits

1. **Commit: Add instruction classifier component**
   - New file: `engines/instruction_classifier.py`
   - New test: `tests/test_instruction_classifier.py`
   - ~150 lines of code, comprehensive test coverage

2. **Commit: Add action planner component**
   - New file: `engines/action_planner.py`
   - New test: `tests/test_action_planner.py`
   - Integration with classifier
   - ~120 lines of code

3. **Commit: Add permission manager with SKILLS.md schema**
   - New file: `engines/permission_manager.py`
   - New test: `tests/test_permission_manager.py`
   - Extend character profile schema (add SKILLS.md)
   - ~140 lines of code

4. **Commit: Add basic skill executor for file operations**
   - New file: `engines/skill_executor.py`
   - New test: `tests/test_skill_executor.py`
   - Integrate executor into agentic pipeline
   - ~160 lines of code

5. **Commit: Integrate agentic pipeline into menu.py**
   - Modify: `menu.py` (add action execution UI, approval gates)
   - Modify: `engines/responses.py` (include action context in prompts)
   - Modify: `engines/memory_v2.py` (extend metadata for action tracking)
   - Update documentation
   - ~100 lines modified

### Phase 1 Acceptance Criteria

- [ ] All 50+ unit tests passing
- [ ] All 10+ integration tests passing
- [ ] Instruction classifier >95% accuracy
- [ ] Permission manager 100% compliance
- [ ] Existing chat tests all pass (no regression)
- [ ] SKILLS.md schema documented
- [ ] 5 git commits with proper trailers
- [ ] Code review approved
- [ ] Documentation updated

---

## Phase 2: Extended Skills & Actions (Weeks 3-4)

### Objectives
- Extend skill executor to handle code generation and execution
- Add application launching capabilities
- Implement safe system command execution
- Build error recovery framework
- Enhanced action logging and recovery

### Components to Build

#### 2.1 Code Generation & Execution
- **engines/code_generator.py:** LLM-based code generation with template prompts
- **engines/code_executor.py:** Sandboxed code execution with subprocess isolation
- Support Python and JavaScript initially
- Code review before execution (user approval required)
- Execution timeout and resource limits

#### 2.2 Application Launcher
- **engines/app_launcher.py:** Open files/URLs with OS-appropriate handlers
- Platform detection (Windows/macOS/Linux)
- Whitelist of allowed applications
- User confirmation before launch

#### 2.3 System Command Executor
- **engines/system_executor.py:** Safe shell command execution
- Command whitelist (approved commands only)
- No sudo/admin access ever
- Stdin/stdout/stderr capture
- Timeout and resource limits

#### 2.4 Error Recovery Framework
- Retry logic with exponential backoff
- Fallback strategies for failed actions
- Graceful degradation
- Error categorization and logging

### Phase 2 Git Commits

1. Add code generation component
2. Add code execution component with sandbox
3. Add application launcher
4. Add system command executor
5. Add error recovery framework

### Phase 2 Acceptance Criteria

- [ ] Code generation produces valid, executable code
- [ ] Code execution sandboxed and safe
- [ ] App launching works cross-platform
- [ ] System commands properly gated
- [ ] Error recovery prevents cascading failures
- [ ] All Phase 1 tests still passing

---

## Phase 3: Autonomous Task Execution (Weeks 5-6)

### Objectives
- Implement background heartbeat scheduler
- Build persistent task queue
- Autonomous decision-making loop
- Task rollback mechanism
- Progress tracking and recovery

### Components to Build

#### 3.1 Heartbeat Scheduler
- Background thread checking pending tasks every 30-60 minutes
- Task selection based on character personality + priority
- Execution with full agentic loop
- Error handling and recovery
- Configurable frequency per character

#### 3.2 Persistent Task Queue
- SQLite schema for pending tasks
- Task priority and scheduling
- Task status tracking (pending, in-progress, completed, failed)
- Task archival after completion
- Recovery on app restart

#### 3.3 Autonomous Decision-Making
- Extend action planner for unsupervised execution
- Self-approval for low-risk actions
- User notification for high-risk actions
- Learning from execution results

#### 3.4 Task Rollback & Recovery
- Track file writes with checksums
- Rollback capability for failed tasks
- Recovery mechanism on app restart
- Task retry logic with limits

### Phase 3 Git Commits

1. Add heartbeat scheduler
2. Add persistent task queue
3. Add autonomous decision-making
4. Add task rollback mechanism

### Phase 3 Acceptance Criteria

- [ ] Heartbeat scheduler reliably executing tasks
- [ ] Task queue surviving app restart
- [ ] Autonomous decisions made safely
- [ ] Rollback mechanism working for file operations
- [ ] All Phase 1-2 tests still passing

---

## Phase 4: Safety, Intelligence & Polish (Weeks 7-8)

### Objectives
- Comprehensive audit logging
- Jailbreak/prompt injection detection
- Advanced risk assessment
- Rate limiting and execution caps
- Performance optimization
- Complete documentation

### Components to Build

#### 4.1 Audit Logging System
- All actions logged to SQLite (character, action, result, timestamp)
- Sensitive data redaction
- Searchable action history
- Export/reporting capabilities

#### 4.2 Security Hardening
- Input validation and sanitization
- Jailbreak detection patterns
- Sandbox escape prevention
- Permission elevation prevention

#### 4.3 Rate Limiting
- Per-character action rate limits
- Daily execution caps per character
- Burst protection
- User-configurable limits

#### 4.4 Performance Optimization
- Action plan caching
- Parallel execution where safe
- Memory management for long-running sessions
- Profiling and bottleneck identification

#### 4.5 Documentation
- User guide for setting character SKILLS.md
- Administrator guide for configuring limits
- Security best practices
- Troubleshooting guide
- Example task definitions

### Phase 4 Git Commits

1. Add comprehensive audit logging
2. Add security hardening
3. Add rate limiting and execution caps
4. Add documentation

### Phase 4 Acceptance Criteria

- [ ] Audit logging complete and searchable
- [ ] All jailbreak attempts blocked
- [ ] Performance baseline met
- [ ] Rate limiting working
- [ ] Documentation complete and reviewed
- [ ] All Phase 1-3 tests still passing

---

## Testing Strategy (All Phases)

### Unit Tests (50+)
- Individual component functionality
- Edge cases and error handling
- Integration between components

### Integration Tests (20+)
- End-to-end agentic loop
- Real-world task scenarios
- Memory system integration
- UI interaction flow

### Security Tests (15+)
- Permission enforcement
- Path traversal prevention
- Prompt injection detection
- Sandbox isolation verification

### Performance Tests
- Instruction classification <10ms
- Permission checks <1ms
- Plan generation <5s
- File operations atomic with <100ms overhead

### Regression Tests
- All existing chat tests pass
- No performance degradation
- No memory leaks
- TUI responsiveness maintained

---

## Git Commit Strategy

**Commit after each significant component:**
1. Each classifier/planner/executor component
2. Each phase integration into menu.py
3. Each test suite addition
4. Documentation updates

**Commit messages follow format:**
```
[Phase N] Component name: Brief description

Why this change, what it accomplishes, related tests

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

---

## Success Metrics

| Metric | Target | Verification |
|--------|--------|---------------|
| Classifier accuracy | >95% | Test suite |
| Permission compliance | 100% | Security audit |
| Test coverage | >85% | Coverage report |
| Classification latency | <10ms | Benchmarks |
| Permission check latency | <1ms | Benchmarks |
| File operation latency | <100ms | Benchmarks |
| Autonomous task reliability | >99% | 100+ task executions |
| Jailbreak success rate | 0% | Adversarial testing |
| Documentation | 100% complete | Review checklist |
| Existing test regression | 0 failures | CI/CD pipeline |

---

## Open Questions Requiring User Input

1. **Code execution approval:** Always require user approval, or configurable per character?
   - Current recommendation: Per-character setting in SKILLS.md with default=require_approval

2. **Heartbeat frequency:** 30 minutes, 60 minutes, or user-configurable?
   - Current recommendation: User-configurable with default=60min

3. **Task persistence:** Should pending tasks survive app restart?
   - Current recommendation: Yes, with recovery mechanism (retry with exponential backoff)

4. **File safety:** Per-character isolated directories or shared with whitelist?
   - Current recommendation: Per-character scoped directories in `character_data/{character_name}/tasks/`

5. **Execution limits:** Daily cap on autonomous tasks per character?
   - Current recommendation: Yes, with default limit=10 tasks/day

6. **Context window:** Maximum actions to include in agentic planning context?
   - Current recommendation: Last 5 completed actions + current task

---

## Timeline Summary

| Phase | Duration | Start | End | Key Deliverables |
|-------|----------|-------|-----|------------------|
| 1 | 2 weeks | Week 1 | Week 2 | Classifier, Planner, Executor, Permissions |
| 2 | 2 weeks | Week 3 | Week 4 | Code gen, App launch, System commands |
| 3 | 2 weeks | Week 5 | Week 6 | Heartbeat, Scheduler, Rollback |
| 4 | 2 weeks | Week 7 | Week 8 | Audit, Security, Performance, Docs |
| **Total** | **8 weeks** | Week 1 | Week 8 | Production-ready agentic system |

---

**Status:** Awaiting user feedback on open questions before Phase 1 implementation begins.

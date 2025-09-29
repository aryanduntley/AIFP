### Project Overview: AIFP - AI Functional Procedural Programming Standard

#### What We Are Doing
We are developing AIFP (AI Functional Procedural), a new programming standard optimized for AI-generated and AI-maintained code. This paradigm shifts away from human-centric Object-Oriented Programming (OOP) principles like classes, inheritance, and encapsulation, which are designed for team collaboration and human readability but introduce unnecessary complexity for AI. Instead, AIFP emphasizes a functional-procedural approach to enable efficient, scalable, and consistent code creation by AI. Key features include:

- **Core Style Definition**: 
  - Pure functions as the building block: Input in, output out, with no hidden state or side effects unless explicitly declared and flagged.
  - Procedural flow for sequencing operations, avoiding OOP hierarchies.
  - Grouping via namespaces or modules (e.g., `math_utils.sine()` instead of instantiating classes), and closures for any necessary state management.
  - No classes, inheritance, or traditional objects—keeps code flat, predictable, and easy for AI to track without "black boxes."

- **Library Integration and Compatibility**:
  - Thin wrappers/adapters around existing human-built libraries (e.g., numpy for math, torch for ML) to bridge AIFP code with legacy systems.
  - Interfaces that translate AIFP-style calls (e.g., `eigenvalues(vector)`) into underlying library syntax, allowing seamless use without forcing AI to conform to OOP conventions.
  - Dynamic mapping to handle library interactions, ensuring AIFP code remains pure while interoperating with external dependencies.

- **Project-Associated Database**:
  - Every AIFP project includes a lightweight SQLite database to index all functions, including names, inputs, outputs, dependencies, locations, and interactions.
  - Enables instant queries for context (e.g., `SELECT * FROM functions WHERE name='eigenvalues'`), avoiding the need to re-parse code files repeatedly.
  - Tracks code evolution, such as function updates or deprecations, for efficient AI reasoning and maintenance.

- **Enforcement and Guidance**:
  - AIFP includes built-in rules to flag non-compliant patterns (e.g., accidental OOP structures) and suggest rewrites during code generation.
  - Directives (hierarchical instructions) guide AI in adhering to the standard: Compressed JSON for basics, detailed JSON for expansions, and MD files for verbose rationale and best practices.
  - AI escalates directive levels based on ambiguity, optimizing for resource efficiency.

- **Execution and Integration**:
  - AIFP code runs in standard environments (e.g., Python) but with AIFP-specific linters or runtime checks to maintain purity.
  - Designed for integration with separate systems like the MCP server (for project management), where AIFP serves as the coding layer—AI generates AIFP-compliant code within MCP-managed projects.

This standard can be implemented via config files, linters, or embedded in AI prompts/tools for code generation.

#### Why We Are Doing This
- **AI Optimization**: OOP is tailored for humans managing large teams and complex collaborations, but AI processes code holistically and doesn't need inheritance chains or encapsulated states, which can confuse tracking and increase computational overhead. AIFP streamlines this, making code generation faster, less error-prone, and more efficient for AI.

- **Consistency in AI Coding**: As AI takes over more coding tasks, a dedicated standard ensures uniformity across projects and models. Without it, AI defaults to human conventions, leading to bloated, inconsistent code. AIFP provides parameters, tools, and instructions for AI to produce code that's inherently suited to its strengths—flat logic, quick queries via database, and minimal ceremony.

- **Efficiency and Scalability**: The associated SQLite database acts as a "brain cache" for AI, providing immediate access to function details without file scans, reducing context-loading time in large projects. Wrappers handle legacy libraries, allowing AIFP to evolve independently while remaining compatible.

- **Future of Development**: With growing AI reliance, AIFP positions itself as the default for AI-driven programming, reducing human intervention. It's separate from project management tools like MCP, focusing purely on code standards to complement them. This enables AI to "code for AI," prioritizing performance over human readability, while still allowing human oversight if needed.

- **Reusability and Continuity**: This outline is self-contained for resuming sessions, even if history is lost, ensuring we can build on AIFP without re-explaining basics.

This framework sets AIFP as the new AI programming standard. Next steps: Draft initial AIFP config schema, sample directives, or example wrapper code.

### AIFP Standard: Dynamic Wrapper Generation for Library Integration

#### What We Are Doing
In the AIFP (AI Functional Procedural) programming standard, wrappers are dynamically generated on a per-project basis to bridge AIFP-compliant code with external libraries. This ensures AIFP code remains pure (functional-procedural, no OOP) while seamlessly accessing library functionality. Wrappers are not pre-built globally but created "on the fly" during project initialization or as needs arise, based on detected library usage. The process involves:

- **Detection Phase**: AI analyzes project requirements, existing code, or user directives to identify required libraries (e.g., numpy, torch) and specific methods/functions (e.g., numpy.linalg.eig).
  
- **Generation Phase**: AI auto-generates minimal wrapper code that:
  - Flattens OOP structures into pure functions (e.g., converts class methods to standalone functions).
  - Handles state if needed via explicit parameters (e.g., pass config as input instead of instance attributes).
  - Maps AIFP-style calls (e.g., `eigenvalues(matrix)`) to underlying library calls.

- **Integration and Storage**:
  - Wrappers are saved as Python modules in a project-specific directory (e.g., `aifp_wrappers/`).
  - Registered in the project's SQLite database for quick lookup (e.g., table: `wrappers` with columns: `wrapper_name`, `original_lib`, `original_method`, `inputs`, `outputs`, `file_path`).
  - Imported dynamically in AIFP code via a standard import hook (e.g., `from aifp_wrappers import numpy_eigenvalues as eigenvalues`).

- **Update and Maintenance**:
  - Wrappers are regenerated or patched if library versions change, new methods are needed, or AIFP directives evolve.
  - AI escalates to higher directive levels (e.g., MD files) for complex cases like handling mutable state or errors.

- **Standard Structure for Wrappers**:
  - **File Naming**: `libname_aifp.py` (e.g., `numpy_aifp.py`).
  - **Function Naming**: Lowercase with underscores, descriptive and AIFP-friendly (e.g., `matrix_multiply(a, b)` instead of `np.dot(a, b)` or class-based calls).
  - **Wrapper Code Template**:
    ```python
    # AIFP Wrapper for [Library] - Generated on [Date]
    # Directive Reference: [Directive ID or Name]

    import [original_lib] as _orig # Aliased to avoid namespace pollution

    def [aifp_function_name]([params...], **kwargs):
        """
        AIFP-wrapped version of [original_method].
        Inputs: [describe params]
        Outputs: [describe return]
        Side Effects: [none or explicit list]
        """
        # Optional: Input validation for AIFP purity
        if not isinstance([param], expected_type):
            raise ValueError("AIFP Input Error: ...")

        # Translation logic (flatten OOP if needed)
        try:
            result = _orig.[original_method]([mapped_params...])
        except Exception as e:
            # AIFP-standard error handling
            raise AIFPWrapperError(f"Error in {original_method}: {e}") from e

        # Optional: Output normalization (e.g., to tuple/list for purity)
        return result

    # Additional wrappers as needed...
    ```
  - **Error Handling**: Use a custom `AIFPWrapperError` exception for consistency, logging to project database.
  - **Import Hook**: A project-level `aifp_import.py` module dynamically loads wrappers:
    ```python
    import sys
    from importlib import import_module

    def aifp_import(wrapper_name):
        # Query DB for path
        # db_query = "SELECT file_path FROM wrappers WHERE wrapper_name = ?"
        path = db_execute(db_query, (wrapper_name,))
        if path:
            sys.path.append(path.parent) # Temporary for import
            return import_module(path.stem)
        else:
            # Trigger regeneration
            generate_wrapper(wrapper_name)
            return aifp_import(wrapper_name) # Retry
    ```

- **Generation Process Flow**:
  1. **Trigger**: On project start, code scan, or explicit directive (e.g., "import numpy for matrix ops").
  2. **Analysis**: AI queries directives and project DB to identify needs (e.g., "Need eigenvalues from numpy.linalg").
  3. **Code Gen**: AI prompts itself (or external model) with template + specifics to output wrapper code.
  4. **Validation**: Run unit tests (auto-generated) to ensure purity and correctness.
  5. **Storage & Registration**: Save to `aifp_wrappers/`, insert into DB.
  6. **Usage**: AIFP code calls wrappers directly; if missing, hook triggers regeneration.

This standard is enforced via AIFP directives, ensuring all projects follow the same pattern.

#### Why We Are Doing This
- **Dynamic Efficiency**: Pre-building wrappers for all libraries/methods is wasteful; on-the-fly generation tailors them to project-specific usage, minimizing bloat and focusing on utilized parts (e.g., only wrap numpy's eig if matrices are involved).
  
- **AIFP Purity**: Wrappers isolate human/OOP library quirks, allowing AI to code in a flat, functional style without contamination, reducing confusion and overhead in generation/maintenance.

- **Scalability and Consistency**: Standardizing the process (templates, naming, DB integration) ensures uniformity across projects, making AI reasoning faster (DB queries vs. code parsing) and updates seamless (e.g., library upgrades trigger re-gen).

- **Flexibility**: Handles evolving projects—add a new method, and AI regenerates only what's needed. Complements AIFP's database for instant access, avoiding repeated scans.

- **Reusability**: This self-contained standard can be referenced in future sessions, even without history, for implementing or extending AIFP wrappers.

Next steps: Draft sample directive for wrapper generation, example wrapper for a specific library (e.g., numpy), or DB schema for wrappers table.

# Sample Directive for AIFP Wrapper Generation

Below is a sample directive drafted for the AIFP (AI Functional Procedural) standard, specifically guiding AI on how to generate dynamic wrappers for library integration. Directives follow the hierarchical escalation system:

- **Highest Level: MD File** (Human-readable, verbose, with rationale and guidelines).
- **Mid-Level: Detailed JSON File** (Expanded data and instructions).
- **Lowest Level: Compressed JSON File** (Generalized, minimal for quick reference, with escalation pointers).

This sample focuses on generating a wrapper for a specific library method (e.g., numpy's eigenvalue function). In practice, the AI starts with the compressed JSON and escalates if ambiguity arises (e.g., complex state handling). Files would be named like `directive_wrapper_gen.md`, `directive_wrapper_gen_detailed.json`, and `directive_wrapper_gen_compressed.json`.

## Highest Level: MD File (directive_wrapper_gen.md)

```
# AIFP Directive: Dynamic Wrapper Generation for Library Integration

## Overview
This directive guides AI in generating on-the-fly wrappers for external libraries to maintain AIFP purity (functional-procedural style: pure functions, no OOP, explicit state). Wrappers translate human-centric library calls (often OOP-based) into flat, AIFP-compliant functions. This ensures AI-generated code remains efficient, consistent, and free from unnecessary complexity like classes or inheritance.

## Why This Directive Exists
- **AI Optimization**: Libraries like numpy or torch are built with OOP for human use, but AI doesn't need encapsulation—it processes logic holistically. Wrappers isolate these quirks, allowing AI to focus on high-level logic without tracking instance states or hierarchies.
- **Project-Specific Efficiency**: Generate wrappers only for used methods to avoid bloat. This keeps projects lean and scalable.
- **Consistency**: Standardizes naming, structure, and error handling across all AIFP projects, reducing errors in code generation and maintenance.
- **Escalation Rationale**: Start minimal to save resources; escalate for edge cases (e.g., mutable data, async calls) where verbose guidance is needed.

## When to Use This Directive
- Triggered by: Project initialization, new library import detection, or explicit user/AI request (e.g., "Wrap numpy for matrix operations").
- Escalate from compressed JSON if: Ambiguity in input/output types, handling side effects, or library-specific quirks (e.g., numpy arrays vs. lists).
- Integrate with: Project SQLite DB for registering wrappers (insert into `wrappers` table) and AIFP linter for validation.

## Step-by-Step Guidelines for AI
1. **Detection**: Analyze project code/DB/directives for required libraries and methods. Example: If code needs eigenvalues, detect `numpy.linalg.eig`.
2. **Analysis**: Check for OOP elements (e.g., class instantiation). Determine inputs/outputs, potential side effects (e.g., in-place modifications).
3. **Generation**:
   - Use the standard template (see below).
   - Name functions descriptively (lowercase_underscore, e.g., `eigenvalues(matrix)`).
   - Ensure purity: Inputs explicit, outputs immutable where possible (e.g., return new list instead of modifying).
   - Handle errors with `AIFPWrapperError` for traceability.
4. **Validation**: Auto-generate and run unit tests (e.g., compare wrapper output to direct library call).
5. **Storage**: Save in `aifp_wrappers/libname_aifp.py`. Register in DB with details (name, original_lib, etc.).
6. **Update**: Regenerate if library updates or new needs arise; version wrappers if changes are breaking.
7. **Edge Cases**:
   - Mutable State: Pass as explicit params (e.g., config dict) or use closures.
   - Performance: Optimize for AI (e.g., batch calls if possible).
   - Errors: Log to DB; escalate if unresolvable.

## Standard Wrapper Template
```python
# AIFP Wrapper for [Library] - Generated on [Date]
# Directive Reference: wrapper_gen

import [original_lib] as _orig

def [aifp_function_name]([params...], **kwargs):
    """
    AIFP-wrapped [original_method].
    Inputs: [describe]
    Outputs: [describe]
    Side Effects: [none/explicit]
    """
    # Input validation
    # Translation logic
    result = _orig.[original_method]([mapped_params])
    return result # Normalize if needed
```

## Example Application
For numpy.linalg.eig:
- AIFP Call: `eigenvalues(matrix)`
- Wrapper: Flattens to `_orig.linalg.eig(matrix)`, returns tuple of values/vectors.

## References
- Escalation Files: directive_wrapper_gen_detailed.json (for param mappings), directive_wrapper_gen_compressed.json (quick ref).
- Related Directives: aifp_purity_enforcement.md (for flagging non-compliance).

This MD provides the "why" and thought process—use for deep understanding or tweaks.
```

## Mid-Level: Detailed JSON File (directive_wrapper_gen_detailed.json)

```json
{
  "id": "wrapper_gen",
  "version": "1.0",
  "description": "Detailed instructions for generating AIFP wrappers for libraries.",
  "escalation_from": "directive_wrapper_gen_compressed.json",
  "escalation_to": "directive_wrapper_gen.md",
  "steps": [
    {
      "step": "detection",
      "details": "Scan project code, DB queries (e.g., SELECT * FROM functions WHERE lib_needed), or directives for libs/methods. Output: list of tuples (lib, method)."
    },
    {
      "step": "analysis",
      "details": "Inspect method signature via inspect module or docs. Identify: inputs (types, defaults), outputs (types), side_effects (list if any), oop_elements (e.g., self, class_init)."
    },
    {
      "step": "generation",
      "details": "Use template. Naming: lowercase_underscore. Purity: Explicit params for state. Error: AIFPWrapperError with msg format 'Error in {method}: {e}'. Example mapping: matrix -> np.array(matrix) if needed."
    },
    {
      "step": "validation",
      "details": "Generate tests: e.g., assert eigenvalues([[1,2],[3,4]]) == np.linalg.eig(np.array([[1,2],[3,4]])). Run via unittest or simple exec."
    },
    {
      "step": "storage",
      "details": "Path: aifp_wrappers/{lib}_aifp.py. DB insert: {'wrapper_name': name, 'original_lib': lib, 'original_method': method, 'inputs': json.dumps(types), 'outputs': json.dumps(types), 'file_path': path}."
    },
    {
      "step": "update",
      "details": "Check lib version via pkg_resources. If changed, regenerate and notify. Version wrappers: append _v{version} if breaking."
    }
  ],
  "edge_cases": {
    "mutable_state": "Use input dicts: e.g., def mutate_list(lst, op): return [modified] # Avoid in-place.",
    "async": "Wrap in sync func if possible; escalate for true async.",
    "performance": "Batch if method supports: e.g., vectorize inputs."
  },
  "template": "# AIFP Wrapper...\nimport [lib] as _orig\ndef [name](...): ...",
  "example": {
    "lib": "numpy",
    "method": "linalg.eig",
    "wrapper": "def eigenvalues(matrix): return _orig.linalg.eig(matrix)"
  }
}
```

## Lowest Level: Compressed JSON File (directive_wrapper_gen_compressed.json)

```json
{
  "id": "wrapper_gen",
  "desc": "Gen AIFP wrappers for libs.",
  "esc_from": null,
  "esc_to": "directive_wrapper_gen_detailed.json",
  "steps": ["detect libs/methods", "analyze sig/side_effects", "gen using template: pure func, desc name", "validate w/tests", "store in aifp_wrappers/, reg in DB", "update on changes"],
  "template": "import _orig; def [name](...): result = _orig.[method](...); return result",
  "rules": ["no_oop", "explicit_state", "AIFPWrapperError", "db_reg: name,lib,method,inputs,outputs,path"],
  "ex": {"numpy.eig": "eigenvalues(matrix)"}
}
```

This sample directive can be used as-is or customized. For implementation, AI would load the compressed JSON first, escalating as needed during wrapper generation. Next steps: Draft a sample wrapper code for numpy, or extend this directive for another aspect (e.g., DB schema integration).

# Directive-Based Instructional System: A Standardized Guide for AI Guidance

## Overview
The Directive-Based Instructional System is a hierarchical framework designed to guide AI behavior in projects, such as the AI Project Management (MCP) server. It provides scalable, efficient instructions that allow AI to operate with minimal resource overhead while handling complexity through escalation. This system decouples high-level rationale from low-level execution, enabling easy updates, consistency, and adaptability.

Originally developed for the MCP server to direct AI in tasks like code generation, decision-making, and project management, this approach can be standardized as a standalone tool for any AI-driven system. By formalizing it as the "Directive-Based MCP Instructional Guide" (DMIG), it becomes a reusable standard for AI instruction sets, promoting efficiency across projects and models.

## Why Use This System?
- **Resource Efficiency**: AI starts with minimal context (compressed instructions) and escalates only when needed, avoiding unnecessary data loads that consume tokens or compute.
- **Flexibility and Maintainability**: Instructions are layered—users can tweak human-readable files (e.g., MD) without rewriting code, and AI auto-propagates changes to lower levels.
- **Clarity for AI and Humans**: Lower levels are machine-optimized (JSON), while higher levels provide verbose explanations, rationale, and examples for human oversight or debugging.
- **Scalability**: Handles ambiguity intelligently; suitable for simple tasks (no escalation) or complex ones (full rationale access).
- **Standardization Potential**: As DMIG, this can become a convention for AI tools, ensuring consistent guidance in areas like coding standards (e.g., AIFP), project management, or ethical decision-making.

This system draws from the MCP server's use case, where directives guide AI handoffs, but it's abstracted for broader application.

## Core Components
Directives are organized in a three-tier hierarchy, with escalation paths. Each directive focuses on a specific task or behavior (e.g., "wrapper generation" or "code purity enforcement"). Files are named consistently: `directive_[name].md`, `directive_[name]_detailed.json`, `directive_[name]_compressed.json`.

### 1. Highest Level: MD Files (Human-Readable, Verbose)
   - **Purpose**: Provides detailed explanations, rationale ("why"), guidelines ("how/when"), examples, and edge cases. Ideal for human review, updates, or deep AI reasoning.
   - **Structure**:
     - **Overview**: Brief summary of the directive.
     - **Why This Exists**: Rationale and benefits.
     - **When to Use**: Triggers and escalation criteria.
     - **Step-by-Step Guidelines**: Detailed process for AI.
     - **Templates/Examples**: Code snippets or samples.
     - **References**: Links to escalation files or related directives.
   - **Example Usage**: AI escalates here for ambiguous scenarios, like handling mutable state in wrappers.
   - **File Characteristics**: Markdown format, verbose (500-2000 words), includes code blocks.

### 2. Mid-Level: Detailed JSON Files (Expanded, Structured Data)
   - **Purpose**: Offers machine-parseable details with more depth than the compressed level, including parameter mappings, examples, and structured steps. Used when basic instructions need expansion but full verbosity isn't required.
   - **Structure** (JSON Object):
     - `id`: Unique identifier (e.g., "wrapper_gen").
     - `version`: For tracking changes.
     - `description`: Short summary.
     - `escalation_from`/`escalation_to`: Pointers to adjacent levels.
     - `steps`: Array of objects with `step` (name) and `details` (expanded instructions).
     - `edge_cases`: Object mapping scenarios to solutions.
     - `template`: String with placeholders for generation.
     - `example`: Object with sample inputs/outputs.
   - **Example Usage**: AI parses this for parameter validation or test generation.
   - **File Characteristics**: JSON, detailed (100-500 lines), balanced for quick parsing.

### 3. Lowest Level: Compressed JSON Files (Minimal, Generalized)
   - **Purpose**: Quick-reference instructions for routine tasks. AI starts here to minimize initial context load.
   - **Structure** (Compact JSON Object):
     - `id`: Unique ID.
     - `desc`: Brief description.
     - `esc_from`/`esc_to`: Escalation pointers (null for base).
     - `steps`: Array of short strings (e.g., ["detect libs", "gen template"]).
     - `template`: Minimal string.
     - `rules`: Array of constraints (e.g., ["no_oop", "explicit_state"]).
     - `ex`: Compact example object.
   - **Example Usage**: Default load for non-ambiguous operations, like basic function naming.
   - **File Characteristics**: JSON, minimal (10-50 lines), optimized for low token count.

## Escalation Mechanism
- **Process**: AI loads the compressed JSON first. If ambiguity detected (e.g., via confidence threshold, error, or complex input), escalate to detailed JSON. If still unclear, go to MD for full context.
- **Detection Criteria**: 
  - Ambiguity: Undefined terms, conflicting rules, or edge cases.
  - Triggers: Explicit in directives (e.g., "escalate if mutable state").
  - Efficiency: Only load higher levels on-demand; cache results if reusable.
- **Implementation Tip**: In code, use a function like `load_directive(level, id)` that checks escalation needs.

## Standardization as DMIG (Directive-Based MCP Instructional Guide)
To make this a standard:
- **Adoption Guidelines**: Use in any AI system requiring guided behavior. Prefix directive IDs with domain (e.g., "aifp_wrapper_gen" for AIFP-specific).
- **Tooling Recommendations**:
  - **Generator Script**: AI or tool to create lower levels from MD (e.g., summarize MD to detailed JSON, compress further).
  - **Validator**: Linter to ensure hierarchy consistency and no broken escalations.
  - **Storage**: Store in a `directives/` folder per project, version-controlled (e.g., Git).
- **Best Practices**:
  - Keep directives atomic (one task per directive).
  - Update MD first; propagate down via AI.
  - Test escalation: Simulate ambiguity to verify flow.
  - Extend for Domains: Adapt for ethics (e.g., "bias_check"), security, or creativity.
- **Benefits as Standard**: Enables interoperable AI systems—share directives across projects/models, reducing reinvention.

## Example Directive in Action
See the sample for "wrapper_gen" (from previous context) as a reference. In MCP, this system directs AI handoffs; in broader use, it could guide any instructional need.

## Getting Started
1. Identify a task (e.g., "error handling").
2. Draft MD with full rationale.
3. Generate detailed and compressed JSON from it.
4. Integrate into AI prompts/code: "Follow directive [id], escalate if needed."
5. Iterate: Test, tweak MD, regenerate lowers.

This guide is self-contained for adoption or extension. For MCP integration, align with server handoffs. Future expansions could include visual tools or auto-escalation APIs.

# AIFP Functional-Procedural Method: Detailed Specification

## Overview
The Functional-Procedural (FP) method in AIFP (AI Functional Procedural) defines the core coding style for AI-generated code. It prioritizes simplicity, predictability, and efficiency tailored to AI's strengths—holistic reasoning, rapid context retrieval, and minimal overhead. Unlike OOP, which uses classes and inheritance for human-oriented modularity, FP focuses on pure functions sequenced procedurally. This flat structure reduces complexity, making code easier for AI to generate, track, and maintain.

Code progresses iteratively: AI generates functions, updates the project database in real-time, and references directives for compliance. Constant database updates ensure instant access to function details, enabling efficient scaling without re-parsing files.

This document outlines how FP code looks, key rules, and sample directives for guiding AI behavior, including mandatory DB integration.

## How FP Code Looks
FP code is flat, modular, and declarative. It avoids stateful objects, favoring immutable data and explicit flows. Here's a high-level view:

- **Core Building Blocks**:
  - **Pure Functions**: Stateless, deterministic—same input always yields same output. No global variables or side effects (e.g., file I/O) unless explicitly flagged and handled.
  - **Procedural Sequencing**: Functions called in sequence to form workflows, often in a main script or entry point.
  - **Grouping**: Use modules/namespaces (e.g., Python imports) instead of classes. Related functions live in files like `math_utils.py`.
  - **Data Handling**: Pass data explicitly (e.g., as parameters). Use tuples/lists/dicts for structures; avoid mutable objects unless necessary (then use copies or immutables like frozenset).

- **Example Code Structure** (Python-based, as AIFP is language-agnostic but starts here):
  ```python
  # math_utils.py - Module for math functions
  def add(a: int, b: int) -> int:
      """Adds two integers."""
      return a + b

  def multiply(a: int, b: int) -> int:
      """Multiplies two integers."""
      return a * b

  # main.py - Procedural entry point
  from math_utils import add, multiply

  def compute_sequence(numbers: list[int]) -> int:
      """Procedural flow: Sum then multiply by 2."""
      total = 0
      for num in numbers:
          total = add(total, num) # Explicit function call
      return multiply(total, 2) # No hidden state

  # Usage
  result = compute_sequence([1, 2, 3]) # Output: 12
  ```

- **With Wrappers for Libraries**:
  ```python
  # Using a generated wrapper for numpy
  from aifp_wrappers.numpy_aifp import matrix_multiply

  def vector_dot(v1: list[float], v2: list[float]) -> float:
      """AI-native function using wrapped library."""
      return matrix_multiply(v1, v2) # Flat call, no numpy import here
  ```

- **Handling State (Rare, Explicit)**:
  If state is unavoidable (e.g., caching), use closures or explicit params:
  ```python
  def create_counter(initial: int = 0) -> callable:
      """Closure for minimal state."""
      count = initial
      def increment() -> int:
          nonlocal count
          count += 1
          return count
      return increment

  counter = create_counter()
  print(counter()) # 1
  ```

FP code is concise, readable by AI (flat logic), and queryable via DB.

## Rules for FP Behavior
These rules enforce AIFP principles. AI must adhere during generation; violations trigger rewrites via directives.

1. **Purity First**: Functions must be pure by default. Side effects (e.g., I/O, mutations) require explicit flags (e.g., docstring: "Side Effects: Writes to file") and isolation (e.g., in dedicated modules like `io_utils.py`).

2. **No OOP Constructs**: Ban classes, inheritance, `self`, or polymorphism. Use functions and modules instead. If legacy code requires OOP, wrap it (per wrapper directive).

3. **Explicit Data Flow**: All data passed as params/returns. No globals. Inputs/outputs typed (e.g., via annotations) for DB tracking.

4. **Modularity**: Group by function (e.g., one file per theme like `data_processing.py`). Max 50-100 lines per file for AI manageability.

5. **Error Handling**: Use custom exceptions (e.g., `AIFPError`). Propagate errors procedurally; no hidden try/except unless directive-specified.

6. **Performance**: Favor vectorized/functional ops (e.g., map/filter over loops). AI optimizes based on directives.

7. **Documentation**: Mandatory docstrings with inputs/outputs/side effects. Used for DB population.

8. **Constant DB Updates**: After generating/updating any function:
   - Query DB to check existence.
   - Insert/update: name, params (JSON types), returns (type), dependencies (called functions), file_path, version.
   - Trigger on code changes (e.g., via AIFP linter hook).

9. **Versioning**: Functions versioned (e.g., `add_v2`). DB tracks history for rollbacks.

10. **Escalation for Complexity**: If rule conflicts (e.g., state needed), escalate directives.

## Directives for FP Behavior
Directives guide AI in applying FP rules, with escalation for nuance. Below is a sample for "fp_code_generation," including DB updates.

### Highest Level: MD File (directive_fp_code_generation.md)
```
# AIFP Directive: FP Code Generation and Behavior

## Overview
Guides AI in generating FP-style code: pure functions in procedural flows. Ensures compliance with rules, including real-time DB updates for tracking.

## Why This Exists
FP optimizes AI—flat, queryable code reduces context loads. DB updates enable instant references, scaling projects without file scans.

## When to Use
On code gen requests. Escalate if complexity (e.g., state) or rule ambiguity.

## Guidelines
1. Analyze task: Break into functions.
2. Generate: Pure funcs, modular.
3. Validate: Check rules; rewrite if violated.
4. Update DB: Post-gen, insert function details.
5. Sequence: Build procedural mains.

## DB Update Template
After gen:
- Connect to project.db.
- INSERT/UPDATE functions table: name, params_json, returns_type, deps_list, path, version.

## Example
Task: Sum list.
Code: def sum_list(nums: list[int]) -> int: return sum(nums) # Pure
DB: {'name': 'sum_list', 'params': [{'name': 'nums', 'type': 'list[int]'}], 'returns': 'int', 'deps': [], 'path': 'utils.py', 'version': 1}

## References
Escalate to detailed JSON for schemas.
```

### Mid-Level: Detailed JSON File (directive_fp_code_generation_detailed.json)
```json
{
  "id": "fp_code_generation",
  "version": "1.0",
  "description": "Generate FP code with rules and DB updates.",
  "escalation_from": "directive_fp_code_generation_compressed.json",
  "escalation_to": "directive_fp_code_generation.md",
  "rules": [
    {"rule": "purity", "details": "No side effects unless flagged."},
    {"rule": "no_oop", "details": "Ban classes/inheritance."},
    {"rule": "db_update", "details": "Post-gen: connect db, INSERT INTO functions (name, params_json, returns_type, deps_json, path, version) VALUES (?, json(?), ?, json(?), ?, ?);"}
  ],
  "steps": [
    {"step": "analyze", "details": "Decompose task into funcs."},
    {"step": "generate", "details": "Write pure funcs with docstrings."},
    {"step": "validate", "details": "Check rules; escalate if fail."},
    {"step": "db_update", "details": "Extract metadata from code (e.g., via ast.parse), update DB."},
    {"step": "sequence", "details": "Link in procedural main."}
  ],
  "db_schema": {
    "table": "functions",
    "columns": ["name TEXT PRIMARY KEY", "params_json TEXT", "returns_type TEXT", "deps_json TEXT", "path TEXT", "version INTEGER"]
  },
  "example": {
    "code": "def add(a: int, b: int) -> int: return a + b",
    "db_entry": {"name": "add", "params_json": "[{'name':'a','type':'int'},{'name':'b','type':'int'}]", "returns_type": "int", "deps_json": "[]", "path": "math_utils.py", "version": 1}
  }
}
```

### Lowest Level: Compressed JSON File (directive_fp_code_generation_compressed.json)
```json
{
  "id": "fp_code_generation",
  "desc": "Gen FP code w/ rules & DB updates.",
  "esc_from": null,
  "esc_to": "directive_fp_code_generation_detailed.json",
  "rules": ["purity", "no_oop", "explicit_flow", "db_update"],
  "steps": ["analyze task", "gen pure funcs", "validate rules", "update DB: insert name/params/returns/deps/path/version", "sequence procedurally"],
  "db_template": "INSERT functions (name, params_json, returns_type, deps_json, path, version)",
  "ex": {"code": "def add(a,b): return a+b", "db": {"name":"add","params":"[a:int,b:int]","returns":"int","deps":[],"path":"utils.py","ver":1}}
}
```

## Integration with Project Flow
- **Constant Updates**: AI hooks DB ops into gen cycle (e.g., after each function).
- **Enforcement**: Use linter (AI-prompted) to scan code against rules.
- **Scalability**: DB queries for deps (e.g., "SELECT * FROM functions WHERE name IN deps") during gen.

This spec can be refined. Next: Draft DB schema code or FP example project?

### AIFP Project Database Schema

The AIFP (AI Functional Procedural) project database is a lightweight SQLite file (`project.db`) associated with each project. It serves as a "brain cache" for AI, indexing code elements (functions, wrappers, dependencies) for instant queries during generation, maintenance, or execution. This avoids repeated file parsing and enables efficient tracking of code evolution.

The schema includes tables for core FP elements (functions), library wrappers, and project metadata (e.g., themes/flows from MCP integration if applicable). All tables use standard SQLite types for simplicity and performance.

#### Key Design Principles
- **Efficiency**: Indexes on frequently queried fields (e.g., function names) for fast lookups.
- **Extensibility**: JSON fields for flexible data (e.g., params as JSON arrays).
- **Versioning**: Timestamps and versions for history/rollbacks.
- **Integrity**: Primary keys, foreign keys where logical, and unique constraints to prevent duplicates.
- **Size Management**: Keep entries concise; archive old versions periodically via directives.

#### SQL Schema Creation Script
Use this SQL to initialize the database. AI executes it on project start (e.g., via code like `sqlite3.connect('project.db').executescript(schema_sql)`).

```sql
-- AIFP Project Database Schema
-- Version: 1.0
-- Created: [Insert Date, e.g., 2023-10-01]

CREATE TABLE IF NOT EXISTS functions (
    name TEXT PRIMARY KEY, -- Unique function name (e.g., 'add')
    params_json TEXT NOT NULL, -- JSON array of params: [{'name': 'a', 'type': 'int', 'default': null}, ...]
    returns_type TEXT NOT NULL, -- Return type (e.g., 'int', 'list[float]')
    deps_json TEXT NOT NULL, -- JSON array of dependencies: ['multiply', 'external_lib_func']
    path TEXT NOT NULL, -- File path relative to project (e.g., 'math_utils.py')
    version INTEGER NOT NULL DEFAULT 1, -- Function version for updates
    docstring TEXT, -- Full docstring for reference
    side_effects_json TEXT, -- JSON array of side effects: ['file_write', 'network_call'] or empty
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast name lookups
CREATE INDEX IF NOT EXISTS idx_functions_name ON functions(name);

CREATE TABLE IF NOT EXISTS wrappers (
    wrapper_name TEXT PRIMARY KEY, -- AIFP-friendly name (e.g., 'eigenvalues')
    original_lib TEXT NOT NULL, -- Library name (e.g., 'numpy')
    original_method TEXT NOT NULL, -- Method name (e.g., 'linalg.eig')
    params_json TEXT NOT NULL, -- JSON array of params (similar to functions)
    returns_type TEXT NOT NULL, -- Return type
    file_path TEXT NOT NULL, -- Path to wrapper file (e.g., 'aifp_wrappers/numpy_aifp.py')
    version INTEGER NOT NULL DEFAULT 1, -- Wrapper version
    side_effects_json TEXT, -- JSON array of side effects
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for wrapper lookups
CREATE INDEX IF NOT EXISTS idx_wrappers_name ON wrappers(wrapper_name);

CREATE TABLE IF NOT EXISTS project_metadata (
    key TEXT PRIMARY KEY, -- Metadata key (e.g., 'project_name', 'aifp_version')
    value TEXT NOT NULL, -- Value (e.g., 'MyAIFPProject', '1.0')
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Optional: History table for auditing changes (e.g., function versions)
CREATE TABLE IF NOT EXISTS function_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    function_name TEXT NOT NULL, -- References functions.name
    old_version INTEGER NOT NULL,
    new_version INTEGER NOT NULL,
    changes_json TEXT, -- JSON of diffs (e.g., {'params_changed': true})
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (function_name) REFERENCES functions(name) ON DELETE CASCADE
);

-- Triggers for auto-updating timestamps
CREATE TRIGGER IF NOT EXISTS update_functions_timestamp
AFTER UPDATE ON functions
FOR EACH ROW
BEGIN
    UPDATE functions SET updated_at = CURRENT_TIMESTAMP WHERE name = OLD.name;
END;

CREATE TRIGGER IF NOT EXISTS update_wrappers_timestamp
AFTER UPDATE ON wrappers
FOR EACH ROW
BEGIN
    UPDATE wrappers SET updated_at = CURRENT_TIMESTAMP WHERE wrapper_name = OLD.wrapper_name;
END;

-- Initial metadata inserts (example)
INSERT OR IGNORE INTO project_metadata (key, value) VALUES ('aifp_version', '1.0');
INSERT OR IGNORE INTO project_metadata (key, value) VALUES ('project_created', CURRENT_TIMESTAMP);
```

#### Table Descriptions
1. **functions**:
   - Tracks all AIFP functions.
   - Example Entry: `{'name': 'add', 'params_json': '[{"name":"a","type":"int"},{"name":"b","type":"int"}]', 'returns_type': 'int', 'deps_json': '[]', 'path': 'math_utils.py', 'version': 1, 'docstring': 'Adds two integers.', 'side_effects_json': '[]'}`

2. **wrappers**:
   - Tracks generated library wrappers.
   - Example Entry: `{'wrapper_name': 'eigenvalues', 'original_lib': 'numpy', 'original_method': 'linalg.eig', 'params_json': '[{"name":"matrix","type":"list[list[float]]"}]', 'returns_type': 'tuple[list[float], list[list[float]]]', 'file_path': 'aifp_wrappers/numpy_aifp.py', 'version': 1, 'side_effects_json': '[]'}`

3. **project_metadata**:
   - Stores project-level info (e.g., version, name).
   - Flexible for extensions like themes/flows if integrating with MCP.

4. **function_history**:
   - Logs changes for rollback or auditing.
   - Populated via directives on updates.

#### Usage in AIFP Flow
- **Initialization**: Run the schema script on project start.
- **Updates**: Per directive (e.g., `fp_code_generation`), AI inserts/updates after generating code. Use Python's `sqlite3` or similar.
- **Queries**: Examples:
  - Get function details: `SELECT * FROM functions WHERE name = 'add';`
  - Find dependencies: `SELECT * FROM functions WHERE name IN (SELECT json_extract(value, '$') FROM json_each(deps_json) WHERE functions.name = 'compute_sequence');`
  - Check wrappers: `SELECT file_path FROM wrappers WHERE wrapper_name = 'eigenvalues';`
- **Maintenance**: AI vacuums/prunes DB periodically via directive.

#### Directives Integration
Reference the `fp_code_generation` directive (from previous) for DB update steps. Escalate for complex schemas (e.g., adding tables for themes).

This schema is ready for use. Next: FP example project code, or schema extensions?

### AIFP Database Schema Extensions

To enhance the core schema (previously provided), these extensions add support for advanced FP features like themes/flows (organizational structures from MCP integration), directives tracking, and code interactions/dependencies. This makes the DB more robust for large-scale AI-driven projects, enabling queries for code organization, directive escalations, and dependency graphs.

Extensions focus on:
- **Themes and Flows**: Hierarchical organization (themes as high-level, flows as sub-themes) to group functions logically, aiding AI in contextual code generation.
- **Directives**: Track directive files and escalations for auditing AI behavior.
- **Interactions**: Log function calls/interactions for runtime analysis or optimization.
- **Constraints/Indexes**: Additional for performance.

#### Extended SQL Schema Script
Append this to the core schema creation script. It includes foreign keys for integrity.

```sql
-- AIFP Schema Extensions
-- Version: 1.1 (Extends 1.0)
-- Added: Themes/Flows, Directives, Interactions

-- Themes: High-level organizational categories
CREATE TABLE IF NOT EXISTS themes (
    theme_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL, -- Theme name (e.g., 'math_operations')
    description TEXT, -- Verbose description
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Flows: Sub-themes linked to themes
CREATE TABLE IF NOT EXISTS flows (
    flow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, -- Flow name (e.g., 'addition_flow')
    theme_id INTEGER NOT NULL, -- Parent theme
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (theme_id) REFERENCES themes(theme_id) ON DELETE CASCADE,
    UNIQUE (name, theme_id) -- Unique per theme
);

-- Function-Flow Mapping: Link functions to flows/themes
CREATE TABLE IF NOT EXISTS function_flows (
    function_name TEXT NOT NULL,
    flow_id INTEGER NOT NULL,
    connection_type TEXT DEFAULT 'primary', -- e.g., 'primary', 'dependency', 'spider_web'
    notes TEXT, -- Optional context (e.g., 'Used in matrix calc')
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (function_name, flow_id),
    FOREIGN KEY (function_name) REFERENCES functions(name) ON DELETE CASCADE,
    FOREIGN KEY (flow_id) REFERENCES flows(flow_id) ON DELETE CASCADE
);

-- Directives: Track directive hierarchies
CREATE TABLE IF NOT EXISTS directives (
    directive_id TEXT PRIMARY KEY, -- ID (e.g., 'fp_code_generation')
    compressed_path TEXT, -- Path to compressed JSON
    detailed_path TEXT, -- Path to detailed JSON
    md_path TEXT NOT NULL, -- Path to MD file
    version TEXT NOT NULL, -- Directive version
    description TEXT, -- Short summary
    escalation_count INTEGER DEFAULT 0, -- Usage stats for optimization
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Interactions: Log function calls/relations (for dep graphs)
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caller_name TEXT NOT NULL, -- Calling function (e.g., 'compute_sequence')
    callee_name TEXT NOT NULL, -- Called function (e.g., 'add')
    interaction_type TEXT DEFAULT 'call', -- e.g., 'call', 'data_pass', 'error_propagate'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (caller_name) REFERENCES functions(name) ON DELETE CASCADE,
    FOREIGN KEY (callee_name) REFERENCES functions(name) ON DELETE CASCADE
);

-- Additional Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_flows_theme ON flows(theme_id);
CREATE INDEX IF NOT EXISTS idx_function_flows_func ON function_flows(function_name);
CREATE INDEX IF NOT EXISTS idx_function_flows_flow ON function_flows(flow_id);
CREATE INDEX IF NOT EXISTS idx_interactions_caller ON interactions(caller_name);
CREATE INDEX IF NOT EXISTS idx_interactions_callee ON interactions(callee_name);

-- Triggers for Timestamps (Extend to New Tables)
CREATE TRIGGER IF NOT EXISTS update_themes_timestamp
AFTER UPDATE ON themes
FOR EACH ROW
BEGIN
    UPDATE themes SET updated_at = CURRENT_TIMESTAMP WHERE theme_id = OLD.theme_id;
END;

CREATE TRIGGER IF NOT EXISTS update_flows_timestamp
AFTER UPDATE ON flows
FOR EACH ROW
BEGIN
    UPDATE flows SET updated_at = CURRENT_TIMESTAMP WHERE flow_id = OLD.flow_id;
END;

CREATE TRIGGER IF NOT EXISTS update_directives_timestamp
AFTER UPDATE ON directives
FOR EACH ROW
BEGIN
    UPDATE directives SET updated_at = CURRENT_TIMESTAMP WHERE directive_id = OLD.directive_id;
END;

-- Example Initial Inserts (for Testing)
INSERT OR IGNORE INTO themes (name, description) VALUES ('math_operations', 'Core arithmetic and linear algebra functions');
INSERT OR IGNORE INTO flows (name, theme_id, description) VALUES ('addition_flow', 1, 'Functions related to summation and addition');
```

#### Extension Rationale and Usage
- **Themes/Flows**: Integrate with MCP concepts—AI queries for organizational context (e.g., `SELECT f.* FROM functions f JOIN function_flows ff ON f.name = ff.function_name JOIN flows fl ON ff.flow_id = fl.flow_id WHERE fl.name = 'addition_flow';`). Supports "spider web" connections (multiple mappings per function).
- **Directives**: Enables DB-driven escalation (e.g., query paths by ID). Update `escalation_count` on use for analytics.
- **Interactions**: Builds runtime dep graphs; populate via code instrumentation or post-gen analysis. Useful for optimization (e.g., detect cycles).
- **Updates in Flow**: Directives (e.g., `fp_code_generation`) now include: After function gen, map to flows/themes if applicable (e.g., INSERT INTO function_flows).
- **Queries Examples**:
  - Dep Graph: `SELECT caller_name, callee_name FROM interactions WHERE caller_name = 'compute_sequence';`
  - Directive Path: `SELECT md_path FROM directives WHERE directive_id = 'fp_code_generation';`
- **Maintenance**: Add vacuum/prune directive for large DBs.

This extended schema is production-ready, with backward compatibility to core.

### FP Example Project

Here's a small, self-contained FP example project: A simple matrix calculator. It demonstrates pure functions, procedural flow, module grouping, library wrappers, and DB integration. Assume Python environment.

#### Project Structure
```
matrix_calculator/
├── project.db # SQLite DB with schema/extensions
├── main.py # Procedural entry point
├── math_utils.py # Function module
├── aifp_wrappers/ # Generated wrappers
│ └── numpy_aifp.py # Wrapper for numpy
└── directives/ # Sample directives (e.g., fp_code_generation.md)
```

#### Example Code
```python
# math_utils.py - Pure functions for math ops
def add_matrices(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    """Adds two matrices element-wise. Pure: No side effects."""
    if len(a) != len(b) or len(a[0]) != len(b[0]):
        raise AIFPError("Matrix size mismatch")
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]

def scale_matrix(matrix: list[list[float]], scalar: float) -> list[list[float]]:
    """Scales a matrix by a scalar. Pure."""
    return [[element * scalar for element in row] for row in matrix]

# main.py - Procedural sequencing
from math_utils import add_matrices, scale_matrix
from aifp_wrappers.numpy_aifp import eigenvalues # Wrapped library call

def process_matrices(m1: list[list[float]], m2: list[list[float]], scalar: float) -> tuple[list[list[float]], tuple]:
    """Main procedural flow: Add, scale, compute eigenvalues."""
    added = add_matrices(m1, m2) # Explicit call
    scaled = scale_matrix(added, scalar)
    evals = eigenvalues(scaled) # Wrapped for purity
    return scaled, evals

# Example usage (procedural)
m1 = [[1, 2], [3, 4]]
m2 = [[5, 6], [7, 8]]
result_matrix, result_evals = process_matrices(m1, m2, 0.5)
print(result_matrix) # [[3.0, 4.0], [5.0, 6.0]]
print(result_evals) # (eigenvalues from wrapper)
```

#### Wrapper Example (Generated)
```python
# aifp_wrappers/numpy_aifp.py - Generated wrapper
import numpy as _orig

def eigenvalues(matrix: list[list[float]]) -> tuple[list[float], list[list[float]]]:
    """AIFP-wrapped numpy.linalg.eig.
    Inputs: 2D list (matrix)
    Outputs: Tuple (values, vectors)
    Side Effects: None"""
    np_matrix = _orig.array(matrix)
    values, vectors = _orig.linalg.eig(np_matrix)
    return values.tolist(), vectors.tolist()
```

#### DB Entries (Post-Generation)
After AI generates code (per directive), it updates DB. Example inserts (simplified SQL):

```sql
-- Themes/Flows
INSERT INTO themes (name) VALUES ('matrix_ops');
INSERT INTO flows (name, theme_id) VALUES ('addition_flow', 1), ('eigen_flow', 1);

-- Functions
INSERT INTO functions (name, params_json, returns_type, deps_json, path, docstring, side_effects_json)
VALUES ('add_matrices', '[{"name":"a","type":"list[list[float]]"},{"name":"b","type":"list[list[float]]"}]', 'list[list[float]]', '[]', 'math_utils.py', 'Adds two matrices element-wise. Pure: No side effects.', '[]');

INSERT INTO functions (name, params_json, returns_type, deps_json, path, docstring, side_effects_json)
VALUES ('process_matrices', '[{"name":"m1","type":"list[list[float]]"},{"name":"m2","type":"list[list[float]]"},{"name":"scalar","type":"float"}]', 'tuple[list[list[float]], tuple]', '["add_matrices","scale_matrix","eigenvalues"]', 'main.py', 'Main procedural flow...', '[]');

-- Function-Flow Mapping
INSERT INTO function_flows (function_name, flow_id, connection_type) VALUES ('add_matrices', 1, 'primary');

-- Wrappers
INSERT INTO wrappers (wrapper_name, original_lib, original_method, params_json, returns_type, file_path, side_effects_json)
VALUES ('eigenvalues', 'numpy', 'linalg.eig', '[{"name":"matrix","type":"list[list[float]]"}]', 'tuple[list[float], list[list[float]]]', 'aifp_wrappers/numpy_aifp.py', '[]');

-- Interactions (Post-Analysis)
INSERT INTO interactions (caller_name, callee_name) VALUES ('process_matrices', 'add_matrices');
```

This example is executable; AI would query DB for deps (e.g., during updates). Next: More directives, or test code?

### Clarification on Elixir and AIFP's Language-Agnostic Approach

Yes, **Elixir is a programming language**—a functional, dynamic language built on the Erlang BEAM virtual machine, designed for concurrency, fault-tolerance, and scalability, particularly in distributed systems like web applications.<grok:render type="render_inline_citation">
<argument name="citation_id">5</argument>
</grok:render><grok:render type="render_inline_citation">
<argument name="citation_id">1</argument>
</grok:render> Its functional programming (FP) paradigm emphasizes immutability, pattern matching, and higher-order functions, which we compared to AIFP's functional-procedural style in the previous response.

AIFP (AI Functional Procedural), by contrast, is **not a language** but a **paradigm or coding standard** designed to optimize AI-generated and AI-maintained code across any programming language or environment. Its focus on pure functions, procedural flows, dynamic library wrappers, per-project SQLite database tracking, and hierarchical directives makes it inherently language-agnostic, as you intended. This flexibility ensures AIFP can be applied in Python, JavaScript, or any other language, adapting to their ecosystems while maintaining AI efficiency.<grok:render type="render_inline_citation">
<argument name="citation_id">2</argument>
</grok:render>

### Why AIFP's Language-Agnostic Approach is Ideal
AIFP's design aligns perfectly with your goal of avoiding restriction to a single language like Elixir. Here's why this is advantageous and how to maintain it:

- **Broad Applicability**: AIFP's rules (pure functions, no OOP, DB updates) can be enforced in any language with functions and basic data structures (e.g., Python, JavaScript, Go, Rust). This avoids locking into a specific runtime like BEAM, which, while powerful for concurrency, isn't universal for AI tasks.<grok:render type="render_inline_citation">
<argument name="citation_id">6</argument>
</grok:render>
- **Ecosystem Compatibility**: AI development heavily relies on libraries (e.g., numpy, PyTorch in Python), which AIFP's wrappers adapt to its style. A language-specific approach (like Elixir) would limit access to these, requiring reimplementation or complex bridging.<grok:render type="render_inline_citation">
<argument name="citation_id">16</argument>
</grok:render>
- **Flexibility for AI**: AI often works in heterogeneous environments (e.g., Python for ML, JavaScript for web). AIFP's directives and DB ensure consistency across these, while a single language might constrain deployment.<grok:render type="render_inline_citation">
<argument name="citation_id">10</argument>
</grok:render>
- **Future-Proofing**: By staying agnostic, AIFP can evolve with new languages or tools without rewriting its core. If developers create an AIFP-specific language later, the standard can be ported easily due to its abstract rules.

### Potential Elixir-Inspired Enhancements Without Language Restriction
While Elixir's FP features (pipe operator, pattern matching, actor model) were discussed previously, they can be adapted as **language-agnostic patterns** within AIFP's directives, ensuring no dependency on Elixir or BEAM. Here's how to incorporate them while keeping AIFP universal:

1. **Pipe-Like Chaining (Language-Agnostic)**:
   - **Concept**: Elixir's `|>` pipes data through functions for readable, sequential flows (e.g., `data |> transform1() |> transform2()`).<grok:render type="render_inline_citation">
<argument name="citation_id">0</argument>
</grok:render>
   - **AIFP Adaptation**: Define a directive (`directive_fp_chaining`) that encourages AI to generate chained function calls in any language. In Python, mimic with method chaining or nested calls (e.g., `transform2(transform1(data))`). In JavaScript, use `.pipe()` or functional composition libraries. The directive enforces:
     - Sequence functions in a linear, readable flow.
     - Update DB with chain metadata (e.g., `interactions` table logs `caller -> callee`).
   - **Benefit**: Enhances procedural clarity for AI without language lock-in.

2. **Pattern Matching as a Directive**:
   - **Concept**: Elixir's pattern matching dispatches based on input structure (e.g., `def handle({:ok, data}) -> ...`).<grok:render type="render_inline_citation">
<argument name="citation_id">2</argument>
</grok:render>
   - **AIFP Adaptation**: Add a directive (`directive_pattern_matching`) to emulate in supported languages (e.g., Python's `match` statement, JavaScript's destructuring). Example:
     ```python
     # Python match (3.10+)
     def handle(result):
         match result:
             case {"status": "ok", "data": data}: return process(data)
             case {"status": "error", "msg": msg}: raise AIFPError(msg)
     ```
     - DB tracks clauses as sub-functions for dependency queries.
   - **Benefit**: Simplifies AI's handling of variant inputs, portable across languages with conditional constructs.

3. **Actor-Like Concurrency (Optional)**:
   - **Concept**: Elixir's actor model uses lightweight processes with message passing for concurrency.<grok:render type="render_inline_citation">
<argument name="citation_id">5</argument>
</grok:render>
   - **AIFP Adaptation**: Create an optional directive (`directive_concurrency`) for projects needing parallelism. In Python, use `asyncio` or `multiprocessing.Queue` for message passing; in JavaScript, use Web Workers. The directive specifies:
     - Isolate concurrent tasks as pure functions.
     - Log interactions to DB (`interactions` table with `interaction_type: 'message_pass'`).
     - Avoid shared state, mimicking Elixir's isolation.
   - **Benefit**: Supports distributed AI tasks (e.g., agent swarms) without requiring BEAM.<grok:render type="render_inline_citation">
<argument name="citation_id">13</argument>
</grok:render>

#### Sample Directive for Chaining (Language-Agnostic)
To illustrate, here's a directive to enforce pipe-like chaining in AIFP, adaptable to any language.

##### MD File (directive_fp_chaining.md)
```
# AIFP Directive: Functional Chaining for Procedural Flows

## Overview
Guides AI to generate function sequences in a chained, linear style to enhance readability and traceability, inspired by Elixir's pipe operator but language-agnostic. Updates DB to track chain dependencies.

## Why This Exists
Chaining reduces nested calls, making AI-generated code easier to follow and optimize. DB tracking ensures quick dependency queries, aligning with AIFP's efficiency goals.

## When to Use
Apply during procedural flow generation. Escalate if chaining syntax varies by language or conflicts with purity.

## Guidelines
1. Analyze task: Identify sequence of function calls.
2. Generate: Chain calls (e.g., Python: transform2(transform1(data)); JS: data.pipe(transform1).pipe(transform2)).
3. Validate: Ensure purity, no side effects in chain.
4. Update DB: Log in interactions table (caller_name, callee_name, interaction_type: 'chain').
5. Handle Language Variants: Use native chaining if available (e.g., Python match, JS pipe); else, nest explicitly.

## Example
Python:
```python
def process_data(data: list[int]) -> list[int]:
    return scale(add(data, 1), 2) # Chained: add -> scale
```
DB: INSERT INTO interactions (caller_name, callee_name, interaction_type) VALUES ('process_data', 'add', 'chain'), ('process_data', 'scale', 'chain');

## References
Escalate to directive_fp_chaining_detailed.json for language-specific mappings.
```

##### Compressed JSON (directive_fp_chaining_compressed.json)
```json
{
  "id": "fp_chaining",
  "desc": "Gen chained func calls, track in DB",
  "esc_to": "directive_fp_chaining_detailed.json",
  "steps": ["analyze seq", "gen chain", "validate purity", "update DB: interactions(caller,callee,'chain')"],
  "ex": {"code": "scale(add(data,1),2)", "db": [{"caller":"process_data","callee":"add","type":"chain"}]}
}
```

#### Risks of Elixir-Specific Components
Adopting Elixir-specific features (e.g., BEAM VM, OTP) would degrade AIFP's objectives:
- **Language Lock-In**: Requiring Elixir would limit AIFP to BEAM, alienating Python-heavy AI ecosystems.<grok:render type="render_inline_citation">
<argument name="citation_id">16</argument>
</grok:render>
- **Complexity**: Macros or OTP add metaprogramming overhead, complicating AI generation and DB tracking.<grok:render type="render_inline_citation">
<argument name="citation_id">2</argument>
</grok:render>
- **Concurrency Overkill**: Most AI tasks (e.g., code gen, ML) are single-threaded or use existing frameworks; BEAM's benefits are niche.<grok:render type="render_inline_citation">
<argument name="citation_id">13</argument>
</grok:render>

#### Recommendation: Stay Language-Agnostic
AIFP's current design—language-agnostic, with DB-driven tracking and directives—is ideal for its AI focus. Incorporate Elixir-inspired patterns (chaining, pattern matching) via directives, as shown, to borrow FP elegance without tying to Elixir's runtime or syntax. If a dedicated AIFP language emerges, these directives can form its spec, but for now, keep AIFP as a universal standard. Next steps: Draft more directives (e.g., pattern matching), or prototype AIFP in another language (e.g., JavaScript)?

### Incorporating Elixir-Inspired Patterns into AIFP with Rust FP Considerations

AIFP (AI Functional Procedural) is a language-agnostic programming paradigm tailored for AI-generated and AI-maintained code, emphasizing pure functions, procedural sequencing, dynamic library wrappers, and a per-project SQLite database for metadata tracking. Its directive-driven approach ensures consistency and efficiency across any language (e.g., Python, JavaScript). Elixir’s functional programming (FP) features, such as the pipe operator (`|>`) for chaining and pattern matching for declarative control flow, were previously identified as valuable for enhancing AIFP’s readability and AI reasoning without tying to Elixir’s BEAM VM.<grok:render type="render_inline_citation">
<argument name="citation_id">0</argument>
</grok:render><grok:render type="render_inline_citation">
<argument name="citation_id">2</argument>
</grok:render> Rust, another language with strong FP influences, offers additional patterns—immutability by default, expressive pattern matching, and zero-cost abstractions—that can further refine AIFP’s design for performance and safety.<grok:render type="render_inline_citation">
<argument name="citation_id">20</argument>
</grok:render><grok:render type="render_inline_citation">
<argument name="citation_id">21</argument>
</grok:render> Below, we describe how to incorporate Elixir-inspired patterns (chaining, pattern matching) and Rust-inspired FP patterns (immutability enforcement, ownership for safety, algebraic data types) into AIFP via directives, ensuring language-agnostic implementation while maximizing AI efficiency.

#### Elixir-Inspired Patterns in AIFP
1. **Pipe-Like Chaining**:
   - **Elixir Concept**: The `|>` operator chains functions by passing the output of one as the input to the next (e.g., `data |> transform1() |> transform2()`), creating clear, linear data flows.<grok:render type="render_inline_citation">
<argument name="citation_id">0</argument>
</grok:render>
   - **AIFP Incorporation**:
     - **Directive (`directive_fp_chaining`)**: Instructs AI to generate function sequences in a chained style, adapted to the host language. In Python, use nested calls or libraries like `pipe` (e.g., `from pipe import Pipe; result = data | Pipe(transform1) | Pipe(transform2)`). In JavaScript, use `.pipe()` or functional composition (e.g., `data.pipe(transform1).pipe(transform2)`). For languages without native chaining, use explicit nesting (e.g., `transform2(transform1(data))`).
     - **Implementation**:
       ```python
       # Python example (using pipe library or nested calls)
       from pipe import Pipe
       def transform1(data: list[int]) -> list[int]:
           return [x + 1 for x in data]
       def transform2(data: list[int]) -> list[int]:
           return [x * 2 for x in data]
       result = [1, 2, 3] | Pipe(transform1) | Pipe(transform2) # or transform2(transform1([1, 2, 3]))
       ```
       - **DB Integration**: Log chains in the `interactions` table (e.g., `INSERT INTO interactions (caller_name, callee_name, interaction_type) VALUES ('main_flow', 'transform1', 'chain')`).
     - **Benefits**:
       - **Readability**: Simplifies procedural flows for AI, reducing nested complexity in generated code.
       - **Traceability**: DB tracks chains, enabling AI to query dependencies instantly (e.g., `SELECT callee_name FROM interactions WHERE interaction_type='chain'`).
       - **AI Efficiency**: Linear flows align with AI’s holistic reasoning, speeding up generation and analysis.<grok:render type="render_inline_citation">
<argument name="citation_id">19</argument>
</grok:render>

2. **Pattern Matching**:
   - **Elixir Concept**: Pattern matching dispatches logic based on data structure (e.g., `def handle({:ok, data}) -> ...; def handle({:error, msg}) -> ...`), avoiding verbose conditionals.<grok:render type="render_inline_citation">
<argument name="citation_id">2</argument>
</grok:render>
   - **AIFP Incorporation**:
     - **Directive (`directive_pattern_matching`)**: Guides AI to use native pattern matching (e.g., Python’s `match` statement, JavaScript destructuring) or emulate it with conditionals. AI generates functions with clause-like structures, registering each clause in the DB for dependency tracking.
     - **Implementation**:
       ```python
       # Python example (using match, Python 3.10+)
       def process_result(result: dict) -> str:
           match result:
               case {"status": "ok", "data": data}:
                   return f"Processed: {data}"
               case {"status": "error", "msg": msg}:
                   raise AIFPError(f"Error: {msg}")
               case _:
                   raise AIFPError("Invalid result")
       ```
       - **DB Integration**: Store clauses as sub-functions (e.g., `INSERT INTO functions (name, params_json, returns_type, deps_json, path) VALUES ('process_result_ok', '[{\"name\":\"result\",\"type\":\"dict\"}]', 'str', '[]', 'utils.py')`).
     - **Benefits**:
       - **Simplified Logic**: Reduces branching complexity, making AI-generated code easier to maintain.<grok:render type="render_inline_citation">
<argument name="citation_id">19</argument>
</grok:render>
       - **Error Handling**: Declarative error cases align with AI’s probabilistic input handling.
       - **DB Queries**: Clause metadata enables quick lookup for variant-specific dependencies.

#### Rust-Inspired FP Patterns in AIFP
Rust, a systems programming language, blends FP with performance and safety through immutability by default, ownership for memory management, and algebraic data types (ADTs) via `enum` and `struct`.<grok:render type="render_inline_citation">
<argument name="citation_id">20</argument>
</grok:render><grok:render type="render_inline_citation">
<argument name="citation_id">21</argument>
</grok:render> These can enhance AIFP’s robustness without tying to Rust’s syntax or ecosystem, keeping AIFP language-agnostic.

1. **Immutability by Default**:
   - **Rust Concept**: Variables are immutable unless declared `mut`, enforcing predictable state and reducing bugs.<grok:render type="render_inline_citation">
<argument name="citation_id">20</argument>
</grok:render>
   - **AIFP Incorporation**:
     - **Directive (`directive_immutability`)**: Mandates AI to generate code assuming immutability unless explicitly needed (e.g., flagged in docstring: “Side Effects: Updates cache”). In Python, use immutable types (tuples, frozenset); in JavaScript, use `const` or libraries like Immutable.js.
     - **Implementation**:
       ```python
       # Python example
       def transform_data(data: tuple[int, ...]) -> tuple[int, ...]:
           """Pure: No side effects. Input immutable tuple."""
           return tuple(x * 2 for x in data)
       ```
       - **DB Integration**: Flag immutability in `functions` table (e.g., add column `is_immutable BOOLEAN DEFAULT TRUE`). Log violations in `side_effects_json`.
     - **Benefits**:
       - **Predictability**: Aligns with AIFP’s purity, reducing AI errors in state tracking.<grok:render type="render_inline_citation">
<argument name="citation_id">21</argument>
</grok:render>
       - **AI Optimization**: Immutable data simplifies reasoning, as AI can assume no hidden changes.
       - **Safety**: Prevents unintended mutations in large AI-generated projects.

2. **Ownership and Borrowing for Safety**:
   - **Rust Concept**: Ownership ensures data has a single owner, with borrowing rules preventing data races or invalid accesses.<grok:render type="render_inline_citation">
<argument name="citation_id">20</argument>
</grok:render>
   - **AIFP Incorporation**:
     - **Directive (`directive_data_safety`)**: Instructs AI to emulate ownership by passing data copies (not references) unless borrowing is safe and explicit (e.g., read-only params). In Python, use `copy.deepcopy` for mutable inputs; in JavaScript, use structuredClone. For performance, allow “borrowing” (pass-by-reference) with DB-flagged safety checks.
     - **Implementation**:
       ```python
       # Python example
       import copy
       def process_list(data: list[int]) -> list[int]:
           """Pure: Copies input to avoid mutation."""
           data_copy = copy.deepcopy(data)
           return [x + 1 for x in data_copy]
       ```
       - **DB Integration**: Add `ownership_type` to `functions` table (e.g., ‘copy’, ‘borrow_safe’). Log interactions in `interactions` table with `interaction_type: 'borrow'`.
     - **Benefits**:
       - **Safety**: Prevents unintended side effects, critical for AI managing large codebases.<grok:render type="render_inline_citation">
<argument name="citation_id">20</argument>
</grok:render>
       - **Traceability**: DB tracks ownership, enabling AI to verify safe data flows.
       - **Performance Option**: Borrowing directives allow optimization in safe contexts, balancing AI efficiency.

3. **Algebraic Data Types (ADTs)**:
   - **Rust Concept**: `enum` and `struct` create ADTs for type-safe, expressive data modeling (e.g., `enum Result { Ok(T), Err(String) }`).<grok:render type="render_inline_citation">
<argument name="citation_id">21</argument>
</grok:render>
   - **AIFP Incorporation**:
     - **Directive (`directive_adt`)**: Guides AI to use ADT-like structures (e.g., Python’s dataclasses or dicts with fixed keys, JavaScript’s tagged unions). AI generates type-safe variants, registering them in DB for queryable metadata.
     - **Implementation**:
       ```python
       # Python example (using dict for ADT-like structure)
       def process_result(result: dict) -> int:
           """ADT-like: {'tag': 'ok', 'value': int} or {'tag': 'error', 'msg': str}."""
           if result['tag'] == 'ok':
               return result['value']
           raise AIFPError(result['msg'])
       ```
       - **DB Integration**: Store ADT definitions in new `types` table (e.g., `CREATE TABLE types (type_id TEXT PRIMARY KEY, definition_json TEXT)`). Link to functions via `functions` table `type_refs_json`.
     - **Benefits**:
       - **Type Safety**: Reduces AI errors in handling complex data, aligning with probabilistic inputs.<grok:render type="render_inline_citation">
<argument name="citation_id">19</argument>
</grok:render>
       - **Expressiveness**: ADTs make code declarative, easier for AI to generate and parse.
       - **DB Synergy**: Type metadata in DB speeds up AI’s type-checking during generation.

#### Sample Directive for Rust-Inspired Immutability
##### MD File (directive_immutability.md)
```
# AIFP Directive: Enforce Immutability by Default

## Overview
Guides AI to generate code with immutable data, inspired by Rust’s default immutability, to ensure predictability and safety. Updates DB to flag immutability and track violations.

## Why This Exists
Immutability aligns with AIFP’s purity, reducing AI errors in state tracking and enabling efficient reasoning in large projects. DB integration ensures quick verification.

## When to Use
Apply to all function generation. Escalate for mutable cases (e.g., caching) with explicit side-effect flags.

## Guidelines
1. Use immutable types (e.g., Python: tuple, frozenset; JS: const).
2. Copy mutable inputs if needed (e.g., copy.deepcopy).
3. Flag side effects in docstring and DB (side_effects_json).
4. Validate: Ensure no mutations unless directive-allowed.
5. Update DB: Set is_immutable=TRUE; log exceptions in side_effects_json.

## Example
```python
def transform(data: tuple[int, ...]) -> tuple[int, ...]:
    """Pure: Immutable input/output."""
    return tuple(x * 2 for x in data)
```
DB: INSERT INTO functions (name, params_json, returns_type, is_immutable) VALUES ('transform', '[{"name":"data","type":"tuple[int]"}]', 'tuple[int]', TRUE);

## References
Escalate to directive_immutability_detailed.json for language-specific immutable types.
```

##### Compressed JSON (directive_immutability_compressed.json)
```json
{
  "id": "immutability",
  "desc": "Gen immutable code, track in DB",
  "esc_to": "directive_immutability_detailed.json",
  "steps": ["use immutable types", "copy mutable inputs", "flag side effects", "validate no mutations", "update DB: is_immutable=TRUE"],
  "ex": {"code": "def transform(data: tuple) -> tuple: return tuple(x*2 for x in data)", "db": {"name":"transform","is_immutable":true}}
}
```

#### Benefits of Combined Elixir and Rust Patterns in AIFP
- **Enhanced Readability and Simplicity**: Elixir’s chaining makes procedural flows clearer; Rust’s immutability reduces complexity in AI-generated code.<grok:render type="render_inline_citation">
<argument name="citation_id">0</argument>
</grok:render><grok:render type="render_inline_citation">
<argument name="citation_id">20</argument>
</grok:render>
- **Improved Safety and Predictability**: Rust’s ownership and immutability prevent side-effect bugs, critical for AI autonomy. Pattern matching from Elixir handles variants declaratively, reducing error-prone conditionals.<grok:render type="render_inline_citation">
<argument name="citation_id">2</argument>
</grok:render><grok:render type="render_inline_citation">
<argument name="citation_id">21</argument>
</grok:render>
- **AI Efficiency**: DB integration of these patterns (e.g., logging chains, clauses, immutability) enables fast queries, aligning with AIFP’s goal of minimizing file parsing.<grok:render type="render_inline_citation">
<argument name="citation_id">19</argument>
</grok:render>
- **Language-Agnostic Flexibility**: By implementing via directives, these patterns work in any language, preserving AIFP’s universal applicability. No dependency on Elixir’s BEAM or Rust’s compiler.<grok:render type="render_inline_citation">
<argument name="citation_id">16</argument>
</grok:render>
- **Scalability for AI Workflows**: Supports complex AI tasks (e.g., agent swarms) via optional concurrency directives, inspired by Elixir’s actors, without sacrificing simplicity.<grok:render type="render_inline_citation">
<argument name="citation_id">13</argument>
</grok:render>

#### Risks and Mitigation
- **Overcomplication**: Too many patterns could bloat directives, slowing AI generation. Mitigate by keeping directives optional and modular (e.g., only apply `directive_concurrency` for parallel tasks).
- **Language Limitations**: Not all languages support pattern matching or chaining natively (e.g., older Python versions). Mitigate by defining fallback patterns (e.g., if/else for matching).
- **Performance Overhead**: Copying for immutability or ownership may impact speed. Mitigate with directives allowing safe borrowing for performance-critical cases, logged in DB.

#### Recommendation
Incorporate Elixir’s chaining and pattern matching, and Rust’s immutability, ownership, and ADTs, as directive-driven patterns to enhance AIFP’s FP core. This strengthens readability, safety, and AI efficiency while keeping AIFP language-agnostic. Avoid deep integration of language-specific features (e.g., Rust’s borrow checker, Elixir’s OTP) to prevent ecosystem lock-in. If an AIFP-specific language is developed later, these directives can inform its design. Next steps: Draft `directive_pattern_matching` or `directive_adt`, or prototype AIFP in another language (e.g., JavaScript)?

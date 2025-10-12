AIFP FP Directives

These directives enforce functional-procedural coding standards, ensuring pure functions, no OOP, immutability, and type safety. They apply when generating or verifying code, updating files, functions, types, and interactions tables in project.db.





directive_fp_purity
Description: Enforces pure functions with no hidden state or side effects.
Flow: Scan code for mutations (e.g., list.append) or globals. Refactor to explicit parameters/returns. Update functions.side_effects_json with purity status.
Workflow: {"trunk": "scan_code", "branches": [{"if": "mutations_detected", "then": "refactor_to_pure", "details": {"explicit_params": true}}, {"if": "pure", "then": "update_functions_table", "details": {"side_effects_json": "none"}}, {"fallback": "prompt_user", "details": {"clarify": "Handle impure function?"}}], "error_handling": {"on_failure": "prompt_user"}}
md_file_path: directives/fp_purity.md
roadblocks_json: [{"issue": "impure_function", "resolution": "Refactor or isolate, prompt user"}]intent_keywords_json: ["pure", "function", "no side effects"]
confidence_threshold: 0.7



directive_fp_no_oop
Description: Prevents OOP constructs like classes or inheritance.
Flow: Detect 'class' or 'self' patterns. Refactor to top-level functions. Escalate to anti_oop_redirect if complex. Log in notes.
Workflow: {"trunk": "scan_code", "branches": [{"if": "oop_detected", "then": "anti_oop_redirect", "details": {"refactor": true}}, {"if": "no_oop", "then": "proceed", "details": {"log_note": true}}, {"fallback": "prompt_user", "details": {"clarify": "Refactor OOP?"}}], "error_handling": {"on_failure": "prompt_user"}}
md_file_path: directives/fp_no_oop.md
roadblocks_json: [{"issue": "complex_oop", "resolution": "Escalate to anti_oop_redirect, prompt user"}]intent_keywords_json: ["no oop", "classless", "functional"]
confidence_threshold: 0.7



directive_fp_chaining
Description: Implements pipe-like chaining for procedural flows.
Flow: Parse function sequences. Generate nested calls (e.g., transform2(transform1(data))). Update interactions table with chain dependencies.
Workflow: {"trunk": "parse_sequence", "branches": [{"if": "chainable_functions", "then": "generate_chaining", "details": {"nested_calls": true}}, {"if": "library_needed", "then": "wrap_library", "details": {"update_interactions": true}}, {"fallback": "prompt_user", "details": {"clarify": "Chain functions?"}}], "error_handling": {"on_failure": "prompt_user"}}
md_file_path: directives/fp_chaining.md
roadblocks_json: [{"issue": "non_chainable", "resolution": "Prompt user for alternative flow"}]intent_keywords_json: ["chain", "pipe", "flow"]
confidence_threshold: 0.6



directive_fp_pattern_matching
Description: Applies declarative control flow via pattern matching.
Flow: Identify variant inputs. Generate match/clause structures (e.g., Python match). Register clauses as sub-functions in functions.
Workflow: {"trunk": "identify_inputs", "branches": [{"if": "variant_inputs", "then": "generate_match", "details": {"store_sub_functions": true}}, {"if": "no_native_match", "then": "emulate_with_dict", "details": {"update_functions": true}}, {"fallback": "prompt_user", "details": {"clarify": "Pattern match needed?"}}], "error_handling": {"on_failure": "prompt_user"}}
md_file_path: directives/fp_pattern_matching.md
roadblocks_json: [{"issue": "complex_inputs", "resolution": "Simplify inputs, prompt user"}]intent_keywords_json: ["pattern match", "match case", "control flow"]
confidence_threshold: 0.6



directive_fp_immutability
Description: Ensures immutability by default for data.
Flow: Check for mutable types (e.g., list). Replace with immutable (e.g., tuple). Update functions.side_effects_json.
Workflow: {"trunk": "check_types", "branches": [{"if": "mutable_detected", "then": "replace_with_immutable", "details": {"copy_inputs": true}}, {"if": "immutable", "then": "update_functions", "details": {"side_effects_json": "immutable"}}, {"fallback": "prompt_user", "details": {"clarify": "Handle mutable data?"}}], "error_handling": {"on_failure": "prompt_user"}}
md_file_path: directives/fp_immutability.md
roadblocks_json: [{"issue": "mutable_inputs", "resolution": "Use immutable types, prompt user"}]intent_keywords_json: ["immutable", "no mutation", "data safety"]
confidence_threshold: 0.7



directive_fp_ownership_safety
Description: Emulates ownership to prevent data races or invalid accesses.
Flow: Pass data copies for mutable params, allow borrowing for read-only. Log ownership_type in functions. Alert on unsafe mutations.
Workflow: {"trunk": "analyze_params", "branches": [{"if": "mutable_params", "then": "pass_copies", "details": {"ownership_type": "copy"}}, {"if": "read_only", "then": "allow_borrow", "details": {"ownership_type": "borrow"}}, {"fallback": "prompt_user", "details": {"clarify": "Handle ownership?"}}], "error_handling": {"on_failure": "alert_user"}}
md_file_path: directives/fp_ownership_safety.md
roadblocks_json: [{"issue": "unsafe_mutation", "resolution": "Isolate mutation, prompt user"}]intent_keywords_json: ["ownership", "data safety", "no races"]
confidence_threshold: 0.6



directive_fp_adt
Description: Uses algebraic data types for type-safe modeling.
Flow: Generate enum/struct-like structures (e.g., tagged dicts). Link to pattern matching. Store in types.
Workflow: {"trunk": "define_adt", "branches": [{"if": "needs_variants", "then": "generate_enum", "details": {"store_in_types": true}}, {"if": "needs_struct", "then": "generate_dict", "details": {"link_to_pattern_matching": true}}, {"fallback": "prompt_user", "details": {"clarify": "Define ADT?"}}], "error_handling": {"on_failure": "prompt_user"}}
md_file_path: directives/fp_adt.md
roadblocks_json: [{"issue": "complex_adt", "resolution": "Simplify structure, prompt user"}]intent_keywords_json: ["adt", "algebraic data", "type safety"]
confidence_threshold: 0.6



directive_fp_anti_oop_redirect
Description: Refactors OOP patterns to FP equivalents.
Flow: Replace classes with functions. Pass state explicitly. Update deps_json in functions. Log in notes.
Workflow: {"trunk": "refactor_oop", "branches": [{"if": "class_detected", "then": "convert_to_functions", "details": {"explicit_state": true}}, {"if": "complex_oop", "then": "prompt_user", "details": {"log_note": true}}, {"fallback": "prompt_user", "details": {"clarify": "Refactor OOP?"}}], "error_handling": {"on_failure": "prompt_user"}}
md_file_path: directives/fp_anti_oop_redirect.md
roadblocks_json: [{"issue": "complex_refactor", "resolution": "Prompt user for manual guidance"}]intent_keywords_json: ["refactor oop", "remove class", "functional"]
confidence_threshold: 0.7



directive_fp_side_effects_flag
Description: Flags and isolates side effects.
Flow: Detect I/O or mutations. Wrap in dedicated modules. Update functions.side_effects_json. Alert if unflagged.
Workflow: {"trunk": "scan_side_effects", "branches": [{"if": "side_effects_detected", "then": "isolate_in_module", "details": {"update_side_effects_json": true}}, {"if": "no_side_effects", "then": "proceed", "details": {"flag_pure": true}}, {"fallback": "prompt_user", "details": {"clarify": "Handle side effect?"}}], "error_handling": {"on_failure": "alert_user"}}
md_file_path: directives/fp_side_effects_flag.md
roadblocks_json: [{"issue": "unflagged_side_effect", "resolution": "Isolate and flag, prompt user"}]intent_keywords_json: ["side effect", "isolate io", "pure"]
confidence_threshold: 0.6



directive_fp_dependency_tracking
Description: Tracks function dependencies.
Flow: Parse calls to build deps_json. Insert into interactions. Query for chain/borrow types.
Workflow: {"trunk": "parse_calls", "branches": [{"if": "dependencies_detected", "then": "update_interactions", "details": {"deps_json": true}}, {"if": "no_dependencies", "then": "proceed", "details": {"log_note": true}}, {"fallback": "prompt_user", "details": {"clarify": "Track dependencies?"}}], "error_handling": {"on_failure": "prompt_user"}}
md_file_path: directives/fp_dependency_tracking.md
roadblocks_json: [{"issue": "complex_deps", "resolution": "Simplify dependencies, prompt user"}]intent_keywords_json: ["dependency", "track calls", "function chain"]
confidence_threshold: 0.6



directive_fp_multi_language
Description: Adapts FP rules to different languages.
Flow: Detect language from files.language. Adjust patterns (e.g., Python match vs. JS destructuring). Update tools table if needed.
Workflow: {"trunk": "detect_language", "branches": [{"if": "python_detected", "then": "apply_python_fp", "details": {"pattern_matching": "match_case"}}, {"if": "js_detected", "then": "apply_js_fp", "details": {"pattern_matching": "destructuring"}}, {"fallback": "prompt_user", "details": {"clarify": "Specify language?"}}], "error_handling": {"on_failure": "prompt_user"}}
md_file_path: directives/fp_multi_language.md
roadblocks_json: [{"issue": "unsupported_language", "resolution": "Prompt user for language support"}]intent_keywords_json: ["language", "multi language", "adapt fp"]
confidence_threshold: 0.6
#!/bin/bash
# Batch SQL cleanup for all remaining FP directive files
# Removes INSERT INTO notes from 26 files (fp_api_design already done)

SCRIPT_DIR="/home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/Tasks"
SCRIPT="$SCRIPT_DIR/cleanup_single_file.py"

# Files to clean (excluding fp_api_design.md - already done)
FILES=(
    "fp_chaining.md"
    "fp_concurrency_safety.md"
    "fp_conditional_elimination.md"
    "fp_const_refactoring.md"
    "fp_currying.md"
    "fp_documentation.md"
    "fp_generic_constraints.md"
    "fp_guard_clauses.md"
    "fp_inheritance_flattening.md"
    "fp_io_isolation.md"
    "fp_logging_safety.md"
    "fp_memoization.md"
    "fp_naming_conventions.md"
    "fp_ownership_safety.md"
    "fp_parallel_purity.md"
    "fp_pattern_matching.md"
    "fp_reflection_limitation.md"
    "fp_runtime_type_check.md"
    "fp_side_effects_flag.md"
    "fp_state_elimination.md"
    "fp_tail_recursion.md"
    "fp_task_isolation.md"
    "fp_test_purity.md"
    "fp_type_inference.md"
    "fp_type_safety.md"
    "fp_wrapper_generation.md"
)

echo "================================================================================"
echo "Batch SQL Cleanup - FP Directives"
echo "================================================================================"
echo "Files to process: ${#FILES[@]}"
echo "Script: $SCRIPT"
echo ""
echo "Starting cleanup..."
echo ""

SUCCESS_COUNT=0
FAIL_COUNT=0
NO_CHANGE_COUNT=0

for file in "${FILES[@]}"; do
    echo "[$((SUCCESS_COUNT + FAIL_COUNT + NO_CHANGE_COUNT + 1))/${#FILES[@]}] Processing: $file"

    if python3 "$SCRIPT" "$file" 2>&1 | grep -q "CLEANUP COMPLETE"; then
        if grep -q "No changes needed" <(python3 "$SCRIPT" "$file" 2>&1); then
            ((NO_CHANGE_COUNT++))
            echo "  → No changes needed"
        else
            ((SUCCESS_COUNT++))
            echo "  → ✓ Cleaned"
        fi
    else
        ((FAIL_COUNT++))
        echo "  → ✗ FAILED"
    fi
    echo ""
done

echo "================================================================================"
echo "Batch Cleanup Complete"
echo "================================================================================"
echo "Successfully cleaned: $SUCCESS_COUNT"
echo "No changes needed: $NO_CHANGE_COUNT"
echo "Failed: $FAIL_COUNT"
echo "Total processed: $((SUCCESS_COUNT + FAIL_COUNT + NO_CHANGE_COUNT))"
echo ""
echo "Backups location: docs/directives-json/backups/sql_cleanup/"
echo ""
echo "Next step: Review cleaned files for fragments or inconsistencies"
echo "================================================================================"

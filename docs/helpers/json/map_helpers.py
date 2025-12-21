#!/usr/bin/env python3
"""
Helper Mapping Script - Phase 8
Systematically map helpers to directives based on name/description matching
"""

import json
from pathlib import Path
from typing import Dict, List

# Define directive categories to consider (exclude FP)
DIRECTIVE_FILES = {
    'project': 'docs/directives-json/directives-project.json',
    'git': 'docs/directives-json/directives-git.json',
    'user_system': 'docs/directives-json/directives-user-system.json',
    'user_pref': 'docs/directives-json/directives-user-pref.json',
}

# Skip FP directives
SKIP_FP = True

# Helper files to process
HELPER_FILES = [
    'docs/helpers/json/helpers-core.json',
    'docs/helpers/json/helpers-orchestrators.json',
    'docs/helpers/json/helpers-git.json',
    'docs/helpers/json/helpers-settings.json',
    'docs/helpers/json/helpers-user-custom.json',
    'docs/helpers/json/helpers-project-1.json',
    'docs/helpers/json/helpers-project-2.json',
    'docs/helpers/json/helpers-project-3.json',
]

def load_directives() -> Dict[str, Dict]:
    """Load all non-FP directives with name, description"""
    directives = {}

    for category, filepath in DIRECTIVE_FILES.items():
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                # Handle both array and object formats
                if isinstance(data, list):
                    directive_list = data
                else:
                    directive_list = [data]

                for directive in directive_list:
                    if isinstance(directive, dict):
                        name = directive.get('name', '')
                        description = directive.get('description', '')
                        directives[name] = {
                            'name': name,
                            'category': category,
                            'description': description,
                            'workflow': directive.get('workflow', {}),
                        }
        except FileNotFoundError:
            print(f"Warning: {filepath} not found")
        except json.JSONDecodeError as e:
            print(f"Error parsing {filepath}: {e}")

    return directives

def load_helpers() -> Dict[str, List[Dict]]:
    """Load all helpers organized by file"""
    helpers_by_file = {}

    for filepath in HELPER_FILES:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                helpers = data.get('helpers', [])
                helpers_by_file[filepath] = helpers
        except FileNotFoundError:
            print(f"Warning: {filepath} not found")

    return helpers_by_file

def keyword_match(helper_name: str, helper_purpose: str,
                  directive_name: str, directive_description: str) -> float:
    """
    Score match between helper and directive based on keywords
    Returns: 0.0-1.0 confidence score
    """
    # Extract keywords from names
    helper_words = set(helper_name.lower().replace('_', ' ').split())
    directive_words = set(directive_name.lower().replace('_', ' ').split())

    # Extract keywords from descriptions
    helper_desc_words = set(helper_purpose.lower().split())
    directive_desc_words = set(directive_description.lower().split())

    # Calculate overlap
    name_overlap = len(helper_words & directive_words)
    desc_overlap = len(helper_desc_words & directive_desc_words)

    # Weighted score
    score = 0.0
    if name_overlap > 0:
        score += 0.5 * (name_overlap / max(len(helper_words), len(directive_words)))
    if desc_overlap > 2:  # At least 3 shared words
        score += 0.3 * (desc_overlap / max(len(helper_desc_words), len(directive_desc_words)))

    # Bonus for exact verb match (get, add, update, delete, etc.)
    helper_verb = helper_name.split('_')[0] if '_' in helper_name else ''
    directive_verb = directive_name.split('_')[1] if '_' in directive_name else ''
    if helper_verb and directive_verb and helper_verb == directive_verb:
        score += 0.2

    return min(score, 1.0)

def generate_mapping_suggestions():
    """Generate suggested mappings for review"""

    print("Loading directives...")
    directives = load_directives()
    print(f"Loaded {len(directives)} non-FP directives")

    print("\nLoading helpers...")
    helpers_by_file = load_helpers()
    total_helpers = sum(len(helpers) for helpers in helpers_by_file.values())
    print(f"Loaded {total_helpers} helpers from {len(helpers_by_file)} files")

    print("\n" + "="*80)
    print("MAPPING SUGGESTIONS")
    print("="*80)

    # Track statistics
    stats = {
        'total_helpers': 0,
        'helpers_with_matches': 0,
        'total_suggestions': 0,
        'high_confidence': 0,  # score >= 0.5
        'medium_confidence': 0,  # 0.3 <= score < 0.5
        'low_confidence': 0,  # score < 0.3
    }

    all_suggestions = []

    # Process each helper file
    for helper_file, helpers in helpers_by_file.items():
        file_name = Path(helper_file).name
        print(f"\n{'='*80}")
        print(f"FILE: {file_name}")
        print(f"{'='*80}\n")

        for helper in helpers:
            stats['total_helpers'] += 1
            helper_name = helper.get('name', '')
            helper_purpose = helper.get('purpose', '')

            # Find matching directives
            matches = []
            for directive_name, directive_data in directives.items():
                score = keyword_match(
                    helper_name, helper_purpose,
                    directive_name, directive_data['description']
                )

                if score > 0.2:  # Threshold for suggestion
                    matches.append({
                        'directive': directive_name,
                        'category': directive_data['category'],
                        'score': score,
                    })

            if matches:
                stats['helpers_with_matches'] += 1
                matches.sort(key=lambda x: x['score'], reverse=True)

                print(f"HELPER: {helper_name}")
                print(f"  Purpose: {helper_purpose[:100]}...")
                print(f"  Matches ({len(matches)}):")

                for match in matches[:5]:  # Show top 5
                    stats['total_suggestions'] += 1
                    confidence = match['score']

                    if confidence >= 0.5:
                        level = "HIGH"
                        stats['high_confidence'] += 1
                    elif confidence >= 0.3:
                        level = "MEDIUM"
                        stats['medium_confidence'] += 1
                    else:
                        level = "LOW"
                        stats['low_confidence'] += 1

                    print(f"    [{level:6}] {confidence:.2f} - {match['directive']} ({match['category']})")

                    all_suggestions.append({
                        'helper': helper_name,
                        'helper_file': file_name,
                        'directive': match['directive'],
                        'category': match['category'],
                        'confidence': confidence,
                        'level': level,
                    })

                print()

    # Print statistics
    print("\n" + "="*80)
    print("STATISTICS")
    print("="*80)
    print(f"Total helpers analyzed: {stats['total_helpers']}")
    print(f"Helpers with matches: {stats['helpers_with_matches']} ({stats['helpers_with_matches']/stats['total_helpers']*100:.1f}%)")
    print(f"Total suggestions: {stats['total_suggestions']}")
    print(f"  High confidence (≥0.5): {stats['high_confidence']} ({stats['high_confidence']/stats['total_suggestions']*100:.1f}%)")
    print(f"  Medium confidence (0.3-0.5): {stats['medium_confidence']} ({stats['medium_confidence']/stats['total_suggestions']*100:.1f}%)")
    print(f"  Low confidence (<0.3): {stats['low_confidence']} ({stats['low_confidence']/stats['total_suggestions']*100:.1f}%)")

    # Save suggestions to JSON for review
    output_file = 'docs/helpers/json/mapping_suggestions.json'
    with open(output_file, 'w') as f:
        json.dump({
            'statistics': stats,
            'suggestions': all_suggestions
        }, f, indent=2)

    print(f"\nSuggestions saved to: {output_file}")
    print("\nNext steps:")
    print("1. Review HIGH confidence suggestions first")
    print("2. Manually verify MEDIUM confidence suggestions")
    print("3. Skip or carefully review LOW confidence suggestions")
    print("4. Add used_by_directives entries to helper JSON files")

if __name__ == '__main__':
    generate_mapping_suggestions()

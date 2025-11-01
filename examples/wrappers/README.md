# Wrapper Examples

This folder contains real-world wrapper implementations for common libraries that need FP-compliant interfaces.

## Purpose

As AIFP develops, we create functional wrappers around OOP and impure libraries. These wrappers serve as:

- **Reference implementations** - Working examples of wrapper patterns in practice
- **Reusable code** - Copy/adapt for similar wrapping needs
- **Pattern demonstrations** - Show how to handle common library patterns
- **Learning resources** - Study how to wrap different library types

## Organization

Wrappers are organized by library/category:

```
examples/wrappers/
├── python/
│   ├── requests_wrapper.py      # HTTP client wrapper
│   ├── sqlite3_wrapper.py       # Database wrapper
│   ├── logging_wrapper.py       # Logger wrapper
│   └── ...
├── javascript/
│   ├── axios_wrapper.js         # HTTP client wrapper
│   ├── mongoose_wrapper.js      # ORM wrapper
│   └── ...
└── README.md (this file)
```

## Related Directives

These wrappers implement patterns from:

- **fp_wrapper_generation** - OOP library wrapping patterns
  - See: [src/aifp/reference/directives/fp_wrapper_generation.md](../../src/aifp/reference/directives/fp_wrapper_generation.md)

- **fp_cross_language_wrappers** - Cross-language FP compliance
  - See: [src/aifp/reference/directives/fp_cross_language_wrappers.md](../../src/aifp/reference/directives/fp_cross_language_wrappers.md)

## Wrapper Principles

All wrappers in this folder follow AIFP guidelines:

1. **Pure interfaces** - Functions accept all inputs as parameters
2. **Result types** - Return `Result<T, E>` instead of throwing exceptions
3. **Explicit dependencies** - No hidden global state or singletons
4. **Immutable data** - Use frozen dataclasses/immutable objects
5. **Effect isolation** - Side effects isolated to wrapper boundary

## Contributing

When adding wrappers to this folder:

1. **Document thoroughly** - Comments explaining wrapper decisions
2. **Include usage examples** - Show how to use the wrapper
3. **Note limitations** - Document what the wrapper doesn't handle
4. **Reference directives** - Link to relevant AIFP directives
5. **Test coverage** - Include or reference tests

## Status

This folder is currently **empty** and will be populated as we develop the MCP server and encounter libraries that need wrapping.

---

*Part of AIFP v1.0 - Functional wrapper examples for real-world libraries*

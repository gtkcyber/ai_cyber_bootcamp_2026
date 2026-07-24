# Conventional Commit Prefixes

Format: `type(scope): subject`

The `scope` is optional. The subject is imperative and 50 characters or fewer.

| type     | use for                                              |
|----------|------------------------------------------------------|
| feat     | a new feature                                        |
| fix      | a bug fix                                             |
| docs     | documentation only                                   |
| style    | formatting, whitespace, no behavior change           |
| refactor | code change that is neither a feature nor a fix      |
| perf     | a performance improvement                            |
| test     | adding or fixing tests                               |
| build    | build system or dependencies                         |
| ci       | CI configuration                                     |
| chore    | maintenance that does not touch src or tests         |

## Examples

```
feat(auth): add TOTP second factor
fix(parser): handle empty CSV header row
docs: explain the IOC output format
```

## Breaking changes

Add a `!` after the type or a `BREAKING CHANGE:` footer:

```
feat(api)!: drop the v1 login endpoint
```

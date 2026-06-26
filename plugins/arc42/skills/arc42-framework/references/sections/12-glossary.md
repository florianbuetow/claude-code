# Section 12 — Glossary

Source: 12-glossary/index.md

## Intent
Defines the key domain and technical terms used throughout the documentation so all stakeholders share a consistent vocabulary. Eliminates synonym and homonym confusion. When the team spans multiple languages, the glossary also serves as a translation reference.

## Evidence tier
code-derivable

## What to look for in the repo
- Domain entity class names in model or domain source files
- Type aliases and enums whose names encode business concepts
- API field names and event names in schema definitions (OpenAPI, Avro, protobuf)
- Existing GLOSSARY.md, DICTIONARY.md, or ubiquitous-language files
- README passages that explain abbreviations or project-specific jargon
- Code comments that clarify what a type or variable means in business terms

## Output template

*<Alphabetically sorted; add a Translation column for multilingual projects>*

| Term | Definition |
|------|-----------|
| `<Term>` | `<definition>` |

*<Optional: multi-language extension>*

| Term | Definition | `<Language 2>` |
|------|-----------|----------------|
|  |  |  |

## Diagrams
none

## Lint (this section)
- T12-* (domain entities named in §5 appear here; each entry is a definition, not just a label; no circular definitions; terms used in other sections are consistently spelled)

## Depends on
- All other sections (terms introduced in §1–§11 should be defined here to maintain a single source of truth for vocabulary)

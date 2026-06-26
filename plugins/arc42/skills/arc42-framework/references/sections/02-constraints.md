# Section 2 — Architecture Constraints

Source: 02-constraints/index.md

## Intent
Lists every non-negotiable boundary — technical, organizational, legal, or conventional — that removes options from the architect's decision space. Constraints must be made explicit even when they are potentially negotiable, because undocumented constraints silently drive decisions in ways that are hard to reverse.

## Evidence tier
code-inferable

## What to look for in the repo
- Build-tool and language choices (pom.xml, pyproject.toml, package.json) locked by organizational policy
- CI/CD configuration files revealing mandated cloud providers or deployment platforms
- LICENSE files, compliance notes, or data-residency policies that restrict technology options
- README sections describing team conventions (versioning schemes, approved library lists, coding standards)
- Infrastructure-as-code that pins deployment targets or network topologies

## Output template

*<Group constraints by type; omit categories that do not apply>*

### Technical Constraints

| Constraint | Explanation |
|------------|-------------|
|  |  |

### Organizational / Political Constraints

| Constraint | Explanation |
|------------|-------------|
|  |  |

### Conventions

| Constraint | Explanation |
|------------|-------------|
|  |  |

## Diagrams
none

## Lint (this section)
- T02-* (each constraint has an explanation; constraints are distinct from solution decisions; constraints reference their source where identifiable)

## Depends on
- §1 (stakeholders and business goals determine which constraints are relevant to capture)

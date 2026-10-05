# Capabilities

Governing parent: [BRAIN.md](../BRAIN.md)

Read this guide when a task or applicable guidance requires a reusable skill, script, or supporting bundle, or when preserving one for another actor or machine. Capability content loads when needed; no startup catalog scan is required.

## Ownership and discovery

A capability supplies a reusable procedure and the files needed to perform it. It does not grant permission or replace [Guidance](../guidance/README.md). Keep one maintained source:

| Owner | Canonical home | Discovery route |
|---|---|---|
| Personal, reusable across projects | `capabilities/<name>/` in the personal brain | Link its entry from the guidance or procedure that needs it. |
| Project with a maintained repository | The project's repository | Link from its brain project README to a source record identifying retrieval and the entry within the repository. |
| Project without a maintained repository | `projects/<project>/capabilities/<name>/` in the personal brain | Link from that project's README. |

These are personal-content homes. The shared framework ships this guide and generic examples, not populated bundles. Do not create empty capability directories or a separate registry. Keep behavioural rules in their shared or project guidance home rather than copying them into capability bundles.

Skills can be selected directly for a task through an agent's native discovery. A stage or rule links to a skill only when that guidance requires it; capability use does not require a stage binding. Native registration follows the maintained bundle rather than creating a second source.

For an external home, follow [Sources](../sources/README.md): record the repository or other authorized retrieval location, relevant revision, and entry path. A local absolute path can identify an installed copy, but cannot by itself explain how to obtain the source elsewhere. Verify current files before use; report unavailable or conflicting sources rather than choosing from stale copies.

## Bundle and dependencies

Use a readable entry such as `SKILL.md` or `README.md`. State what the capability does, when to use it, its required inputs, and its output. Resolve supporting-file links relative to the entry or state the required working directory. Preserve that layout when moving the bundle.

For example, a personal text-checking capability could contain:

```text
capabilities/text-check/
  SKILL.md
  scripts/check_text.py
  config/accepted-terms.txt
```

Its entry links to the script and term list and explains how to supply an input document. The document and generated report remain task data, not part of the reusable bundle.

Follow dependencies beyond the entry: supporting documents, sibling capabilities, scripts, configuration, assets, tools, and runtime packages. Preserve maintained dependency files and known version requirements. Record a missing dependency or unresolved disagreement where the next actor will encounter it; copying the entry alone does not complete the transfer.

Keep credentials and private runtime configuration outside ordinary brain content. Setup instructions name the required access and private-asset provisioning route without including secrets or recordings.

## Setup and use

Keep portable setup instructions with the bundle: how to obtain its dependencies, configure required access, and run a representative check. Put host-specific installation paths and observed results under [Operations](../operations/README.md). Native skill registrations, symlinks, or generated copies are replaceable adapters; they point to the maintained source and are recreated or refreshed when it changes.

Before use, read the entry and required support, check prerequisites on the actual host, and apply the task's authorization. If a runtime lacks a required tool, identify the missing prerequisite and leave the dependent action unperformed.

## Validate a transfer

Use an isolated setup with synthetic inputs. Retrieve the recorded source without relying on the original machine's files, discover the entry through its owning link, install the declared prerequisites, and run a representative operation that exercises supporting files. Check the output against the task's expected result. Remove a required support file in the fixture and confirm the check detects its absence.

Record the source revision, host, exercised operation, result, and remaining limits in personal project or operation records. Link and syntax checks establish only those properties; clean-machine usability requires observed execution. Leave the old source available until the selected transfer and references are verified, then record which home owns future changes.

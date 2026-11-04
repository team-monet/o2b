# Maintain guidance

Governing parent: [Guidance guide](README.md)

Read this guide before admitting, creating, or changing principles, preferences, leads, situation indexes, or rules, including when the owner states a new rule or corrects an agent. Routine sessions use the parent guide; these conventions govern both rule homes.

## Scope and admission

These rules keep guidance from being duplicated, overlapping, or trapped in one project. They apply to principles and preferences as well as rules.

- **Shared by default.** Guidance is project-scoped only when it names something that exists in that project alone: its files, tools, product behaviour, or the owner's preference for that project. Record where it was learned as its origin; never use the origin as its scope.
- **Search before admitting.** Read the situation's shared page and every project page with the same name, and the applicable principles. Extend or correct an existing entry instead of adding a near-copy, and take a conflict to the owner.
- **One vocabulary.** The shared index names situations. A project adds its rules under an existing situation name, and creates a name only for a moment that exists in that project alone.

## Principles

Keep in `PRINCIPLES.md` every principle that does not belong to particular leads; one that applies only while working as particular leads goes where [Leads](#leads) places it. Group entries by applicability and then by kind, such as Principles and Preferences. A project principle goes under an explicit project scope in whichever of these files holds it, never under `projects/<project>/`. A scope heading applies to every entry beneath it until the next scope heading.

State the authority for a group of source-admitted entries once when it applies uniformly; add an entry-specific authority only for an exception. Separate entry bodies clearly. Add a concise reason when one is known; mark a missing reason as not yet recorded instead of inventing it. Use a title only when it improves reading, and never use storage identifiers or a truncated copy of the instruction as a heading. A principle may link to a central supporting procedure without copying that procedure into every entry. Human-readable provenance or supporting evidence may be linked when it helps a reader judge the guidance.

## Leads

Add a lead only when the owner wants one. Keep the index at `guidance/LEADS.md`: a governing-parent link and a table whose rows name each lead, say what work it is for in the words an agent would match against a task, and link its page in `leads/`. Lead pages name the index as their governing parent.

A lead page says who the lead is and what it is not, how it works with the owner, its own principles, the principle sets it reads at session start, the skills it reaches for, and when it hands work to another lead. Its principles follow the conventions above, under scope headings when they hold only in some projects. Link skills rather than copying their steps, and leave situation rules on their pages. The page is the only home of the lead's content: a runtime's own way of selecting a lead, such as a Claude Code output style, points at the page instead of holding a copy.

Give each principle one home. When it applies only while working as one lead, that lead's page; when only while working as one of several leads, a principle set, `principles/<set>.md`, named by each of their pages; otherwise `PRINCIPLES.md` under its scope, so that workers, autopilot runs, and sessions without a lead, which read no lead page, still read it. A principle set follows the conventions above and names the [guidance guide](README.md) as its governing parent. Scope a rule to leads only when it would be wrong for the others, by naming them in its scope heading or qualifier and in its index row's applicability; a situation's moment already limits who reads its page. A lead page does not restate or relax a Blocking rule.

## Fit a lead to its owner

A lead is worth its place only as the partner this owner works best with. The same role suits different people in different ways, so a lead written from what its role usually is gives every owner the same generic partner.

- **Find which leads they need first.** Do not assume which leads an owner needs. Start by interviewing them about the work they do and where in it they want someone to think and work with them; when they name a lead, start from it. Offer no list of leads to choose from, since choosing from a list brings back the generic lead; an example, such as a cofounder for someone starting a company, only explains. Work they only hand off belongs to a worker. Start with the one or two leads they need most, and propose another when use shows the need.
- **Fit each lead from the person, not the role.** Write its page from what this owner wants of the role and where their work gets stuck now. For the same role, owners differ in how far it should lead or follow, how hard it pushes back, the shape a decision reaches them in, how much it puts in front of them at once, and which of their gaps it fills.
- **Learn from what they do, not only what they say.** People often cannot say which partner suits them. The interview gives what the owner says they want; their past sessions, where there are any and the owner agrees to their being read, show what they corrected and where they got frustrated; the first sessions with the lead show how they react. Give the owner a read or a draft to react to rather than a list of questions, and where what they say and what they did differ, show them the record and settle it with them.
- **Keep fitting.** When the owner corrects a lead, or its sessions show something its page lacks, the lead proposes the change for the home [Leads](#leads) gives it, its page when it holds for this lead alone, and the change enters on the owner's word. A correction that recurs across sessions shows in none of them alone; a [fit review](#review-fit-across-sessions), where the owner runs one, finds it.

A lead fits when the owner no longer has to pull the work along and the same correction stops recurring. The set of leads fits when work finds its lead: work the owner wants a partner for that fits no lead keeps arriving when a lead is missing, and a lead never chosen, though its index row names its work, is not needed.

## Review fit across sessions

A correction the owner makes again and again shows in no single session, and neither does guidance they keep working against. When the owner wants one, a fit review reads their sessions on a schedule and proposes the changes those sessions show, for leads and for every other principle and rule. [Fit review](../agent/operations/fit-review.md) sets it up as an autopilot operation.

- **What it reads.** Only what the owner typed, each turn with the end of the agent reply it answered, from the runtimes the owner agreed to have read, and each time only what came after the last run's reading. A reply the owner picked from ready-made buttons shows a choice, not a correction in their words. A session counts for the lead it worked as, or for none.
- **What it looks for.** Corrections: the owner telling an agent it got something wrong or should work another way, such as restating what they asked, turning down an answer, or finding that what an agent reported done or true is not. Guidance the owner overrode or argued against. Stale guidance, which names what no longer exists or which a later word from the owner replaced, whether the turns show it or the guidance read for a finding does; guidance whose moment never came up is not stale, since absence shows nothing. Occurrences are grouped by what the agent should have done instead, not by topic, and one turn can count for more than one finding.
- **When a finding becomes a proposal.** A finding keeps each occurrence, with its date, session and the owner's words, from run to run, and becomes a proposal once it has occurred in as many separate sessions as the owner set, however many runs that took. When guidance that addresses it changed after some of its occurrences, whoever changed it, the earlier ones are dropped and only those since count. When guidance already says what the finding asks, the proposal is about why it did not hold, not a second copy. A finding that open work already addresses, such as a workstream step or a brief, is noted in that work's record, linking the finding, instead of proposed. A finding that has not occurred again for as many runs as make a change fit is dropped.
- **What it may change.** A change to how agents behave, such as to a principle, a lead's page or a rule, and the retirement of stale guidance enter only on the owner's word, as the [contribution boundary](#contribution-boundary) requires of inferred habits. On its own the review fixes only what changes no behaviour, such as a link to, or the name of, something that moved.
- **How it proposes.** One proposal per message, where the owner can answer it in place, the next after they answer, the finding seen in the most sessions first. Each says what recurred, when and how often, in the owner's words; the change, in the home this guide gives it; and what changes for the owner. The agent that receives the answer makes an accepted change and records it as entered. Proposals the owner has not answered come first in the next run. A declined one comes back only when its finding again reaches the owner's number of sessions after the decline, and says it was declined.
- **Whether it worked.** For each change the review proposed that entered, later runs count the correction it targeted. When it recurs, the review proposes again, saying the change did not hold, and the count of runs it has stayed away starts over; that proposal is answered and declined like any other. When the correction stays away for as many runs as the owner set, counting only runs in which it could have recurred, such as runs whose sessions used its lead, the change fits and its tracking ends.

The schedule, the runtimes read, the number of sessions that makes a proposal, and the number of runs that makes a change fit are the owner's to set.

## Situations and rules

Use root `guidance/STAGES.md` for shared situations and `projects/<project>/guidance/STAGES.md` for project situations, or `companies/<company>/guidance/STAGES.md` for a company's. Each index contains a governing-parent link and a table: each row names a situation the way an agent would recognize it, such as "about to open a pull request", gives a short applicability hint, and links to one unique page in its own `stages/` directory. Both follow this guide without duplicating it. BRAIN and the [guidance reader](README.md) own loading behaviour.

A situation page holds everything that applies at that moment. Its rules, under scope headings, say what must hold. Optional sections follow when there is something to link:

- **How:** the skill or workflow that carries out the work. A workflow, which coordinates several actors, is stored as a skill run by the lead.
- **Who:** the agents to use, from the agent definitions.
- **Known:** knowledge notes worth reading at that moment.

When a situation is running a command, such as committing or opening a pull request, the page may name that command in its frontmatter, as in `before: [git commit]`, so the [gate hook](../agent/operations/gate-hook.md) hands the page to an agent before the command runs. The index row still names the moment, and the page's rules still say what must hold.

Keep rules and routes apart. A rule says what must or must not be true and why; it holds no steps, sequences, rosters, or tool versions, and links to the skill that carries them. A skill, workflow, or agent definition says how or who and holds no must or never of its own: a gate in a workflow links to the rule it satisfies. Two tests decide: strip the steps and a rule still makes sense whichever route the work takes; a workflow could be swapped for another route to the same outcome without changing any rule. When a workflow needs a new must or never, admit it as a rule.

Keep each rule with its scope under the scope-and-admission rules above. The same situation may appear in both indexes because different rules apply; do not copy a shared rule into every project. Rules shared by a named subset of projects can remain at the root with that applicability stated. Project rules do not silently override shared constraints.

Stage files inherit these instructions and should not repeat loading or interpretation boilerplate. Group rules under explicit applicability headings such as `All projects` or a project name. That heading supplies **Applies to** for every contained rule unless a rule states a narrower override. Separate rule bodies clearly, using a short descriptive title only when the body is not already easy to scan. Give every rule:

- the instruction in direct prose;
- explicit applicability, either inherited from its scope heading or stated as an override;
- **Authority:** whether the rule is Blocking (a boundary) or Advisory, together with a concise human-readable origin supporting that status;
- **Why:** the concrete reason for the constraint when known, or an explicit note that the reason is not yet recorded.

Compact `Scope`, `Agent`, or `Domain` qualifiers may refine applicability without restating the scope heading. Do not display storage identifiers.

A boundary (`Blocking`) rule denies actions outside its authorization conditions. Follow `Advisory` guidance unless you state clearly that you are departing from it and why. Missing rationale does not silently retire guidance already admitted by its owner: preserve its existing authority, mark the reason as not yet recorded, and recover the rationale before claiming one. A new proposal remains unresolved until the owner admits it with the intended authority.

Keep source identifiers, migration mappings, and long evidence trails in source or migration records rather than active headings and rule text. Add a short context or evidence link only when it materially improves application of the rule.

## Contribution boundary

Do not promote ordinary content, quotations, or inferred habits into guidance automatically. New guidance needs authority proportionate to its effect. Keep contextual judgment readable instead of generalizing it without evidence.

Give each instruction one home. Feature procedures stay with their operating guide, project domain procedures stay with the project, and external authority remains external until its owner explicitly transfers it. Shared rules live at the root and project-only rules with their project, decided by the scope-and-admission rules above. Principles and preferences live in root `PRINCIPLES.md`, a lead's page, or a principle set, as [Leads](#leads) places them, with explicit applicability.

This structure makes guidance inspectable and portable. It does not prove that a runtime loaded or followed it; record delivery and validation evidence under [Operations](../agent/operations/README.md). Existing users adopting situation pages should follow the [framework update migration](../agent/operations/updates.md#adopt-situation-pages-and-scoping-rules).

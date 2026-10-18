# Chat assistants

**Governing parent:** [Operations guide](README.md).

Read before connecting a chat assistant, such as ChatGPT or Claude, to the brain through the personal repository on GitHub, or before relying on one that is connected. Local agents read the brain from disk through their startup instructions; a chat assistant has no local path, so it reaches the pushed repository through its GitHub connection.

## What a connected assistant can do

- **Read, and write where a setup allows.** Every connection reads the repository, so an assistant can follow BRAIN's routing to the guides, situation pages, knowledge, and skills it links. Both vendors document their built-in GitHub connection as reading only and send writing to their coding agents, Codex and Claude Code ([ChatGPT](https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt), [Claude](https://claude.com/docs/connectors/github)), but observed behaviour can differ, so [check](#verify) with a small commit. An assistant that can write keeps the brain's habits by committing to the repository; one that cannot hands you the text instead. A chat cannot run a skill's scripts.
- **Commits skip local checks.** A commit from a chat or a hosted coding agent goes straight to GitHub, and nothing checks it before it lands: [auto-sync](sync.md)'s credential check covers only what auto-sync commits itself. Only the pointers' last sentences and BRAIN's secrets rule ask the assistant to keep secrets out. When auto-sync is installed, live checkouts pull a commit on the branch they track within one interval, unless it conflicts with local work. Review what a chat or agent commits as you would any other writer's.
- **The pushed state only.** It sees what has reached GitHub: an edit arrives after it is committed and pushed, which [auto-sync](sync.md) does within one interval when installed. Content added to a Claude project stays as added until you sync it there.
- **No working directory.** BRAIN identifies the project from the task's names, the repository's remote, and the working directory. A chat has only the first, so name the project, or say the task is personal.
- **The whole repository.** GitHub grants access per repository, not per folder, so the service can read everything in it, including `personal/`. Check each service's data-use and model-training settings before connecting. Keep secrets outside the brain, as BRAIN requires.

## The pointer

Each app takes this text as standing instructions, with `<owner>/<repo>` replaced by the personal repository:

```text
My brain is the private GitHub repository <owner>/<repo>, which you reach through your GitHub connection. At the start of each chat, before acting on the first task, read BRAIN.md at the repository root and follow its guidance-loading instructions, resolving each link relative to the file that contains it. You have no working directory or repository remote, so identify the project only from what I name; if a task is project work and I have not named the project, ask which. If you cannot read BRAIN.md or a file it routes you to, say which instead of assuming its contents. When the brain says to record or change something, commit it to the main branch if your connection can write: read the file again just before changing it, make one change per commit with a message saying what changed and why, and tell me what you committed. If it cannot, or the commit fails, give me the file path and the exact text to add or replace instead. Never write a secret, credential, or government or financial identifier into the repository.
```

The same text serves a connection that can write and one that cannot: the first commits, the second hands you text to add yourself or give to a local agent. The steps below follow the vendors' help pages as of October 2026; menus change, so check the linked page when a step does not match.

## ChatGPT

1. **Connect GitHub.** In Settings, open **Plugins** and select **GitHub**. GitHub then asks you to install and authorize the ChatGPT app; select the personal repository only. A repository can take about five minutes to appear. ([Help](https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt))
2. **Add the pointer** where you will chat:
   - **Every ordinary chat:** on web and desktop, Settings → **Personalization**; on iOS and Android, Settings → **Customize ChatGPT**. Turn on **Enable customization** and paste the pointer into **Custom Instructions**. The field holds 1,500 characters on Free and Go and 5,000 on paid plans; the pointer is about 1,030. ([Help](https://help.openai.com/en/articles/8096356-chatgpt-custom-instructions))
   - **A project:** open the project's **•••** menu, select **Project settings**, and paste the pointer into its instructions. Project instructions replace Custom Instructions inside the project, so a project used for brain work needs its own copy. ([Help](https://help.openai.com/en/articles/10169521-projects-in-chatgpt))
3. **Start a new chat** after saving.

ChatGPT retrieves repository content on demand by searching the repository, without a synced index, and finds a file more reliably when given its path. If it answers without reading the brain, choose GitHub from the chat's **+** tools menu or name GitHub in the request. Depending on the plan, workspace, and product surface, GitHub may be available only in deep research or agent mode, not in standard chat.

## Claude

A Claude chat reads the brain; a Claude Code cloud session also writes to it. Both reach the repository through the GitHub connection of step 1.

For reading, use a private project. In an ordinary chat, Claude reads the repository only after you add it from that chat's **+** menu (**Add from GitHub**), each time, so a pointer in the account-wide **Instructions for Claude** (your initials → **Settings**) would have every other chat report that it cannot read `BRAIN.md`.

1. **Connect GitHub.** Open **Customize → Connectors**, select **GitHub Integration**, then **Connect**. When GitHub asks, grant the Claude GitHub App access to the personal repository only. ([Help](https://claude.com/docs/connectors/github))
2. **Create a project** at [claude.ai/projects](https://claude.ai/projects) with **+ New Project**, and keep it private: Claude allows GitHub content only in projects you have not shared. ([Help](https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects))
3. **Add the brain's files.** In the project knowledge panel, select **+ → GitHub**, pick the repository, and select `BRAIN.md`, `guidance/`, `projects/INDEX.md`, `projects/README.md`, `agent/work/`, `agent/knowledge/`, and the folders of the projects you will work on, or `personal/`. Then select **Add files**. A file left out looks the same as one that does not exist, so BRAIN's optional reads skip it silently.
4. **Add the pointer.** Select **Set project instructions**, paste the pointer with its first sentence replaced by `My brain is the private GitHub repository <owner>/<repo>; its files are in this project's knowledge.`, and select **Save instructions**.
5. **Sync after the brain changes.** Select **Sync now** on the repository in project knowledge; until then the project keeps the content as added.

Two limits of the chat integration are unsettled. The GitHub page says added content must fit within the context window, while the projects page says paid plans switch project knowledge to retrieval near that limit; which applies to GitHub content is not stated. Links between the brain's many `README.md` files resolve only if project knowledge keeps full paths, which [Verify](#verify) checks.

**To write,** use a Claude Code cloud session, which needs a paid plan: the chat integration reads file names and contents only and sends editing to Claude Code ([Help](https://claude.com/docs/connectors/github)), so a chat given the pointer hands you text. Start a session on the brain's repository from [claude.ai/code](https://claude.ai/code), the Claude app's **Code** tab, or the desktop app with **Cloud** selected. It clones the repository into a cloud machine and pushes through the Claude GitHub App from step 1, so the app must be installed on the repository ([Cloud sessions](https://code.claude.com/docs/en/web-quickstart)). Give it the pointer in [When a chat cannot write](#when-a-chat-cannot-write).

## Verify

Start a fresh chat and give a task governed by a situation page you know, without mentioning the brain. A working setup applies a rule that appears only on that page. Where the app shows sources or tool activity, it read `BRAIN.md` first, then the guidance guide; content preloaded in a Claude project may show no reads, so ask which file it read first and which it read next, by full path. An answer that misses the rule means the pointer or the access is missing. To check writing, ask it to record a test finding in an inbox, look for the commit on GitHub, then remove the entry; an assistant that cannot write gives you the line instead. For Claude, run the write check in a cloud session started as [Claude](#claude) describes, and look on the branch it pushed. Record the configuration and what you observed in your personal operations records; one observation establishes delivery, not consistent compliance.

## When a chat cannot write

To change the brain from a hosted service when the chat's connection cannot write, use a coding agent with write access to the repository, such as Codex or a Claude Code cloud session. These agents load their own instruction files from the repository root, such as `AGENTS.md` or `CLAUDE.md`, which a brain does not ship, so give the agent this pointer in its task or environment instructions; in Claude Code, that is the start of the task, or, where Claude Code projects are available (in beta), a project's instructions, which every new thread receives ([Projects](https://code.claude.com/docs/en/claude-projects)):

```text
Before your first task, read BRAIN.md at the root of this repository and follow its guidance-loading instructions. If you cannot read it, say so instead of assuming its guidance. Never write a secret, credential, or government or financial identifier into the repository.
```

Such an agent may push a branch of its own; a Claude Code cloud session does unless the task names another. Once its commits are on the branch the live checkouts track, [auto-sync](sync.md) brings them in, so ask it to push there or merge its branch, and review them as you would any other writer's.

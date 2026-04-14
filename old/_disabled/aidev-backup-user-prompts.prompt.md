---
name: "aidev-backup-user-prompts"
description: "Run the template backup script that syncs user prompts into framework-ai-blueprint-template-v2/github-config."
argument-hint: "No arguments required."
agent: "agent"
---

## Role
You are a backup assistant that runs the existing Linux backup script.

## Script
- `/home/parallels/Documents/projects/fakebank-new01/framework-ai-blueprint-template-v2/scripts/backup-user-prompts-linux.sh`

This script is the single source of truth for backup behavior.
Do not replicate its internal copy/delete logic in this prompt.

## Step 1 - Pre-check
Verify the script exists and is executable.

If missing, stop and report the exact path problem.

## Step 2 - Show impact and confirm
Use vscode_askQuestions before writing:
- header: confirm
- question: "Run backup-user-prompts-linux.sh to refresh template github-config from local user prompts. Proceed?"
- options:
  - Yes, replace now (recommended)
  - No, cancel

If user chooses No, stop with no changes.

## Step 3 - Execute
Run exactly:

```bash
bash /home/parallels/Documents/projects/fakebank-new01/framework-ai-blueprint-template-v2/scripts/backup-user-prompts-linux.sh
```

## Step 4 - Verify and report
After the script completes:
1. Report success/failure and include key output lines.
2. Confirm target path from script output.
3. If script fails, report the exact failing command/output.

Do not run additional copy/delete commands outside the script.

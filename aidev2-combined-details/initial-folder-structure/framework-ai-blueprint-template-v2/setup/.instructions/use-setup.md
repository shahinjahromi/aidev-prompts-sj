Use `setup/setup.sh` by default from the template repository to create a new app repo folder and specs repo folder.

If the prompt explicitly indicates using local user prompts, use `setup/setup-for-user-prompts.sh` instead.

Inputs to collect before running:
- App name: use kebab-case app slug such as `fakebank-customer-frontend-web`
- Implementation: provide the implementation suffix such as `angular`, `react`, or `nodejs`
- Base folder: an existing absolute workspace directory where the new folders will be created

Run (default):
```bash
./setup/setup.sh \
  --output-dir <base-folder> \
  --app-slug <app-name> \
  --impl-suffix <implementation>
```

Run (when prompt says to use local user prompts):
```bash
./setup/setup-for-user-prompts.sh \
  --output-dir <base-folder> \
  --app-slug <app-name> \
  --impl-suffix <implementation>
```

Behavior:
- The blueprint/specs repo folder is created as `<base-folder>/<app-name>-ai-blueprint`
- The app repo folder is created as `<base-folder>/<app-name>-<implementation>`
- The final implementation ID is always `<app-name>-<implementation>`

If the user already knows custom folder names, optionally add:
- `--specs-repo-dir <custom-blueprint-folder>`
- `--app-repo-dir <custom-app-folder>`

Do not run the script if either destination folder already exists.

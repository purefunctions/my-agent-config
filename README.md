# Common Agent Configuration

This repository contains shared skills and setup scripts for AI agents. It is designed to be used as a submodule within your project's agent configuration.

## Installation

1.  **Initialize User Config**: Even if you do not plan to use a remote for your personal configuration, you must initialize a local git repository in your project's user config directory so that this repository can be managed as a nested submodule:
    ```bash
    cd .agent-config/user
    git init
    ```

2.  **Add Submodule**: Add this repository as a submodule to your user agent config:
    ```bash
    git submodule add git@github.com:purefunctions/my-agent-config.git common
    ```

## Usage

Run the setup script located in the `common/` directory to wire skills into your tools:

```bash
# From the user config directory (.agent-config/user/)
python common/setup.py install
```

### Command Reference
- **`python common/setup.py install`**: 
  Updates symlinks based on the current state of local files. Use this for initial setup or after adding new project-specific skills to `../skills/`.
- **`python common/setup.py update`**: 
  Attempts to sync with the latest remote changes for both your user configuration and this submodule before re-linking.

## Git Operations

### Syncing Shared Skills
To pull the latest shared skills from the remote repository:
```bash
# From the user config directory (.agent-config/user/)
git submodule update --remote --recursive common
```

### Contributing Changes
If you modify skills inside this submodule and want to share them:
1. Commit and push your changes inside the `common/` directory.
2. Update the submodule reference in your parent `.agent-config/user` repository.

## Features

### Smart Overrides
The setup script detects when you have a project-specific skill (in `../skills/`) with the same name as a common skill.
- It will **prompt you interactively** to choose which version to install.
- This allows you to keep both versions in your repositories while choosing the implementation that fits your current project best.

### Generic Skills
Skills like `do-validation`, `do-code-review`, and `do-prime` are generic. They rely on your project's `AGENTS.md` file for context-specific commands and structure.

**Required `AGENTS.md` Sections:**

1.  **Project Structure**: Defines scopes for `do-prime`.
    ```markdown
    # Project Structure
    - **cli**: `packages/cli`
    - **server**: `src/server`
    ```

2.  **Validation Commands**: Defines commands for `do-validation` and `do-code-review`.
    ```markdown
    # Validation Commands
    ## Per-File Commands
    - **Format File**: `cargo fmt -- <file>`
    
    ## Project-Wide Commands
    - **Full Test Suite**: `cargo test`

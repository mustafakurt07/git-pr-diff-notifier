# 📨 git-pr-diff-notifier

A lightweight script that sends HTML email notifications summarizing file changes in pull requests — ideal for team reviews and CI/CD pipelines.

---

## 🚀 Features

- 📂 Detects changes in specific file types or folders
- 🧑‍💻 Uses `git blame` to show who changed which line
- 📧 Sends styled HTML email with added/removed lines
- 🔗 Automatically includes PR link, commit message, and file-level diffs
- 🔒 Environment-variable based configuration (no secrets hardcoded)

---

## 📦 Use Case

Ideal for teams who want to:

- Review sensitive config/code files via email before merging
- Track changes in infrastructure, build, or dependency files
- Use inside CI/CD pipelines (e.g. Azure DevOps, GitHub Actions)

---

## ⚙️ Configuration

Set the following environment variables before running the script:

| Variable Name              | Description                                |
|---------------------------|--------------------------------------------|
| `SMTPSERVER`              | SMTP server address (e.g., `smtp.mail.com`)|
| `SMTPPORT`                | SMTP port (e.g., `587`)                     |
| `BUILD_REPOSITORY_LOCALPATH` | Local path of the cloned repo             |
| `SYSTEM_PULLREQUEST_TARGETBRANCH` | Base branch (e.g., `main`, `develop`)|
| `SYSTEM_PULLREQUEST_SOURCEBRANCH` | Source branch (e.g., `feature/xyz`) |
| `BUILD_SOURCEVERSION`     | Commit hash                                |
| `SYSTEM_PULLREQUEST_PULLREQUESTID` | PR ID (for link building)         |
| `SYSTEM_COLLECTIONURI`    | Base URL of your project management tool   |
| `SYSTEM_TEAMPROJECT`      | Project name                               |
| `BUILD_REPOSITORY_NAME`   | Git repository name                        |
| `SYSTEM_PULLREQUEST_TITLE`| PR title                                   |

---

## 🛠️ Running the Script

### From CLI:

\`\`\`bash
python3 pr_diff_notifier.py "kts,gradle,pro,toml"
\`\`\`

> If no extensions are provided, it defaults to: \`toml,kts,gradle,pro\`.

### Inside CI/CD:

Integrate it as a script step, making sure environment variables are set via your pipeline tool (e.g. Azure DevOps, GitHub Actions, Jenkins).

---

## 📬 Email Output Sample

- ✅ Styled HTML  
- ✅ Shows added (🟢) and removed (🔴) lines  
- ✅ Shows line number and author  
- ✅ Organized per file

---

## 🧪 Dependencies

- Python 3.6+  
- `git` CLI must be available  
- Python standard libraries: `smtplib`, `email`, `subprocess`, `re`, `os`, `sys`

---

## 👨‍💻 Author

Created by [Kurt](https://github.com/your-username) — Developer @ QNB

---

## 📄 License

MIT — Feel free to fork, adapt and use in your own team pipelines.

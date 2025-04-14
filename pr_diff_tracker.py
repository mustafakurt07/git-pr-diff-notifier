import os
import sys
import smtplib
import subprocess
import re

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration (Replace with your SMTP and team emails)
SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_PORT = os.environ.get("SMTP_PORT")
EMAIL_USER = os.environ.get("EMAIL_USER")
TEAM_EMAIL = os.environ.get("TEAM_EMAIL")

REPO_DIR = os.getenv('BUILD_REPOSITORY_LOCALPATH')
DEFAULT_EXTENSION = "toml,kts,gradle,pro"
CONFIGURATION_TEAM = os.getenv("CONFIG_REVIEW_TEAM", TEAM_EMAIL)


def get_changed_lines(file_path, base_commit, target_commit):
    try:
        diff = subprocess.check_output(
            f'git diff --unified=0 {base_commit}..{target_commit} -- "{file_path}"',
            shell=True
        ).decode('utf-8')

        if not diff.strip():
            return None

        changed_lines = []
        old_line_num = 0
        new_line_num = 0

        for line in diff.split('\n'):
            if line.startswith('@@'):
                match = re.search(r'@@ \-(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
                if match:
                    old_line_num = int(match.group(1))
                    new_line_num = int(match.group(2))
                continue
            if line.startswith('--- ') or line.startswith('+++ '):
                continue

            author = get_author(file_path, new_line_num)

            if line.startswith('-'):
                changed_lines.append(
                    f'<span style="color: red;">🔴 Line {old_line_num} Deleted by {author}:</span> '
                    f'<span style="color: black;">{line[1:]}</span>'
                )
                old_line_num += 1
            elif line.startswith('+'):
                changed_lines.append(
                    f'<span style="color: green;">🟢 Line {new_line_num} Added by {author}:</span> '
                    f'<span style="color: black;">{line[1:]}</span>'
                )
                new_line_num += 1
            elif line.startswith(' '):
                old_line_num += 1
                new_line_num += 1

        return '<br>'.join(changed_lines) if changed_lines else ""

    except subprocess.CalledProcessError as e:
        print(f"Git error ({file_path}): {e.output.decode()}")
        return "Diff failed"
    except Exception as e:
        print(f"Unexpected error ({file_path}): {str(e)}")
        return "Error occurred"


def get_author(file_path, line_number):
    try:
        output = subprocess.check_output(
            f'git blame -L {line_number},{line_number} --porcelain -- "{file_path}" | grep "^author "',
            shell=True
        ).decode('utf-8').strip()
        return output.replace("author ", "") if output else "Unknown"
    except subprocess.CalledProcessError:
        return "Unknown"


def get_changed_files(extensions, base_branch, current_branch):
    try:
        files = subprocess.check_output([
            'git', 'diff', '--name-only', '--diff-filter=MARC',
            f'origin/{base_branch}...origin/{current_branch}'
        ]).decode('utf-8').splitlines()

        valid_files = []
        for f in files:
            if any(f.endswith(ext) for ext in extensions) or "build-logic" in f:
                diff_output = subprocess.check_output([
                    'git', 'diff', f'origin/{base_branch}...origin/{current_branch}', '--', f
                ]).decode('utf-8').strip()

                is_same = subprocess.run(
                    f'git diff --quiet origin/{base_branch}..origin/{current_branch} -- "{f}"',
                    shell=True
                ).returncode == 0

                if diff_output and not is_same:
                    valid_files.append(f)

        return valid_files
    except Exception as e:
        print(f"Error: {str(e)}")
        return []


def get_commit_messages(base_branch, current_branch):
    try:
        messages = subprocess.check_output([
            'git', 'log', '--pretty=format:%s',
            f'origin/{base_branch}..origin/{current_branch}'
        ]).decode('utf-8').splitlines()
        return messages[0] if messages else "No commit message found"
    except Exception as e:
        print(f"Failed to get commit messages: {str(e)}")
        return "Error occurred"


def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = CONFIGURATION_TEAM
    msg['Subject'] = subject
    msg['Cc'] = TEAM_EMAIL

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


def main():
    extensions = (
        [ext.strip() for ext in sys.argv[1].split(',')] if len(sys.argv) >= 2
        else DEFAULT_EXTENSION.split(',')
    )

    base_branch = os.getenv('SYSTEM_PULLREQUEST_TARGETBRANCH', 'development').replace('refs/heads/', '')
    current_branch = os.getenv('SYSTEM_PULLREQUEST_SOURCEBRANCH', 'HEAD').replace('refs/heads/', '')
    commit_hash = os.getenv('BUILD_SOURCEVERSION')
    organization = os.getenv('SYSTEM_COLLECTIONURI', '').rstrip('/').split('/')[-1]
    project = os.getenv('SYSTEM_TEAMPROJECT', '')
    repo_name = os.getenv('BUILD_REPOSITORY_NAME', '')
    pr_id = os.getenv('SYSTEM_PULLREQUEST_PULLREQUESTID', '')
    pr_title = os.getenv('SYSTEM_PULLREQUEST_TITLE', current_branch)

    if not commit_hash or not REPO_DIR:
        print("Missing required environment variables.")
        sys.exit(1)

    os.chdir(REPO_DIR)

    changed_files = get_changed_files(extensions, base_branch, current_branch)
    if not changed_files:
        print("No relevant file changes found.")
        sys.exit(0)

    commit_message = get_commit_messages(base_branch, current_branch)
    pr_link = f"https://your-pr-system.com/{organization}/{project}/_git/{repo_name}/pullrequest/{pr_id}" if pr_id else "PR link not found"

    email_body = f"""
    <html><body>
    <p><b>Pull Request Detected</b></p>
    <p><b>Title:</b> {pr_title}</p>
    <p><b>Base Branch:</b> {base_branch}</p>
    <p><b>Commit Message:</b> {commit_message}</p>
    <p><b>Link:</b> <a href="{pr_link}">{pr_link}</a></p>
    <hr>
    <b>Changed Files:</b><ul>
    """

    has_changes = False
    for file in changed_files:
        changes = get_changed_lines(file, f'origin/{base_branch}', commit_hash)
        if changes:
            email_body += f"<li><b>{file}</b><br>{changes}</li>"
            has_changes = True

    email_body += "</ul><p>Best regards,<br>Your CI Bot</p></body></html>"

    if has_changes:
        send_email(f"[PR] {base_branch} - Changes in {pr_title}", email_body)
    else:
        print("No changes in specified file types, no email sent.")


if __name__ == "__main__":
    main()

import json
import re
import urllib.request
from datetime import datetime

USERNAME = "mzafram2001"
PROFILE_REPO = "mzafram2001"


def get_public_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?type=owner&sort=updated&per_page=100"
    req = urllib.request.Request(
        url, headers={"User-Agent": "Python-GitHub-Readme-Updater"}
    )

    with urllib.request.urlopen(req) as response:
        repos = json.loads(response.read().decode())

    projects = []
    for repo in repos:
        if repo["fork"] or repo["private"] or repo["name"].lower() == PROFILE_REPO.lower():
            continue

        name = repo["name"]
        html_url = repo["html_url"]
        description = repo["description"] or "No description provided."
        language = f"`{repo['language']}`" if repo["language"] else "`N/A`"

        pushed_at_raw = repo["pushed_at"]
        last_updated = datetime.strptime(
            pushed_at_raw, "%Y-%m-%dT%H:%M:%SZ"
        ).strftime("%Y-%m-%d")

        projects.append(
            {
                "name": name,
                "url": html_url,
                "description": description,
                "stack": language,
                "last_updated": last_updated,
            }
        )

    projects.sort(key=lambda x: x["last_updated"], reverse=True)
    return projects


def generate_markdown_table(projects):
    table = [
        "| Project | Description | Stack | Last updated |",
        "| :--- | :--- | :--- | :--- |",
    ]

    for p in projects:
        row = f"| **[{p['name']}]({p['url']})** | {p['description']} | {p['stack']} | {p['last_updated']} |"
        table.append(row)

    return "\n".join(table)


def update_readme():
    projects = get_public_repos()
    markdown_table = generate_markdown_table(projects)

    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    # 1. Actualizar la tabla de proyectos
    projects_pattern = r"(<!-- PROJECTS_START -->)(.*?)(<!-- PROJECTS_END -->)"
    if re.search(projects_pattern, readme, flags=re.DOTALL):
        readme = re.sub(projects_pattern, f"\\1\n{markdown_table}\n\\3", readme, flags=re.DOTALL)

    # 2. Actualizar la fecha de última revisión ("Last checked")
    today_str = datetime.now().strftime("%Y-%m-%d")
    checked_pattern = r"(<!-- LAST_CHECKED_START -->)(.*?)(<!-- LAST_CHECKED_END -->)"
    if re.search(checked_pattern, readme, flags=re.DOTALL):
        readme = re.sub(checked_pattern, f"\\1Last checked: {today_str}\\3", readme, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"Profile README updated successfully with date {today_str}!")


if __name__ == "__main__":
    update_readme()

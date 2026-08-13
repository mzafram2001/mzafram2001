import json
import re
import urllib.request
from datetime import datetime

USERNAME = "mzafram2001"
PROFILE_REPO = "mzafram2001"  # Repositorio a ignorar


def get_public_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?type=owner&sort=updated&per_page=100"
    req = urllib.request.Request(
        url, headers={"User-Agent": "Python-GitHub-Readme-Updater"}
    )

    with urllib.request.urlopen(req) as response:
        repos = json.loads(response.read().decode())

    projects = []
    for repo in repos:
        # Ignorar repositorios que sean forks, privados o el propio repo de perfil
        if repo["fork"] or repo["private"] or repo["name"].lower() == PROFILE_REPO.lower():
            continue

        name = repo["name"]
        html_url = repo["html_url"]
        description = repo["description"] or "No description provided."
        language = f"`{repo['language']}`" if repo["language"] else "`N/A`"

        # Extraer la fecha del último commit/push (formato ISO 8601: YYYY-MM-DDTHH:MM:SSZ)
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

    # Ordenar por fecha de última actualización (los más recientes primero)
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

    # Reemplazar el texto entre los marcadores <!-- PROJECTS_START --> y <!-- PROJECTS_END -->
    pattern = r"(<!-- PROJECTS_START -->)(.*?)(<!-- PROJECTS_END -->)"
    replacement = f"\\1\n{markdown_table}\n\\3"
    updated_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated_readme)


if __name__ == "__main__":
    update_readme()

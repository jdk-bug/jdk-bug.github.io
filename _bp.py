import subprocess, re, json, os
from datetime import datetime, timezone

repos_dir = "/home/ubuntu/.zeroclaw/workspace/repos"
owner = "jdk-bug"
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

branches_seen = 0
prs_opened = 0
pins_reconciled = 0
skipped_no_issue = 0
skipped_ahead_zero = 0
pins_to_store = []

for repo in ["my-zeroclaw", "html5-skateboard-game", "jdk-bug.github.io"]:
    d = os.path.join(repos_dir, repo)
    if not os.path.isdir(d):
        continue
    subprocess.run(["git", "-C", d, "fetch", "--prune", "origin"], capture_output=True)
    r = subprocess.run(["git", "-C", d, "rev-parse", "--abbrev-ref", "origin/HEAD"], capture_output=True, text=True)
    default = r.stdout.strip().replace("origin/", "") if r.returncode == 0 else "main"
    r = subprocess.run(["git", "-C", d, "for-each-ref", "--format=%(refname:short)", "refs/heads/"], capture_output=True, text=True)
    for branch in r.stdout.strip().split("\n"):
        if not branch or branch in ("main", "master", "develop", "trunk"):
            continue
        branches_seen += 1
        m = re.match(r"^feat/(GH-|issue-)(\d+)", branch)
        if not m:
            skipped_no_issue += 1
            continue
        issue_num = m.group(2)
        r2 = subprocess.run(["git", "-C", d, "rev-list", "--count", f"origin/{default}..{branch}"], capture_output=True, text=True)
        ahead = int(r2.stdout.strip() or 0)
        if ahead == 0:
            skipped_ahead_zero += 1
            continue
        r3 = subprocess.run(["gh", "pr", "list", "--repo", f"{owner}/{repo}", "--search", f"#{issue_num} in:body", "--state", "all", "--json", "number,headRefName,state,url"], capture_output=True, text=True)
        try:
            existing = json.loads(r3.stdout) if r3.stdout.strip() else []
        except:
            existing = []
        if existing:
            open_prs = [p for p in existing if p["state"] == "OPEN"]
            chosen = open_prs[0] if open_prs else existing[0]
            pr_number = chosen["number"]
            pr_state = chosen["state"]
            pr_url = chosen["url"]
            pins_reconciled += 1
            pins_to_store.append({"key": f"pr:{repo}#{issue_num}", "val": f"repo={owner}/{repo} number={issue_num} pr_number={pr_number} pr_state={pr_state} pr_url={pr_url} reconciled=true source=publish-v2"})
            print(f"RECONCILE: {repo} issue #{issue_num} -> PR #{pr_number} ({pr_state})")
            continue
        r4 = subprocess.run(["gh", "issue", "view", "--repo", f"{owner}/{repo}", issue_num, "--json", "title"], capture_output=True, text=True)
        try:
            issue_title = json.loads(r4.stdout)["title"]
        except:
            issue_title = f"Issue #{issue_num}"
        r5 = subprocess.run(["git", "-C", d, "push", "-u", "origin", branch], capture_output=True, text=True)
        if r5.returncode != 0:
            print(f"PUSH FAILED: {repo}/{branch}: {r5.stderr}")
            continue
        r6 = subprocess.run(["gh", "pr", "create", "--repo", f"{owner}/{repo}", "--head", branch, "--base", default, "--title", issue_title, "--body", f"Closes #{issue_num}"], capture_output=True, text=True)
        if r6.returncode != 0:
            print(f"PR CREATE FAILED: {repo}/{branch}: {r6.stderr}")
            continue
        pr_url = r6.stdout.strip()
        pm = re.search(r"#(\d+)", pr_url)
        pr_num = pm.group(1) if pm else "?"
        prs_opened += 1
        pins_to_store.append({"key": f"pr:{repo}#{issue_num}", "val": f"repo={owner}/{repo} number={issue_num} pr_number={pr_num} pr_url={pr_url} published_at={now}"})
        print(f"PR OPENED: {repo} issue #{issue_num} -> PR #{pr_num} ({pr_url})")
        r7 = subprocess.run(["gh", "pr", "merge", "--auto", "--squash", "--repo", f"{owner}/{repo}", str(pr_num)], capture_output=True, text=True)
        if r7.returncode != 0:
            print(f"AUTO-MERGE FAILED (non-fatal): PR #{pr_num}")

print(f"BRANCHES_SEEN={branches_seen}")
print(f"PRS_OPENED={prs_opened}")
print(f"PINS_RECONCILED={pins_reconciled}")
print(f"SKIPPED_NO_ISSUE={skipped_no_issue}")
print(f"SKIPPED_AHEAD_ZERO={skipped_ahead_zero}")
for p in pins_to_store:
    print(f"PIN_STORE:{p['key']}={p['val']}")

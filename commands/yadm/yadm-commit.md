---
name: yadm-commit
description: "Analyzes yadm (dotfiles) changes, stages modified files, and generates
a conventional commit message, then commits."
---

<task>Generate a conventional commit message for yadm (dotfiles) based on the provided state delta.</task>

!{
if ! command -v yadm > /dev/null 2>&1; then
    echo "<error>yadm command not found.</error>"
    exit 1
fi

if ! yadm rev-parse --git-dir > /dev/null 2>&1; then
    echo "<error>yadm is not initialized.</error>"
    exit 1
fi

if ! yadm diff --cached --quiet || ! yadm diff --quiet; then
    echo "<state_delta>"

    echo -n "Changes since last commit: ["
    yadm diff --cached --numstat > /tmp/yadm_stats_$$ 2>/dev/null
    if [ -s /tmp/yadm_stats_$$ ]; then
        awk '{printf "%s (+%s/-%s), ", $3, $1, $2}' /tmp/yadm_stats_$$ | sed 's/, $//'
    else
        yadm diff --numstat | awk '{printf "%s (+%s/-%s), ", $3, $1, $2}' | sed 's/, $//'
    fi
    rm -f /tmp/yadm_stats_$$
    echo "]."

    echo "Prior commit: $(yadm log -1 --format="%h %s" 2>/dev/null || echo 'None')"

    echo "<detailed_diff_stat>"
    yadm diff --cached --stat
    yadm diff --stat
    echo "</detailed_diff_stat>"
    echo "</state_delta>"
else
    echo "<error>No changes to commit.</error>"
    exit 0
fi
}

<rules>
Enforce conventional commit syntax: type(scope?): subject
Scope MUST be the application or config module affected (e.g., zsh, vim, ssh, pipewire).
Ban conversational padding, marketing language, politeness, and markdown wrappers.
Return only the commit message string.
</rules>

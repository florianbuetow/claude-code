# =============================================================================
# Justfile Rules (follow these when editing justfile):
#
# 1. Use printf (not echo) to print colors — some terminals won't render
#    colors with echo.
#
# 2. Always add an empty `@echo ""` line before and after each target's
#    command block.
#
# 3. Always add new targets to the help section and update it when targets
#    are added, modified or removed.
#
# 4. Target ordering in help (and in this file) matters:
#    - Setup targets first (init, setup, install, etc.)
#    - Start/stop/run targets next
#    - Code generation / data tooling targets next
#    - Checks, linting, and tests next (ordered fastest to slowest)
#    Group related targets together and separate groups with an empty
#    `@echo ""` line in the help output.
#
# 5. Composite targets (e.g. ci) that call multiple sub-targets must fail
#    fast: exit 1 on the first error. Never skip over errors or warnings.
#    Use `set -e` or `&&` chaining to ensure immediate abort with the
#    appropriate error message.
#
# 6. Every target must end with a clear short status message:
#    - On success: green (\033[32m) message confirming completion.
#      E.g. printf "\033[32m✓ init completed successfully\033[0m\n"
#    - On failure: red (\033[31m) message indicating what failed, then exit 1.
#      E.g. printf "\033[31m✗ ci failed: tests exited with errors\033[0m\n"
# 7. Targets must be shown in groups separated by empty newlines in the help section.
#    - init/destroy/clean/help on top, ci and other tests on the bottom, between other groups
# =============================================================================

marketplace_name := "florianbuetow-plugins"
marketplace_source := "florianbuetow/claude-code"

# Default recipe: show available commands
_default:
    @just help

# Show help information
help:
    @echo ""
    @clear
    @echo ""
    @printf "\033[0;34m=== claude-code ===\033[0m\n"
    @echo ""
    @printf "\033[0;33mSetup & Lifecycle:\033[0m\n"
    @printf "  %-38s %s\n" "install" "Add marketplace and install all plugins"
    @printf "  %-38s %s\n" "uninstall <plugin>" "Uninstall a plugin by name"
    @printf "  %-38s %s\n" "update" "Update marketplace and all installed plugins"
    @printf "  %-38s %s\n" "help" "Show this help information"
    @echo ""
    @printf "\033[0;33mInfo & Diagnostics:\033[0m\n"
    @printf "  %-38s %s\n" "status" "Show installed vs repo plugin versions"
    @printf "  %-38s %s\n" "validate" "Validate plugin and marketplace manifests"
    @echo ""

# Add marketplace and install all plugins
install:
    #!/usr/bin/env bash
    set -e
    echo ""
    printf "\033[0;34m=== Installing Marketplace & Plugins ===\033[0m\n"
    echo ""
    printf "Adding marketplace {{marketplace_source}}...\n"
    claude plugin marketplace add {{marketplace_source}} 2>&1
    echo ""
    printf "Installing plugins...\n"
    installed_list=$(claude plugin list 2>&1)
    for plugin in $(jq -r '.plugins[].name' .claude-plugin/marketplace.json); do
        if echo "$installed_list" | grep -q "❯ ${plugin}@{{marketplace_name}}"; then
            printf "  Skipping %s (already installed)\n" "$plugin"
        else
            printf "  Installing %s...\n" "$plugin"
            claude plugin install "$plugin@{{marketplace_name}}" --scope user 2>&1
        fi
    done
    echo ""
    printf "\033[32m✓ Install completed — restart Claude Code to pick up new plugins\033[0m\n"
    echo ""

# Uninstall a plugin by name
uninstall plugin:
    #!/usr/bin/env bash
    set -e
    echo ""
    printf "\033[0;34m=== Uninstalling Plugin ===\033[0m\n"
    echo ""
    printf "Uninstalling {{plugin}}...\n"
    claude plugin uninstall "{{plugin}}@{{marketplace_name}}" --scope user 2>&1
    echo ""
    printf "\033[32m✓ Uninstall completed — restart Claude Code to pick up changes\033[0m\n"
    echo ""

# Update marketplace and all installed plugins to latest versions
update:
    #!/usr/bin/env bash
    set -e
    echo ""
    printf "\033[0;34m=== Updating Marketplace & Plugins ===\033[0m\n"
    echo ""
    printf "Updating marketplace {{marketplace_name}}...\n"
    claude plugin marketplace update {{marketplace_name}} 2>&1
    echo ""
    printf "Updating plugins...\n"
    installed_list=$(claude plugin list 2>&1)
    for plugin in $(jq -r '.plugins[].name' .claude-plugin/marketplace.json); do
        if echo "$installed_list" | grep -q "❯ ${plugin}@{{marketplace_name}}"; then
            printf "  Updating %s...\n" "$plugin"
            claude plugin update "$plugin@{{marketplace_name}}" --scope user 2>&1
        else
            printf "  Installing %s (not yet installed)...\n" "$plugin"
            claude plugin install "$plugin@{{marketplace_name}}" --scope user 2>&1
        fi
    done
    echo ""
    printf "\033[32m✓ Update completed — restart Claude Code to pick up changes\033[0m\n"
    echo ""

# Show installed vs repo plugin versions (green = match, red = mismatch)
status:
    #!/usr/bin/env bash
    echo ""
    printf "\033[0;34m=== Plugin Version Status ===\033[0m\n"
    echo ""
    printf "  %-25s %-15s %-15s %s\n" "PLUGIN" "REPO" "INSTALLED" "STATUS"
    printf "  %-25s %-15s %-15s %s\n" "------" "----" "---------" "------"
    installed_list=$(claude plugin list 2>&1)
    jq -r '.plugins[] | "\(.name) \(.version)"' .claude-plugin/marketplace.json | while read -r name repo_version; do
        install_count=$(echo "$installed_list" \
            | grep -c "❯ ${name}@{{marketplace_name}}" || true)
        installed_version=$(echo "$installed_list" \
            | grep -A3 "❯ ${name}@{{marketplace_name}}" \
            | grep "Version:" \
            | head -1 \
            | sed 's/.*Version: //' \
            | tr -d '[:space:]')
        if [ "$install_count" -gt 1 ]; then
            printf "  %-25s %-15s \033[31m%-15s %s\033[0m\n" "$name" "$repo_version" "$installed_version" "✗ duplicate installs ($install_count)"
        elif [ -z "$installed_version" ]; then
            printf "  %-25s %-15s %-15s \033[31m%s\033[0m\n" "$name" "$repo_version" "—" "not installed"
        elif [ "$installed_version" = "$repo_version" ]; then
            printf "  %-25s %-15s \033[32m%-15s %s\033[0m\n" "$name" "$repo_version" "$installed_version" "✓ match"
        else
            printf "  %-25s %-15s \033[31m%-15s %s\033[0m\n" "$name" "$repo_version" "$installed_version" "✗ mismatch"
        fi
    done
    echo ""
    printf "\033[32m✓ Info completed\033[0m\n"
    echo ""

# Validate plugin and marketplace manifests
validate:
    #!/usr/bin/env bash
    set -e
    echo ""
    printf "\033[0;34m=== Validating Manifests ===\033[0m\n"
    echo ""
    printf "Validating marketplace manifest...\n"
    claude plugin validate . 2>&1
    echo ""
    for plugin_dir in plugins/*/; do
        plugin_name=$(basename "$plugin_dir")
        printf "Validating plugin %s...\n" "$plugin_name"
        claude plugin validate "$plugin_dir" 2>&1
    done
    echo ""
    printf "\033[32m✓ All manifests valid\033[0m\n"
    echo ""

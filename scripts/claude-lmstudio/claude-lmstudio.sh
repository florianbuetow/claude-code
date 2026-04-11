#!/usr/bin/env zsh

LMS_BIN="$HOME/.lmstudio/bin/lms"

# Launch Claude Code against a local LM Studio model
claudex() {
    # Check lms binary exists
    if [[ ! -x "$LMS_BIN" ]]; then
        echo "lms binary not found at $LMS_BIN"
        return 1
    fi

    # Check server is running
    local lmstudio_server_status
    lmstudio_server_status=$("$LMS_BIN" server status --json 2>&1) || true
    if ! echo "$lmstudio_server_status" | grep -q '"running":true'; then
        echo "LM Studio server is not running. Start it with: lms server start"
        return 1
    fi

    # Fetch all models metadata from LM Studio
    local all_models_json
    all_models_json=$("$LMS_BIN" ls --json 2>/dev/null)

    if [[ -z "$all_models_json" || "$all_models_json" == "[]" ]]; then
        echo "No models found."
        return 1
    fi

    # Get currently loaded model keys
    local loaded_json
    loaded_json=$("$LMS_BIN" ps --json 2>/dev/null)
    local loaded_keys
    loaded_keys=$(echo "$loaded_json" | jq -r '.[].modelKey' 2>/dev/null)

    # Filter out embedding models, sort by publisher then modelKey
    local sorted_models
    sorted_models=$(echo "$all_models_json" | jq -r '
        [.[] | select(.type == "llm")
             | select(.modelKey | test("embed|-e5-|ocr[^a-zA-Z]|ocr$"; "i") | not)]
        | sort_by(.publisher // "zzz", .modelKey)
        | .[]
        | [.modelKey, .publisher // "other", (.maxContextLength // 0 | tostring), (.sizeBytes // 0 | tostring)]
        | @tsv
    ' 2>/dev/null)

    if [[ -z "$sorted_models" ]]; then
        echo "No models found after filtering."
        return 1
    fi

    echo "Available LM Studio models:"
    echo
    local i=1 ctx_k size_gb current_publisher=""
    local model_list=()
    while IFS=$'\t' read -r model_key publisher max_ctx size_bytes; do
        # Print publisher header on change
        if [[ "$publisher" != "$current_publisher" ]]; then
            [[ -n "$current_publisher" ]] && echo
            printf "  \033[0;33m%s\033[0m\n" "$publisher"
            current_publisher="$publisher"
        fi

        model_list+=("$model_key")
        ctx_k=$(( max_ctx / 1024 ))
        size_gb=$(printf "%.1f" "$(( size_bytes / 1073741824.0 ))")
        if echo "$loaded_keys" | grep -qx "$model_key"; then
            printf "  \033[0;32m%2d) %-45s %4dk ctx  %5.1f GB  (loaded)\033[0m\n" "$i" "$model_key" "$ctx_k" "$size_gb"
        else
            printf "  %2d) %-45s %4dk ctx  %5.1f GB\n" "$i" "$model_key" "$ctx_k" "$size_gb"
        fi
        ((i++))
    done <<< "$sorted_models"
    echo

    read -r "choice?Select a model (1-${#model_list[@]}): "

    if [[ ! "$choice" =~ ^[0-9]+$ ]] || (( choice < 1 || choice > ${#model_list[@]} )); then
        echo "Invalid selection."
        return 1
    fi

    local selected="${model_list[$choice]}"
    local selected_ctx selected_size
    selected_ctx=$(echo "$all_models_json" | jq -r --arg m "$selected" '.[] | select(.modelKey == $m) | (.maxContextLength // 0)' 2>/dev/null)
    selected_size=$(echo "$all_models_json" | jq -r --arg m "$selected" '.[] | select(.modelKey == $m) | (.sizeBytes // 0)' 2>/dev/null)
    local selected_ctx_k=$(( selected_ctx / 1024 ))
    local selected_size_gb=$(printf "%.1f" "$(( selected_size / 1073741824.0 ))")
    # Context size selection
    local ctx_options=(256 200 128 96 64 48 32 24 16 8 4)
    local available_ctx=()
    for c in "${ctx_options[@]}"; do
        if (( c <= selected_ctx_k )); then
            available_ctx+=("$c")
        fi
    done

    echo
    echo "Context size (default: ${selected_ctx_k}k):"
    echo
    printf "  \033[0;32m%2d) %dk (native max)\033[0m\n" 1 "$selected_ctx_k"
    local ci=2
    for c in "${available_ctx[@]}"; do
        if (( c != selected_ctx_k )); then
            printf "  %2d) %dk\n" "$ci" "$c"
            ((ci++))
        fi
    done
    echo

    read -r "ctx_choice?Select context size (1-$((ci - 1))) [1]: "
    [[ -z "$ctx_choice" ]] && ctx_choice=1

    local chosen_ctx_k
    if (( ctx_choice == 1 )); then
        chosen_ctx_k=$selected_ctx_k
    else
        # Offset by 2 because option 1 is native, and available_ctx may include native
        local idx=2
        chosen_ctx_k=""
        for c in "${available_ctx[@]}"; do
            if (( c != selected_ctx_k )); then
                if (( idx == ctx_choice )); then
                    chosen_ctx_k=$c
                    break
                fi
                ((idx++))
            fi
        done
    fi

    if [[ -z "$chosen_ctx_k" ]]; then
        echo "Invalid selection."
        return 1
    fi

    local chosen_ctx_tokens=$(( chosen_ctx_k * 1024 ))
    local selected_label="$selected  ${chosen_ctx_k}k ctx"
    local we_loaded=false

    # Load model if not already loaded
    if "$LMS_BIN" ps 2>/dev/null | grep -q "$selected"; then
        echo "Model already loaded: $selected_label"
    else
        echo "Loading model: $selected_label ..."
        echo
        if ! "$LMS_BIN" load "$selected" -y -c "$chosen_ctx_tokens"; then
            echo "Failed to load model: $selected"
            return 1
        fi
        we_loaded=true
        echo
        echo "Model loaded: $selected_label"
    fi

    # Export env vars and launch claude
    export ANTHROPIC_BASE_URL=http://localhost:1234
    export ANTHROPIC_AUTH_TOKEN=lmstudio
    echo
    claude --model "$selected"

    # Cleanup: unset env vars
    unset ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN

    # Unload model only if we loaded it
    if [[ "$we_loaded" == "true" ]]; then
        echo "Unloading model: $selected ..."
        "$LMS_BIN" unload "$selected" || echo "Warning: failed to unload model"
        echo "Model unloaded: $selected"
    fi
}

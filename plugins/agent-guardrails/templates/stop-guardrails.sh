#!/bin/bash
set -euo pipefail

input=$(cat)

# Prevent infinite loop: if hook already fired on this response, let it through
stop_hook_active=$(echo "$input" | jq -r '.stop_hook_active // false')
if [ "$stop_hook_active" = "true" ]; then
  echo '{}'
  exit 0
fi

message=$(echo "$input" | jq -r '.last_assistant_message // ""')

if [ -z "$message" ]; then
  echo '{}'
  exit 0
fi

blocked=()

# no-speculative-language
if echo "$message" | grep -qiE '(probably|most likely|possibly|perhaps|presumably|I believe|I think|I'\''m (fairly |not entirely |pretty )?confident|if I recall correctly|as far as I know|from my understanding|it (seems|appears) (like|that|to be)|it looks like|this (looks|seems) (correct|right)|that looks right|I'\''ll? assume|assuming that|this should (work|fix|resolve|handle|do the trick)|should be fine|everything should be working|that should do it|likely caused by|might be happening because|could be (due to|a|caused)|one possible explanation|a common cause|may have (already|been)|may be (a|the|related|caused)|might have|could have been|not sure (if|whether|why|what)|I'\''m not certain)'; then
  blocked+=("no-speculative-language: Don't guess. Investigate to confirm, or state explicitly what you know and don't know.")
fi

# no-stalling
if echo "$message" | grep -qiE '(let me take a step back|taking a step back|before I proceed|before we proceed|before I continue|a few things to consider|there are some considerations|it'\''s worth noting|it'\''s important to note|one thing to keep in mind|let me (first )?explain|to summarize what|to clarify what|let me first understand|now let me also)'; then
  blocked+=("no-stalling: Stop padding and act. If you need info, get it. If you have info, act on it.")
fi

# no-preference-asking
if echo "$message" | grep -qiE '((shall|should|can|could|may) (I|we)\b|(want|like|need|ready for) me to\b|(would|do) you (want|like|prefer|rather|think|need|mind)\b|would you\b.*\bor\b|your (call|choice|decision|preference)|up to you|let me know\b|(does|how does) (this|that|it) look|(sound|look) good|((any|some|no)thing|what) else (you|to|would|I|we|can)|is there anything else|what would you like|which (would|do) you|which (approach|option) would you|(there are|here are) (a few|some|several|multiple) (approaches|options|ways|alternatives|choices)|happy to .*(either|whichever|whatever)|or (should|do|would|can|could) (I|we|you)\b|what.*feels right|which.*feels right|which.*do you (want|prefer|think)|how about (we|I)\b|\b(what|which|who|whom|whose|where|when|why|how)\b[^.!:?]*\?)'; then
  blocked+=("no-preference-asking: Do not ask for preference, seek approval, or defer decisions. The detection uses structural patterns (modal+I/we, want-me-to, do-you-X, your-decision-noun, approval-seeking, option-presenting, question-word+?) not a phrase list. If the grammatical structure of your sentence is asking the user to make a decision you should make yourself, it will be caught. Only ask the user if you genuinely cannot determine the best choice after thorough investigation, and explain exactly why.")
fi

# no-false-completion
if echo "$message" | grep -qiE '(all done|all set|we'\''re all set|we'\''re good|you'\''re all set|that'\''s everything|nothing else needs|no other changes|the fix is complete|implementation is complete|fully implemented|fully working|everything is working|everything works|Done[.!]|Complete[.!]|Finished[.!]|task is (complete|done|finished)|changes are (in|done|ready|committed|pushed)|that'\''s it[.!]|good to go|ready (to go|for review|to merge))'; then
  blocked+=("no-false-completion: Run tests or verification commands and show the output before claiming completion.")
fi

# no-skipping
if echo "$message" | grep -qiE '(i('\''m| am) skipping|skip(ping)? this|let('\''s| us) skip|we('\''ll| will) skip|i('\''ll| will) skip|the rest (looks|seems|is) fine|everything else (seems|looks|is) (correct|fine|ok)|that part should be fine|should be straightforward|without (seeing|running|testing)|I haven'\''t tested this|similar changes would be needed|you get the idea|the pattern is the same|and so on|the other files don'\''t need|don'\''t think we need to change|I won'\''t go through every|and similar for the (other|rest)|the same (approach|pattern|logic) (applies|works) for|I'\''ll leave (that|the rest|it) (to|for|as)|left as an exercise|beyond the scope|outside the scope|for brevity|I don'\''t have access|I can'\''t access)'; then
  blocked+=("no-skipping: Don't skip or hand-wave. If something shouldn't be done, explain why. If it should be done, do it.")
fi

# no-dismissing
if echo "$message" | grep -qiE '(not a real (bug|issue|error|problem)|can be ignored|just a warning|pre-existing (error|warning|bug|issue)|safe to ignore|not worth (fixing|investigating|worrying)|doesn'\''t matter|not important|harmless|benign|false positive|not a concern|don'\''t worry about|nothing to worry about|expected (error|warning|failure)|that'\''s fine|this is fine|a non-issue|just (cosmetic|informational|noise)|shouldn'\''t (matter|cause|be a problem))'; then
  blocked+=("no-dismissing: Don't dismiss issues without investigation. Diagnose the cause, then decide if action is needed. If you believe something is fine, show the evidence.")
fi

# no-echo-back
if echo "$message" | grep -qiE '(I'\''ll (now |first |start by |proceed to |begin by )|Here'\''s (what I'\''ll|my plan|the plan)|Let me (start|begin) by |First,? I'\''ll |I'\''m going to (start|begin) by |Let me (now )?go ahead and |I'\''ll go ahead and |Let me walk (you )?through)'; then
  blocked+=("no-echo-back: The user said go. Execute — don't restate the plan.")
fi

# no-robotic-comments
if echo "$message" | grep -qiE '((\/{2}|#) (This (function|method|class|component|module|hook|handler|service|helper|utility) (handles|is responsible for|provides|manages|implements|creates|defines|sets up|configures|ensures|takes care of)|Import(s| the| necessary| required)|Initialize(s)? the|Handle(s)? the|Set(s)? up the|Check(s)? (if|whether) the|Ensure(s)? (that )?the|Validate(s)? the|Process(es)? the|Helper (function|method) (to|for|that)))'; then
  blocked+=("no-robotic-comments: Write human code. Remove robotic comment blocks that describe what is obvious from the code itself.")
fi

# no-over-explaining
if echo "$message" | grep -qiE '(The reason (I|for this|behind this|we)|This change (ensures|makes sure|guarantees|is needed)|I (chose|went with|opted for|decided on|used) this approach because|This is (necessary|needed|required) because|What this does is|The purpose of this (change|update|fix|refactor) is|I made this change (because|to ensure|so that)|This (ensures|guarantees|makes sure) that the)'; then
  blocked+=("no-over-explaining: Don't over-explain obvious changes. The diff speaks for itself.")
fi

if [ ${#blocked[@]} -eq 0 ]; then
  echo '{}'
  exit 0
fi

# Build block response
reason=$(printf '%s\n' "${blocked[@]}")

jq -n --arg reason "$reason" '{
  "decision": "block",
  "reason": $reason
}'

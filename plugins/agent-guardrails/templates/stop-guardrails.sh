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

# no-guessing
if echo "$message" | grep -qiE '(probably|most likely|possibly|perhaps|presumably|I believe|I think|I'\''m (fairly |not entirely |pretty )?confident|if I recall correctly|as far as I know|from my understanding|it (seems|appears) (like|that|to be)|it looks like|this (looks|seems) (correct|right)|that looks right|I'\''ll? assume|assuming that|this should (work|fix|resolve|handle|do the trick)|should be fine|everything should be working|that should do it|likely caused by|might be happening because|could be (due to|a|caused)|one possible explanation|a common cause|may have (already|been)|may be (a|the|related|caused)|might have|could have been|not sure (if|whether|why|what)|I'\''m not certain|(looks|seems) (correct|right|done|complete|implemented|fixed|fine)|likely (correct|right|done|complete|implemented|fixed|fine))'; then
  blocked+=("You made a claim you haven't verified. Investigate to confirm or deny it before proceeding.")
fi

# no-stalling
if echo "$message" | grep -qiE '(let me take a step back|taking a step back|before I proceed|before we proceed|before I continue|a few things to consider|there are some considerations|it'\''s worth noting|it'\''s important to note|one thing to keep in mind|let me (first )?explain|to summarize what|to clarify what|let me first understand|now let me also)'; then
  blocked+=("Your task is not complete. Continue working. If you need information, retrieve it now. If you have the information, act on it now.")
fi

# no-preference-asking
if echo "$message" | grep -qiE '(would you prefer|would you like me to|would you rather|do you want me to|want me to\b.*\?|should I\b.*\?|which approach would you|which option would you|what would you prefer|let me know which|let me know how you|there are a few approaches|there are several options|here are some options|which would you like|happy to go either way|shall I|what.*feels right|which level feels right|which.*do you (want|prefer|think))'; then
  blocked+=("Re-read the requirements, specifications, and instructions you have been given. The answer to your question can be derived from the context. Make the best engineering decision based on what you already know. If after thorough review you genuinely cannot determine the answer, write on a single line: ESCALATING QUESTION: I am requiring an answer to the following - [state your question without a question mark]")
fi

# no-false-completion
if echo "$message" | grep -qiE '(all done|all set|we'\''re all set|we'\''re good|you'\''re all set|that'\''s everything|nothing else needs|no other changes|the fix is complete|implementation is complete|fully implemented|fully working|everything is working|everything works)'; then
  blocked+=("That sounds great. However, did you verify your results. Run all available tests and show their output. Do a manual check of the changes. If this is a web project, use Playwright MCP or CLI to manually test the changes and features you implemented. Show the verification output, then restate your completion claim.")
fi

# no-skipping
if echo "$message" | grep -qiE '(i('\''m| am) skipping|skip(ping)? this|let('\''s| us) skip|we('\''ll| will) skip|i('\''ll| will) skip|the rest (looks|seems|is) fine|everything else (seems|looks|is) (correct|fine|ok)|that part should be fine|should be straightforward|without (seeing|running|testing)|I haven'\''t tested this|have not (verified|confirmed|checked|validated|tested)|haven'\''t (verified|confirmed|checked|validated|tested)|similar changes would be needed|you get the idea|the pattern is the same|and so on|the other files don'\''t need|don'\''t think we need to change|I won'\''t go through every|and similar for the (other|rest)|the same (approach|pattern|logic) (applies|works) for|I'\''ll leave (that|the rest|it) (to|for|as)|left as an exercise|beyond the scope|outside the scope|for brevity|I don'\''t have access|I can'\''t access)'; then
  blocked+=("Your task is not complete. Do the work instead of describing it. If something cannot be done, explain exactly why. If it can be done, do it now.")
fi

# no-dismissing
if echo "$message" | grep -qiE '(not a real (bug|issue|error|problem)|can be ignored|just a warning|(is a |just a |only a )pre-existing|the only (failure|error|issue|problem|warning|bug) (is|was|being|comes from)|safe to ignore|not worth (fixing|investigating|worrying)|doesn'\''t matter|not important|harmless|benign|false positive|not a concern|don'\''t worry about|nothing to worry about|expected (error|warning|failure))'; then
  blocked+=("Do not dismiss issues without investigation. Diagnose the root cause and show evidence for your conclusion - test output, code references, or logs. No evidence means no dismissal.")
fi

# no-cosmetic
if echo "$message" | grep -qiE '\bcosmetic(s|ally)?\b'; then
  blocked+=("Nothing is ever cosmetic. Issues dismissed as cosmetic become technical debt. Investigate whether it can be solved quickly with minimal changes and report back - without using the word cosmetic.")
fi

# no-caveats
if echo "$message" | grep -qiE '\bcaveats?\b'; then
  blocked+=("You just mentioned a caveat, please review it and address it if you can deduce the correction from the intent and tasks I asked you to complete. I understand that you sometimes just mention caveats thinking that it is useful to mention it, but if it is not directly related to the task I've asked you to complete or stands in the way of completing it and aligning the final result with my intent then stop giving me caveat information that is non-actionable.")
fi

# no-flagging
if echo "$message" | grep -qiE '(\bto flag\b|\bflagging\b|\bflag(ged)? (this|that|it|these|those)\b|\b(I|we)('\''?ve| have| had)? flagged\b|\bas flagged\b|\bflagged (above|earlier|previously)\b|\b(should|shall|can|could|would|must|will|'\''?ll|let me|let'\''?s) flag\b|\bflag (a|an|one) (issue|concern|problem|risk|thing)\b)'; then
  blocked+=("You flagged something, does that mean you saw an issue that stands in the way of completing our goal and producing results that align with the intent of what we are doing? If so I expect you to dive into it, find evidence that this is an issue, and then address it in alignment with our goal and intent. I am not interested in knowing about issues if there is nothing you can do about them. Only flag things to me when you are unable to resolve the flagged issues. Giving me more information than necessary to complete or judge the outcome of our task is counterproductive.")
fi

if [ ${#blocked[@]} -eq 0 ]; then
  echo '{}'
  exit 0
fi

# Build block response
reason=$(printf '%s ' "${blocked[@]}")

jq -n --arg reason "$reason" '{
  "decision": "block",
  "reason": $reason
}'

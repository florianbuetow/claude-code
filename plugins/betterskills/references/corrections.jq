def said: [.message.content[]? | select(type == "object" and .type == "text") | .text] | join(" ");
def flat($n): gsub("\\s+"; " ") | if length > $n then .[0:$n] + "…" else . end;
foreach (inputs | fromjson? // empty) as $e ({};
  if .file != input_filename then {file: input_filename} else . end
  | .hit = null
  | if $e.type == "assistant" then (($e | said) as $t | if $t != "" then .last = $t else . end)
    elif $e.type == "user" and ($e.isMeta | not) and ($e.isSidechain | not) then
      ((if ($e.message.content | type) == "string" then $e.message.content else ($e | said) end)) as $t
      | if ($t | test("^\\s*(no|nope|wrong|stop|undo|revert)\\b|\\b(instead|again|i said|i told you|i asked|that.?s not|not what i|you forgot|you missed|you didn.?t|why did you|should have|don.?t|do not|too (long|short|verbose)|shorter|simpler|rather than|actually|still)\\b"; "i"))
           and ($t | startswith("<") | not)
        then .hit = {date: ($e.timestamp // "" | .[0:10]), text: $t, after: .last}
        else . end
    else . end;
  .hit // empty | .file = (input_filename | split("/") | .[-2]))
| "\(.date)  \(.file)  \(.text | flat(240))\n    after: …\(.after // "" | .[-160:] | flat(160))"

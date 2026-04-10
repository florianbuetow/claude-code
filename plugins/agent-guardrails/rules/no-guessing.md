---
name: no-guessing
pattern: (?i)(probably|most likely|possibly|perhaps|presumably|I believe|I think|I'?m (fairly |not entirely |pretty )?confident|if I recall correctly|as far as I know|from my understanding|it (seems|appears) (like|that|to be)|it looks like|this (looks|seems) (correct|right)|that looks right|I'?ll? assume|assuming that|this should (work|fix|resolve|handle|do the trick)|should be fine|everything should be working|that should do it|likely caused by|might be happening because|could be (due to|a|caused)|one possible explanation|a common cause|may have (already|been)|may be (a|the|related|caused)|might have|could have been|not sure (if|whether|why|what)|I'?m not certain)
message: "You made a claim you haven't verified. Investigate to confirm or deny it before proceeding."
---

Stop — you made an unverified claim.

You asserted something without evidence. Before proceeding:
1. Investigate — run a command, read the code, or check the output to confirm or deny your claim.
2. Report what you found — state the verified fact, not what you expected to find.
3. If you cannot verify right now, say exactly what is unverified and why — then continue with what you can verify.

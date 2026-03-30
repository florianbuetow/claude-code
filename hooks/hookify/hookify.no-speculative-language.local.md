---
name: no-speculative-language
enabled: true
event: stop
pattern: (?i)(probably|most likely|possibly|perhaps|presumably|I believe|I think|I'?m (fairly |not entirely |pretty )?confident|if I recall correctly|as far as I know|from my understanding|it (seems|appears) (like|that|to be)|it looks like|this (looks|seems) (correct|right)|that looks right|I'?ll? assume|assuming that|this should (work|fix|resolve|handle|do the trick)|should be fine|everything should be working|that should do it|likely caused by|might be happening because|could be (due to|a|caused)|one possible explanation|a common cause|may have (already|been)|may be (a|the|related|caused)|might have|could have been|not sure (if|whether|why|what)|I'?m not certain)
action: block
---

**Stop - speculative language detected.**

You used hedging or speculative language (e.g., "probably", "I think", "this should work", "it seems like", "likely caused by", "may have been", "not sure if"). Don't guess. Either:
1. **Investigate** to confirm the cause or result, or
2. **State explicitly** what you know and what you don't know.

No hedging. No unverified claims. Verify before asserting.

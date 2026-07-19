---
name: no-caveats
pattern: (?i)\bcaveats?\b
message: "You just mentioned a caveat, please review it and address it if you can deduce the correction from the intent and tasks I asked you to complete. I understand that you sometimes just mention caveats thinking that it is useful to mention it, but if it is not directly related to the task I've asked you to complete or stands in the way of completing it and aligning the final result with my intent then stop giving me caveat information that is non-actionable."
---

Do not hand over caveats you could have acted on.

1. Re-read the caveat against the intent and the tasks you were given.
2. If the correction can be deduced from that intent, apply it instead of reporting it.
3. If it is not directly related to the task and does not stand in the way of completing it, drop it. A caveat the user cannot act on is noise.

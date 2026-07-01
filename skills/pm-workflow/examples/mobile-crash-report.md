# Example: PM loop for a reported crash on mobile

## Starting point

User complaint via support: "The app crashes when I try to upload a photo on my iPhone."

---

## Phase 1: Draft issue

Using `write-issue`:

**Title:** App crashes when uploading photos on iOS

**Problem:** Users on iOS report the app crashes during photo upload. Root cause unknown — could be file size limits, format handling, or a platform-specific API difference. Frequency appears high based on support volume.

**Acceptance criteria (draft):**
- [ ] Photo upload completes without crashing on iOS 16+
- [ ] Error messages shown for unsupported formats instead of silent crash
- [ ] Regression test added for the iOS upload path

---

## Phase 2: Share

Posted issue link to:
- 3 affected users via support thread
- iOS engineer (tech lead)
- Product stakeholder

Questions asked:
- "Does this match what you experienced? Any steps I'm missing?"
- "What file types and sizes triggered it?"
- "Is there a crash log in TestFlight or Firebase?"

---

## Phase 3: Gather feedback

```
[User A] clarifies — only happens with HEIC files, JPEG works fine
[User B] clarifies — also happens with videos, not just photos
[Tech Lead] adds — HEIC conversion not handled server-side, that's the likely root cause
[Tech Lead] adds — crash logs available in Firebase Crashlytics under event "upload_fail"
[Stakeholder] adds — video upload is a separate feature, defer that finding
```

Saturation reached after 2 rounds — new feedback confirming, not changing.

---

## Phase 4: Synthesize

**What changed:** HEIC is the specific format, not all photos. Video is out of scope (separate issue opened: #51).

**What's consistent:** iOS-only, upload path, users agree on the symptom.

**Decision made:** Scope this to HEIC → convert server-side or reject with clear error. Video deferred to #51.

---

## Phase 5: Refined issue

**Title:** iOS photo upload crashes on HEIC format

**Problem:** iOS saves photos in HEIC format by default. The upload endpoint doesn't handle HEIC — no conversion, no rejection with a useful error — resulting in a silent crash. Firebase Crashlytics event: `upload_fail`.

**Acceptance criteria:**
- [ ] HEIC files are either converted to JPEG server-side or rejected with a clear error message ("This file format isn't supported. Please use JPEG or PNG.")
- [ ] No crash on upload attempt with any file format
- [ ] Regression test covers HEIC upload path
- [ ] Crash rate for `upload_fail` drops to zero in Crashlytics after deploy

**Out of scope:** Video upload (tracked in #51).

---

## Phase 6: Validate

- [x] Engineer can start without asking questions? Yes — format, expected behavior, and crash event identified
- [x] Acceptance criteria testable? Yes — Crashlytics metric is measurable
- [x] Root cause identified? Yes — HEIC with no server-side handling
- [x] Scope explicit? Yes — video explicitly deferred
- [x] Open questions? None remaining

**Ready.**

---

## Phase 7: Finalize

```bash
glab issue update 47 --label "ready-for-eng"
python $GITLAB post-issue-comment webapp 47 \
  "Validated with 3 users and tech lead. Root cause: HEIC format not handled server-side. Scope limited to photo upload; video deferred to #51. Ready for eng."
```

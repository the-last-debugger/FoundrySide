# Collaboration Bridge — FoundrySide

One durable, versioned place where the builder (agent), the sponsor (human owner)
and oversight (ChatGPT) exchange state, questions, approvals and research verdicts.
Chat decides in flight; the repository holds the record.

Ported unchanged from `ODE/docs/COLLAB/`, which was adapted from
`OLPRS_v2/docs/COLLAB/`. The format is identical on purpose: an entry written here
is readable in either of the other two repositories, and the same checker runs in
all three.

## Roles

| Role | Who | Writes |
| --- | --- | --- |
| **Builder** | the coding agent (DeepSeek) | code, tests, docs, investigations; every change arrives here as a `ready_for_review` item |
| **Sponsor** | human owner | scope, budget, access, direction — and the only role that can reverse a kill |
| **Oversight** | ChatGPT | reads the repo, reviews items and evidence, challenges claims |

Autonomy boundary, carried over from the two prior repositories: the builder may run
anything that costs nothing and is reversible, and may commit and push. Anything that
spends money, creates an account, contacts a third party, holds itself out as advice,
or commits the sponsor to an obligation is a `blocker` entry awaiting a sponsor
decision. This is the same line `PRE_PROPOSAL.md` §12 and §17 draw.

## Files

| File | Rule |
| --- | --- |
| `THREAD.md` | Append-only. One entry per event. Never edited after it is pushed. |
| `REVIEW_QUEUE.md` | Mutable ledger. One row per reviewable change. |
| `DECISIONS.md` | Accepted decisions only. No proposals. |
| `PROPOSALS.md` | Pivot options, open questions and improvement ideas awaiting a decision. |

## Entry format

```
### 2026-11-03T11:52:00Z · builder · research
CRITIQUE recorded: the pre-proposal has no falsifier and ignores its own prior results.
- revision: 93f2320
- ref: CRITIQUE.md
```

`- revision:` is the commit the entry is about. **Oversight reviews must include it**,
because a verdict is only meaningful for the exact revision that was read. `- ref:`
points at a queue row or a file.

Authors: `builder` | `sponsor` | `oversight`

Kinds: `note` | `question` | `answer` | `review` | `decision` | `direction` |
`clarification` | `blocker` | `evidence` | `research` | `response`

`response` was added after the sponsor used it for a substantive reply; the checker
rejects any kind outside this list, and a header that does not parse is now an error
rather than being absorbed into the entry above it.

Write entries with the helper so the shape stays valid:

```powershell
$py = "C:\Users\tuyaa\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
& $py scripts\collab_note.py --author builder --kind evidence --message "9 tests pass" --revision e590f9c
& $py scripts\collab_check.py
```

## Review loop (direct-to-main)

Commits land on `main` immediately, so the queue records review **after** the push.
There is no merge step to gate, and pretending otherwise would make the ledger lie.

| State | Set by | Meaning |
| --- | --- | --- |
| `draft` | builder | Work exists locally or is planned; not pushed, or pushed only as a follow-up to an open row. |
| `ready_for_review` | builder | Committed and pushed. Awaiting oversight. |
| `changes_requested` | oversight | Oversight reviewed it and wants a follow-up commit. The row stays open. |
| `accepted` | oversight | Oversight reviewed this exact revision and accepts it. Terminal; it does **not** mean a merge happened, because the commit is already on `main`. |

The builder never writes `changes_requested` or `accepted`. Those are verdicts.

**Who may issue a verdict.** Oversight is the intended reviewer, but the sponsor is the
project owner and has issued verdicts directly — as a `response` that names queue rows
rather than as a `review`. The checker therefore treats an entry as verdict-bearing when:

- the author is `oversight` or `sponsor`, **and**
- the kind is `review`, **or** the kind is `response` and the entry names an `RQ-` row.

A `response` that names no row is directions, not a verdict, and produces no warning. The
builder can never authorise anything, which is the property that matters. This rule was
written after the sponsor's 2026-11-03 review, which was otherwise correct but would have
been invisible to the checker.

**Field aliases.** `- revision reviewed:` and `- refs:` are accepted alongside `- revision:`
and `- ref:`, because both were used in practice and both are unambiguous. The value must
still be a bare token, and a verdict still fails if its recorded revision differs from the
row's.

## Enforced invariants

`python scripts\collab_check.py` (also run by the test suite) fails when:

- a row is `accepted` or `changes_requested` without an oversight `review` entry
  naming it — so the queue cannot claim a verdict that was never recorded;
- that review's recorded revision differs from the row's `Revision` — a review of an
  older commit cannot authorise a newer one;
- a verdict row has no revision, or a revision that is not a commit SHA;
- a recorded revision does not exist in this git history, so a verdict cannot be
  attached to a commit that was never made;
- an oversight `review` entry names a queue id that does not exist;
- a row uses a state outside the table above, or has the wrong number of columns;
- `DECISIONS.md` contains anything marked `**Status:** proposed` — proposals belong
  in `PROPOSALS.md`;
- `THREAD.md` has lost a line relative to the previous commit that touched it
  (`--history-audit` extends this across the whole history).

## Evidence standard

Claims about behaviour need a command and its observed result, not a summary:

```
$ python -m unittest discover -s tests
Ran 19 tests in 0.2s
OK
```

A claim about the world needs a source that has been re-fetched and can be quoted,
or it must be labelled `blocked`/`unverified` in the record. FoundrySide inherits
this rule from ODE, where a reviewer that did not re-test a TLS claim propagated a
false one into four files. See `CRITIQUE.md` §4 on why that matters more here than
usual: every interesting quantity in this project is a comparison against a market,
and a comparison is exactly the kind of claim that survives review while being wrong.

## The one thing this protocol cannot check

Oversight reviews reasoning. It does not, by default, re-fetch the sources. A review
that reads only the diff and the dossier is checking argument quality, not evidence
quality, and the two fail independently. When a row turns on a factual claim — a
provider's terms of service, a price, a coverage number — oversight should ask for
the fetch output rather than accept the document's rendering of it.

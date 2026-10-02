# Pre-live frozen-payload integrity blocker

Status: `HARD_BLOCKER — NO K5/K6 GENERATION SENT`.

The K5 and K6 manifests record `final_request_payload_sha256`, but the frozen
builder code shows that each hash covers a planning object (model, prompt,
asset SHA, representation and generation settings), not the exact provider
HTTP body. It omits provider-specific request structure and, for image rows,
the encoded image bytes. K5 image rows also identify only the PNG as their
input asset while their prompt asserts a supplied structured physical context;
that context is not an input asset in those rows. A production dispatch adapter
cannot reconstruct exact request bytes and verify the declared final-payload
hash without adding material that is absent from the frozen payload record.

Consequently, issuing K5/K6 requests would either (a) send an unverified,
newly constructed payload, or (b) modify/re-freeze K5/K6 inputs/hashes. Both
violate the frozen-design and pre-dispatch integrity rules. This is not a
software retry/lifecycle issue and cannot be resolved safely by executor code.

Required human scientific decision: authorize a prospective, versioned
K5/K6 payload-integrity amendment that either freezes exact provider request
serializations (including provider-specific bodies and all image/context
parts), or explicitly changes the integrity contract. No outcome data exist,
so such an amendment can remain prospective, but it must be approved and
frozen before any generation request.

## Resolution

`BLOCKER_RESOLVED_PROSPECTIVELY` on 2026-10-02 after explicit human
authorization and while K5/K6 generation calls remained zero. Commit
`44388b3` and tag `ka-iro-krisis-request-serialization-v1` add deterministic
provider-specific body serialization, explicit K5 image-context linkage, body
and envelope hashes, and offline reconstruction validation. The original
scientific K5/K6 freezes remain unchanged.

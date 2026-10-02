# KA-IRO KRISIS v2 request-serialization amendment

Status: `PROSPECTIVE_PRE_EXECUTION_REQUEST_SERIALIZATION_AMENDMENT`.

Before this amendment, K5/K6 generation calls were zero and no model output was available or inspected. The K5/K6 scientific designs remain unchanged: sampling, scenes, model panel, interfaces, representations, K6 pairs, execution-order keys, hypotheses, and K3 outcomes are untouched.

The original freezes fixed scientific design and planning-object hashes, but not reconstructible provider HTTP bytes. This amendment supplements rather than rewrites them. It distinguishes scientific input content (prompt, frozen image/context bytes, model, interface and parameters), provider serialization (Gemini content/parts and Groq messages/data URLs/JSON mode), and transport/authentication (runtime secrets and volatile headers, never tracked).

For K5 image rows, the existing same-scene deterministic text-equivalent asset is the uniquely produced structured physical context and is now explicitly supplied. It contains decision-time scene state only; no K3 action outcomes, labels, or model output are included. The amendment freezes canonical UTF-8 JSON body bytes, non-secret envelopes, hashes, byte lengths, endpoints and explicit generation configuration. Original `final_request_payload_sha256` values remain preserved as `planning_object_sha256`.

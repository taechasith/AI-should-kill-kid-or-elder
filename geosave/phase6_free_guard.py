"""Fail-closed authorization checks for the Phase 6 zero-cost provider panel.

This module contains no credential values, HTTP client, or billing action.  It
checks the immutable conditions that must be true before an executor is even
permitted to construct a remote request.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


FREE_ONLY_MODE = "FREE_ONLY"
PILOT_PURPOSE = "multimodal_capability_pilot"
BENCHMARK_PURPOSE = "benchmark"
ALLOWED_PROVIDER_MODELS = {
    "gemini": {"gemini-3.6-flash", "gemini-2.5-flash-lite"},
    "groq": {"qwen/qwen3.8-27b"},
}
REQUIRED_CREDENTIAL_ENV = {"gemini": "GEMINI_API_KEY", "groq": "GROQ_API_KEY"}


class FreeOnlyAuthorizationError(PermissionError):
    """Raised before a request that could violate the USD 0 / THB 0 policy."""


@dataclass(frozen=True)
class FreeOnlyExecutionGuard:
    """Validate a request against the frozen zero-cost execution contract."""

    budget_mode: str
    max_authorized_usd: float
    max_authorized_thb: float
    allow_paid_fallback: bool
    allow_provider_upgrade: bool
    allow_credit_purchase: bool
    allow_automatic_billing: bool
    registry_status: str

    @classmethod
    def from_policy(cls, policy: Mapping[str, object], registry_status: str) -> "FreeOnlyExecutionGuard":
        return cls(
            budget_mode=str(policy.get("budget_mode")),
            max_authorized_usd=float(policy.get("max_authorized_usd", -1)),
            max_authorized_thb=float(policy.get("max_authorized_thb", -1)),
            allow_paid_fallback=bool(policy.get("allow_paid_fallback")),
            allow_provider_upgrade=bool(policy.get("allow_provider_upgrade")),
            allow_credit_purchase=bool(policy.get("allow_credit_purchase")),
            allow_automatic_billing=bool(policy.get("allow_automatic_billing")),
            registry_status=registry_status,
        )

    def assert_request_permitted(
        self,
        *,
        provider: str,
        model_id: str,
        purpose: str,
        credential_present: bool,
        access_tier: str,
        billing_enabled: bool,
        rate_limit_verified: bool,
    ) -> None:
        if self.budget_mode != FREE_ONLY_MODE:
            raise FreeOnlyAuthorizationError("Phase 6 requires FREE_ONLY budget mode")
        if self.max_authorized_usd != 0.0 or self.max_authorized_thb != 0.0:
            raise FreeOnlyAuthorizationError("Phase 6 free policy must authorize exactly USD 0 and THB 0")
        if any((self.allow_paid_fallback, self.allow_provider_upgrade, self.allow_credit_purchase, self.allow_automatic_billing)):
            raise FreeOnlyAuthorizationError("Phase 6 free policy must prohibit all paid routes")
        if provider not in ALLOWED_PROVIDER_MODELS or model_id not in ALLOWED_PROVIDER_MODELS[provider]:
            raise FreeOnlyAuthorizationError("provider/model is not in the frozen zero-cost allowlist")
        if not credential_present:
            raise FreeOnlyAuthorizationError(f"missing required credential presence for {provider}")
        if access_tier not in {"free_tier", "free_plan"}:
            raise FreeOnlyAuthorizationError("provider access is not verified as free")
        if billing_enabled:
            raise FreeOnlyAuthorizationError("billing-enabled provider account is prohibited")
        if not rate_limit_verified:
            raise FreeOnlyAuthorizationError("current free-quota rate limit is not verified")
        if purpose == PILOT_PURPOSE:
            if self.registry_status != "FREE_ONLY_PILOT_AUTHORIZED":
                raise FreeOnlyAuthorizationError("the registry is not authorized for the three-call free pilot")
        elif purpose == BENCHMARK_PURPOSE:
            if self.registry_status != "FREE_ACCESS_VERIFIED_EXECUTABLE":
                raise FreeOnlyAuthorizationError("the registry is not frozen executable after a successful free pilot")
        else:
            raise FreeOnlyAuthorizationError("unrecognized Phase 6 execution purpose")

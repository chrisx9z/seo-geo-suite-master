#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schema.org v2 High-Leverage Generators & E-Commerce / Deprecated Rich-Result Validator
(Integrated from AgriciDaniel/claude-seo: schema_generate.py, schema_ecommerce_validate.py).

Provides:
  - generate_reservation_schema(...)
  - generate_order_action_schema(...)
  - generate_discussion_schema(...)
  - generate_profile_page_schema(...)
  - validate_ecommerce_schema(payload, require_eu_energy=False) -> dict
"""

from __future__ import annotations

from typing import Optional

DEPRECATED_SCHEMA_TYPES: dict[str, str] = {
    "Vehicle": "Vehicle Listing rich result retired June 2025.",
    "VehicleListing": "Vehicle Listing rich result retired June 2025.",
    "ClaimReview": "Claim Review rich result retired June 2025.",
    "EstimatedSalary": "Estimated Salary rich result retired June 2025.",
    "LearningVideo": "Learning Video rich result retired June 2025.",
    "Course": "Course Info carousel variant retired June 2025.",
    "SpecialAnnouncement": "Special Announcement rich result deprecated July 2025.",
    "HowTo": "HowTo rich result deprecated September 2023.",
    "FAQPage": "FAQPage rich results retired for all sites May 7, 2026.",
}

_REQUIRED_PRODUCT_FIELDS = ("name", "image", "offers")
_RECOMMENDED_PRODUCT_FIELDS = ("description",)
_RECOMMENDED_OFFER_FIELDS = ("price", "priceCurrency", "availability")
_REQUIRED_RETURN_POLICY_FIELDS = ("applicableCountry", "returnPolicyCategory")
_REQUIRED_SHIPPING_FIELDS = ("shippingDestination", "deliveryTime")


def generate_reservation_schema(
    provider: str,
    start: str,
    *,
    end: Optional[str] = None,
    party_size: Optional[int] = None,
    reservation_id: Optional[str] = None,
    reservation_for_name: Optional[str] = None,
    customer_name: Optional[str] = None,
    customer_email: Optional[str] = None,
    kind: str = "FoodEstablishmentReservation",
) -> dict:
    payload: dict = {
        "@context": "https://schema.org",
        "@type": kind,
        "reservationStatus": "https://schema.org/ReservationConfirmed",
        "provider": {"@type": "Organization", "name": provider},
        "reservationFor": {
            "@type": "FoodEstablishment" if kind == "FoodEstablishmentReservation" else "Place",
            "name": reservation_for_name or provider,
        },
        "startTime": start,
    }
    if end:
        payload["endTime"] = end
    if party_size is not None:
        payload["partySize"] = int(party_size)
    if reservation_id:
        payload["reservationId"] = reservation_id
    if customer_name or customer_email:
        person: dict = {"@type": "Person"}
        if customer_name:
            person["name"] = customer_name
        if customer_email:
            person["email"] = customer_email
        payload["underName"] = person
    return payload


def generate_order_action_schema(
    merchant: str,
    *,
    order_url: str,
    name: str = "Order online",
    accepted_payment_method: Optional[list[str]] = None,
    delivery_method: Optional[list[str]] = None,
) -> dict:
    payload: dict = {
        "@context": "https://schema.org",
        "@type": "OrderAction",
        "name": name,
        "target": {
            "@type": "EntryPoint",
            "urlTemplate": order_url,
            "inLanguage": "en-US",
            "actionPlatform": [
                "https://schema.org/DesktopWebPlatform",
                "https://schema.org/MobileWebPlatform",
            ],
        },
        "deliveryMethod": delivery_method or [
            "https://schema.org/OnSitePickup",
            "https://schema.org/ParcelService",
        ],
        "priceSpecification": {
            "@type": "PriceSpecification",
            "eligibleTransactionVolume": {
                "@type": "PriceSpecification",
                "minPrice": 0,
                "priceCurrency": "USD",
            },
        },
        "merchant": {"@type": "Organization", "name": merchant},
    }
    if accepted_payment_method:
        payload["acceptedPaymentMethod"] = [
            {"@type": "PaymentMethod", "name": m} for m in accepted_payment_method
        ]
    return payload


def generate_discussion_schema(
    headline: str,
    author: str,
    *,
    url: str,
    date_published: str,
    text: Optional[str] = None,
    date_modified: Optional[str] = None,
    interaction_count: Optional[dict] = None,
    comment_count: Optional[int] = None,
) -> dict:
    payload: dict = {
        "@context": "https://schema.org",
        "@type": "DiscussionForumPosting",
        "headline": headline,
        "author": {"@type": "Person", "name": author},
        "datePublished": date_published,
        "url": url,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }
    if text:
        payload["text"] = text
    if date_modified:
        payload["dateModified"] = date_modified
    if comment_count is not None:
        payload["commentCount"] = int(comment_count)
    if interaction_count:
        payload["interactionStatistic"] = [
            {
                "@type": "InteractionCounter",
                "interactionType": f"https://schema.org/{k}",
                "userInteractionCount": int(v),
            }
            for k, v in interaction_count.items()
        ]
    return payload


def generate_profile_page_schema(
    name: str,
    *,
    url: str,
    description: Optional[str] = None,
    same_as: Optional[list[str]] = None,
    knows_about: Optional[list[str]] = None,
    works_for: Optional[str] = None,
    image: Optional[str] = None,
    job_title: Optional[str] = None,
) -> dict:
    person: dict = {"@type": "Person", "name": name, "url": url}
    if description:
        person["description"] = description
    if same_as:
        person["sameAs"] = list(same_as)
    if knows_about:
        person["knowsAbout"] = list(knows_about)
    if works_for:
        person["worksFor"] = {"@type": "Organization", "name": works_for}
    if image:
        person["image"] = image
    if job_title:
        person["jobTitle"] = job_title

    return {
        "@context": "https://schema.org",
        "@type": "ProfilePage",
        "mainEntity": person,
        "url": url,
    }


def _iter_typed(payload, target_type: str):
    if isinstance(payload, dict):
        kind = payload.get("@type")
        if isinstance(kind, str) and kind == target_type:
            yield payload
        elif isinstance(kind, list) and target_type in kind:
            yield payload
        for v in payload.values():
            yield from _iter_typed(v, target_type)
    elif isinstance(payload, list):
        for v in payload:
            yield from _iter_typed(v, target_type)


def _all_types(payload) -> list[str]:
    types: list[str] = []
    if isinstance(payload, dict):
        kind = payload.get("@type")
        if isinstance(kind, str):
            types.append(kind)
        elif isinstance(kind, list):
            types.extend(t for t in kind if isinstance(t, str))
        for v in payload.values():
            types.extend(_all_types(v))
    elif isinstance(payload, list):
        for v in payload:
            types.extend(_all_types(v))
    return types


def _has_type(payload: dict, target_type: str) -> bool:
    kind = payload.get("@type")
    if isinstance(kind, str):
        return kind == target_type
    if isinstance(kind, list):
        return target_type in kind
    return False


def validate_ecommerce_schema(payload: dict | list, *, require_eu_energy: bool = False) -> dict:
    """Validate Product JSON-LD against Google 2025-2026 merchant-listing rules and deprecated types."""
    findings: list[dict] = []

    for kind in _all_types(payload):
        if kind in DEPRECATED_SCHEMA_TYPES:
            sev = "Info" if kind == "FAQPage" else "Critical"
            findings.append({
                "severity": sev,
                "rule": "deprecated-type",
                "message": f"@type={kind!r}: {DEPRECATED_SCHEMA_TYPES[kind]}",
            })

    products = list(_iter_typed(payload, "Product"))
    if not products:
        findings.append({
            "severity": "High",
            "rule": "missing-product",
            "message": "No @type=\"Product\" block found in the JSON-LD.",
        })

    for prod in products:
        for field in _REQUIRED_PRODUCT_FIELDS:
            if field not in prod or prod[field] in (None, "", []):
                findings.append({
                    "severity": "High",
                    "rule": f"missing-product-{field}",
                    "message": f"Product is missing required {field!r}.",
                })

        for field in _RECOMMENDED_PRODUCT_FIELDS:
            if field not in prod or prod[field] in (None, "", []):
                findings.append({
                    "severity": "Medium",
                    "rule": f"recommended-product-{field}",
                    "message": f"Product is missing recommended {field!r}.",
                })

        offers = prod.get("offers", [])
        offers_list = [offers] if isinstance(offers, dict) else (offers if isinstance(offers, list) else [])

        for offer in offers_list:
            if not isinstance(offer, dict):
                continue
            if _has_type(offer, "AggregateOffer"):
                findings.append({
                    "severity": "High",
                    "rule": "merchant-listing-offer-type",
                    "message": "Merchant listings require offers.@type='Offer', not 'AggregateOffer'.",
                })
            elif not _has_type(offer, "Offer"):
                findings.append({
                    "severity": "High",
                    "rule": "merchant-listing-offer-type",
                    "message": "Merchant listings require offers.@type='Offer'.",
                })
            for field in _RECOMMENDED_OFFER_FIELDS:
                if field not in offer or offer[field] in (None, "", []):
                    findings.append({
                        "severity": "Medium",
                        "rule": f"recommended-offer-{field}",
                        "message": f"Offer is missing recommended {field!r}.",
                    })

        return_policy = prod.get("hasMerchantReturnPolicy") or (
            offers_list[0].get("hasMerchantReturnPolicy") if offers_list else None
        )
        if not return_policy:
            findings.append({
                "severity": "Medium",
                "rule": "missing-return-policy",
                "message": "Product (or its Offer) is missing hasMerchantReturnPolicy.",
            })
        elif isinstance(return_policy, dict):
            for field in _REQUIRED_RETURN_POLICY_FIELDS:
                if field not in return_policy:
                    findings.append({
                        "severity": "Medium",
                        "rule": f"return-policy-{field}",
                        "message": f"MerchantReturnPolicy is missing {field!r}.",
                    })

        shipping = prod.get("shippingDetails") or (
            offers_list[0].get("shippingDetails") if offers_list else None
        )
        if not shipping:
            findings.append({
                "severity": "Medium",
                "rule": "missing-shipping-details",
                "message": "Product (or its Offer) is missing shippingDetails.",
            })
        elif isinstance(shipping, dict):
            for field in _REQUIRED_SHIPPING_FIELDS:
                if field not in shipping:
                    findings.append({
                        "severity": "Medium",
                        "rule": f"shipping-{field}",
                        "message": f"OfferShippingDetails is missing {field!r}.",
                    })

        if require_eu_energy and "energyEfficiencyClass" not in prod:
            findings.append({
                "severity": "High",
                "rule": "missing-eu-energy-class",
                "message": "EU mode: in-scope products require energyEfficiencyClass per EPREL regulation.",
            })

    severities = [f["severity"] for f in findings]
    return {
        "ok": all(s not in ("Critical", "High") for s in severities),
        "findings": findings,
        "summary": {
            "critical": severities.count("Critical"),
            "high": severities.count("High"),
            "medium": severities.count("Medium"),
            "info": severities.count("Info"),
        },
    }

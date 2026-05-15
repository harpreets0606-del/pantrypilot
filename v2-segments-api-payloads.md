# Klaviyo v2 Segment API Payloads — POST `/api/segments/`

Once Zapier→Klaviyo auth is complete, these are the exact request bodies I will POST to Klaviyo via Zapier's `_zap_raw_request` mutating action.

**Note on casing:** Klaviyo's REST API uses snake_case in request bodies (despite the MCP returning camelCase in reads). Payloads below use snake_case.

**Required header:** `revision: 2024-10-15`, `accept: application/vnd.api+json`, `content-type: application/vnd.api+json`

---

## Payload 1 — `BC — High AOV Retail v2 ($45+)`

```json
{
  "data": {
    "type": "segment",
    "attributes": {
      "name": "BC — High AOV Retail v2 ($45+)",
      "definition": {
        "condition_groups": [
          {
            "conditions": [
              {
                "type": "profile-metric",
                "metric_id": "Sxnb5T",
                "measurement": "count",
                "measurement_filter": {
                  "type": "numeric",
                  "operator": "greater-than",
                  "value": 0
                },
                "timeframe_filter": {
                  "type": "date",
                  "operator": "in-the-last",
                  "unit": "day",
                  "quantity": 1095
                },
                "metric_filters": [
                  {
                    "property": "$value",
                    "filter": {
                      "type": "numeric",
                      "operator": "greater-than",
                      "value": 45
                    }
                  }
                ]
              }
            ]
          },
          {
            "conditions": [
              {
                "type": "profile-metric",
                "metric_id": "Sxnb5T",
                "measurement": "count",
                "measurement_filter": {
                  "type": "numeric",
                  "operator": "greater-than",
                  "value": 0
                },
                "timeframe_filter": {
                  "type": "date",
                  "operator": "in-the-last",
                  "unit": "day",
                  "quantity": 1095
                },
                "metric_filters": [
                  {
                    "property": "Collections",
                    "filter": {
                      "type": "list",
                      "operator": "contains-any",
                      "value": ["_retail"]
                    }
                  }
                ]
              }
            ]
          },
          {
            "conditions": [
              {
                "type": "profile-marketing-consent",
                "consent": {
                  "channel": "email",
                  "can_receive_marketing": true,
                  "consent_status": {
                    "subscription": "subscribed",
                    "filters": null
                  }
                }
              }
            ]
          }
        ]
      }
    }
  }
}
```

**Expected count:** 8,000–15,000

---

## Payload 2 — `BC — New Retail Customers L30D v2`

```json
{
  "data": {
    "type": "segment",
    "attributes": {
      "name": "BC — New Retail Customers L30D v2",
      "definition": {
        "condition_groups": [
          {
            "conditions": [
              {
                "type": "profile-metric",
                "metric_id": "Sxnb5T",
                "measurement": "count",
                "measurement_filter": {
                  "type": "numeric",
                  "operator": "greater-than",
                  "value": 0
                },
                "timeframe_filter": {
                  "type": "date",
                  "operator": "in-the-last",
                  "unit": "day",
                  "quantity": 30
                },
                "metric_filters": [
                  {
                    "property": "Collections",
                    "filter": {
                      "type": "list",
                      "operator": "contains-any",
                      "value": ["_retail"]
                    }
                  }
                ]
              }
            ]
          },
          {
            "conditions": [
              {
                "type": "profile-metric",
                "metric_id": "Sxnb5T",
                "measurement": "count",
                "measurement_filter": {
                  "type": "numeric",
                  "operator": "equals",
                  "value": 1
                },
                "timeframe_filter": {
                  "type": "date",
                  "operator": "in-the-last",
                  "unit": "day",
                  "quantity": 1095
                },
                "metric_filters": [
                  {
                    "property": "Collections",
                    "filter": {
                      "type": "list",
                      "operator": "contains-any",
                      "value": ["_retail"]
                    }
                  }
                ]
              }
            ]
          },
          {
            "conditions": [
              {
                "type": "profile-marketing-consent",
                "consent": {
                  "channel": "email",
                  "can_receive_marketing": true,
                  "consent_status": {
                    "subscription": "subscribed",
                    "filters": null
                  }
                }
              }
            ]
          }
        ]
      }
    }
  }
}
```

**Expected count:** 1,600–1,800 (vs. 1,539 currently)

---

## Payload 3 — `BC — Unengaged Subscribed 180D v2 (sunset)`

```json
{
  "data": {
    "type": "segment",
    "attributes": {
      "name": "BC — Unengaged Subscribed 180D v2 (sunset)",
      "definition": {
        "condition_groups": [
          {
            "conditions": [
              {
                "type": "profile-metric",
                "metric_id": "SZ8GZJ",
                "measurement": "count",
                "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0},
                "timeframe_filter": {"type": "date", "operator": "in-the-last", "unit": "day", "quantity": 180},
                "metric_filters": null
              }
            ]
          },
          {
            "conditions": [
              {
                "type": "profile-metric",
                "metric_id": "W3AFKt",
                "measurement": "count",
                "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0},
                "timeframe_filter": {"type": "date", "operator": "in-the-last", "unit": "day", "quantity": 180},
                "metric_filters": null
              }
            ]
          },
          {
            "conditions": [
              {
                "type": "profile-metric",
                "metric_id": "XQ2zfW",
                "measurement": "count",
                "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0},
                "timeframe_filter": {"type": "date", "operator": "in-the-last", "unit": "day", "quantity": 180},
                "metric_filters": null
              }
            ]
          },
          {
            "conditions": [
              {
                "type": "profile-metric",
                "metric_id": "UfaNeY",
                "measurement": "count",
                "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0},
                "timeframe_filter": {"type": "date", "operator": "in-the-last", "unit": "day", "quantity": 180},
                "metric_filters": null
              }
            ]
          },
          {
            "conditions": [
              {
                "type": "profile-metric",
                "metric_id": "Sxnb5T",
                "measurement": "count",
                "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0},
                "timeframe_filter": {"type": "date", "operator": "in-the-last", "unit": "day", "quantity": 180},
                "metric_filters": null
              }
            ]
          },
          {
            "conditions": [
              {
                "type": "profile-metric",
                "metric_id": "UMyAwd",
                "measurement": "count",
                "measurement_filter": {"type": "numeric", "operator": "greater-than", "value": 0},
                "timeframe_filter": {"type": "date", "operator": "in-the-last", "unit": "day", "quantity": 180},
                "metric_filters": null
              }
            ]
          },
          {
            "conditions": [
              {
                "type": "profile-marketing-consent",
                "consent": {
                  "channel": "email",
                  "can_receive_marketing": true,
                  "consent_status": {
                    "subscription": "subscribed",
                    "filters": null
                  }
                }
              }
            ]
          }
        ]
      }
    }
  }
}
```

The new condition is the 6th group: `Received Email (UMyAwd) count > 0 in last 180d`.

**Expected count:** 25,000–32,000 (vs. 34,248 currently)

---

## Fix 4 — DROPPED

Cannot do retail-only filter on Viewed Product events because Klaviyo's JS data layer doesn't pass underscore-prefixed Shopify collections (`_retail`) to product-view events. Original RTzA5N is good enough for GAds — DPR creatives are retail anyway. Re-visit if/when Shopify→Klaviyo data layer is enhanced to include collection metadata on product views.

---

## After you authenticate

Tell me **"auth done"** and I'll execute the 3 POSTs in order, verify each created segment exists, pull profile counts, and report.

# Welcome Series — Visual Flow Diagram
*Bargain Chemist • Klaviyo flow `SehWRt` • No-coupon strategy*

---

## Recommended structure

```mermaid
flowchart TD
    Start([🌐 Trigger: Added to Website Form]) --> Wait0[⏱️ Wait 5 minutes]
    Wait0 --> E1[📧 Email 1<br/><b>Welcome to the Family</b><br/>Subject: Welcome to Bargain Chemist 👋]
    E1 --> Delay1[⏱️ Wait 1 day]
    Delay1 --> Check1{Placed Order<br/>since trigger?}
    Check1 -->|Yes| Exit1([✅ Exit flow])
    Check1 -->|No| E2[📧 Email 2<br/><b>Best Sellers</b><br/>Subject: Here's what's flying off our shelves]
    E2 --> Delay2[⏱️ Wait 2 days]
    Delay2 --> Check2{Placed Order<br/>since trigger?}
    Check2 -->|Yes| Exit2([✅ Exit flow])
    Check2 -->|No| E3[📧 Email 3<br/><b>Last Nudge</b><br/>Subject: 3 reasons NZ shops with us]
    E3 --> End([🏁 Flow complete])

    classDef email fill:#FF0031,color:#fff,stroke:#7B1523,stroke-width:2px
    classDef wait fill:#fef3c7,color:#92400e,stroke:#f59e0b
    classDef check fill:#dbeafe,color:#1e40af,stroke:#3b82f6
    classDef exit fill:#dcfce7,color:#166534,stroke:#22c55e
    class E1,E2,E3 email
    class Wait0,Delay1,Delay2 wait
    class Check1,Check2 check
    class Start,Exit1,Exit2,End exit
```

---

## Timeline view

```mermaid
gantt
    title Welcome Series — 3 emails over 3 days
    dateFormat HH
    axisFormat Day %d
    section Customer journey
    Signs up via website form        :milestone, m1, 00, 0h
    Email 1 — Welcome                :crit, e1, 00, 1h
    Email 2 — Best Sellers           :crit, after e1, 24h
    Email 3 — Last Nudge             :crit, after e2, 48h
```

---

## Step-by-step in Klaviyo (after deleting the 3 conditional splits)

| Step | Action type | Configuration |
|------|-------------|---------------|
| 1 | Trigger | Added to Website Form (existing — keep) |
| 2 | Time Delay | **5 minutes** (or set to 0 for immediate) |
| 3 | Send Email | Template: `BC — Welcome Email 1 — Welcome to the Family`<br/>Subject: `Welcome to Bargain Chemist, {{ first_name\|default:'there' }} 👋`<br/>From: `hello@bargainchemist.co.nz` |
| 4 | Time Delay | **1 day** |
| 5 | Conditional Split | "Placed Order at least once since starting this flow"<br/>YES → Exit • NO → continue |
| 6 | Send Email | Template: `BC — Welcome Email 2 — Best Sellers`<br/>Subject: `{{ first_name\|default:'There' }}, here's what's flying off our shelves` |
| 7 | Time Delay | **2 days** |
| 8 | Conditional Split | "Placed Order at least once since starting this flow"<br/>YES → Exit • NO → continue |
| 9 | Send Email | Template: `BC — Welcome Email 3 — Last Nudge`<br/>Subject: `{{ first_name\|default:'Still here' }} — 3 reasons NZ shops at Bargain Chemist` |

---

## How to view this diagram as a real picture

- **GitHub** — open this file on github.com → mermaid renders automatically
- **VS Code** — install the "Markdown Preview Mermaid Support" extension → Cmd/Ctrl+Shift+V on this file
- **Notion** — paste the mermaid block into a new "code" block and set language to `mermaid`
- **Online** — copy the mermaid code block and paste at https://mermaid.live for an instant preview

For a true rendered image, also see the companion HTML mockup at `welcome-flow-diagram.html` in this folder — just double-click to open in any browser.

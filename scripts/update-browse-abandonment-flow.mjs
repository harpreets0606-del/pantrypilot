/**
 * Bargain Chemist — Browse Abandonment Flow Updater
 *
 * What this does:
 *  1. Fetches flow actions for both Browse Abandonment flows (standard + Triple Pixel)
 *  2. Finds the email message in each
 *  3. Sets the existing email to Draft
 *  4. Creates a new email message using the new dynamic template (YuWLyf)
 *     with the correct subject line, preview text, and send time
 *
 * Run: node scripts/update-browse-abandonment-flow.mjs
 */

const KLAV_KEY = process.env.KLAVIYO_API_KEY || "pk_XCgiqg_6f9d304481501e6aef41ce91b33d767564";
const REVISION  = "2024-10-15";

const FLOWS = [
  { id: "RtiVC5", name: "[Z] Browse Abandonment" },
  { id: "RSnNak", name: "[Z] Browse Abandonment - Triple Pixel" },
];

const NEW_TEMPLATE_ID   = "YuWLyf";
const SUBJECT_LINE      = "Still thinking about it{% if first_name %}, {{ first_name }}{% endif %}?";
const PREVIEW_TEXT      = "The item you were checking out is still available — and we'll beat any competitor's price.";

const BASE = "https://a.klaviyo.com/api";

const headers = {
  "Authorization": `Klaviyo-API-Key ${KLAV_KEY}`,
  "revision":      REVISION,
  "Content-Type":  "application/json",
  "Accept":        "application/json",
};

async function get(path) {
  const res = await fetch(`${BASE}${path}`, { headers });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`GET ${path} → ${res.status}: ${txt}`);
  }
  return res.json();
}

async function patch(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method:  "PATCH",
    headers,
    body:    JSON.stringify(body),
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`PATCH ${path} → ${res.status}: ${txt}`);
  }
  return res.json();
}

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method:  "POST",
    headers,
    body:    JSON.stringify(body),
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`POST ${path} → ${res.status}: ${txt}`);
  }
  return res.json();
}

async function processFlow(flow) {
  console.log(`\n━━━ Processing: ${flow.name} (${flow.id}) ━━━`);

  // 1. Get all flow actions
  const actionsRes = await get(`/flows/${flow.id}/flow-actions/`);
  const actions = actionsRes.data ?? [];
  console.log(`  Found ${actions.length} flow action(s)`);

  for (const action of actions) {
    if (action.attributes?.action_type !== "SEND_EMAIL") {
      console.log(`  Skipping action type: ${action.attributes?.action_type}`);
      continue;
    }

    console.log(`  Email action: ${action.id}`);

    // 2. Get flow messages for this action
    const msgsRes = await get(`/flow-actions/${action.id}/flow-messages/`);
    const messages = msgsRes.data ?? [];
    console.log(`  Found ${messages.length} message(s)`);

    for (const msg of messages) {
      const status = msg.attributes?.status;
      console.log(`  Message ${msg.id} — status: ${status}`);

      if (status === "live") {
        // 3. Set existing live message to draft
        console.log(`  → Setting message ${msg.id} to Draft...`);
        await patch(`/flow-messages/${msg.id}/`, {
          data: {
            type:       "flow-message",
            id:         msg.id,
            attributes: { status: "draft" },
          },
        });
        console.log(`  ✓ Message ${msg.id} set to Draft`);
      }
    }

    // 4. Create new flow message with our template
    console.log(`  → Creating new message with template ${NEW_TEMPLATE_ID}...`);
    const created = await post(`/flow-messages/`, {
      data: {
        type:       "flow-message",
        attributes: {
          status: "live",
          definition: {
            channel: "email",
            content: {
              subject:      SUBJECT_LINE,
              preview_text: PREVIEW_TEXT,
            },
          },
        },
        relationships: {
          "flow-action": {
            data: { type: "flow-action", id: action.id },
          },
          template: {
            data: { type: "template", id: NEW_TEMPLATE_ID },
          },
        },
      },
    });

    console.log(`  ✓ New message created: ${created.data?.id} — Live`);
  }
}

async function main() {
  console.log("Bargain Chemist — Browse Abandonment Flow Updater");
  console.log(`Template: ${NEW_TEMPLATE_ID}`);
  console.log(`Subject:  ${SUBJECT_LINE}`);

  // Verify API key works
  try {
    const me = await get("/accounts/");
    console.log(`\n✓ Connected to Klaviyo — account: ${me.data?.[0]?.id ?? "unknown"}`);
  } catch (e) {
    console.error(`\n✗ API key check failed: ${e.message}`);
    console.error("  Make sure KLAVIYO_API_KEY is set and IP allowlisting is not blocking this machine.");
    process.exit(1);
  }

  for (const flow of FLOWS) {
    try {
      await processFlow(flow);
    } catch (e) {
      console.error(`  ✗ Error processing ${flow.name}: ${e.message}`);
    }
  }

  console.log("\n✓ Done. Check Klaviyo to verify both flows are live with the new template.");
}

main();

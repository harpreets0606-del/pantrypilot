"""
Patches the two Flu Season source templates (SMDszN and WALe6F) to replace
their non-standard footers with the standard Bargain Chemist footer:
  - "Get social with us!" heading
  - TikTok / Facebook / Instagram / LinkedIn icons
  - Red legal disclaimer block
  - Red unsubscribe block with org name and address

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py fix_flu_footer.py           # dry run - prints what would change
    py fix_flu_footer.py --apply   # applies the patches
"""

import os, sys, requests, time

API_KEY  = os.environ.get("KLAVIYO_API_KEY", "")
REVISION = "2024-10-15.pre"
BASE_URL = "https://a.klaviyo.com/api"
APPLY    = "--apply" in sys.argv

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Standard BC footer as table rows (fits inside any container table)
STANDARD_FOOTER_ROWS = """\
<!-- Footer: Get social -->
<tr>
<td align="center" style="padding:9px 18px; font-family:Helvetica,Arial,sans-serif; font-size:28px; font-weight:bold; color:#222222; text-align:center; background-color:#ffffff;">
Get social with us!
</td>
</tr>
<!-- Footer: Social icons -->
<tr>
<td align="center" style="padding:9px; background-color:#ffffff;">
<a href="https://tiktok.com/@bargainchemistnz" style="text-decoration:none; display:inline-block; margin:0 5px;" target="_blank">
<img alt="TikTok" src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/black/tiktok_96.png" style="width:48px; display:inline-block;" width="48"/>
</a>
<a href="https://www.facebook.com/BargainChemist/" style="text-decoration:none; display:inline-block; margin:0 5px;" target="_blank">
<img alt="Facebook" src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/black/facebook_96.png" style="width:48px; display:inline-block;" width="48"/>
</a>
<a href="https://instagram.com/bargainchemistnz" style="text-decoration:none; display:inline-block; margin:0 5px;" target="_blank">
<img alt="Instagram" src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/black/instagram_96.png" style="width:48px; display:inline-block;" width="48"/>
</a>
<a href="https://nz.linkedin.com/company/bargain-chemist" style="text-decoration:none; display:inline-block; margin:0 5px;" target="_blank">
<img alt="LinkedIn" src="https://d3k81ch9hvuctc.cloudfront.net/company/XCgiqg/images/791081ec-bce5-4d35-9ee4-aa35ada53088.png" style="width:48px; display:inline-block;" width="48"/>
</a>
</td>
</tr>
<!-- Footer: Legal disclaimer -->
<tr>
<td style="padding:15px 30px 9px; font-family:Helvetica,Arial,sans-serif; font-size:11px; color:#ffffff; line-height:1.3; text-align:center; font-weight:100; background-color:#FF0031;">
Please note that not all products may be available in all stores, please call your closest Bargain Chemist pharmacy or visit our store locator to find a
<a href="https://www.bargainchemist.co.nz/pages/find-a-store" style="color:#ffffff; text-decoration:underline;">pharmacy near you</a>.
Prices shown are online prices only and may differ to in store.
Save price, and Why Pay pricing is based on the recommended retailer price (RRP). Where no RRP is supplied, RRP is based on what is found at competing New Zealand retailers.
Actual delivered product packaging may differ slightly from the product image shown online.
<a href="https://www.bargainchemist.co.nz/pages/best-price-guarantee-our-policy-new-zealands-cheapest-chemist" style="color:#ffffff; text-decoration:underline;">Price beat guarantee</a>
- If you find a cheaper everyday price on an identical in stock item at a New Zealand pharmacy we will beat the difference by 10%.
*Vitamins and minerals are supplementary to and not a replacement for a balanced diet. Always read the label, use only as directed. If symptoms persist, see your healthcare professional.
Weight management products should be used with a balanced diet and exercise.
**Pharmacist only products - your pharmacist will advise you whether this preparation is suitable for your condition. The pharmacist reserves the right not to supply when contrary to our professional and ethical obligation.
</td>
</tr>
<!-- Footer: Unsubscribe -->
<tr>
<td align="center" style="padding:5px 18px 20px; font-family:Helvetica,Arial,sans-serif; font-size:11px; color:#ffffff; font-weight:100; text-align:center; line-height:1.1; background-color:#FF0031;">
No longer want to receive these emails? {% unsubscribe %}.<br/>
{{ organization.name }} {{ organization.full_address }}
</td>
</tr>"""


def get_template(tpl_id):
    r = requests.get(f"{BASE_URL}/templates/{tpl_id}", headers=HEADERS,
                     params={"fields[template]": "name,html"}, timeout=15)
    r.raise_for_status()
    attrs = r.json()["data"]["attributes"]
    return attrs["name"], attrs["html"]


def patch_template(tpl_id, name, html):
    payload = {"data": {"type": "template", "id": tpl_id,
                        "attributes": {"name": name, "html": html}}}
    r = requests.patch(f"{BASE_URL}/templates/{tpl_id}",
                       headers=HEADERS, json=payload, timeout=30)
    return r.ok, r.status_code


def fix_smd_szn(html: str) -> str:
    """
    SMDszN (Flu Season Email 1) uses a container table structure.
    Footer marker: <!-- FOOTER -->
    Closing tags after inner table rows: </table>\n</td></tr></table>\n</body>\n</html>
    """
    marker = "<!-- FOOTER -->"
    if marker not in html:
        raise ValueError("Footer marker not found in SMDszN")
    before = html[:html.index(marker)]
    closing = "\n</table>\n</td></tr></table>\n</body>\n</html>"
    return before + STANDARD_FOOTER_ROWS + closing


def fix_wa_le6f(html: str) -> str:
    """
    WALe6F (Flu Season Email 2) uses a wrapper table structure.
    Footer marker: <!-- ── FOOTER
    Closing tags: </table>\n<!-- /Email container -->\n</td></tr>\n</table>\n<!-- /Outer wrapper -->\n</body>\n</html>
    """
    # Find the footer comment (flexible — matches partial string)
    marker = None
    for candidate in ["<!-- ── FOOTER", "<!-- FOOTER", "<!-- footer"]:
        if candidate in html:
            marker = candidate
            break
    if not marker:
        raise ValueError("Footer marker not found in WALe6F")
    before = html[:html.index(marker)]
    closing = (
        "\n</table>\n"
        "<!-- /Email container -->\n"
        "</td></tr>\n"
        "</table>\n"
        "<!-- /Outer wrapper -->\n"
        "</body>\n</html>"
    )
    return before + STANDARD_FOOTER_ROWS + closing


TEMPLATES = [
    ("SMDszN", "[Z] Flow - Flu Season Email 1 (Immune Support)", fix_smd_szn),
    ("WALe6F", "[Z] Flow - Flu Season Email 2",                  fix_wa_le6f),
]


def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var.")
        sys.exit(1)

    mode = "APPLY" if APPLY else "DRY RUN"
    print(f"fix_flu_footer.py ({mode})\n")

    for tpl_id, expected_name, fixer in TEMPLATES:
        print(f"-- {expected_name} ({tpl_id}) --")
        try:
            name, html = get_template(tpl_id)
            print(f"  Fetched: {name} ({len(html):,} chars)")
        except Exception as e:
            print(f"  ERROR fetching: {e}")
            continue

        try:
            new_html = fixer(html)
        except ValueError as e:
            print(f"  ERROR: {e}")
            continue

        old_has_unsubscribe = "{% unsubscribe" in html
        new_has_unsubscribe = "{% unsubscribe" in new_html
        old_has_social = "tiktok_96.png" in html
        new_has_social = "tiktok_96.png" in new_html
        old_has_legal = "Please note that not all products" in html
        new_has_legal = "Please note that not all products" in new_html

        print(f"  Before: unsubscribe={old_has_unsubscribe}  social={old_has_social}  legal={old_has_legal}")
        print(f"  After:  unsubscribe={new_has_unsubscribe}  social={new_has_social}  legal={new_has_legal}")
        print(f"  Size change: {len(html):,} -> {len(new_html):,} chars")

        if APPLY:
            ok, status = patch_template(tpl_id, name, new_html)
            if ok:
                print(f"  Patched OK")
            else:
                print(f"  FAILED (HTTP {status})")
        else:
            print(f"  [DRY RUN] Would patch {tpl_id}")

        print()
        time.sleep(0.3)

    if not APPLY:
        print("Run with --apply to patch the templates.")


if __name__ == "__main__":
    main()

# Flow Messages — Extracted Content (2026-05-07 snapshot)

## Welcome Series, Email #2

- **File**: `QYfRCd-welcome-email2.json`
- **Subject**: 'See What Others Are Raving About 👇'
- **Preview**: 'Top picks + real reviews to help you choose.'
- **From**: `hello@bargainchemist.co.nz` (label: 'Bargain Chemist')
- **Reply-to**: ''
- **Body**: 93,300 HTML chars, 571 words of visible text

**Body text excerpt**:

> Free Shipping on Orders over $79* Shop Products Clearance Find a Pharmacy Contact Us Hi {{ first_name|default:'there' }}, Explore Kiwi favourites - vetted and loved. From health essentials to beauty must-haves, these are the products that keep popping up in carts and getting 5 ★ reviews from real customers. {% if feeds.Best_Selling_No_Clearance|index:0 %} {% with item=feeds.Best_Selling_No_Clearance|index:0%} {% with Title=item.title|safe Price=item.price|default:"" Compare_at=item.regular_price|default:"" %} {{ Title }} {{ Price }} Buy Now {% endwith %} {% endwith %} {% endif %} {% if feeds.B...

**Brand cues**:

- Hex colours: #000000, #0645ad, #222222, #2A2A2A, #363636, #861628, #EE2737, #FAFAFA, #FDDDD9, #FF0031, #FFFFFF, #f7f7f7, #ffffff
- Fonts: 'Arial Black', 'Arial Bold', Gadget, sans-serif, Helvetica, Arial, Helvetica, Arial, sans-serif, Helvetica,Arial, Ubuntu, Helvetica, Arial, sans-serif
- Button texts: 
 | 

- Sample image URLs: https://d3k81ch9hvuctc.cloudfront.net/company/XCgiqg/images/7f95167c-f567-4494-aeb2-c188e0af097c.png, https://d3k81ch9hvuctc.cloudfront.net/company/XCgiqg/images/73bfda85-312a-4adc-a242-7bf95585bf06.png, https://d3k81ch9hvuctc.cloudfront.net/company/XCgiqg/images/15d09b1b-d7a7-472b-8c0c-c31b7c25424c.png
- Linked URLs (unique): https://instagram.com/bargainchemistnz, https://nz.linkedin.com/company/bargain-chemist, https://www.bargainchemist.co.nz/, https://www.bargainchemist.co.nz/collections/allergies-hay-fever-sinus, https://www.bargainchemist.co.nz/collections/best-selling-collection, https://www.bargainchemist.co.nz/collections/clearance-deals, https://www.bargainchemist.co.nz/collections/cold-flu, https://www.bargainchemist.co.nz/collections/fragrances

---

## [Z] Added to Cart Abandonment Email #1

- **File**: `TCgQED-cart-email1.json`
- **Subject**: 'This one’s popular for a reason'
- **Preview**: 'Just popping in - your item’s still waiting.'
- **From**: `hello@bargainchemist.co.nz` (label: 'Bargain Chemist')
- **Reply-to**: ''
- **Body**: 66,330 HTML chars, 280 words of visible text

**Body text excerpt**:

> Free Shipping on Orders over $79* Shop Products Clearance Find a Pharmacy Contact Us Hi {{ first_name|default:'there' }}, You added this to your cart — just popping by in case you were interrupted. It’s a popular pick, and one that customers come back to time and time again. {{ event|lookup:'Product Name'|default:'' }} Quantity: {{ event.Quantity|default:'' }} Price: {% currency_format event|lookup:'Price'|floatformat:2 %} Return To Your Cart Need Some Help? Contact Us Get Social With Us No longer want to receive these emails? {% unsubscribe %}. {{ organization.name }} {{ organization.full_add...

**Brand cues**:

- Hex colours: #000000, #0645ad, #222222, #33439c, #861628, #FAFAFA, #FF0031, #FFFFFF, #f7f7f7, #ffffff
- Fonts: 'Arial Black', 'Arial Bold', Gadget, sans-serif, Arial, "Helvetica Neue", Helvetica, sans-serif, Arial, 'Helvetica Neue', Helvetica, sans-serif, Helvetica, Arial, Helvetica, Arial, sans-serif
- Button texts: 
 | 

- Sample image URLs: https://d3k81ch9hvuctc.cloudfront.net/company/XCgiqg/images/7f95167c-f567-4494-aeb2-c188e0af097c.png, https://d3k81ch9hvuctc.cloudfront.net/company/XCgiqg/images/73bfda85-312a-4adc-a242-7bf95585bf06.png, {{ event.ImageURL }}
- Linked URLs (unique): https://instagram.com/bargainchemistnz, https://nz.linkedin.com/company/bargain-chemist, https://www.bargainchemist.co.nz/, https://www.bargainchemist.co.nz/cart, https://www.bargainchemist.co.nz/collections/allergies-hay-fever-sinus, https://www.bargainchemist.co.nz/collections/clearance-deals, https://www.bargainchemist.co.nz/collections/cold-flu, https://www.bargainchemist.co.nz/collections/fragrances

---

## Email #2

- **File**: `TpkzDd-cart-email2.json`
- **Subject**: 'Your cart’s still saved'
- **Preview**: 'No pressure — just a quick reminder.'
- **From**: `hello@bargainchemist.co.nz` (label: 'Bargain Chemist')
- **Reply-to**: 'hello@bargainchemist.co.nz'
- **Body**: 67,124 HTML chars, 311 words of visible text

**Body text excerpt**:

> Free Shipping on Orders over $79* Shop Products Clearance Find a Pharmacy Contact Us Hi {{ first_name|default:'there' }}, Your cart’s still saved if you’re ready to continue. This product is a favourite for good reason: great quality, great value, and trusted by customers across NZ. {{ event|lookup:'Product Name'|default:'' }} Quantity: {{ event.Quantity|default:'' }} Price: {% currency_format event|lookup:'Price'|floatformat:2 %} Return To Your Cart Need Some Help? Contact Us Get Social With Us No longer want to receive these emails? {% unsubscribe %}. {{ organization.name }} {{ organization....

**Brand cues**:

- Hex colours: #000000, #0645ad, #222222, #33439c, #861628, #888888, #FAFAFA, #FF0031, #FFFFFF, #aaaaaa, #f4f4f4, #f7f7f7, #ffffff
- Fonts: 'Arial Black', 'Arial Bold', Gadget, sans-serif, Arial, "Helvetica Neue", Helvetica, sans-serif, Arial, 'Helvetica Neue', Helvetica, sans-serif, Arial,Helvetica,sans-serif, Helvetica, Arial
- Button texts: 
 | 

- Sample image URLs: https://d3k81ch9hvuctc.cloudfront.net/company/XCgiqg/images/7f95167c-f567-4494-aeb2-c188e0af097c.png, https://d3k81ch9hvuctc.cloudfront.net/company/XCgiqg/images/73bfda85-312a-4adc-a242-7bf95585bf06.png, {{ event.ImageURL }}
- Linked URLs (unique): https://instagram.com/bargainchemistnz, https://nz.linkedin.com/company/bargain-chemist, https://www.bargainchemist.co.nz/, https://www.bargainchemist.co.nz/cart, https://www.bargainchemist.co.nz/collections/allergies-hay-fever-sinus, https://www.bargainchemist.co.nz/collections/clearance-deals, https://www.bargainchemist.co.nz/collections/cold-flu, https://www.bargainchemist.co.nz/collections/fragrances

---

## Welcome Series, Email #1

- **File**: `U2HQmW-welcome-email1.json`
- **Subject**: 'Thanks for signing up to Bargain Chemist!'
- **Preview**: 'Welcome to Bargain Chemist'
- **From**: `hello@bargainchemist.co.nz` (label: 'Bargain Chemist')
- **Reply-to**: ''
- **Body**: 86,553 HTML chars, 512 words of visible text

**Body text excerpt**:

> Free Shipping on Orders over $79* Shop Products Clearance Find a Pharmacy Contact Us Hi {{ first_name|default:'there' }}, Welcome to Bargain Chemist - Where Kiwi prices meet everyday essentials. Thanks for joining us! Bargain Chemist is 100% Kiwi owned - which means we work hard every day to bring you great health, beauty, and wellness products at prices you’ll love. To help us tailor these emails just for you, tell us a little about how we can help care for you and your family by updating your email preferences by clicking the button below. {% manage_preferences 'Your Preferences' %} {% if fe...

**Brand cues**:

- Hex colours: #000000, #0645ad, #222222, #2A2A2A, #363636, #861628, #EE2737, #FAFAFA, #FDDDD9, #FF0031, #FFFFFF, #f7f7f7, #ffffff
- Fonts: 'Arial Black', 'Arial Bold', Gadget, sans-serif, Helvetica, Arial, Helvetica, Arial, sans-serif, Helvetica,Arial, Ubuntu, Helvetica, Arial, sans-serif
- Button texts: 
 | 

- Sample image URLs: https://d3k81ch9hvuctc.cloudfront.net/company/XCgiqg/images/7f95167c-f567-4494-aeb2-c188e0af097c.png, https://d3k81ch9hvuctc.cloudfront.net/company/XCgiqg/images/c69415b6-3ee8-4a84-b4b1-9a63274ab1e3.png, https://d3k81ch9hvuctc.cloudfront.net/company/XCgiqg/images/15d09b1b-d7a7-472b-8c0c-c31b7c25424c.png
- Linked URLs (unique): https://instagram.com/bargainchemistnz, https://nz.linkedin.com/company/bargain-chemist, https://www.bargainchemist.co.nz/, https://www.bargainchemist.co.nz/collections/allergies-hay-fever-sinus, https://www.bargainchemist.co.nz/collections/clearance-deals, https://www.bargainchemist.co.nz/collections/cold-flu, https://www.bargainchemist.co.nz/collections/fragrances, https://www.bargainchemist.co.nz/collections/home-household

---

## [Z] Welcome - Email 1 - Welcome

- **File**: `UC2XAR-welcome-nocoupon-email1.json`
- **Subject**: "Welcome to Bargain Chemist, {{ first_name|default:'there' }}!"
- **Preview**: ''
- **From**: `hello@bargainchemist.co.nz` (label: 'Bargain Chemist')
- **Reply-to**: 'orders@bargainchemist.co.nz'
- **Body**: 8,884 HTML chars, 233 words of visible text

**Body text excerpt**:

> Shop Now | Find a Pharmacy Welcome Great to have you, {{ first_name|default:'there' }}! You've just joined NZ's most trusted pharmacy family. Hi {{ first_name|default:'there' }}, Thanks for signing up to Bargain Chemist. Whether you're after vitamins, skincare, haircare, baby products, or everyday essentials — we've got you covered with NZ's lowest prices. And our promise is simple: we'll beat any pharmacy price in New Zealand by 10%. So you always get the best deal, every time. Start Shopping 🏆 Price Beat Guarantee Beat any NZ pharmacy price by 10% 🚚 Free Shipping On all orders over $79 💊 Exp...

**Brand cues**:

- Hex colours: #222222, #333333, #666666, #FF0031, #eeeeee, #f7f7f7, #f9f9f9, #ffffff
- Fonts: Helvetica,Arial,sans-serif
- Button texts: 
- Sample image URLs: https://d3k81ch9hvuctc.cloudfront.net/company/XCgiqg/images/65fb5fbb-6bce-4df9-995e-bfa1bad9d04d.png, https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/black/tiktok_96.png, https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/black/facebook_96.png
- Linked URLs (unique): https://instagram.com/bargainchemistnz, https://nz.linkedin.com/company/bargain-chemist, https://tiktok.com/@bargainchemistnz, https://www.bargainchemist.co.nz/, https://www.bargainchemist.co.nz/collections/all, https://www.bargainchemist.co.nz/pages/best-price-guarantee-our-policy-new-zealands-cheapest-chemist, https://www.bargainchemist.co.nz/pages/find-a-store, https://www.facebook.com/BargainChemist/

---

## Email #6

- **File**: `VJwtx3-welcome-email6.json`
- **Subject**: 'Your Local Bargain Chemist is Ready to Help 👋'
- **Preview**: 'Discover in-store benefits & what’s waiting nearby.'
- **From**: `hello@bargainchemist.co.nz` (label: 'Bargain Chemist')
- **Reply-to**: 'hello@bargainchemist.co.nz'
- **Body**: 52,177 HTML chars, 314 words of visible text

**Body text excerpt**:

> Free Shipping on Orders over $79* Shop Products Clearance Find a Pharmacy Contact Us Hi {{ first_name|default:'there' }}, Whether you’re after quick advice, prescription support, or local pick-up, your Bargain Chemist team is just around the corner. Our pharmacists are friendly, knowledgeable and ready to help with all of life’s health needs - from vitamins to skincare and everything in between. Find your nearest store Need Some Help? Contact Us Get Social With Us No longer want to receive these emails? {% unsubscribe %}. {{ organization.name }} {{ organization.full_address }} Please note that...

**Brand cues**:

- Hex colours: #000000, #0645ad, #222222, #363636, #861628, #888888, #FAFAFA, #FF0031, #FFFFFF, #aaaaaa, #f4f4f4, #f7f7f7, #ffffff
- Fonts: 'Arial Black', 'Arial Bold', Gadget, sans-serif, Arial,Helvetica,sans-serif, Helvetica, Arial, Helvetica, Arial, sans-serif, Helvetica,Arial
- Button texts: 
 | 

- Sample image URLs: https://d3k81ch9hvuctc.cloudfront.net/company/XCgiqg/images/7f95167c-f567-4494-aeb2-c188e0af097c.png, https://d3k81ch9hvuctc.cloudfront.net/company/XCgiqg/images/73bfda85-312a-4adc-a242-7bf95585bf06.png, https://d3k81ch9hvuctc.cloudfront.net/company/XCgiqg/images/50378b7a-4441-41bc-b98d-968918cafd76.png
- Linked URLs (unique): https://instagram.com/bargainchemistnz, https://nz.linkedin.com/company/bargain-chemist, https://www.bargainchemist.co.nz/, https://www.bargainchemist.co.nz/collections/clearance-deals, https://www.bargainchemist.co.nz/pages/best-price-guarantee-our-policy-new-zealands-cheapest-chemist, https://www.bargainchemist.co.nz/pages/contact, https://www.bargainchemist.co.nz/pages/find-a-store, https://www.bargainchemist.co.nz/policies/shipping-policy

---

## [Z] Post-Purchase Email 1

- **File**: `XJENuf-order-confirm-email1.json`
- **Subject**: "{{ person.first_name|default:'friend' }}, order confirmed!"
- **Preview**: "Your order is confirmed and being prepared. Here's what happens next."
- **From**: `hello@bargainchemist.co.nz` (label: 'Bargain Chemist')
- **Reply-to**: 'orders@bargainchemist.co.nz'
- **Body**: 11,914 HTML chars, 332 words of visible text

**Body text excerpt**:

> Your order is confirmed Free Shipping on Orders over $79* Shop Products Clearance Find a Pharmacy Contact Us Order received You're all sorted, {{ first_name|default:'friend' }}! Your Bargain Chemist order is confirmed — saving New Zealanders every day Hi {{ first_name|default:'there' }}, Great news — your order has been received and is being processed. Here's what happens next: 1 Processing — We're picking and packing your order right now 2 Dispatch — You'll receive a shipping notification once it's on its way 3 Delivery — Your order will arrive at your door. Standard NZ delivery applies Need ...

**Brand cues**:

- Hex colours: #1a1a1a, #222222, #333333, #7B1523, #CC1B2A, #FF0031, #f5f5f5, #fef6f7, #ffffff
- Fonts: Helvetica,Arial,sans-serif
- Button texts: 
- Sample image URLs: https://cdn.shopify.com/s/files/1/0317/1926/0297/files/logo-2025.png?v=1747706218, https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/black/tiktok_96.png, https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/black/facebook_96.png
- Linked URLs (unique): https://instagram.com/bargainchemistnz, https://nz.linkedin.com/company/bargain-chemist, https://tiktok.com/@bargainchemistnz, https://www.bargainchemist.co.nz, https://www.bargainchemist.co.nz/collections/all, https://www.bargainchemist.co.nz/collections/clearance, https://www.bargainchemist.co.nz/pages/best-price-guarantee-our-policy-new-zealands-cheapest-chemist, https://www.bargainchemist.co.nz/pages/contact

---


(function () {
  'use strict';

  var script = document.currentScript;
  var COMPANY_ID = (script && script.dataset.klaviyoCompanyId) || 'XCgiqg';
  var LIST_ID = (script && script.dataset.klaviyoListId) || 'RhChwn';
  var ENDPOINT =
    'https://a.klaviyo.com/client/back-in-stock-subscriptions/?company_id=' +
    encodeURIComponent(COMPANY_ID);
  var REVISION = '2024-10-15';

  function init() {
    document.querySelectorAll('[data-kl-bis]').forEach(setupContainer);
    document.addEventListener('variant:change', onVariantChange);
    document.addEventListener('variantChange', onVariantChange);
  }

  function setupContainer(container) {
    var available = container.dataset.variantAvailable === 'true';
    container.hidden = available;
    if (available) return;

    var form = container.querySelector('[data-kl-bis-form]');
    if (!form || form.dataset.klBisBound === '1') return;
    form.dataset.klBisBound = '1';
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      submit(container, form);
    });
  }

  function onVariantChange(event) {
    var variant = event && event.detail && (event.detail.variant || event.detail);
    if (!variant || !variant.id) return;
    document.querySelectorAll('[data-kl-bis]').forEach(function (container) {
      container.dataset.variantId = String(variant.id);
      container.dataset.variantTitle = variant.title || '';
      container.dataset.variantAvailable = variant.available ? 'true' : 'false';
      var nameEl = container.querySelector('[data-kl-bis-variant-name]');
      if (nameEl) nameEl.textContent = variant.title || '';
      var msg = container.querySelector('[data-kl-bis-msg]');
      if (msg) {
        msg.textContent = '';
        msg.className = 'kl-bis__msg';
      }
      container.hidden = !!variant.available;
    });
  }

  function submit(container, form) {
    var emailEl = form.querySelector('[data-kl-bis-email]');
    var phoneEl = form.querySelector('[data-kl-bis-phone]');
    var marketingEl = form.querySelector('[data-kl-bis-marketing]');
    var msg = form.querySelector('[data-kl-bis-msg]');
    var btn = form.querySelector('[data-kl-bis-submit]');

    var email = (emailEl && emailEl.value || '').trim();
    var phone = (phoneEl && phoneEl.value || '').trim();
    var marketingOptIn = !!(marketingEl && marketingEl.checked);

    if (!email && !phone) {
      showMsg(msg, 'Please enter an email or mobile number.', 'error');
      return;
    }
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      showMsg(msg, 'Please enter a valid email address.', 'error');
      return;
    }
    var variantId = container.dataset.variantId;
    if (!variantId) {
      showMsg(msg, 'Could not detect the product variant. Please refresh the page.', 'error');
      return;
    }

    var profile = { type: 'profile', attributes: {} };
    if (email) profile.attributes.email = email;
    if (phone) profile.attributes.phone_number = normalisePhone(phone);

    var payload = {
      data: {
        type: 'back-in-stock-subscription',
        attributes: {
          channels: buildChannels(email, phone),
          profile: { data: profile }
        },
        relationships: {
          variant: {
            data: { type: 'catalog-variant', id: '$shopify:::$default:::' + variantId }
          }
        }
      }
    };

    btn.disabled = true;
    showMsg(msg, 'Submitting…', '');

    fetch(ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        revision: REVISION
      },
      body: JSON.stringify(payload)
    })
      .then(function (res) {
        if (res.status === 202 || res.ok) return null;
        return res.json().then(
          function (body) {
            throw new Error(extractError(body) || 'Subscription failed (' + res.status + ').');
          },
          function () {
            throw new Error('Subscription failed (' + res.status + ').');
          }
        );
      })
      .then(function () {
        if (marketingOptIn && (email || phone)) {
          return subscribeToList(email, phone).catch(function () {});
        }
      })
      .then(function () {
        showMsg(msg, "You're on the list. We'll let you know as soon as it's back.", 'success');
        form.reset();
      })
      .catch(function (err) {
        showMsg(msg, err.message || 'Something went wrong. Please try again.', 'error');
      })
      .finally(function () {
        btn.disabled = false;
      });
  }

  function buildChannels(email, phone) {
    var channels = [];
    if (email) channels.push('EMAIL');
    if (phone) channels.push('SMS');
    return channels;
  }

  function subscribeToList(email, phone) {
    var subscriptions = {};
    if (email) subscriptions.email = { marketing: { consent: 'SUBSCRIBED' } };
    if (phone) subscriptions.sms = { marketing: { consent: 'SUBSCRIBED' } };

    var profile = { type: 'profile', attributes: { subscriptions: subscriptions } };
    if (email) profile.attributes.email = email;
    if (phone) profile.attributes.phone_number = normalisePhone(phone);

    var body = {
      data: {
        type: 'profile-subscription-bulk-create-job',
        attributes: {
          profiles: { data: [profile] },
          historical_import: false
        },
        relationships: {
          list: { data: { type: 'list', id: LIST_ID } }
        }
      }
    };

    return fetch(
      'https://a.klaviyo.com/client/subscriptions/?company_id=' + encodeURIComponent(COMPANY_ID),
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', revision: REVISION },
        body: JSON.stringify(body)
      }
    );
  }

  function normalisePhone(raw) {
    var trimmed = raw.replace(/[^\d+]/g, '');
    if (!trimmed) return '';
    if (trimmed.charAt(0) === '+') return trimmed;
    if (trimmed.indexOf('0') === 0) return '+64' + trimmed.slice(1);
    return '+' + trimmed;
  }

  function extractError(body) {
    try {
      if (body && body.errors && body.errors.length) {
        return body.errors.map(function (e) { return e.detail || e.title; }).join(' ');
      }
    } catch (_) {}
    return null;
  }

  function showMsg(el, text, kind) {
    if (!el) return;
    el.textContent = text;
    el.className = 'kl-bis__msg' + (kind ? ' kl-bis__msg--' + kind : '');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

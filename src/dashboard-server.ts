import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import { BetaAnalyticsDataClient } from '@google-analytics/data';
import { GoogleAdsApi, enums } from 'google-ads-api';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.DASHBOARD_PORT || 3030;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

// ── GA4 client ─────────────────────────────────────────────────────────────

function getGA4Client() {
  return new BetaAnalyticsDataClient({
    credentials: {
      client_email: process.env.GA4_CLIENT_EMAIL,
      private_key: process.env.GA4_PRIVATE_KEY?.replace(/\\n/g, '\n'),
    },
  });
}

// ── Google Ads client ───────────────────────────────────────────────────────

function getAdsClient() {
  return new GoogleAdsApi({
    client_id: process.env.GOOGLE_ADS_CLIENT_ID!,
    client_secret: process.env.GOOGLE_ADS_CLIENT_SECRET!,
    developer_token: process.env.GOOGLE_ADS_DEVELOPER_TOKEN!,
  });
}

// ── Routes ──────────────────────────────────────────────────────────────────

app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// GA4: overview metrics (sessions, users, pageviews, bounce rate)
app.get('/api/ga4/overview', async (req, res) => {
  try {
    const propertyId = process.env.GA4_PROPERTY_ID;
    if (!propertyId) return res.status(500).json({ error: 'GA4_PROPERTY_ID not configured' });

    const client = getGA4Client();
    const dateRange = (req.query.range as string) || '7daysAgo';

    const [response] = await client.runReport({
      property: `properties/${propertyId}`,
      dateRanges: [{ startDate: dateRange, endDate: 'today' }],
      metrics: [
        { name: 'sessions' },
        { name: 'totalUsers' },
        { name: 'screenPageViews' },
        { name: 'bounceRate' },
        { name: 'averageSessionDuration' },
        { name: 'conversions' },
      ],
    });

    const row = response.rows?.[0]?.metricValues ?? [];
    res.json({
      sessions: parseInt(row[0]?.value ?? '0'),
      users: parseInt(row[1]?.value ?? '0'),
      pageviews: parseInt(row[2]?.value ?? '0'),
      bounceRate: parseFloat(row[3]?.value ?? '0').toFixed(2),
      avgSessionDuration: parseFloat(row[4]?.value ?? '0').toFixed(0),
      conversions: parseInt(row[5]?.value ?? '0'),
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// GA4: daily sessions trend
app.get('/api/ga4/trend', async (req, res) => {
  try {
    const propertyId = process.env.GA4_PROPERTY_ID;
    if (!propertyId) return res.status(500).json({ error: 'GA4_PROPERTY_ID not configured' });

    const client = getGA4Client();
    const dateRange = (req.query.range as string) || '30daysAgo';

    const [response] = await client.runReport({
      property: `properties/${propertyId}`,
      dateRanges: [{ startDate: dateRange, endDate: 'today' }],
      dimensions: [{ name: 'date' }],
      metrics: [{ name: 'sessions' }, { name: 'totalUsers' }],
      orderBys: [{ dimension: { dimensionName: 'date' } }],
    });

    const data = (response.rows ?? []).map((row) => ({
      date: row.dimensionValues?.[0]?.value,
      sessions: parseInt(row.metricValues?.[0]?.value ?? '0'),
      users: parseInt(row.metricValues?.[1]?.value ?? '0'),
    }));

    res.json(data);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// GA4: top pages
app.get('/api/ga4/top-pages', async (req, res) => {
  try {
    const propertyId = process.env.GA4_PROPERTY_ID;
    if (!propertyId) return res.status(500).json({ error: 'GA4_PROPERTY_ID not configured' });

    const client = getGA4Client();

    const [response] = await client.runReport({
      property: `properties/${propertyId}`,
      dateRanges: [{ startDate: '7daysAgo', endDate: 'today' }],
      dimensions: [{ name: 'pagePath' }],
      metrics: [{ name: 'screenPageViews' }, { name: 'averageSessionDuration' }],
      orderBys: [{ metric: { metricName: 'screenPageViews' }, desc: true }],
      limit: 10,
    });

    const data = (response.rows ?? []).map((row) => ({
      page: row.dimensionValues?.[0]?.value,
      views: parseInt(row.metricValues?.[0]?.value ?? '0'),
      avgDuration: parseFloat(row.metricValues?.[1]?.value ?? '0').toFixed(0),
    }));

    res.json(data);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// GA4: traffic sources
app.get('/api/ga4/sources', async (req, res) => {
  try {
    const propertyId = process.env.GA4_PROPERTY_ID;
    if (!propertyId) return res.status(500).json({ error: 'GA4_PROPERTY_ID not configured' });

    const client = getGA4Client();

    const [response] = await client.runReport({
      property: `properties/${propertyId}`,
      dateRanges: [{ startDate: '7daysAgo', endDate: 'today' }],
      dimensions: [{ name: 'sessionDefaultChannelGroup' }],
      metrics: [{ name: 'sessions' }],
      orderBys: [{ metric: { metricName: 'sessions' }, desc: true }],
    });

    const data = (response.rows ?? []).map((row) => ({
      source: row.dimensionValues?.[0]?.value,
      sessions: parseInt(row.metricValues?.[0]?.value ?? '0'),
    }));

    res.json(data);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// Google Ads: campaign performance
app.get('/api/ads/campaigns', async (req, res) => {
  try {
    const customerId = process.env.GOOGLE_ADS_CUSTOMER_ID;
    const refreshToken = process.env.GOOGLE_ADS_REFRESH_TOKEN;
    if (!customerId || !refreshToken) {
      return res.status(500).json({ error: 'Google Ads credentials not configured' });
    }

    const client = getAdsClient();
    const customer = client.Customer({
      customer_id: customerId,
      refresh_token: refreshToken,
    });

    const dateRange = (req.query.range as string) || 'LAST_7_DAYS';

    const campaigns = await customer.report({
      entity: 'campaign',
      attributes: ['campaign.id', 'campaign.name', 'campaign.status'],
      metrics: [
        'metrics.impressions',
        'metrics.clicks',
        'metrics.cost_micros',
        'metrics.ctr',
        'metrics.conversions',
        'metrics.conversions_value',
        'metrics.average_cpc',
      ],
      segments: [],
      constraints: {
        'campaign.status': enums.CampaignStatus.ENABLED,
      },
      date_constant: dateRange as any,
      limit: 20,
    });

    const data = campaigns.map((c: any) => ({
      id: c.campaign.id,
      name: c.campaign.name,
      status: c.campaign.status,
      impressions: c.metrics.impressions,
      clicks: c.metrics.clicks,
      cost: (c.metrics.cost_micros / 1_000_000).toFixed(2),
      ctr: (c.metrics.ctr * 100).toFixed(2),
      conversions: c.metrics.conversions,
      conversionValue: c.metrics.conversions_value?.toFixed(2),
      avgCpc: (c.metrics.average_cpc / 1_000_000).toFixed(2),
    }));

    res.json(data);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// Google Ads: account-level summary
app.get('/api/ads/summary', async (req, res) => {
  try {
    const customerId = process.env.GOOGLE_ADS_CUSTOMER_ID;
    const refreshToken = process.env.GOOGLE_ADS_REFRESH_TOKEN;
    if (!customerId || !refreshToken) {
      return res.status(500).json({ error: 'Google Ads credentials not configured' });
    }

    const client = getAdsClient();
    const customer = client.Customer({
      customer_id: customerId,
      refresh_token: refreshToken,
    });

    const dateRange = (req.query.range as string) || 'LAST_7_DAYS';

    const rows = await customer.report({
      entity: 'customer',
      metrics: [
        'metrics.impressions',
        'metrics.clicks',
        'metrics.cost_micros',
        'metrics.ctr',
        'metrics.conversions',
        'metrics.conversions_value',
        'metrics.average_cpc',
        'metrics.search_impression_share',
      ],
      date_constant: dateRange as any,
    });

    const m = rows[0]?.metrics ?? {};
    res.json({
      impressions: m.impressions ?? 0,
      clicks: m.clicks ?? 0,
      cost: ((m.cost_micros ?? 0) / 1_000_000).toFixed(2),
      ctr: ((m.ctr ?? 0) * 100).toFixed(2),
      conversions: m.conversions ?? 0,
      conversionValue: (m.conversions_value ?? 0).toFixed(2),
      avgCpc: ((m.average_cpc ?? 0) / 1_000_000).toFixed(2),
      impressionShare: ((m.search_impression_share ?? 0) * 100).toFixed(1),
      roas: m.cost_micros
        ? ((m.conversions_value ?? 0) / (m.cost_micros / 1_000_000)).toFixed(2)
        : '0',
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// Google Ads: daily spend trend
app.get('/api/ads/trend', async (req, res) => {
  try {
    const customerId = process.env.GOOGLE_ADS_CUSTOMER_ID;
    const refreshToken = process.env.GOOGLE_ADS_REFRESH_TOKEN;
    if (!customerId || !refreshToken) {
      return res.status(500).json({ error: 'Google Ads credentials not configured' });
    }

    const client = getAdsClient();
    const customer = client.Customer({
      customer_id: customerId,
      refresh_token: refreshToken,
    });

    const rows = await customer.report({
      entity: 'customer',
      metrics: ['metrics.clicks', 'metrics.cost_micros', 'metrics.conversions'],
      segments: ['segments.date'],
      date_constant: 'LAST_30_DAYS' as any,
      order_by: [{ field: 'segments.date', sort_order: 'ASC' }],
    });

    const data = rows.map((r: any) => ({
      date: r.segments.date,
      clicks: r.metrics.clicks,
      cost: ((r.metrics.cost_micros ?? 0) / 1_000_000).toFixed(2),
      conversions: r.metrics.conversions,
    }));

    res.json(data);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`Bargain Chemist Dashboard running at http://localhost:${PORT}`);
});

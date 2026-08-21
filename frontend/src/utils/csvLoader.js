/**
 * CSV Loader Utility for direct client-side static CSV fetching & data processing
 */

export function parseCSV(csvText) {
  const lines = csvText.trim().split('\n');
  if (lines.length === 0) return [];
  
  const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
  
  return lines.slice(1).map(line => {
    // Handle comma inside quoted fields if needed
    const values = line.split(',').map(v => v.trim().replace(/^"|"$/g, ''));
    const row = {};
    headers.forEach((header, index) => {
      row[header] = values[index];
    });
    return row;
  });
}

export async function loadEntropyScores() {
  try {
    const baseUrl = import.meta.env.BASE_URL || '/';
    const csvUrl = `${baseUrl.endsWith('/') ? baseUrl : baseUrl + '/'}hcp_entropy_scores.csv`;
    const response = await fetch(csvUrl);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const text = await response.text();
    return parseCSV(text);
  } catch (error) {
    console.error("Error loading hcp_entropy_scores.csv:", error);
    return [];
  }
}

export async function loadMLRecommendations() {
  try {
    const baseUrl = import.meta.env.BASE_URL || '/';
    const csvUrl = `${baseUrl.endsWith('/') ? baseUrl : baseUrl + '/'}hcp_ml_recommendations.csv`;
    const response = await fetch(csvUrl);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const text = await response.text();
    return parseCSV(text);
  } catch (error) {
    console.error("Error loading hcp_ml_recommendations.csv:", error);
    return [];
  }
}

const CHANNEL_MAP = {
  "rep_visit": "Rep Visit",
  "phone_call": "Phone Call",
  "webinar": "Webinar",
  "email": "Email",
  "digital_ad": "Digital Ad",
  "Rep Visit": "Rep Visit",
  "Phone Call": "Phone Call",
  "Webinar": "Webinar",
  "Email": "Email",
  "Digital Ad": "Digital Ad"
};

export function formatChannelName(ch) {
  return CHANNEL_MAP[ch] || ch || "Rep Visit";
}

export function formatSpecialty(spec) {
  if (!spec) return "General";
  return spec.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}

export function getAllHcpsFromCSV(entropyRows) {
  return entropyRows.map(row => {
    const score = parseFloat(row.entropy_weighted_score) || 0;
    return {
      hcp_id: String(row.hcp_id),
      first_name: row.first_name || '',
      last_name: row.last_name || '',
      specialty: formatSpecialty(row.specialty),
      overall_engagement_score_100: score,
      segment: row.segment || 'low_value',
      opt_out_flag: row.opt_out_flag === 'True' || row.opt_out_flag === 'true',
      recommended_channel: formatChannelName(row.recommended_channel || row.ml_primary_channel)
    };
  }).sort((a, b) => b.overall_engagement_score_100 - a.overall_engagement_score_100);
}

export function getHcpStatsFromCSV(entropyRows) {
  const total = entropyRows.length;
  let optedOut = 0;
  let highly = 0;
  let moderately = 0;
  let low = 0;
  let disengaged = 0;

  entropyRows.forEach(row => {
    const isOptOut = row.opt_out_flag === 'True' || row.opt_out_flag === 'true';
    const score = parseFloat(row.entropy_weighted_score) || 0;

    if (isOptOut) optedOut++;
    if (score >= 70) highly++;
    else if (score >= 40) moderately++;
    else if (score >= 1) low++;
    else disengaged++;
  });

  return {
    total_hcps: total,
    eligible_hcps: total - optedOut,
    opted_out: optedOut,
    highly_engaged_hcps: highly,
    moderately_engaged_hcps: moderately,
    low_engaged_hcps: low,
    disengaged_hcps: disengaged
  };
}

export function getHcpByIdFromCSV(entropyRows, mlRows, id) {
  const row = entropyRows.find(r => String(r.hcp_id).trim() === String(id).trim());
  if (!row) return null;

  const score = parseFloat(row.entropy_weighted_score) || 0;
  const preferredChannel = formatChannelName(row.recommended_channel || row.ml_primary_channel || "Rep Visit");

  const channelScores = {
    "Rep Visit": Math.min(1.0, parseFloat(row.entropy_channel_score_rep_visit) || 0),
    "Phone Call": Math.min(1.0, parseFloat(row.entropy_channel_score_phone_call) || 0),
    "Webinar": Math.min(1.0, parseFloat(row.entropy_channel_score_webinar) || 0),
    "Email": Math.min(1.0, parseFloat(row.entropy_channel_score_email) || 0),
    "Digital Ad": Math.min(1.0, parseFloat(row.entropy_channel_score_digital_ad) || 0)
  };

  const totalChannelScore = Object.values(channelScores).reduce((sum, v) => sum + v, 0);

  const weightedContributions = {};
  Object.keys(channelScores).forEach(ch => {
    weightedContributions[ch] = totalChannelScore > 0 
      ? channelScores[ch] / totalChannelScore 
      : 0.2;
  });

  // Check ML recommendations for this HCP
  const hcpMlRecs = mlRows
    ? mlRows.filter(r => String(r.hcp_id).trim() === String(id).trim())
    : [];

  return {
    hcp_id: String(row.hcp_id),
    doctor_name: `Dr. ${row.first_name} ${row.last_name}`,
    first_name: row.first_name,
    last_name: row.last_name,
    specialty: formatSpecialty(row.specialty),
    segment: row.segment,
    territory: row.territory,
    practice_type: row.practice_type,
    city: row.city,
    state: row.state,
    opt_out_flag: row.opt_out_flag === 'True' || row.opt_out_flag === 'true',
    overall_engagement_score: score,
    overall_engagement_score_100: score,
    preferred_channel: preferredChannel,
    channel_scores: channelScores,
    weighted_contributions: weightedContributions,
    ml_recommendations: hcpMlRecs
  };
}

export function generateChatbotResponse(userMessage, currentHcp, allHcps) {
  const q = userMessage.toLowerCase();

  if (q.includes("hcp") || q.includes("doctor") || q.includes("who")) {
    if (currentHcp) {
      return `Currently analyzing Dr. ${currentHcp.first_name} ${currentHcp.last_name} (ID: ${currentHcp.hcp_id}), specialized in ${currentHcp.specialty}. overall score is ${Math.round(currentHcp.overall_engagement_score)}/100. Preferred channel: ${currentHcp.preferred_channel}.`;
    }
    return `We currently have ${allHcps.length} HCPs in our dataset. Enter an HCP ID (e.g., 1, 2, 3...) in the search bar to inspect individual scorecards!`;
  }

  if (q.includes("score") || q.includes("engagement") || q.includes("level")) {
    if (currentHcp) {
      const score = Math.round(currentHcp.overall_engagement_score);
      const level = score >= 70 ? "Highly Engaged" : score >= 40 ? "Moderately Engaged" : "Low Engagement";
      return `Dr. ${currentHcp.last_name}'s engagement score is ${score}/100, classified as "${level}".`;
    }
    return `Engagement scores range from 0 to 100 based on weighted entropy scores across Rep Visits, Webinars, Emails, Phone Calls, and Digital Ads.`;
  }

  if (q.includes("channel") || q.includes("recommend") || q.includes("next best")) {
    if (currentHcp) {
      return `The primary recommended engagement channel for Dr. ${currentHcp.last_name} is ${currentHcp.preferred_channel}.`;
    }
    return `Our ML model ranks engagement channels (Rep Visit, Webinar, Email, Phone Call, Digital Ad) to provide personalized Next Best Action recommendations for each HCP.`;
  }

  if (q.includes("rank") || q.includes("top") || q.includes("leaderboard")) {
    if (allHcps.length > 0) {
      const top3 = allHcps.slice(0, 3).map((h, i) => `#${i+1} Dr. ${h.first_name} ${h.last_name} (${Math.round(h.overall_engagement_score_100)} pts)`).join(', ');
      return `Top ranked HCPs: ${top3}. Click the burger menu (☰) to view the full leaderboard!`;
    }
    return `You can view the full HCP rankings by opening the menu drawer (☰).`;
  }

  return `🤖 I am your HCP AI Assistant. Ask me about engagement scores, channel recommendations, top ranked HCPs, or search for an HCP ID!`;
}

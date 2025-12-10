import axios from 'axios'

// Analytics API endpoint for tracking and resetting usage data
const ANALYTICS_API_URL = '/api/analytics'

/**
 * Resets all analytics data in the system.
 * Admin-only functionality to clear query history, model selection data, and performance metrics.
 * Used during testing or when starting fresh analytics collection.
 *
 * @returns {Promise<Object>} Confirmation response of reset operation
 * @throws {Error} If reset fails due to permissions or server error
 */
export async function resetAnalytics() {
  try {
    const response = await axios.post(`${ANALYTICS_API_URL}/reset`)
    return response.data
  } catch (error) {
    console.error('Failed to reset analytics:', error)
    throw new Error('Failed to reset analytics data')
  }
}

import axios from 'axios'

const ANALYTICS_API_URL = '/api/analytics'

export async function resetAnalytics() {
  try {
    const response = await axios.post(`${ANALYTICS_API_URL}/reset`)
    return response.data
  } catch (error) {
    console.error('Failed to reset analytics:', error)
    throw new Error('Failed to reset analytics data')
  }
}

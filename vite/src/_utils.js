
export const _getPaginatedApiResources = async (request) => {
  let pagedRequest = request
  let results = []
  try {
    while(pagedRequest) {
      const response = await fetch(pagedRequest, {mode: 'cors'})
      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`)
      }
      const data = await response.json()
      results = results.concat(data.results)
      pagedRequest = data.next || null
    }
  } catch (error) {
    console.error('Error fetching data:', error)
  }
  return results
}

export const _getApiResource = async (request) => {
  try {
    const response = await fetch(request, {mode: 'cors'})
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('Error fetching data:', error)
  }
}
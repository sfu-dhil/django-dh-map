import { Offcanvas, Modal } from 'bootstrap'

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

export const _generateSoloFetchApiResourceStore = (resourcesApiUrl) => {
  return {
    state: () => ({
      loadedObject: null,
    }),
    actions: {
      async get() {
        if (this.loadedObject) { return this.loadedObject }

        this.loadedObject = await _getApiResource(resourcesApiUrl)
        return this.loadedObject
      },
    },
    persist: {
      storage: sessionStorage
    },
  }
}

export const _generateApiResourceStore = (resourceApiUrlFunction, resourcesApiUrl) => {
  return {
    state: () => ({
      loadedObjects: [],
      loadedAll: false,
    }),
    getters: {
      objectMap: (state) => state.loadedObjects.reduce((result, o) => result.set(o.id, o), new Map()),
    },
    actions: {
      async getById(id) {
        if (!id || !Number.isInteger(id) || id <= 0) { return null }
        if (this.objectMap.has(id)) { return this.objectMap.get(id) }

        const resource = await _getApiResource(resourceApiUrlFunction(id))
        this.loadedObjects.push(resource)
        return resource
      },
      async getAll() {
        if (this.loadedAll) { return this.loadedObjects }

        this.loadedObjects = await _getPaginatedApiResources(resourcesApiUrl)
        this.loadedAll = true
        return this.loadedObjects
      },
    },
    persist: {
      storage: sessionStorage
    },
  }
}

export const toggleOffcanvas = (offcanvasEl, show) => {
  if (offcanvasEl) {
    const bsOffcanvas = Offcanvas.getOrCreateInstance(offcanvasEl)
    show ? bsOffcanvas.show() : bsOffcanvas.hide()
  }
}

export const toggleModal = (modalEl, show) => {
  if (modalEl) {
    const bsModal = Modal.getOrCreateInstance(modalEl)
    show ? bsModal.show() : bsModal.hide()
  }
}

export const _stopAllMedia = () => {
  document.querySelectorAll('audio').forEach( (audio) => {
    if (!audio.paused && !audio.ended) { audio.pause() }
  })
  document.querySelectorAll('video').forEach( (video) => {
    if (!video.paused && !video.ended) { video.pause() }
  })
}
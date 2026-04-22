import { defineStore } from 'pinia'
import { getCenter, boundingExtent } from 'ol/extent'
import { MapResourceTypes } from '../_resourceTypes.js'

export const useDisplayOpenlayersStore = defineStore('display-openlayers', {
  state: () => ({
    baseUnboundExtent: null,
    extent: null,
    center: null,
    zoom: null,
    rotation: null,
  }),
  getters: {},
  actions: {
    reset () {
      this.baseUnboundExtent = null
      this.extent = null
      this.center = null
      this.zoom = null
      this.rotation = null
    },
    init (map) {
      if (map && [MapResourceTypes.overheadImageMap, MapResourceTypes.xyzMap].includes(map.resourcetype)) {
        this.baseUnboundExtent = undefined
        this.extent = map.properties?.bounding_box ? boundingExtent(map.properties?.bounding_box.flat()) : undefined
        if (map.resourcetype === MapResourceTypes.overheadImageMap) {
          this.baseUnboundExtent = [0, -map.height, map.width, 0]
          if (this.extent === undefined) {
            this.extent = this.baseUnboundExtent
          }
        }
        // defaults
        this.center = this.extent ? getCenter(this.extent) : [0, 0]
        this.zoom = map.min_zoom && map.max_zoom ? (map.max_zoom - map.min_zoom) / 2 : 1
        this.rotation = 0
        // optional initial value overrides
        if (map.properties?.initial) {
          this.center = map.properties.initial.center
          this.zoom = map.properties.initial.zoom
          this.rotation = map.properties.initial.rotation
        }
      } else {
        this.reset()
      }
    },
  },
  persist: {
    storage: sessionStorage,
  },
})

export const useDisplayPannellumStore = defineStore('display-pannellum', {
  state: () => ({
    hfov: null,
    yaw: null,
    pitch: null,
  }),
  getters: {},
  actions: {
    reset () {
      this.hfov = null
      this.yaw = null
      this.pitch = null
    },
    init (map) {
      if (map && [MapResourceTypes.panoramaImageMap].includes(map.resourcetype)) {
        // defaults
        this.hfov = 100
        this.yaw = 0
        this.pitch = 0
        // optional initial value overrides
        if (map.properties?.initial) {
          this.hfov = map.properties.initial.hfov
          this.yaw = map.properties.initial.yaw
          this.pitch = map.properties.initial.pitch
        }
      } else {
        this.reset()
      }
    },
  },
  persist: {
    storage: sessionStorage,
  },
})

export const useDisplayImageModalStore = defineStore('display-image-modal', {
  state: () => ({
    shown: false,
    object: null,
  }),
  getters: {},
  actions: {
    showImage (object) {
      this.object = object
      this.shown = true
    },
  },
})

export const useDisplayImageGalleryModalStore = defineStore('display-image-gallery-modal', {
  state: () => ({
    shown: false,
    objects: [],
    galleryIndex: null,
  }),
  getters: {},
  actions: {
    showGalleryImage (galleryIndex, objects) {
      this.objects = objects
      this.shown = true
      this.galleryIndex = galleryIndex
    },
  },
})

export const useDisplayStore = defineStore('display', {
  state: () => ({
    welcomeModalShown: false,
    mapSelectSidebarShown: false,
    infoPageIdShown: null,
    infoPageSelectionSidebarShown: false,
    featureIdHover: null,
    featureIdShown: null,
    featureSelectionSidebarShown: false,
  }),
  getters: {},
  actions: {
    forceShowInitialWelcomeMessage() {
      if (!document.cookie.split("; ").find((row) => row.startsWith("showInitialWelcomeModal"))) {
        // set cookie to expire 1 day from now
        const exp = (new Date(Date.now() + 86400e3)).toUTCString()
        document.cookie = `showInitialWelcomeModal=true; expires=${exp}; SameSite=None; Secure`
        this.welcomeModalShown = true
      }
    },
    showInfoPage(infoPage) {
      this.infoPageIdShown = infoPage.id
    },
    showFeature(feature) {
      this.featureIdShown = feature.id
    },
    showWelcomeMessage() {
      this.welcomeModalShown = true
    },
    hideSidebars() {
      this.infoPageSelectionSidebarShown = false
      this.featureSelectionSidebarShown = false
      this.mapSelectSidebarShown = false
    },
    showMapSelectSidebar() {
      this.hideSidebars()
      this.mapSelectSidebarShown = true
    },
    showInfoPageSelectionSidebar() {
      this.hideSidebars()
      this.infoPageSelectionSidebarShown = true
    },
    showFeatureSelectionSidebar() {
      this.hideSidebars()
      this.featureSelectionSidebarShown = true
    },
  },
  persist: {
    storage: sessionStorage,
  },
})
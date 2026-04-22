export const MapResourceTypes = Object.freeze({
  xyzMap: 'XyzMap',
  overheadImageMap: 'OverheadImageMap',
  panoramaImageMap: 'PanoramaImageMap',
})

export const MapGeojsonResourceTypes = Object.freeze({
  feature: 'MapGeoJsonFeature',
  transition: 'MapGeoJsonTransition',
  label: 'MapGeoJsonLabel',
})

export const IconResourceTypes = Object.freeze({
  image: 'IconImage',
  numbered: 'IconNumbered',
})

export const ContentItemResourceTypes = Object.freeze({
  richText: 'ContentBlockRichText',
  image: 'ContentBlockImage',
  imageGallery: 'ContentBlockImageGallery',
  beforeAndAfterImage: 'ContentBlockImageBeforeAndAfter',
  video: 'ContentBlockVideo',
  audio: 'ContentBlockAudio',
})
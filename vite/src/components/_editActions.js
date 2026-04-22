export const EditModeActionTypes = Object.freeze({
  move: 'move',
  add: 'add',
  remove: 'remove',
  boundingBox: 'bounding-box',
  initialView: 'initial-view',
})
export const EditModeAddActionTypes = Object.freeze({
  feature: 'add-feature',
  map: 'add-map',
  label: 'add-label',
})
export const EditModeBoundingBoxActionTypes = Object.freeze({
  move: 'bounding-box-move',
  add: 'bounding-box-add-replace',
})
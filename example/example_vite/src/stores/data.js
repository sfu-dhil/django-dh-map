import { defineStore } from 'pinia'
import {
  _generateSoloFetchApiResourceStore,
  _generateApiResourceStore,
} from '../_utils.js'

export const useMapsStore = defineStore('data-maps', _generateApiResourceStore((id) => `/api/maps/${id}`, '/api/maps'))
export const useFeaturesStore = defineStore('data-features', _generateApiResourceStore((id) => `/api/features/${id}`, '/api/features'))
export const useInfoPageStore = defineStore('data-info-pages', _generateApiResourceStore((id) => `/api/pages/${id}`, '/api/pages'))
export const useStaticContentStore = defineStore('data-static-content', _generateSoloFetchApiResourceStore('/api/content'))
/**
 * Units store for managing measurement units
 */
import { defineStore } from 'pinia'
import api from '../api/axios'

export interface Unit {
  id: number
  code: string
  name: string
  is_system: boolean
  created_at: string
}

export const useUnitsStore = defineStore('units', {
  state: () => ({
    units: [] as Unit[],
    loading: false,
    error: null as string | null,
    loaded: false,
  }),

  getters: {
    unitOptions: (state) => {
      return state.units.map(unit => ({
        value: unit.code,
        label: `${unit.name} (${unit.code})`,
      }))
    },

    getUnitByCode: (state) => {
      return (code: string) => state.units.find(u => u.code === code)
    },
  },

  actions: {
    async fetchUnits() {
      if (this.loaded && this.units.length > 0) {
        return // Use cached data
      }

      this.loading = true
      this.error = null

      try {
        const res = await api.get<Unit[]>('/units/')
        this.units = res.data
        this.loaded = true
      } catch (e: any) {
        this.error = e.response?.data?.detail || e.message
        throw e
      } finally {
        this.loading = false
      }
    },

    async createUnit(code: string, name: string) {
      try {
        const res = await api.post<Unit>('/units/', { code, name })
        this.units.push(res.data)
        return res.data
      } catch (e: any) {
        this.error = e.response?.data?.detail || e.message
        throw e
      }
    },

    async deleteUnit(id: number) {
      try {
        await api.delete(`/units/${id}/`)
        this.units = this.units.filter(u => u.id !== id)
      } catch (e: any) {
        this.error = e.response?.data?.error || e.message
        throw e
      }
    },

    /**
     * Find best matching unit for a given value
     */
    findMatchingUnit(value: string): Unit | null {
      if (!value) return null

      const normalized = value.toUpperCase().trim()

      // Exact code match
      const exactMatch = this.units.find(u => u.code === normalized)
      if (exactMatch) return exactMatch

      // Common aliases
      const aliases: Record<string, string> = {
        'KGS': 'KG',
        'KILOGRAMS': 'KG',
        'KILOGRAM': 'KG',
        'KILOS': 'KILO',
        'PCS': 'PCS',
        'PIECES': 'PCS',
        'PIECE': 'PCS',
        'PC': 'PCS',
        'LTR': 'L',
        'LITER': 'L',
        'LITERS': 'L',
        'LITRE': 'L',
        'LITRES': 'L',
        'MTR': 'M',
        'METER': 'M',
        'METERS': 'M',
        'METRE': 'M',
        'METRES': 'M',
        'GMS': 'GRAM',
        'GRAMS': 'GRAM',
        'GM': 'GRAM',
        'G': 'GRAM',
        'BAGS': 'BAG',
        'BOXES': 'BOX',
        'PACKS': 'PACK',
        'PACKET': 'PACK',
        'PACKETS': 'PACK',
        'UNITS': 'UNIT',
        'TONS': 'TON',
        'TONNE': 'TON',
        'TONNES': 'TON',
        'GALLONS': 'GALLON',
        'GAL': 'GALLON',
        'FT': 'FOOT',
        'FEET': 'FOOT',
        'YD': 'YARD',
        'YARDS': 'YARD',
        'CENTIMETER': 'CM',
        'CENTIMETERS': 'CM',
        'MILLIMETER': 'MM',
        'MILLIMETERS': 'MM',
        'IN': 'INCH',
        'INCHES': 'INCH',
        'LB': 'POUND',
        'LBS': 'POUND',
        'POUNDS': 'POUND',
        'OZ': 'OUNCE',
        'OUNCES': 'OUNCE',
        'CUPS': 'CUP',
        'TBSP': 'TABLESPOON',
        'TABLESPOONS': 'TABLESPOON',
        'TSP': 'TEASPOON',
        'TEASPOONS': 'TEASPOON',
        'DOZ': 'DOZEN',
        'DOZENS': 'DOZEN',
        'DZ': 'DOZEN',
      }

      const aliasCode = aliases[normalized]
      if (aliasCode) {
        const aliasMatch = this.units.find(u => u.code === aliasCode)
        if (aliasMatch) return aliasMatch
      }

      // Fuzzy match by name
      const lowerValue = value.toLowerCase()
      const nameMatch = this.units.find(u => 
        u.name.toLowerCase().includes(lowerValue) || 
        lowerValue.includes(u.name.toLowerCase())
      )
      if (nameMatch) return nameMatch

      return null
    },
  },
})

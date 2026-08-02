/**
 * Import Wizard types
 */

export interface WizardStep {
  number: number
  title: string
  description: string
}

export const WIZARD_STEPS: WizardStep[] = [
  { number: 1, title: 'Upload', description: 'Select file & entity type' },
  { number: 2, title: 'Map Columns', description: 'Match columns to fields' },
  { number: 3, title: 'Preview', description: 'Review & select rows' },
  { number: 4, title: 'Results', description: 'Import summary' },
]

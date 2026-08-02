/**
 * Import field configurations for each entity type.
 * Defines which fields can be imported and their metadata.
 */

export interface ImportFieldConfig {
  key: string
  label: string
  required: boolean
  type: 'string' | 'decimal' | 'boolean' | 'unit' | 'choice'
  choices?: string[]
  default?: any
  example: string
  aliases: string[]
}

export interface EntityImportConfig {
  entityType: string
  displayName: string
  apiEndpoint: string
  fields: ImportFieldConfig[]
  uniqueFields: string[]
}

export const IMPORT_CONFIGS: Record<string, EntityImportConfig> = {
  customer: {
    entityType: 'customer',
    displayName: 'Customers',
    apiEndpoint: '/customers',
    uniqueFields: ['name'],
    fields: [
      {
        key: 'name',
        label: 'Customer Name',
        required: true,
        type: 'string',
        example: 'John Doe',
        aliases: ['customer_name', 'full_name', 'customer'],
      },
      {
        key: 'email',
        label: 'Email',
        required: false,
        type: 'string',
        example: 'john@example.com',
        aliases: ['email_address', 'e-mail'],
      },
      {
        key: 'phone',
        label: 'Phone',
        required: false,
        type: 'string',
        example: '+1234567890',
        aliases: ['phone_number', 'mobile', 'contact', 'tel'],
      },
      {
        key: 'address',
        label: 'Address',
        required: false,
        type: 'string',
        example: '123 Main St',
        aliases: ['street_address', 'location'],
      },
      {
        key: 'city',
        label: 'City',
        required: false,
        type: 'string',
        example: 'New York',
        aliases: ['town'],
      },
      {
        key: 'balance',
        label: 'Opening Balance',
        required: false,
        type: 'decimal',
        default: 0,
        example: '0.00',
        aliases: ['opening_balance', 'initial_balance', 'amount'],
      },
      {
        key: 'is_active',
        label: 'Active',
        required: false,
        type: 'boolean',
        default: true,
        example: 'true',
        aliases: ['active', 'status'],
      },
    ],
  },

  vendor: {
    entityType: 'vendor',
    displayName: 'Vendors',
    apiEndpoint: '/vendors',
    uniqueFields: ['name'],
    fields: [
      {
        key: 'name',
        label: 'Vendor Name',
        required: true,
        type: 'string',
        example: 'ABC Supplies Ltd',
        aliases: ['vendor_name', 'company', 'supplier', 'supplier_name'],
      },
      {
        key: 'email',
        label: 'Email',
        required: false,
        type: 'string',
        example: 'contact@supplier.com',
        aliases: ['email_address', 'e-mail'],
      },
      {
        key: 'phone',
        label: 'Phone',
        required: false,
        type: 'string',
        example: '+1234567890',
        aliases: ['phone_number', 'mobile', 'contact', 'tel'],
      },
      {
        key: 'address',
        label: 'Address',
        required: false,
        type: 'string',
        example: '456 Industrial Ave',
        aliases: ['street_address', 'location'],
      },
      {
        key: 'contact_person',
        label: 'Contact Person',
        required: false,
        type: 'string',
        example: 'Jane Smith',
        aliases: ['contact_name', 'representative', 'rep'],
      },
      {
        key: 'balance',
        label: 'Opening Balance',
        required: false,
        type: 'decimal',
        default: 0,
        example: '0.00',
        aliases: ['opening_balance', 'initial_balance', 'amount'],
      },
      {
        key: 'is_active',
        label: 'Active',
        required: false,
        type: 'boolean',
        default: true,
        example: 'true',
        aliases: ['active', 'status'],
      },
    ],
  },

  product: {
    entityType: 'product',
    displayName: 'Products',
    apiEndpoint: '/products',
    uniqueFields: ['name', 'unit'],
    fields: [
      {
        key: 'name',
        label: 'Product Name',
        required: true,
        type: 'string',
        example: 'Widget A',
        aliases: ['product_name', 'item', 'item_name', 'product'],
      },
      {
        key: 'unit',
        label: 'Unit',
        required: true,
        type: 'unit',
        example: 'PCS',
        aliases: ['uom', 'unit_of_measure', 'measurement'],
      },
      {
        key: 'cop',
        label: 'Cost of Production / Price',
        required: true,
        type: 'decimal',
        example: '100.00',
        aliases: ['cost', 'cost_of_production', 'price', 'unit_cost', 'cost_price'],
      },
      {
        key: 'quantity',
        label: 'Initial Stock',
        required: false,
        type: 'decimal',
        default: 0,
        example: '50',
        aliases: ['qty', 'stock', 'initial_quantity', 'initial_stock', 'opening_stock'],
      },
      {
        key: 'product_type',
        label: 'Product Type',
        required: false,
        type: 'choice',
        choices: ['MANUFACTURED', 'PURCHASED'],
        default: 'MANUFACTURED',
        example: 'MANUFACTURED',
        aliases: ['type', 'category'],
      },
    ],
  },

  raw_material: {
    entityType: 'raw_material',
    displayName: 'Raw Materials',
    apiEndpoint: '/raw-materials',
    uniqueFields: ['name', 'unit'],
    fields: [
      {
        key: 'name',
        label: 'Material Name',
        required: true,
        type: 'string',
        example: 'Steel Rod',
        aliases: ['material_name', 'item', 'item_name', 'material', 'raw_material'],
      },
      {
        key: 'unit',
        label: 'Unit',
        required: true,
        type: 'unit',
        example: 'KG',
        aliases: ['uom', 'unit_of_measure', 'measurement'],
      },
      {
        key: 'quantity',
        label: 'Initial Stock',
        required: false,
        type: 'decimal',
        default: 0,
        example: '100',
        aliases: ['qty', 'stock', 'initial_quantity', 'initial_stock', 'opening_stock'],
      },
      {
        key: 'reorder_level',
        label: 'Reorder Level',
        required: false,
        type: 'decimal',
        default: 0,
        example: '10',
        aliases: ['reorder', 'minimum_stock', 'min_stock', 'threshold'],
      },
    ],
  },

  asset: {
    entityType: 'asset',
    displayName: 'Assets',
    apiEndpoint: '/assets',
    uniqueFields: ['name'],
    fields: [
      {
        key: 'name',
        label: 'Asset Name',
        required: true,
        type: 'string',
        example: 'CNC Machine #1',
        aliases: ['asset_name', 'item', 'item_name', 'asset'],
      },
      {
        key: 'description',
        label: 'Description',
        required: false,
        type: 'string',
        example: 'Main production CNC machine',
        aliases: ['desc', 'details', 'notes'],
      },
      {
        key: 'category',
        label: 'Category',
        required: false,
        type: 'string',
        example: 'Production Equipment',
        aliases: ['asset_category', 'group'],
      },
      {
        key: 'type',
        label: 'Type',
        required: true,
        type: 'choice',
        choices: ['MACHINE', 'MOLD', 'EQUIPMENT', 'FURNITURE', 'VEHICLE', 'BUILDING', 'TECHNOLOGY', 'OTHER'],
        default: 'EQUIPMENT',
        example: 'MACHINE',
        aliases: ['asset_type'],
      },
      {
        key: 'value',
        label: 'Current Value',
        required: false,
        type: 'decimal',
        example: '50000.00',
        aliases: ['current_value', 'worth'],
      },
      {
        key: 'purchase_value',
        label: 'Purchase Value',
        required: false,
        type: 'decimal',
        example: '75000.00',
        aliases: ['cost', 'purchase_price', 'original_value', 'purchase_cost'],
      },
      {
        key: 'location',
        label: 'Location',
        required: false,
        type: 'string',
        example: 'Factory Floor A',
        aliases: ['place', 'position'],
      },
      {
        key: 'status',
        label: 'Status',
        required: false,
        type: 'choice',
        choices: ['ACTIVE', 'INACTIVE', 'MAINTENANCE', 'DISPOSED'],
        default: 'ACTIVE',
        example: 'ACTIVE',
        aliases: ['asset_status', 'condition'],
      },
    ],
  },
}

/**
 * Get field config by key
 */
export function getFieldConfig(entityType: string, fieldKey: string): ImportFieldConfig | undefined {
  const config = IMPORT_CONFIGS[entityType]
  if (!config) return undefined
  return config.fields.find(f => f.key === fieldKey)
}

/**
 * Get all entity types available for import
 */
export function getImportableEntities(): { value: string; label: string }[] {
  return Object.entries(IMPORT_CONFIGS).map(([key, config]) => ({
    value: key,
    label: config.displayName,
  }))
}

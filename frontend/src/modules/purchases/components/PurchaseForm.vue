<template>
	<div class="modal-overlay" @click.self="$emit('close')">
		<div class="modal-container">
			<form @submit.prevent="onSubmit" class="modal-content">
				<!-- Header -->
				<div class="modal-header">
					<h2 class="modal-title">
						<svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
						</svg>
						{{ purchase?.id ? 'Edit Purchase' : 'New Purchase' }}
					</h2>
					<button type="button" @click="$emit('close')" class="close-button">
						<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
						</svg>
					</button>
				</div>
				<!-- Body -->
				<div class="modal-body">
					<!-- Purchase Information -->
					<div class="section">
						<h3 class="section-title">Purchase Information</h3>
						<div class="form-grid">
							<div class="form-group">
								<label for="vendor" class="form-label">Vendor <span class="required">*</span></label>
								<select v-model="form.vendor" id="vendor" class="form-input" required>
									<option value="">Select Vendor</option>
									<option v-for="vendor in vendors" :key="vendor.id" :value="vendor.id">{{ vendor.name }}</option>
								</select>
							</div>
							<div class="form-group">
								<label for="date" class="form-label">Date <span class="required">*</span></label>
								<input v-model="form.date" id="date" type="date" class="form-input" required />
							</div>
						</div>
					</div>
					<!-- Products Section -->
					<div class="section">
						<h3 class="section-title">Products</h3>
						<div class="add-product-section">
							<div class="add-product-grid">
								<div class="form-group">
									<label class="form-label">Product</label>
									<select v-model="newItem.product_id" class="form-input">
										<option value="">Select Product</option>
										<option v-for="product in products" :key="product.id" :value="product.id">
											{{ product.name }} ({{ product.unit }})
										</option>
									</select>
								</div>
								<div class="form-group">
									<label class="form-label">Quantity</label>
									<input v-model.number="newItem.quantity" type="number" step="0.01" min="0.01" class="form-input" placeholder="0" />
								</div>
								<div class="form-group">
									<label class="form-label">Unit Cost</label>
									<input v-model.number="newItem.unit_cost" type="number" step="0.01" min="0" class="form-input" placeholder="0.00" />
								</div>
								<div class="form-group">
									<label class="form-label">&nbsp;</label>
									<button type="button" @click="addProduct" class="btn-add" :disabled="!newItem.product_id || !newItem.quantity || !newItem.unit_cost">
										<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
										</svg>
										Add
									</button>
								</div>
							</div>
						</div>
						<div v-if="purchaseItems.length > 0" class="products-list">
							<div v-for="(item, index) in purchaseItems" :key="index" class="product-item">
								<div class="product-info">
									<div class="product-name">{{ getProductName(item.product_id) }}</div>
									<div class="product-details">
										{{ item.quantity }} × ₨{{ item.unit_cost.toFixed(2) }} = ₨{{ (item.quantity * item.unit_cost).toFixed(2) }}
									</div>
								</div>
								<button type="button" @click="removeProduct(index)" class="btn-remove">
									<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
									</svg>
								</button>
							</div>
						</div>
						<div v-else class="empty-products">
							<p>No products added. Add products above to create a purchase.</p>
						</div>
						<div class="total-section">
							<div class="total-row">
								<span class="total-label">Total Amount:</span>
								<span class="total-value">₨{{ totalAmount.toFixed(2) }}</span>
							</div>
						</div>
					</div>
					<!-- Bill & Payment Section -->
					<div class="section">
						<h3 class="section-title">Bill & Payments</h3>
						<div class="form-grid">
							<div class="form-group">
								<label class="form-label">Bill Number</label>
								<input v-model="billForm.number" class="form-input" placeholder="Bill Number" />
							</div>
							<div class="form-group">
								<label class="form-label">Payment Method</label>
								<select v-model="billForm.payment_method" class="form-input">
									<option value="CASH">Cash</option>
									<option value="CHEQUE">Cheque</option>
									<option value="BANK_TRANSFER">Bank Transfer</option>
								</select>
							</div>
							<div class="form-group">
								<label class="form-label">Bill Amount</label>
								<input v-model.number="billForm.amount" type="number" min="0" class="form-input" placeholder="Amount" />
							</div>
							<div class="form-group">
								<label class="form-label">Status</label>
								<span class="form-input" :class="billForm.payment_status.toLowerCase()">{{ billForm.payment_status }}</span>
							</div>
						</div>
						<div class="payments-section mt-4">
							<h4 class="mb-2">Payments</h4>
							<ul v-if="billPayments.length > 0" class="payments-list">
								<li v-for="p in billPayments" :key="p.id">
									{{ p.date }} - ₨{{ p.amount.toFixed(2) }} ({{ p.method }}) <span v-if="p.reference">[{{ p.reference }}]</span>
								</li>
							</ul>
							<div v-else class="empty-payments">No payments yet.</div>
							<div class="add-payment-grid mt-2">
								<input v-model.number="newPayment.amount" type="number" min="0.01" class="form-input" placeholder="Amount" />
								<select v-model="newPayment.method" class="form-input">
									<option value="CASH">Cash</option>
									<option value="CHEQUE">Cheque</option>
									<option value="BANK_TRANSFER">Bank Transfer</option>
								</select>
								<input v-model="newPayment.reference" class="form-input" placeholder="Reference (optional)" />
								<button type="button" class="btn-add" @click="addPayment" :disabled="!canAddPayment">Add Payment</button>
							</div>
						</div>
					</div>
				</div>
				<!-- Footer -->
				<div class="modal-footer">
					<button type="button" @click="$emit('close')" class="btn-cancel">Cancel</button>
					<button type="submit" class="btn-save" :disabled="purchaseItems.length === 0">{{ purchase?.id ? 'Update Purchase' : 'Create Purchase' }}</button>
				</div>
			</form>
		</div>
	</div>
</template>
<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useBillStore } from '../stores/billing'
import type { Bill, Payment } from '../types/billing'

const emit = defineEmits(['save', 'close'])
const props = defineProps<{ purchase?: any, vendors: any[], products: any[] }>()

const form = ref({ vendor: '', date: new Date().toISOString().split('T')[0] })
const purchaseItems = ref<Array<{ product_id: number; quantity: number; unit_cost: number }>>([])
const newItem = ref({ product_id: 0, quantity: 0, unit_cost: 0 })
const totalAmount = computed(() => purchaseItems.value.reduce((sum, item) => sum + (item.quantity * item.unit_cost), 0))

const billStore = useBillStore()
const billForm = ref<Partial<Bill>>({ number: '', payment_method: 'CASH', amount: 0, payment_status: 'UNPAID', payments: [] })
billForm.value.amount = totalAmount.value
const billPayments = ref<Payment[]>([])
const newPayment = ref<Partial<Payment>>({ amount: 0, method: 'CASH', reference: '' })
const canAddPayment = computed(() => newPayment.value.amount && newPayment.value.method)

watch(totalAmount, (val) => { billForm.value.amount = val })

function getProductName(productId: number): string {
	const product = props.products.find((p: any) => p.id === productId)
	return product ? product.name : 'Unknown Product'
}
function addProduct() {
	if (!newItem.value.product_id || !newItem.value.quantity || !newItem.value.unit_cost) return
	purchaseItems.value.push({ ...newItem.value })
	newItem.value = { product_id: 0, quantity: 0, unit_cost: 0 }
}
function removeProduct(index: number) { purchaseItems.value.splice(index, 1) }
async function addPayment() {
	if (!canAddPayment.value) return
	const payload = { amount: newPayment.value.amount, method: newPayment.value.method, reference: newPayment.value.reference, bill: billForm.value.id }
	const payment = await billStore.addPayment(payload)
	billPayments.value.push(payment)
	newPayment.value = { amount: 0, method: 'CASH', reference: '' }
	billForm.value.payment_status = payment.bill ? payment.bill.payment_status : billForm.value.payment_status
}
onMounted(async () => {
	if (props.purchase && props.purchase.id) {
		try {
			const bill = await billStore.fetchBill(props.purchase.id)
			billForm.value = bill
			billPayments.value = bill.payments || []
		} catch (e) {
			billForm.value = { number: '', payment_method: 'CASH', amount: totalAmount.value, payment_status: 'UNPAID', payments: [] }
			billPayments.value = []
		}
	}
})
function onSubmit() {
	emit('save', { ...form.value, items: purchaseItems.value, total_amount: totalAmount.value })
	if (billForm.value.number && billForm.value.amount) {
		billStore.createBill({ ...billForm.value, purchase: props.purchase?.id, amount: totalAmount.value })
	}
}
</script>
<style scoped>
/* ...styles similar to SalesForm.vue... */
</style>
 
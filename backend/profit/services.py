from collections import defaultdict
from decimal import Decimal

from products.models import Product
from sales.models import SaleItem
from .models import ProductCost

SEASON_BY_MONTH = {
    3: 'Spring', 4: 'Spring', 5: 'Spring',
    6: 'Summer', 7: 'Summer', 8: 'Summer',
    9: 'Autumn', 10: 'Autumn', 11: 'Autumn',
    12: 'Winter', 1: 'Winter', 2: 'Winter',
}
SEASON_ORDER = ['Spring', 'Summer', 'Autumn', 'Winter']

ZERO = Decimal('0')


def season_for_month(month):
    return SEASON_BY_MONTH[month]


class CostLookup:
    """Resolves the unit cost per dozen for a product as of a given date,
    from versioned ProductCost history, falling back to Product.cop when
    no cost history exists yet for that product/date (e.g. pre-history sales)."""

    def __init__(self, product_ids):
        self._history = defaultdict(list)
        rows = ProductCost.objects.filter(product_id__in=product_ids).order_by('valid_from')
        for row in rows:
            self._history[row.product_id].append((row.valid_from, row.component_type_id, row.amount_per_dozen))
        self._cop_fallback = dict(Product.objects.filter(id__in=product_ids).values_list('id', 'cop'))

    def breakdown_as_of(self, product_id, as_of):
        """component_id -> (amount_per_dozen, valid_from) for the latest cost of each
        component type in effect on `as_of`."""
        latest_by_component = {}
        for valid_from, component_id, amount in self._history.get(product_id, ()):
            if valid_from > as_of:
                break
            latest_by_component[component_id] = (amount, valid_from)
        return latest_by_component

    def unit_cost_per_dozen(self, product_id, as_of):
        breakdown = self.breakdown_as_of(product_id, as_of)
        if breakdown:
            return sum((amount for amount, _ in breakdown.values()), ZERO)
        return self._cop_fallback.get(product_id) or ZERO

    def cop_fallback(self, product_id):
        return self._cop_fallback.get(product_id) or ZERO


def compute_profit_rows(*, product_id=None, size_range_id=None, color_id=None, city=None,
                         year=None, month=None, season=None, date_from=None, date_to=None):
    """Returns one dict per SaleItem with revenue/cost/profit already computed."""
    qs = SaleItem.objects.select_related('sale', 'sale__customer', 'product')
    if product_id:
        qs = qs.filter(product_id=product_id)
    if size_range_id:
        qs = qs.filter(size_range_id=size_range_id)
    if color_id:
        qs = qs.filter(color_id=color_id)
    if city:
        qs = qs.filter(sale__customer__city__iexact=city)
    if year:
        qs = qs.filter(sale__date__year=year)
    if month:
        qs = qs.filter(sale__date__month=month)
    if date_from:
        qs = qs.filter(sale__date__date__gte=date_from)
    if date_to:
        qs = qs.filter(sale__date__date__lte=date_to)

    items = list(qs)
    if season:
        items = [i for i in items if season_for_month(i.sale.date.month) == season]

    cost_lookup = CostLookup({i.product_id for i in items})

    rows = []
    for item in items:
        as_of = item.sale.date.date()
        unit_cost = cost_lookup.unit_cost_per_dozen(item.product_id, as_of)
        cost = unit_cost * item.quantity_dozens
        revenue = item.subtotal
        profit_amount = revenue - cost
        rows.append({
            'product_id': item.product_id,
            'product_name': item.product.name,
            'city': item.sale.customer.city or 'Unknown',
            'year': as_of.year,
            'month': as_of.month,
            'season': season_for_month(as_of.month),
            'quantity_dozens': item.quantity_dozens,
            'revenue': revenue,
            'cost': cost,
            'profit_amount': profit_amount,
        })
    return rows


GROUP_KEY_FUNCS = {
    'product': lambda r: (r['product_id'], r['product_name']),
    'month': lambda r: (f"{r['year']:04d}-{r['month']:02d}", f"{r['year']:04d}-{r['month']:02d}"),
    'season': lambda r: (r['season'], r['season']),
    'year': lambda r: (r['year'], str(r['year'])),
    'location': lambda r: (r['city'], r['city']),
}


def _sorted_keys(group_by, categories_map):
    keys = list(categories_map.keys())
    if group_by in ('month', 'year'):
        return sorted(keys)
    if group_by == 'season':
        return sorted(keys, key=lambda k: SEASON_ORDER.index(k) if k in SEASON_ORDER else 99)
    return sorted(keys, key=lambda k: str(categories_map[k]).lower())


def _metric_value(bucket, metric, unit):
    revenue = bucket['revenue']
    cost = bucket['cost']
    profit_amount = bucket['profit_amount']
    qty = bucket['quantity_dozens'] * 12 if unit == 'piece' else bucket['quantity_dozens']
    if metric == 'revenue':
        return revenue
    if metric == 'cost':
        return cost
    if metric == 'profit_ratio':
        return (profit_amount / revenue) if revenue else ZERO
    if metric == 'profit_per_unit':
        return (profit_amount / qty) if qty else ZERO
    if metric == 'quantity':
        return qty
    return profit_amount


def aggregate(rows, group_by, unit='dozen'):
    """Groups rows by `group_by` (product/month/season/year/location), returns one
    summary dict per group with revenue/cost/profit_amount/profit_ratio/profit_per_unit."""
    keyfunc = GROUP_KEY_FUNCS[group_by]
    buckets = {}
    labels = {}
    for r in rows:
        key, label = keyfunc(r)
        labels[key] = label
        b = buckets.setdefault(key, {'revenue': ZERO, 'cost': ZERO, 'profit_amount': ZERO, 'quantity_dozens': 0})
        b['revenue'] += r['revenue']
        b['cost'] += r['cost']
        b['profit_amount'] += r['profit_amount']
        b['quantity_dozens'] += r['quantity_dozens']

    result = []
    for key in _sorted_keys(group_by, labels):
        b = buckets[key]
        qty = b['quantity_dozens'] * 12 if unit == 'piece' else b['quantity_dozens']
        result.append({
            'key': key,
            'label': labels[key],
            'unit': unit,
            'quantity': qty,
            'revenue': b['revenue'],
            'cost': b['cost'],
            'profit_amount': b['profit_amount'],
            'profit_ratio': (b['profit_amount'] / b['revenue']) if b['revenue'] else ZERO,
            'profit_per_unit': (b['profit_amount'] / qty) if qty else ZERO,
        })
    return result


def summary_totals(rows, unit='dozen'):
    revenue = sum((r['revenue'] for r in rows), ZERO)
    cost = sum((r['cost'] for r in rows), ZERO)
    profit_amount = revenue - cost
    quantity_dozens = sum((r['quantity_dozens'] for r in rows), 0)
    qty = quantity_dozens * 12 if unit == 'piece' else quantity_dozens
    return {
        'unit': unit,
        'quantity': qty,
        'revenue': revenue,
        'cost': cost,
        'profit_amount': profit_amount,
        'profit_ratio': (profit_amount / revenue) if revenue else ZERO,
        'profit_per_unit': (profit_amount / qty) if qty else ZERO,
    }


def build_trend(rows, x, series=None, unit='dozen', metric='profit_amount'):
    """Shapes aggregated rows for a chart: {categories: [...], series: [{name, data}]}."""
    x_keyfunc = GROUP_KEY_FUNCS[x]

    if not series:
        agg = aggregate(rows, x, unit)
        return {
            'categories': [r['label'] for r in agg],
            'series': [{'name': metric, 'data': [float(r[metric]) for r in agg]}],
        }

    series_keyfunc = GROUP_KEY_FUNCS[series]
    x_labels = {}
    series_labels = {}
    data = defaultdict(lambda: defaultdict(lambda: {'revenue': ZERO, 'cost': ZERO, 'profit_amount': ZERO, 'quantity_dozens': 0}))

    for r in rows:
        xk, xl = x_keyfunc(r)
        sk, sl = series_keyfunc(r)
        x_labels[xk] = xl
        series_labels[sk] = sl
        b = data[sk][xk]
        b['revenue'] += r['revenue']
        b['cost'] += r['cost']
        b['profit_amount'] += r['profit_amount']
        b['quantity_dozens'] += r['quantity_dozens']

    x_keys = _sorted_keys(x, x_labels)
    categories = [x_labels[k] for k in x_keys]

    result_series = []
    for sk in sorted(series_labels.keys(), key=lambda k: str(series_labels[k]).lower()):
        values = []
        for xk in x_keys:
            bucket = data[sk].get(xk)
            values.append(float(_metric_value(bucket, metric, unit)) if bucket else 0.0)
        result_series.append({'name': series_labels[sk], 'data': values})

    return {'categories': categories, 'series': result_series}

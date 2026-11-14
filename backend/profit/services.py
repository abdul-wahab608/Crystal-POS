from collections import defaultdict
from decimal import Decimal

from django.utils import timezone

from products.models import Product
from production.services import production_runs_by_product
from purchases.models import PurchaseItem
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
UNIT_METRICS = ('quantity', 'profit_per_unit')

MANUAL = 'MANUAL'
PRODUCTION = 'PRODUCTION'
PURCHASE = 'PURCHASE'
COP = 'COP'
MISSING = 'MISSING'
SOURCE_WEAKNESS = {MANUAL: 0, PRODUCTION: 1, PURCHASE: 2, COP: 3, MISSING: 4}


def season_for_month(month):
    return SEASON_BY_MONTH[month]


class CostLookup:
    def __init__(self, product_ids):
        product_ids = set(product_ids)
        self._history = defaultdict(list)
        for row in ProductCost.objects.filter(product_id__in=product_ids).order_by('valid_from'):
            self._history[row.product_id].append((row.valid_from, row.component_type_id, row.amount_per_dozen))
        self._cop = dict(Product.objects.filter(id__in=product_ids).values_list('id', 'cop'))
        self._production = production_runs_by_product(product_ids)
        self._purchase_costs = defaultdict(list)
        purchase_lines = (
            PurchaseItem.objects
            .filter(product_id__in=product_ids, product__product_type='PURCHASED')
            .order_by('purchase__date', 'id')
            .values_list('product_id', 'purchase__date', 'unit_cost')
        )
        for product_id, purchased_at, unit_cost in purchase_lines:
            self._purchase_costs[product_id].append((timezone.localdate(purchased_at), unit_cost))

    def breakdown_as_of(self, product_id, as_of):
        latest_by_component = {}
        for valid_from, component_id, amount in self._history.get(product_id, ()):
            if valid_from > as_of:
                break
            latest_by_component[component_id] = (amount, valid_from)
        return latest_by_component

    def production_runs(self, product_id):
        return self._production.get(product_id, [])

    def production_run_as_of(self, product_id, as_of):
        for run in self.production_runs(product_id):
            if run['date'] <= as_of and run['unit_cost'] is not None:
                return run
        return None

    def purchase_cost_as_of(self, product_id, as_of):
        cost = None
        for purchased_on, unit_cost in self._purchase_costs.get(product_id, ()):
            if purchased_on > as_of:
                break
            cost = unit_cost
        return cost

    def resolve(self, product_id, as_of):
        breakdown = self.breakdown_as_of(product_id, as_of)
        if breakdown:
            return sum((amount for amount, _ in breakdown.values()), ZERO), MANUAL
        run = self.production_run_as_of(product_id, as_of)
        if run:
            return run['unit_cost'], PRODUCTION
        purchase_cost = self.purchase_cost_as_of(product_id, as_of)
        if purchase_cost is not None and purchase_cost > ZERO:
            return purchase_cost, PURCHASE
        cop = self._cop.get(product_id) or ZERO
        if cop > ZERO:
            return cop, COP
        return None, MISSING


def compute_profit_rows(*, product_id=None, size_range_id=None, color_id=None, city=None,
                        year=None, month=None, season=None, date_from=None, date_to=None):
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
        items = [i for i in items if season_for_month(timezone.localtime(i.sale.date).month) == season]

    cost_lookup = CostLookup({i.product_id for i in items})

    rows = []
    for item in items:
        as_of = timezone.localdate(item.sale.date)
        unit_cost, cost_source = cost_lookup.resolve(item.product_id, as_of)
        revenue = item.subtotal
        cost = None if unit_cost is None else unit_cost * item.quantity
        rows.append({
            'product_id': item.product_id,
            'product_name': item.product.name,
            'city': item.sale.customer.city or 'Unknown',
            'year': as_of.year,
            'month': as_of.month,
            'season': season_for_month(as_of.month),
            'unit': item.product.unit,
            'quantity': item.quantity,
            'revenue': revenue,
            'cost': cost,
            'profit_amount': None if cost is None else revenue - cost,
            'cost_source': cost_source,
        })
    return rows


GROUP_KEY_FUNCS = {
    'product': lambda r: (r['product_id'], r['product_name']),
    'month': lambda r: (f"{r['year']:04d}-{r['month']:02d}", f"{r['year']:04d}-{r['month']:02d}"),
    'season': lambda r: (r['season'], r['season']),
    'year': lambda r: (r['year'], str(r['year'])),
    'location': lambda r: (r['city'], r['city']),
    'unit': lambda r: (r['unit'], r['unit']),
}


def _sorted_keys(group_by, categories_map):
    keys = list(categories_map.keys())
    if group_by in ('month', 'year'):
        return sorted(keys)
    if group_by == 'season':
        return sorted(keys, key=lambda k: SEASON_ORDER.index(k) if k in SEASON_ORDER else 99)
    return sorted(keys, key=lambda k: str(categories_map[k]).lower())


def _new_bucket():
    return {
        'revenue': ZERO, 'cost': ZERO, 'profit_amount': ZERO,
        'cost_sources': set(), 'quantities': defaultdict(lambda: ZERO),
    }


def _add_row(bucket, row):
    bucket['revenue'] += row['revenue']
    bucket['quantities'][row['unit']] += row['quantity']
    bucket['cost_sources'].add(row['cost_source'])
    if row['cost'] is not None:
        bucket['cost'] += row['cost']
        bucket['profit_amount'] += row['profit_amount']


def _weakest_source(sources):
    # A group is only as reliable as its least reliable row, so the group reports the weakest source.
    if not sources:
        return None
    return max(sources, key=SOURCE_WEAKNESS.__getitem__)


def _summarize(bucket):
    quantities = bucket['quantities']
    units = sorted(quantities)
    revenue = bucket['revenue']
    cost_source = _weakest_source(bucket['cost_sources'])
    cost_missing = cost_source == MISSING
    profit_amount = None if cost_missing else bucket['profit_amount']
    summary = {
        'revenue': revenue,
        'cost': None if cost_missing else bucket['cost'],
        'profit_amount': profit_amount,
        'profit_ratio': None if cost_missing else ((profit_amount / revenue) if revenue else ZERO),
        'quantities': [{'unit': u, 'quantity': quantities[u]} for u in units],
        'unit': None,
        'quantity': None,
        'profit_per_unit': None,
        'cost_source': cost_source,
        'cost_sources': sorted(bucket['cost_sources']),
        'cost_missing': cost_missing,
    }
    if len(units) == 1:
        unit = units[0]
        qty = quantities[unit]
        summary['unit'] = unit
        summary['quantity'] = qty
        if not cost_missing:
            summary['profit_per_unit'] = (profit_amount / qty) if qty else ZERO
    elif not units:
        summary['quantity'] = ZERO
    return summary


def aggregate(rows, group_by):
    keyfunc = GROUP_KEY_FUNCS[group_by]
    buckets = {}
    labels = {}
    for r in rows:
        key, label = keyfunc(r)
        labels[key] = label
        _add_row(buckets.setdefault(key, _new_bucket()), r)

    result = []
    for key in _sorted_keys(group_by, labels):
        result.append({'key': key, 'label': labels[key], **_summarize(buckets[key])})
    return result


def summary_totals(rows):
    bucket = _new_bucket()
    for r in rows:
        _add_row(bucket, r)
    return _summarize(bucket)


def _point(summary, metric):
    value = summary[metric]
    return (None if value is None else float(value)), summary['cost_source'], summary['cost_missing']


def _series_block(name, points):
    return {
        'name': name,
        'data': [p[0] for p in points],
        'cost_source': [p[1] for p in points],
        'cost_missing': [p[2] for p in points],
    }


def build_trend(rows, x, series=None, metric='profit_amount'):
    x_keyfunc = GROUP_KEY_FUNCS[x]
    if metric in UNIT_METRICS and not series:
        series = 'unit'

    if not series:
        agg = aggregate(rows, x)
        return {
            'categories': [r['label'] for r in agg],
            'series': [_series_block(metric, [_point(r, metric) for r in agg])],
        }

    series_keyfunc = GROUP_KEY_FUNCS[series]
    x_labels = {}
    series_labels = {}
    data = defaultdict(dict)

    for r in rows:
        xk, xl = x_keyfunc(r)
        sk, sl = series_keyfunc(r)
        x_labels[xk] = xl
        series_labels[sk] = sl
        data[sk].setdefault(xk, _new_bucket())
        _add_row(data[sk][xk], r)

    x_keys = _sorted_keys(x, x_labels)
    categories = [x_labels[k] for k in x_keys]

    result_series = []
    for sk in sorted(series_labels.keys(), key=lambda k: str(series_labels[k]).lower()):
        points = []
        for xk in x_keys:
            bucket = data[sk].get(xk)
            points.append(_point(_summarize(bucket), metric) if bucket else (0.0, None, False))
        result_series.append(_series_block(series_labels[sk], points))

    return {'categories': categories, 'series': result_series}

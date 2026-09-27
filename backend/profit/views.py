from datetime import date
from decimal import Decimal

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsManagerUser
from .models import CostComponentType, ProductCost
from .serializers import CostComponentTypeSerializer, ProductCostSerializer
from .services import CostLookup, aggregate, build_trend, compute_profit_rows, summary_totals


class IsAuthenticatedForReadManagerForWrite(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return IsManagerUser().has_permission(request, view)


class CostComponentTypeViewSet(viewsets.ModelViewSet):
    queryset = CostComponentType.objects.all()
    serializer_class = CostComponentTypeSerializer
    permission_classes = [IsAuthenticatedForReadManagerForWrite]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def perform_create(self, serializer):
        serializer.save(is_system=False)

    def update(self, request, *args, **kwargs):
        if self.get_object().is_system:
            return Response({'error': 'System cost components cannot be renamed.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if self.get_object().is_system:
            return Response({'error': 'System cost components cannot be deleted.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class ProductCostViewSet(viewsets.ModelViewSet):
    queryset = ProductCost.objects.select_related('product', 'component_type').all()
    serializer_class = ProductCostSerializer
    permission_classes = [IsAuthenticatedForReadManagerForWrite]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        qs = super().get_queryset()
        product_id = self.request.query_params.get('product')
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Current effective cost per component type for a product, as of today (or ?as_of=YYYY-MM-DD)."""
        product_id = request.query_params.get('product')
        if not product_id:
            return Response({'error': 'product query param is required'}, status=status.HTTP_400_BAD_REQUEST)
        product_id = int(product_id)

        as_of_param = request.query_params.get('as_of')
        as_of = date.fromisoformat(as_of_param) if as_of_param else date.today()

        lookup = CostLookup([product_id])
        breakdown = lookup.breakdown_as_of(product_id, as_of)
        component_names = {c.id: c.name for c in CostComponentType.objects.filter(id__in=breakdown.keys())}

        components = [
            {
                'component_type': component_id,
                'component_type_name': component_names.get(component_id, ''),
                'amount_per_dozen': amount,
                'valid_from': valid_from,
            }
            for component_id, (amount, valid_from) in breakdown.items()
        ]

        using_fallback = not bool(components)
        total = sum((c['amount_per_dozen'] for c in components), Decimal('0')) if components else lookup.cop_fallback(product_id)

        return Response({
            'product': product_id,
            'as_of': as_of,
            'components': components,
            'total_per_dozen': total,
            'using_fallback_cop': using_fallback,
        })


class ProfitFilterMixin:
    def _parse_filters(self, request):
        params = request.query_params
        return {
            'product_id': params.get('product') or None,
            'size_range_id': params.get('size_range') or None,
            'color_id': params.get('color') or None,
            'city': params.get('city') or None,
            'year': params.get('year') or None,
            'month': params.get('month') or None,
            'season': params.get('season') or None,
            'date_from': params.get('date_from') or None,
            'date_to': params.get('date_to') or None,
        }


class ProfitSummaryView(ProfitFilterMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filters = self._parse_filters(request)
        unit = request.query_params.get('unit', 'dozen')
        group_by = request.query_params.get('group_by')

        rows = compute_profit_rows(**filters)

        if group_by:
            return Response({'unit': unit, 'group_by': group_by, 'rows': aggregate(rows, group_by, unit)})
        return Response(summary_totals(rows, unit))


class ProfitTrendView(ProfitFilterMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filters = self._parse_filters(request)
        unit = request.query_params.get('unit', 'dozen')
        metric = request.query_params.get('metric', 'profit_amount')
        x = request.query_params.get('x', 'month')
        series = request.query_params.get('series') or None

        rows = compute_profit_rows(**filters)
        return Response(build_trend(rows, x, series=series, unit=unit, metric=metric))

from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Report
from .serializers import ReportSerializer
from sales.models import SaleItem
from django.db.models import Sum, Count, F


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]


def _base_sale_items(request):
    """Return SaleItem queryset filtered by optional date range from query params."""
    qs = SaleItem.objects.select_related(
        'sale', 'sale__customer', 'product', 'size_range', 'color'
    )
    start = request.query_params.get('start_date')
    end = request.query_params.get('end_date')
    if start:
        qs = qs.filter(sale__date__gte=start)
    if end:
        qs = qs.filter(sale__date__lte=end)
    return qs


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales_report(request):
    """Overall sales summary grouped by date."""
    qs = _base_sale_items(request)
    data = (
        qs
        .values(date=F('sale__date__date'))
        .annotate(
            total_sales=Sum(F('unit_price') * F('quantity_dozens')),
            total_dozens=Sum('quantity_dozens'),
            transaction_count=Count('sale', distinct=True),
        )
        .order_by('-date')
    )
    return Response(list(data))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_report(request):
    """Stock levels per product variant in dozens."""
    from products.models import ProductVariant
    variants = ProductVariant.objects.select_related('product', 'size_range', 'color').filter(
        quantity_dozens__gte=0
    ).values(
        'product__name', 'size_range__name', 'color__name', 'quantity_dozens'
    ).order_by('product__name', 'size_range__name', 'color__name')
    return Response(list(variants))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_report(request):
    """Sales grouped per customer."""
    qs = _base_sale_items(request)
    customer_id = request.query_params.get('customer')
    if customer_id:
        qs = qs.filter(sale__customer_id=customer_id)

    data = (
        qs
        .values('sale__customer_id', 'sale__customer__name', 'sale__customer__city')
        .annotate(
            total_sales=Sum(F('unit_price') * F('quantity_dozens')),
            total_dozens=Sum('quantity_dozens'),
            sale_count=Count('sale', distinct=True),
        )
        .order_by('-total_sales')
    )
    result = [
        {
            'customer_id': row['sale__customer_id'],
            'customer_name': row['sale__customer__name'],
            'city': row['sale__customer__city'] or '',
            'total_sales': float(row['total_sales'] or 0),
            'total_dozens': row['total_dozens'] or 0,
            'sale_count': row['sale_count'] or 0,
        }
        for row in data
    ]
    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def area_report(request):
    """Sales grouped by customer city/area."""
    qs = _base_sale_items(request)
    data = (
        qs
        .values(area=F('sale__customer__city'))
        .annotate(
            total_sales=Sum(F('unit_price') * F('quantity_dozens')),
            total_dozens=Sum('quantity_dozens'),
            customer_count=Count('sale__customer', distinct=True),
            sale_count=Count('sale', distinct=True),
        )
        .order_by('-total_sales')
    )
    result = [
        {
            'area': row['area'] or 'Unknown',
            'total_sales': float(row['total_sales'] or 0),
            'total_dozens': row['total_dozens'] or 0,
            'customer_count': row['customer_count'] or 0,
            'sale_count': row['sale_count'] or 0,
        }
        for row in data
    ]
    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def article_report(request):
    """Sales grouped by product (article)."""
    qs = _base_sale_items(request)
    product_id = request.query_params.get('product')
    if product_id:
        qs = qs.filter(product_id=product_id)

    data = (
        qs
        .values('product__id', 'product__name', 'product__unit')
        .annotate(
            total_sales=Sum(F('unit_price') * F('quantity_dozens')),
            total_dozens=Sum('quantity_dozens'),
            sale_count=Count('sale', distinct=True),
        )
        .order_by('-total_dozens')
    )
    result = [
        {
            'product_id': row['product__id'],
            'product_name': row['product__name'],
            'unit': row['product__unit'],
            'total_sales': float(row['total_sales'] or 0),
            'total_dozens': row['total_dozens'] or 0,
            'sale_count': row['sale_count'] or 0,
        }
        for row in data
    ]
    return Response(result)


class CustomerSalesReportView(APIView):
    """Detailed customer sales with size/color breakdown."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = _base_sale_items(request)
        product_id = request.query_params.get('product')
        size_range_id = request.query_params.get('size_range')
        color_id = request.query_params.get('color')
        customer_id = request.query_params.get('customer')

        if product_id:
            qs = qs.filter(product_id=product_id)
        if size_range_id:
            qs = qs.filter(size_range_id=size_range_id)
        if color_id:
            qs = qs.filter(color_id=color_id)
        if customer_id:
            qs = qs.filter(sale__customer_id=customer_id)

        data = (
            qs
            .values(
                'sale__customer_id', 'sale__customer__name', 'sale__customer__city',
                'product__name', 'size_range__name', 'color__name',
            )
            .annotate(
                total_sales=Sum(F('unit_price') * F('quantity_dozens')),
                total_dozens=Sum('quantity_dozens'),
            )
            .order_by('sale__customer__name', 'product__name')
        )
        result = [
            {
                'customer_id': row['sale__customer_id'],
                'customer_name': row['sale__customer__name'],
                'city': row['sale__customer__city'] or '',
                'product': row['product__name'],
                'size_range': row['size_range__name'],
                'color': row['color__name'],
                'total_sales': float(row['total_sales'] or 0),
                'total_dozens': row['total_dozens'] or 0,
            }
            for row in data
        ]
        return Response(result)

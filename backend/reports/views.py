from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Report
from .serializers import ReportSerializer
from sales.models import SaleItem
from decimal import Decimal

from django.db.models import Sum, Count, F
from django.utils import timezone

from customers.models import Customer
from payments.models import Payment
from products.models import Product
from purchases.models import Purchase
from raw_materials.models import RawMaterial
from sales.models import Sale
from vendors.models import Vendor


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
        qs = qs.filter(sale__date__date__gte=start)
    if end:
        qs = qs.filter(sale__date__date__lte=end)
    return qs


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales_report(request):
    """Overall sales summary grouped by date."""
    qs = _base_sale_items(request)
    data = (
        qs
        .values(date=F('sale__date__date'), unit=F('product__unit'))
        .annotate(
            total_sales=Sum('subtotal'),
            total_quantity=Sum('quantity'),
            transaction_count=Count('sale', distinct=True),
        )
        .order_by('-date')
    )
    return Response(list(data))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_report(request):
    """Stock levels per product variant, in each product's unit."""
    from products.models import ProductVariant
    variants = ProductVariant.objects.select_related('product', 'size_range', 'color').filter(
        quantity__gte=0
    ).values(
        'product__name', 'size_range__name', 'color__name', 'product__unit', 'quantity'
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
        .values('sale__customer_id', 'sale__customer__name', 'sale__customer__city', 'product__unit')
        .annotate(
            total_sales=Sum('subtotal'),
            total_quantity=Sum('quantity'),
            sale_count=Count('sale', distinct=True),
        )
        .order_by('-total_sales')
    )
    result = [
        {
            'customer_id': row['sale__customer_id'],
            'customer_name': row['sale__customer__name'],
            'city': row['sale__customer__city'] or '',
            'unit': row['product__unit'],
            'total_sales': float(round(row['total_sales'] or 0, 2)),
            'total_quantity': row['total_quantity'] or 0,
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
        .values(area=F('sale__customer__city'), unit=F('product__unit'))
        .annotate(
            total_sales=Sum('subtotal'),
            total_quantity=Sum('quantity'),
            customer_count=Count('sale__customer', distinct=True),
            sale_count=Count('sale', distinct=True),
        )
        .order_by('-total_sales')
    )
    result = [
        {
            'area': row['area'] or 'Unknown',
            'unit': row['unit'],
            'total_sales': float(round(row['total_sales'] or 0, 2)),
            'total_quantity': row['total_quantity'] or 0,
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
            total_sales=Sum('subtotal'),
            total_quantity=Sum('quantity'),
            sale_count=Count('sale', distinct=True),
        )
        .order_by('-total_quantity')
    )
    result = [
        {
            'product_id': row['product__id'],
            'product_name': row['product__name'],
            'unit': row['product__unit'],
            'total_sales': float(round(row['total_sales'] or 0, 2)),
            'total_quantity': row['total_quantity'] or 0,
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
                total_sales=Sum('subtotal'),
                total_quantity=Sum('quantity'),
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
                'total_sales': float(round(row['total_sales'] or 0, 2)),
                'total_quantity': row['total_quantity'] or 0,
            }
            for row in data
        ]
        return Response(result)


def _sum(queryset, field):
    return queryset.aggregate(total=Sum(field))['total'] or Decimal('0')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)

    sales = Sale.objects.all()
    received = Payment.objects.filter(payment_type=Payment.INCOMING)

    def period(start, end=None):
        sale_qs = sales.filter(date__date__gte=start, date__date__lte=end or today)
        payment_qs = received.filter(payment_date__date__gte=start, payment_date__date__lte=end or today)
        return {
            'sales_total': _sum(sale_qs, 'total_amount'),
            'sales_count': sale_qs.count(),
            'received_total': _sum(payment_qs, 'amount'),
        }

    return Response({
        'today': {'date': today, **period(today, today)},
        'month': {'start': month_start, 'end': today, **period(month_start)},
        'outstanding_customer_balance': _sum(Customer.objects.filter(balance__gt=0), 'balance'),
        'vendor_payables': _sum(Vendor.objects.filter(balance__gt=0), 'balance'),
        'vendor_bills_unpaid': _sum(Purchase.objects.all(), 'total_amount') - _sum(
            Payment.objects.filter(payment_type=Payment.OUTGOING, purchase__isnull=False), 'amount'
        ),
        'low_stock_raw_materials': RawMaterial.objects.filter(quantity__lte=F('reorder_level')).count(),
        'out_of_stock_products': Product.objects.filter(quantity__lte=0).count(),
    })

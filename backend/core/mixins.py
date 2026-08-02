"""
Mixins for import functionality across all entity ViewSets
"""
import csv
import io
import re
from decimal import Decimal, InvalidOperation
from difflib import SequenceMatcher

import pandas as pd
from django.db import transaction
from django.apps import apps
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Unit, ImportSession


def similarity_ratio(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def normalize_unit(value):
    """Normalize unit value for matching"""
    if not value:
        return None
    
    value = str(value).strip().upper()
    
    # Common aliases mapping
    aliases = {
        'KGS': 'KG',
        'KILOGRAMS': 'KG',
        'KILOGRAM': 'KG',
        'KILO': 'KILO',
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
    
    # Direct alias match
    if value in aliases:
        return aliases[value]
    
    return value


def find_or_create_unit(value):
    """
    Find existing unit or create new one.
    Returns (unit_code, is_new)
    """
    if not value:
        return None, False
    
    normalized = normalize_unit(value)
    
    # Try exact match first
    unit = Unit.objects.filter(code=normalized).first()
    if unit:
        return unit.code, False
    
    # Try fuzzy matching with existing units
    all_units = Unit.objects.all()
    best_match = None
    best_ratio = 0
    
    for unit in all_units:
        # Check code similarity
        code_ratio = similarity_ratio(normalized, unit.code)
        name_ratio = similarity_ratio(normalized, unit.name)
        
        max_ratio = max(code_ratio, name_ratio)
        if max_ratio > best_ratio:
            best_ratio = max_ratio
            best_match = unit
    
    # If similarity >= 80%, use existing unit
    if best_ratio >= 0.8 and best_match:
        return best_match.code, False
    
    # Create new unit
    # Generate a proper code and name
    code = normalized[:20]  # Max 20 chars
    name = value.strip().title()
    
    new_unit = Unit.objects.create(
        code=code,
        name=name,
        is_system=False
    )
    
    return new_unit.code, True


def parse_decimal(value, default=0):
    """Safely parse a decimal value"""
    if value is None or value == '' or (isinstance(value, float) and pd.isna(value)):
        return Decimal(str(default))
    try:
        # Handle string with commas
        if isinstance(value, str):
            value = value.replace(',', '').strip()
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal(str(default))


def parse_boolean(value, default=True):
    """Safely parse a boolean value"""
    if value is None or value == '' or (isinstance(value, float) and pd.isna(value)):
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 'active', 'y')
    return default


class BulkImportMixin:
    """
    Mixin to add bulk import functionality to ModelViewSets.
    
    Subclasses should define:
    - import_entity_type: str (e.g., 'customer', 'vendor')
    - import_fields: dict mapping field names to their config
    - import_unique_fields: list of fields that identify duplicates
    """
    
    import_entity_type = None
    import_fields = {}
    import_unique_fields = []
    
    def get_import_permissions(self):
        """Override to customize import permissions"""
        return [IsAdminUser()]
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser, JSONParser])
    def bulk_import(self, request):
        """
        Bulk import records from uploaded file or JSON data.
        
        Accepts:
        - File upload (CSV/Excel) with 'file' parameter
        - JSON array with 'data' parameter
        - 'mappings' parameter: JSON object mapping file columns to model fields
        """
        # Check permissions
        for permission in self.get_import_permissions():
            if not permission.has_permission(request, self):
                return Response(
                    {'error': 'You do not have permission to perform bulk imports.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        file = request.FILES.get('file')
        json_data = request.data.get('data')
        mappings = request.data.get('mappings', {})
        
        # Parse mappings if string
        if isinstance(mappings, str):
            import json
            try:
                mappings = json.loads(mappings)
            except:
                mappings = {}
        
        if not file and not json_data:
            return Response(
                {'error': 'No file or data provided. Upload a CSV/Excel file or send JSON data.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse file or use JSON data
        if file:
            try:
                df = self._parse_file(file)
            except Exception as e:
                return Response(
                    {'error': f'Failed to parse file: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Convert JSON data to DataFrame
            if isinstance(json_data, str):
                import json
                json_data = json.loads(json_data)
            df = pd.DataFrame(json_data)
        
        if df.empty:
            return Response(
                {'error': 'No data found in the uploaded file.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Apply column mappings
        if mappings:
            df = df.rename(columns=mappings)
        
        # Process import
        result = self._process_import(request, df, file.name if file else 'json_import')
        
        return Response(result, status=status.HTTP_200_OK if result['success_count'] > 0 else status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def download_template(self, request):
        """Download a CSV template with correct headers for this entity"""
        # Check permissions
        for permission in self.get_import_permissions():
            if not permission.has_permission(request, self):
                return Response(
                    {'error': 'You do not have permission to download templates.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Build template with field names and example data
        fields = self.get_import_field_config()
        headers = []
        examples = []
        
        for field_name, config in fields.items():
            headers.append(field_name)
            examples.append(config.get('example', ''))
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerow(examples)
        
        # Create response
        from django.http import HttpResponse
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.import_entity_type}_template.csv"'
        
        return response
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def preview_import(self, request):
        """
        Parse file and return preview data for mapping UI.
        Returns first 10 rows and detected columns.
        """
        file = request.FILES.get('file')
        
        if not file:
            return Response(
                {'error': 'No file provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            df = self._parse_file(file)
        except Exception as e:
            return Response(
                {'error': f'Failed to parse file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get preview data
        preview_rows = df.head(10).fillna('').to_dict('records')
        columns = list(df.columns)
        
        # Get expected fields for this entity
        expected_fields = self.get_import_field_config()
        
        # Auto-suggest mappings based on column names
        suggested_mappings = {}
        for col in columns:
            col_lower = col.lower().strip()
            for field_name, config in expected_fields.items():
                field_lower = field_name.lower()
                aliases = [a.lower() for a in config.get('aliases', [])]
                
                if col_lower == field_lower or col_lower in aliases:
                    suggested_mappings[col] = field_name
                    break
        
        return Response({
            'columns': columns,
            'preview_rows': preview_rows,
            'total_rows': len(df),
            'expected_fields': expected_fields,
            'suggested_mappings': suggested_mappings
        })
    
    def get_import_field_config(self):
        """
        Return field configuration for import.
        Override in subclass to customize.
        
        Format:
        {
            'field_name': {
                'required': bool,
                'type': 'string' | 'decimal' | 'boolean' | 'unit' | 'choice',
                'choices': [...],  # for choice type
                'example': 'Example value',
                'aliases': ['other_name', 'alt_name'],  # for auto-mapping
            }
        }
        """
        return self.import_fields

    @action(detail=False, methods=['get'])
    def get_import_fields(self, request):
        fields = []
        for name, config in self.import_fields.items():
            field = {'name': name}
            field.update(config)
            fields.append(field)
        return Response({'fields': fields})

    @action(detail=False, methods=['post'])
    def validate_import(self, request):
        if not request.FILES.get('file'):
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'valid': True})

    def _parse_file(self, file):
        """Parse uploaded CSV or Excel file into DataFrame"""
        filename = file.name.lower()
        
        if filename.endswith('.csv'):
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    file.seek(0)
                    df = pd.read_csv(file, encoding=encoding)
                    return df
                except UnicodeDecodeError:
                    continue
            raise ValueError('Unable to decode CSV file. Please use UTF-8 encoding.')
        
        elif filename.endswith(('.xlsx', '.xls')):
            file.seek(0)
            df = pd.read_excel(file, engine='openpyxl')
            return df
        
        else:
            raise ValueError('Unsupported file format. Please upload CSV or Excel (.xlsx) file.')
    
    def _process_import(self, request, df, filename):
        """Process the DataFrame and create records"""
        # Create import session
        session = ImportSession.objects.create(
            entity_type=self.import_entity_type,
            user=request.user,
            file_name=filename,
            total_rows=len(df),
            status='processing'
        )
        
        success_count = 0
        error_count = 0
        duplicate_count = 0
        imported_ids = []
        errors = []
        new_units = []
        
        # Get the model and serializer
        model = self.get_queryset().model
        serializer_class = self.get_serializer_class()
        
        # Process in batches of 100
        batch_size = 100
        total_batches = (len(df) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min((batch_num + 1) * batch_size, len(df))
            batch_df = df.iloc[start_idx:end_idx]
            
            for idx, row in batch_df.iterrows():
                row_num = idx + 2  # +2 for 1-based index and header row
                row_data = row.to_dict()
                
                try:
                    # Transform row data to model format
                    transformed_data, row_new_units = self._transform_row(row_data)
                    new_units.extend(row_new_units)
                    
                    # Check for duplicates
                    is_duplicate, duplicate_info = self._check_duplicate(transformed_data)
                    if is_duplicate:
                        duplicate_count += 1
                        errors.append({
                            'row': row_num,
                            'type': 'duplicate',
                            'message': f'Duplicate record found: {duplicate_info}',
                            'data': row_data
                        })
                        continue
                    
                    # Validate with serializer
                    serializer = serializer_class(data=transformed_data)
                    if not serializer.is_valid():
                        error_count += 1
                        errors.append({
                            'row': row_num,
                            'type': 'validation',
                            'message': str(serializer.errors),
                            'data': row_data
                        })
                        continue
                    
                    # Create record
                    with transaction.atomic():
                        instance = serializer.save()
                        imported_ids.append(instance.pk)
                        success_count += 1
                
                except Exception as e:
                    error_count += 1
                    errors.append({
                        'row': row_num,
                        'type': 'error',
                        'message': str(e),
                        'data': row_data
                    })
        
        # Update session
        session.success_count = success_count
        session.error_count = error_count
        session.duplicate_count = duplicate_count
        session.imported_ids = imported_ids
        session.errors = errors
        
        if success_count == 0 and error_count > 0:
            session.status = 'failed'
        elif error_count > 0 or duplicate_count > 0:
            session.status = 'partial'
        else:
            session.status = 'success'
        
        session.save()
        
        return {
            'session_id': str(session.id),
            'total_rows': len(df),
            'success_count': success_count,
            'error_count': error_count,
            'duplicate_count': duplicate_count,
            'new_units': list(set(new_units)),
            'errors': errors[:50],  # Limit errors in response
            'status': session.status
        }
    
    def _transform_row(self, row_data):
        """
        Transform row data from file format to model format.
        Override in subclass for custom transformations.
        Returns (transformed_data, new_units_created)
        """
        transformed = {}
        new_units = []
        fields = self.get_import_field_config()
        
        for field_name, config in fields.items():
            value = row_data.get(field_name)
            field_type = config.get('type', 'string')
            
            if field_type == 'decimal':
                transformed[field_name] = parse_decimal(value, config.get('default', 0))
            elif field_type == 'boolean':
                transformed[field_name] = parse_boolean(value, config.get('default', True))
            elif field_type == 'unit':
                unit_code, is_new = find_or_create_unit(value)
                transformed[field_name] = unit_code
                if is_new and unit_code:
                    new_units.append(unit_code)
            elif field_type == 'choice':
                # Normalize choice values
                choices = config.get('choices', [])
                if value:
                    value_upper = str(value).upper().strip()
                    for choice in choices:
                        if value_upper == choice.upper():
                            transformed[field_name] = choice
                            break
                    else:
                        # Use first choice as default
                        transformed[field_name] = choices[0] if choices else value
                else:
                    transformed[field_name] = config.get('default', choices[0] if choices else None)
            else:
                # String or other types
                if value is not None and not (isinstance(value, float) and pd.isna(value)):
                    transformed[field_name] = str(value).strip()
                elif config.get('required', False):
                    transformed[field_name] = ''
        
        return transformed, new_units
    
    def _check_duplicate(self, data):
        """
        Check if record already exists based on unique fields.
        Returns (is_duplicate, duplicate_info)
        """
        if not self.import_unique_fields:
            return False, None
        
        model = self.get_queryset().model
        filter_kwargs = {}
        
        for field in self.import_unique_fields:
            value = data.get(field)
            if value is not None:
                # Case-insensitive match for string fields
                filter_kwargs[f'{field}__iexact'] = value
        
        if not filter_kwargs:
            return False, None
        
        existing = model.objects.filter(**filter_kwargs).first()
        if existing:
            return True, str(existing)
        
        return False, None


class BulkExportMixin:
    """
    Mixin to add bulk export functionality to ModelViewSets.
    
    Subclasses should define:
    - export_fields: dict mapping field names to their display config
    - export_filename: str base filename for exports
    """
    
    export_fields = {}
    export_filename = 'export'
    
    def get_export_permissions(self):
        """Override to customize export permissions"""
        from rest_framework.permissions import IsAuthenticated
        return [IsAuthenticated()]
    
    def get_export_queryset(self):
        """Override to customize the queryset for export"""
        return self.get_queryset()
    
    def get_export_field_config(self):
        """
        Return field configuration for export.
        Override in subclass to customize.
        
        Format:
        {
            'field_name': {
                'label': 'Display Label',
                'type': 'string' | 'decimal' | 'boolean' | 'date' | 'datetime',
                'format': 'optional format string',
            }
        }
        """
        return self.export_fields
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export records to CSV or Excel format.
        
        Query params:
        - export_format: 'csv' or 'excel' (default: csv)
        - fields: comma-separated list of fields to include (optional)
        - All other filter params supported by the viewset
        """
        # Check permissions
        for permission in self.get_export_permissions():
            if not permission.has_permission(request, self):
                return Response(
                    {'error': 'You do not have permission to export data.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        export_format = request.query_params.get('export_format', 'csv').lower()
        requested_fields = request.query_params.get('fields', '')
        
        if export_format not in ('csv', 'excel', 'xlsx'):
            return Response(
                {'error': 'Invalid format. Use "csv" or "excel".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get queryset (applies any filters from URL params)
        queryset = self.filter_queryset(self.get_export_queryset())
        
        # Get field configuration
        field_config = self.get_export_field_config()
        
        # Filter fields if requested
        if requested_fields:
            requested = [f.strip() for f in requested_fields.split(',')]
            field_config = {k: v for k, v in field_config.items() if k in requested}
        
        if not field_config:
            return Response(
                {'error': 'No fields to export.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Build export data
        data = []
        for obj in queryset:
            row = {}
            for field_name, config in field_config.items():
                value = self._get_field_value(obj, field_name, config)
                label = config.get('label', field_name)
                row[label] = value
            data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Generate response
        if export_format in ('excel', 'xlsx'):
            return self._export_excel(df)
        else:
            return self._export_csv(df)
    
    def _get_field_value(self, obj, field_name, config):
        """Extract and format field value from object"""
        # Handle nested fields (e.g., 'user.username')
        value = obj
        for part in field_name.split('.'):
            if value is None:
                break
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break
        
        # Handle callable (methods, properties)
        if callable(value):
            value = value()
        
        # Format based on type
        field_type = config.get('type', 'string')
        
        if value is None:
            return ''
        
        if field_type == 'boolean':
            return 'Yes' if value else 'No'
        elif field_type == 'date':
            if hasattr(value, 'strftime'):
                fmt = config.get('format', '%Y-%m-%d')
                return value.strftime(fmt)
            return str(value)
        elif field_type == 'datetime':
            if hasattr(value, 'strftime'):
                fmt = config.get('format', '%Y-%m-%d %H:%M:%S')
                return value.strftime(fmt)
            return str(value)
        elif field_type == 'decimal':
            if isinstance(value, Decimal):
                return float(value)
            return value
        else:
            return str(value) if value else ''
    
    def _export_csv(self, df):
        """Export DataFrame as CSV"""
        from django.http import HttpResponse
        
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8')
        
        response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{self.export_filename}.csv"'
        
        return response
    
    def _export_excel(self, df):
        """Export DataFrame as Excel"""
        from django.http import HttpResponse
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=self.export_filename[:31])
        
        output.seek(0)
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{self.export_filename}.xlsx"'
        
        return response


class BatchActionsMixin:
    """
    Mixin to add batch operations to ModelViewSets.
    
    Provides:
    - bulk_delete: Delete multiple records at once
    - bulk_update: Update multiple records with same values
    - bulk_activate: Set is_active=True for multiple records
    - bulk_deactivate: Set is_active=False for multiple records
    """
    
    def get_batch_permissions(self):
        """Override to customize batch action permissions"""
        from rest_framework.permissions import IsAuthenticated
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """
        Delete multiple records.
        
        Request body:
        {
            "ids": [1, 2, 3, ...]
        }
        """
        # Check permissions
        for permission in self.get_batch_permissions():
            if not permission.has_permission(request, self):
                return Response(
                    {'error': 'You do not have permission to perform batch operations.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response(
                {'error': 'No IDs provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(ids, list):
            return Response(
                {'error': 'IDs must be a list.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(pk__in=ids)
        count = queryset.count()
        
        if count == 0:
            return Response(
                {'error': 'No matching records found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if any records cannot be deleted
        errors = []
        deleted_count = 0
        
        with transaction.atomic():
            for obj in queryset:
                try:
                    # Check for custom delete validation
                    if hasattr(self, 'validate_batch_delete'):
                        error = self.validate_batch_delete(obj)
                        if error:
                            errors.append({'id': obj.pk, 'error': error})
                            continue
                    
                    obj.delete()
                    deleted_count += 1
                except Exception as e:
                    errors.append({'id': obj.pk, 'error': str(e)})
        
        return Response({
            'deleted_count': deleted_count,
            'errors': errors if errors else None,
            'message': f'Successfully deleted {deleted_count} record(s).'
        })
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Update multiple records with the same values.
        
        Request body:
        {
            "ids": [1, 2, 3, ...],
            "data": {
                "field1": "value1",
                "field2": "value2"
            }
        }
        """
        # Check permissions
        for permission in self.get_batch_permissions():
            if not permission.has_permission(request, self):
                return Response(
                    {'error': 'You do not have permission to perform batch operations.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        ids = request.data.get('ids', [])
        update_data = request.data.get('data', {})
        
        if not ids:
            return Response(
                {'error': 'No IDs provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not update_data:
            return Response(
                {'error': 'No update data provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get allowed fields for batch update
        allowed_fields = getattr(self, 'batch_update_fields', None)
        if allowed_fields:
            update_data = {k: v for k, v in update_data.items() if k in allowed_fields}
            
            if not update_data:
                return Response(
                    {'error': f'No valid fields to update. Allowed fields: {allowed_fields}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        queryset = self.get_queryset().filter(pk__in=ids)
        count = queryset.count()
        
        if count == 0:
            return Response(
                {'error': 'No matching records found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Perform update
        try:
            with transaction.atomic():
                updated_count = queryset.update(**update_data)
            
            return Response({
                'updated_count': updated_count,
                'message': f'Successfully updated {updated_count} record(s).'
            })
        except Exception as e:
            return Response(
                {'error': f'Update failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def bulk_activate(self, request):
        """
        Activate multiple records (set is_active=True).
        
        Request body:
        {
            "ids": [1, 2, 3, ...]
        }
        """
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response(
                {'error': 'No IDs provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if model has is_active field
        model = self.get_queryset().model
        if not hasattr(model, 'is_active'):
            return Response(
                {'error': 'This entity does not support activation/deactivation.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(pk__in=ids)
        updated_count = queryset.update(is_active=True)
        
        return Response({
            'updated_count': updated_count,
            'message': f'Successfully activated {updated_count} record(s).'
        })
    
    @action(detail=False, methods=['post'])
    def bulk_deactivate(self, request):
        """
        Deactivate multiple records (set is_active=False).
        
        Request body:
        {
            "ids": [1, 2, 3, ...]
        }
        """
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response(
                {'error': 'No IDs provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if model has is_active field
        model = self.get_queryset().model
        if not hasattr(model, 'is_active'):
            return Response(
                {'error': 'This entity does not support activation/deactivation.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(pk__in=ids)
        updated_count = queryset.update(is_active=False)
        
        return Response({
            'updated_count': updated_count,
            'message': f'Successfully deactivated {updated_count} record(s).'
        })

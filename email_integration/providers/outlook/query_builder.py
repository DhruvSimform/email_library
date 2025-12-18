from __future__ import annotations

from email_integration.domain.models.email_filter import EmailSearchFilter


class OutlookQueryBuilder:
    """
    Translates provider-agnostic EmailSearchFilter
    into Microsoft Graph (Outlook) query parameters.

    Output keys:
    - $filter  → structured OData filters
    - $search  → full-text search
    - $orderby → sorting

    Field Consistency:
    - All fields used in $filter are tracked
    - $orderby is built from tracked filter fields + receivedDateTime
    - Ensures API compatibility and consistent sorting behavior
    """

    # ==========================================
    # OData Field Catalog
    # Valid Microsoft Graph API fields that can be
    # used in both $filter and $orderby
    # ==========================================
    FILTERABLE_FIELDS = {
        'hasAttachments',
        'receivedDateTime',
        'InferenceClassification',
        'flag/flagStatus',
    }

    @staticmethod
    def _extract_field_from_special_filter(special_filter: str) -> str | None:
        """
        Extract the field name from a special filter string.
        
        Examples:
            "hasAttachments eq true" → "hasAttachments"
            "InferenceClassification eq 'Focused'" → "InferenceClassification"
            "flag/flagStatus eq 'flagged'" → "flag/flagStatus"
        """
        if " " not in special_filter:
            return None
        
        field = special_filter.split()[0]
        
        # Handle nested properties like "flag/flagStatus"
        if field in OutlookQueryBuilder.FILTERABLE_FIELDS:
            return field
        return None

    @staticmethod
    def build(filters: EmailSearchFilter, special_filters: list[str] | None = None, special_order: str | None = None) -> dict[str, str]:
        filter_parts: list[str] = []
        search_parts: list[str] = []
        active_filter_fields: list[str] = []  # Track which fields are used in filters

        if special_filters:
            filter_parts.extend(special_filters)
            # Extract field names from special filters for orderby consistency
            for special_filter in special_filters:
                field = OutlookQueryBuilder._extract_field_from_special_filter(special_filter)
                if field and field not in active_filter_fields:
                    active_filter_fields.append(field)
        
        # =========================
        # Address-based filters
        # =========================
        if filters.from_address:
            search_parts.append(f"from:{filters.from_address}")

        if filters.to_addresses:
            for address in filters.to_addresses:
                search_parts.append(f"recipients:{address}")
        
        # =========================
        # Content-based filters
        # =========================
        if filters.subject_contains:
            search_parts.append(f"subject:{filters.subject_contains}")

        if filters.body_contains:
            search_parts.append(filters.body_contains)

        if filters.has_words:
            search_parts.extend(filters.has_words)

        # =========================
        # Attachment-based filters
        # =========================
        if filters.has_attachments is True:
            filter_parts.append("hasAttachments eq true")
            if 'hasAttachments' not in active_filter_fields:
                active_filter_fields.append('hasAttachments')

        # =========================
        # Read / unread filters
        # =========================
        if filters.is_read is True:
            filter_parts.append("isRead eq true")
        elif filters.is_read is False:
            filter_parts.append("isRead eq false")


        # =========================
        # Date-based filters
        # =========================
        if filters.start_date:
            filter_parts.append(
                f"receivedDateTime ge {filters.start_date.isoformat()}"
            )
            if 'receivedDateTime' not in active_filter_fields:
                active_filter_fields.append('receivedDateTime')

        if filters.end_date:
            filter_parts.append(
                f"receivedDateTime le {filters.end_date.isoformat()}"
            )
            if 'receivedDateTime' not in active_filter_fields:
                active_filter_fields.append('receivedDateTime')

        
        # =========================
        # Final assembly
        # =========================
        params: dict[str, str] = {}

        if filter_parts:
            params["$filter"] = " and ".join(filter_parts)
        if search_parts:
            params["$search"] = f"\"{' '.join(search_parts)}\""

        # =========================
        # Build orderby parameter
        # =========================
        # Priority: special_order > auto-generated from active fields > receivedDateTime
        if special_order:
            params["$orderby"] = special_order
        elif active_filter_fields:
            # Auto-generate orderby from active filter fields + receivedDateTime
            orderby_fields = []
            
            # Add active filter fields in the order they were tracked
            for field in active_filter_fields:
                if field != 'receivedDateTime':
                    orderby_fields.append(field)
            
            # Always end with receivedDateTime for consistent secondary sorting
            orderby_fields.append("receivedDateTime desc")
            
            params["$orderby"] = ",".join(orderby_fields)
        # else:
        #     params["$orderby"] = "receivedDateTime desc"

        return params

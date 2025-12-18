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
    """

    @staticmethod
    def build(filters: EmailSearchFilter, special_filters: list[str] | None = None, special_order: str | None = None) -> dict[str, str]:
        filter_parts: list[str] = []
        search_parts: list[str] = []

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

        if filters.end_date:
            filter_parts.append(
                f"receivedDateTime le {filters.end_date.isoformat()}"
            )

        if special_filters:
            filter_parts.extend(special_filters)
        
        # =========================
        # Final assembly
        # =========================
        params: dict[str, str] = {}

        if filter_parts:
            params["$filter"] = " and ".join(filter_parts)

        if search_parts:
            params["$search"] = f"\"{' '.join(search_parts)}\""

        if special_order:
            params["$orderby"] = special_order
        # else:
        #     params["$orderby"] = "receivedDateTime desc"

        return params

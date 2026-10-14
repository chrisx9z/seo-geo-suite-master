# -*- coding: utf-8 -*-
from .healer import Auto404Healer
from .datetime_schema_healer import DateTimeSchemaHealer, DateTimeAuditResult

AutoHealer = Auto404Healer

__all__ = [
    'Auto404Healer',
    'AutoHealer',
    'DateTimeSchemaHealer',
    'DateTimeAuditResult',
]

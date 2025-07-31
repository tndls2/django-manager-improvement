from typing import Optional, Dict, List, Any
from django.db.models import Q, QuerySet
from django.db import models
from rest_framework.generics import get_object_or_404

from .query_builder import QueryBuilder


class BaseManager:
    """
    기본 Manager 클래스 - 모든 Manager가 상속받아 사용
    """
    model_class = None
    
    @classmethod
    def query(cls, queryset: Optional[QuerySet] = None) -> QueryBuilder:
        """QueryBuilder 인스턴스 반환"""
        return QueryBuilder(cls.model_class, queryset)
    
    @classmethod
    def get_queryset(cls, **base_filters) -> QuerySet:
        """기본 QuerySet 반환"""
        return cls.model_class.objects.filter(**base_filters)
    
    @classmethod
    def get(cls, **kwargs):
        """단일 객체 조회"""
        return cls.model_class.objects.filter(**kwargs).first()
    
    @classmethod
    def get_or_404(cls, **kwargs):
        """단일 객체 조회 (404 에러)"""
        return get_object_or_404(cls.model_class, **kwargs)
    
    @classmethod
    def get_list(
        cls,
        filters: Dict = None,
        excludes: Dict = None,
        order_by: List[str] = None,
        select_related: List[str] = None,
        prefetch_related: List[str] = None,
        **base_filters
    ) -> QuerySet:
        """기본 리스트 조회"""
        builder = cls.query().filter(**base_filters)
        
        if filters:
            for key, value in filters.items():
                builder = builder.filter(**{key: value})
                
        if excludes:
            for key, value in excludes.items():
                builder = builder.exclude(**{key: value})
                
        if select_related:
            builder = builder.select_related(*select_related)
            
        if prefetch_related:
            builder = builder.prefetch_related(*prefetch_related)
            
        if order_by:
            builder = builder.order_by(*order_by)
            
        return builder.build()
    
    @classmethod
    def create(cls, **data):
        """객체 생성"""
        return cls.model_class.objects.create(**data)
    
    @classmethod
    def update_or_create(cls, defaults: Dict = None, **kwargs):
        """객체 생성 또는 업데이트"""
        return cls.model_class.objects.update_or_create(
            defaults=defaults or {}, **kwargs
        )
    
    @classmethod
    def bulk_create(cls, objs: List[Dict], **kwargs):
        """대량 생성"""
        instances = [cls.model_class(**obj) for obj in objs]
        return cls.model_class.objects.bulk_create(instances, **kwargs)
    
    @classmethod
    def bulk_update(cls, objs: List, fields: List[str], **kwargs):
        """대량 업데이트"""
        return cls.model_class.objects.bulk_update(objs, fields, **kwargs)
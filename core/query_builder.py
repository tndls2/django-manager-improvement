from django.db.models import Q, QuerySet
from typing import Any, Dict, List, Optional, Union


class QueryBuilder:
    """
    Django ORM 쿼리 빌더 - 체이닝과 복잡한 쿼리 작성을 위한 헬퍼 클래스
    """
    
    def __init__(self, model_class, queryset: Optional[QuerySet] = None):
        self.model_class = model_class
        self._queryset = queryset or model_class.objects.all()
        self._q_filters = Q()
        self._q_excludes = Q()
        
    def filter(self, **kwargs) -> 'QueryBuilder':
        """기본 필터링"""
        self._queryset = self._queryset.filter(**kwargs)
        return self
        
    def exclude(self, **kwargs) -> 'QueryBuilder':
        """기본 제외"""
        self._queryset = self._queryset.exclude(**kwargs)
        return self
        
    def q_filter(self, q_obj: Q) -> 'QueryBuilder':
        """Q 객체를 사용한 필터링"""
        self._q_filters &= q_obj
        return self
        
    def q_exclude(self, q_obj: Q) -> 'QueryBuilder':
        """Q 객체를 사용한 제외"""
        self._q_excludes |= q_obj
        return self
        
    def or_filter(self, *q_objs: Q) -> 'QueryBuilder':
        """OR 조건 필터링"""
        or_q = Q()
        for q_obj in q_objs:
            or_q |= q_obj
        self._q_filters &= or_q
        return self
        
    def select_related(self, *fields) -> 'QueryBuilder':
        """select_related 체이닝"""
        self._queryset = self._queryset.select_related(*fields)
        return self
        
    def prefetch_related(self, *fields) -> 'QueryBuilder':
        """prefetch_related 체이닝"""
        self._queryset = self._queryset.prefetch_related(*fields)
        return self
        
    def annotate(self, **kwargs) -> 'QueryBuilder':
        """annotate 체이닝"""
        self._queryset = self._queryset.annotate(**kwargs)
        return self
        
    def order_by(self, *fields) -> 'QueryBuilder':
        """정렬"""
        self._queryset = self._queryset.order_by(*fields)
        return self
        
    def distinct(self, *fields) -> 'QueryBuilder':
        """중복 제거"""
        if fields:
            self._queryset = self._queryset.distinct(*fields)
        else:
            self._queryset = self._queryset.distinct()
        return self
        
    def using(self, db_alias: str) -> 'QueryBuilder':
        """데이터베이스 지정"""
        self._queryset = self._queryset.using(db_alias)
        return self
        
    def build(self) -> QuerySet:
        """최종 QuerySet 반환"""
        if self._q_filters:
            self._queryset = self._queryset.filter(self._q_filters)
        if self._q_excludes:
            self._queryset = self._queryset.exclude(self._q_excludes)
        return self._queryset
        
    def get(self, **kwargs):
        """단일 객체 조회"""
        return self.build().get(**kwargs)
        
    def first(self):
        """첫 번째 객체 조회"""
        return self.build().first()
        
    def last(self):
        """마지막 객체 조회"""
        return self.build().last()
        
    def count(self) -> int:
        """개수 조회"""
        return self.build().count()
        
    def exists(self) -> bool:
        """존재 여부 확인"""
        return self.build().exists()
        
    def values(self, *fields):
        """values 조회"""
        return self.build().values(*fields)
        
    def values_list(self, *fields, **kwargs):
        """values_list 조회"""
        return self.build().values_list(*fields, **kwargs)
from typing import Dict, List, Optional

from django.db.models import Model, QuerySet
from django.shortcuts import get_object_or_404


class BaseManager:
    """
    기본 Manager 클래스
    - 기본 CRUD 연산 제공
    - 각 도메인 Manager는 이를 상속받아 비즈니스 로직 메서드 추가
    """

    model_class = None

    @classmethod
    def get_by_id(cls, pk) -> Optional[Model]:
        """ID로 단일 객체 조회"""
        return cls.model_class.objects.filter(pk=pk).first()

    @classmethod
    def get_by_id_or_404(cls, pk) -> Model:
        """ID로 단일 객체 조회 (404 에러)"""
        return get_object_or_404(cls.model_class, pk=pk)

    @classmethod
    def get_one(cls, **kwargs) -> Optional[Model]:
        """조건으로 단일 객체 조회"""
        return cls.model_class.objects.filter(**kwargs).first()

    @classmethod
    def get_or_404(cls, **kwargs) -> Model:
        """조건으로 단일 객체 조회 (404 에러)"""
        return get_object_or_404(cls.model_class, **kwargs)

    @classmethod
    def find_all(cls, **kwargs) -> QuerySet:
        """모든 객체 조회"""
        return cls.model_class.objects.filter(**kwargs)

    @classmethod
    def exists(cls, **kwargs) -> bool:
        """객체 존재 여부 확인"""
        return cls.model_class.objects.filter(**kwargs).exists()

    @classmethod
    def count(cls, **kwargs) -> int:
        """객체 개수 조회"""
        return cls.model_class.objects.filter(**kwargs).count()

    @classmethod
    def create(cls, **data) -> Model:
        """단일 객체 생성"""
        instance = cls.model_class(**data)
        instance.save()
        return instance

    @classmethod
    def create_or_update(cls, defaults: Dict = None, **kwargs) -> tuple:
        """객체 생성 또는 업데이트"""
        return cls.model_class.objects.update_or_create(
            defaults=defaults or {}, **kwargs
        )

    @classmethod
    def bulk_create(cls, objs: List[Dict], **kwargs) -> List[Model]:
        """대량 생성"""
        instances = [cls.model_class(**obj) for obj in objs]
        return cls.model_class.objects.bulk_create(instances, **kwargs)

    @classmethod
    def update_by_id(cls, pk, **data) -> int:
        """ID로 객체 업데이트"""
        return cls.model_class.objects.filter(pk=pk).update(**data)

    @classmethod
    def update_all(cls, filters: Dict, **data) -> int:
        """조건에 맞는 모든 객체 업데이트"""
        return cls.model_class.objects.filter(**filters).update(**data)

    @classmethod
    def bulk_update(cls, objs: List[Model], fields: List[str], **kwargs) -> List[Model]:
        """대량 업데이트"""
        return cls.model_class.objects.bulk_update(objs, fields, **kwargs)

    @classmethod
    def delete_by_id(cls, pk) -> tuple:
        """ID로 객체 삭제"""
        return cls.model_class.objects.filter(pk=pk).delete()

    @classmethod
    def delete_all(cls, **kwargs) -> tuple:
        """조건에 맞는 모든 객체 삭제"""
        return cls.model_class.objects.filter(**kwargs).delete()

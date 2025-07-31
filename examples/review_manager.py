"""
개선된 Review Manager 예시
"""
from typing import Optional, Dict, List
from django.db.models import Q, Count, Avg, Sum, QuerySet
from django.db import transaction

from core.base_manager import BaseManager
# from review.models import Review  # 실제 프로젝트에서는 모델 import


class ReviewManager(BaseManager):
    """
    개선된 Review Manager - QueryBuilder를 활용한 체이닝 지원
    """
    # model_class = Review  # 실제 프로젝트에서는 모델 클래스 지정
    
    @classmethod
    def get_by_shop(cls, shop_id: int):
        """특정 샵의 리뷰 QueryBuilder 반환"""
        return cls.query().filter(shop_id=shop_id)
    
    @classmethod
    def get_published_reviews(cls, shop_id: int):
        """게시된 리뷰만 조회"""
        return (cls.get_by_shop(shop_id)
                .filter(posting_status='published')
                .filter(is_deleted=False)
                .build())
    
    @classmethod
    def get_reviews_with_high_rating(cls, shop_id: int, min_rating: int = 4):
        """높은 평점 리뷰 조회"""
        return (cls.get_by_shop(shop_id)
                .filter(ratings__gte=min_rating)
                .filter(posting_status='published')
                .order_by('-ratings', '-created_at')
                .build())
    
    @classmethod
    def get_reviews_with_media(cls, shop_id: int):
        """미디어가 있는 리뷰 조회"""
        return (cls.get_by_shop(shop_id)
                .or_filter(
                    Q(review_photo_set__isnull=False),
                    Q(review_video_set__isnull=False)
                )
                .prefetch_related('review_photo_set', 'review_video_set')
                .distinct()
                .build())
    
    @classmethod
    def get_product_reviews_with_stats(cls, shop_id: int, product_id: int):
        """상품별 리뷰와 통계"""
        return (cls.get_by_shop(shop_id)
                .filter(product_id=product_id)
                .filter(posting_status='published')
                .select_related('product_fk', 'order_item_fk__order_fk')
                .prefetch_related('review_badge', 'review_photo_set')
                .annotate(
                    badge_count=Count('review_badge'),
                    photo_count=Count('review_photo_set')
                )
                .order_by('-created_at')
                .build())
    
    @classmethod
    def get_reviews_by_date_range(cls, shop_id: int, start_date, end_date):
        """날짜 범위별 리뷰 조회"""
        return (cls.get_by_shop(shop_id)
                .filter(created_at__date__gte=start_date)
                .filter(created_at__date__lte=end_date)
                .order_by('-created_at')
                .build())
    
    @classmethod
    def get_sns_reviews_pending(cls, shop_id: int):
        """SNS 인증 대기 중인 리뷰"""
        return (cls.get_by_shop(shop_id)
                .filter(review_type='SNS')
                .filter(is_sns_completed=False)
                .filter(sns_deauthed_at__isnull=True)
                .select_related('product_fk')
                .build())
    
    @classmethod
    def get_reviews_with_complex_filter(cls, shop_id: int, filters: Dict):
        """복잡한 필터링 조건"""
        builder = cls.get_by_shop(shop_id)
        
        # 평점 필터
        if 'min_rating' in filters:
            builder = builder.filter(ratings__gte=filters['min_rating'])
        if 'max_rating' in filters:
            builder = builder.filter(ratings__lte=filters['max_rating'])
            
        # 텍스트 검색
        if 'search_text' in filters:
            builder = builder.or_filter(
                Q(content__icontains=filters['search_text']),
                Q(product_fk__name__icontains=filters['search_text'])
            )
            
        # 미디어 필터
        if filters.get('has_media'):
            builder = builder.or_filter(
                Q(review_photo_set__isnull=False),
                Q(review_video_set__isnull=False)
            ).distinct()
            
        # 뱃지 필터
        if filters.get('has_badge'):
            builder = builder.filter(review_badge__isnull=False).distinct()
            
        return (builder
                .select_related('product_fk', 'order_item_fk__order_fk')
                .prefetch_related('review_badge', 'review_photo_set')
                .annotate(badge_count=Count('review_badge'))
                .order_by('-created_at')
                .build())
    
    @classmethod
    def get_review_statistics(cls, shop_id: int):
        """리뷰 통계 조회"""
        return (cls.get_by_shop(shop_id)
                .filter(posting_status='published')
                .aggregate(
                    total_count=Count('id'),
                    avg_rating=Avg('ratings'),
                    total_points=Sum('total_point')
                ))
    
    @classmethod
    def get_badge_creatable_reviews(cls, shop_id: int, max_badge_count: int = 3):
        """뱃지 추가 가능한 리뷰"""
        return (cls.get_by_shop(shop_id)
                .filter(posting_status='published')
                .annotate(badge_count=Count('review_badge'))
                .filter(badge_count__lt=max_badge_count)
                .prefetch_related('review_badge')
                .build())
    
    @classmethod
    @transaction.atomic
    def bulk_update_status(cls, shop_id: int, review_ids: List[int], 
                          status: str) -> int:
        """리뷰 상태 대량 업데이트"""
        updated_count = (cls.get_by_shop(shop_id)
                        .filter(id__in=review_ids)
                        .build()
                        .update(posting_status=status))
        return updated_count
    
    @classmethod
    def soft_delete(cls, shop_id: int, review_id: int):
        """소프트 삭제"""
        return (cls.get_by_shop(shop_id)
                .filter(id=review_id)
                .build()
                .update(
                    is_deleted=True,
                    is_visible=False,
                    posting_status='hidden'
                ))
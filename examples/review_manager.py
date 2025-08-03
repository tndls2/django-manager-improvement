from datetime import date
from typing import Dict, List

from django.db import transaction
from django.db.models import Avg, Count, Q, QuerySet, Sum

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_manager import BaseManager
from models import Review


class ReviewManager(BaseManager):
    """
    Review 도메인 Manager

    - BaseManager의 기본 CRUD 상속
    - 리뷰 비즈니스 로직에 특화된 메서드 제공
    """

    model_class: type[Review] = Review

    @classmethod
    def find_posted_by_shop(cls, shop_id: int) -> QuerySet:
        """shop 별 게시된 리뷰 조회"""
        return cls.find_all(shop_id=shop_id, posting_status="게시됨", is_deleted=False)

    @classmethod
    def find_by_product(cls, shop_id: int, product_id: int) -> QuerySet:
        """상품별 리뷰 조회"""
        return cls.find_all(shop_id=shop_id, product_id=product_id)

    @classmethod
    def find_high_rating_reviews(cls, shop_id: int, min_rating: int = 4) -> QuerySet:
        """높은 평점 리뷰 조회"""
        return (
            Review.objects.filter(shop_id=shop_id, ratings__gte=min_rating)
            .filter(posting_status="게시됨")
            .order_by("-ratings", "-created_at")
        )

    @classmethod
    def find_reviews_with_media(cls, shop_id: int) -> QuerySet:
        """미디어가 있는 리뷰 조회 (기본 구현)"""
        return cls.model_class.objects.filter(shop_id=shop_id)

    @classmethod
    def find_by_date_range(
        cls, shop_id: int, start_date: date, end_date: date
    ) -> QuerySet:
        """날짜 범위별 리뷰 조회"""
        return (
            cls.model_class.objects.filter(shop_id=shop_id)
            .filter(created_at__date__gte=start_date)
            .filter(created_at__date__lte=end_date)
            .order_by("-created_at")
        )

    @classmethod
    def find_sns_pending_reviews(cls, shop_id: int) -> QuerySet:
        """SNS 인증 대기 중인 리뷰 조회"""
        return cls.model_class.objects.filter(
            shop_id=shop_id,
            review_type="SNS",
            is_sns_completed=False,
            sns_deauthed_at__isnull=True,
        ).select_related("product_fk")

    @classmethod
    def get_shop_review_stats(cls, shop_id: int) -> Dict:
        """샵 리뷰 통계 조회"""
        return cls.model_class.objects.filter(
            shop_id=shop_id, posting_status="게시됨"
        ).aggregate(
            total_count=Count("id"),
            avg_rating=Avg("ratings"),
            total_points=Sum("total_point"),
        )

    @classmethod
    def search_reviews(cls, shop_id: int, search_params: Dict) -> QuerySet:
        """리뷰 검색 (복잡한 필터링)"""
        queryset = cls.model_class.objects.filter(shop_id=shop_id)

        # 평점 범위
        if "min_rating" in search_params:
            queryset = queryset.filter(ratings__gte=search_params["min_rating"])
        if "max_rating" in search_params:
            queryset = queryset.filter(ratings__lte=search_params["max_rating"])

        # 키워드 검색
        if "keyword" in search_params:
            queryset = queryset.filter(
                Q(content__icontains=search_params["keyword"])
                | Q(product_fk__name__icontains=search_params["keyword"])
            )

        # 미디어 필터
        if search_params.get("has_media"):
            queryset = queryset.filter(
                Q(reviewphoto__isnull=False) | Q(reviewvideo__isnull=False)
            ).distinct()

        # 뱃지 필터
        if search_params.get("has_badge"):
            queryset = queryset.filter(reviewbadge__isnull=False).distinct()

        return (
            queryset.select_related("product_fk")
            .order_by("-created_at")
        )

    @classmethod
    def post_review(cls, shop_id: int, review_id: int) -> bool:
        """리뷰 게시"""
        updated = cls.update_all(
            {"shop_id": shop_id, "id": review_id},
            posting_status="게시됨",
            is_visible=True,
        )
        return updated > 0

    @classmethod
    def hide_review(cls, shop_id: int, review_id: int) -> bool:
        """리뷰 숨김"""
        updated = cls.update_all(
            {"shop_id": shop_id, "id": review_id},
            posting_status="숨김",
            is_visible=False,
        )
        return updated > 0

    @classmethod
    @transaction.atomic
    def bulk_update_status(
        cls, shop_id: int, review_ids: List[int], status: str
    ) -> int:
        """리뷰 상태 대량 업데이트"""
        return cls.update_all(
            {"shop_id": shop_id, "id__in": review_ids}, posting_status=status
        )

    @classmethod
    def soft_delete_review(cls, shop_id: int, review_id: int) -> bool:
        """리뷰 소프트 삭제"""
        updated = cls.update_all(
            {"shop_id": shop_id, "id": review_id},
            is_deleted=True,
            is_visible=False,
            posting_status="숨김",
        )
        return updated > 0

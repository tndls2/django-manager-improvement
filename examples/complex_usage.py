"""
복잡한 쿼리에서의 개선된 Manager 사용 예시
"""
from django.db.models import Q, Count, Avg
from examples.review_manager import ReviewManager


# 1. 복잡한 검색 조건
def search_reviews_advanced(shop_id: int, search_params: dict):
    """고급 검색"""
    builder = ReviewManager.get_by_shop(shop_id)
    
    # 텍스트 검색
    if search_params.get('keyword'):
        builder = builder.or_filter(
            Q(content__icontains=search_params['keyword']),
            Q(product_fk__name__icontains=search_params['keyword'])
        )
    
    # 평점 범위
    if search_params.get('min_rating'):
        builder = builder.filter(ratings__gte=search_params['min_rating'])
    
    # 미디어 필터
    if search_params.get('has_media'):
        builder = builder.or_filter(
            Q(review_photo_set__isnull=False),
            Q(review_video_set__isnull=False)
        )
    
    return (builder
            .select_related('product_fk')
            .prefetch_related('review_badge', 'review_photo_set')
            .annotate(
                badge_count=Count('review_badge'),
                media_count=Count('review_photo_set')
            )
            .distinct()
            .order_by('-created_at')
            .build())


# 2. 통계 쿼리
def get_product_review_stats(shop_id: int, product_id: int):
    """상품별 리뷰 통계"""
    return (ReviewManager.get_by_shop(shop_id)
            .filter(product_id=product_id)
            .filter(posting_status='published')
            .aggregate(
                total_reviews=Count('id'),
                avg_rating=Avg('ratings'),
                reviews_with_photos=Count('id', filter=Q(review_photo_set__isnull=False))
            ))


# 3. Feature에서 사용 예시
class ReviewFeature:
    @staticmethod
    def get_trending_reviews(shop_id: int, days: int = 7):
        """최근 인기 리뷰"""
        from datetime import datetime, timedelta
        
        start_date = datetime.now() - timedelta(days=days)
        
        return (ReviewManager.get_by_shop(shop_id)
                .filter(created_at__gte=start_date)
                .filter(ratings__gte=4)
                .annotate(
                    engagement_score=Count('review_badge') + Count('review_photo_set')
                )
                .filter(engagement_score__gt=0)
                .select_related('product_fk')
                .prefetch_related('review_badge', 'review_photo_set')
                .order_by('-engagement_score', '-ratings')
                .build()[:10])
    
    @staticmethod
    def get_reviews_needing_attention(shop_id: int):
        """관리자 확인이 필요한 리뷰"""
        return (ReviewManager.get_by_shop(shop_id)
                .or_filter(
                    Q(ratings__lte=2),  # 낮은 평점
                    Q(is_alert=True),   # 알림 키워드 포함
                )
                .filter(posting_status='published')
                .select_related('product_fk')
                .annotate(
                    priority_score=(5 - Count('ratings'))
                )
                .order_by('-priority_score', '-created_at')
                .build())
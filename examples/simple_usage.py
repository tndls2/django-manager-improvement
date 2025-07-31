"""
단순한 쿼리에서의 개선된 Manager 사용 예시
"""
from examples.review_manager import ReviewManager


# ========== 기존 방식 vs 개선된 방식 비교 ==========

# 1. 단일 객체 조회
def get_review_by_id(shop_id: int, review_id: int):
    # 기존 방식
    review = ReviewManager.get(shop_id=shop_id, id=review_id)
    
    # 개선된 방식 (동일하게 간단)
    review = ReviewManager.get_by_shop(shop_id).filter(id=review_id).first()
    
    return review


# 2. 기본 리스트 조회
def get_shop_reviews(shop_id: int):
    # 기존 방식
    reviews = ReviewManager.get_list(shop_id=shop_id, order_by=['-created_at'])
    
    # 개선된 방식 (더 직관적)
    reviews = ReviewManager.get_by_shop(shop_id).order_by('-created_at').build()
    
    return reviews


# 3. 간단한 필터링
def get_published_reviews(shop_id: int):
    # 기존 방식
    reviews = ReviewManager.get_list(
        shop_id=shop_id,
        filters={'posting_status': 'published', 'is_deleted': False}
    )
    
    # 개선된 방식 (메서드 체이닝으로 더 읽기 쉬움)
    reviews = (ReviewManager.get_by_shop(shop_id)
               .filter(posting_status='published')
               .filter(is_deleted=False)
               .build())
    
    return reviews


# 4. 개수 조회
def count_shop_reviews(shop_id: int):
    # 기존 방식
    count = ReviewManager.count(shop_id=shop_id)
    
    # 개선된 방식 (체이닝 가능)
    count = ReviewManager.get_by_shop(shop_id).count()
    
    return count


# 5. 존재 여부 확인
def has_reviews(shop_id: int, product_id: int):
    # 기존 방식
    exists = ReviewManager.check_exist(
        shop_id=shop_id, 
        filters={'product_id': product_id}
    )
    
    # 개선된 방식 (더 직관적)
    exists = (ReviewManager.get_by_shop(shop_id)
              .filter(product_id=product_id)
              .exists())
    
    return exists


# ========== 실제 사용 시나리오 ==========

# View에서 사용 - 단순한 경우
class ReviewListView:
    def get(self, request, shop_id):
        # 매우 단순한 조회
        reviews = ReviewManager.get_by_shop(shop_id).build()
        return reviews
    
    def get_with_basic_filter(self, request, shop_id):
        # 기본 필터링
        reviews = (ReviewManager.get_by_shop(shop_id)
                   .filter(is_deleted=False)
                   .order_by('-created_at')
                   .build())
        return reviews


# Feature에서 사용 - 단순한 비즈니스 로직
class ReviewFeature:
    @staticmethod
    def get_product_reviews(shop_id: int, product_id: int):
        """상품별 리뷰 조회 - 단순"""
        return (ReviewManager.get_by_shop(shop_id)
                .filter(product_id=product_id)
                .filter(is_deleted=False)
                .order_by('-created_at')
                .build())
    
    @staticmethod
    def get_recent_reviews(shop_id: int, days: int = 7):
        """최근 리뷰 조회 - 단순"""
        from datetime import datetime, timedelta
        
        start_date = datetime.now() - timedelta(days=days)
        return (ReviewManager.get_by_shop(shop_id)
                .filter(created_at__gte=start_date)
                .order_by('-created_at')
                .build())


# ========== 점진적 마이그레이션 예시 ==========

def migrate_gradually(shop_id: int):
    # 1단계: 기존 방식
    reviews_old = ReviewManager.get_list(shop_id=shop_id)
    
    # 2단계: 새로운 방식으로 변경
    reviews_new = ReviewManager.get_by_shop(shop_id).build()
    
    # 3단계: 필요에 따라 체이닝 추가
    reviews_enhanced = (ReviewManager.get_by_shop(shop_id)
                       .filter(is_deleted=False)
                       .order_by('-created_at')
                       .build())
    
    return reviews_enhanced
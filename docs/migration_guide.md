# 마이그레이션 가이드

## 단계별 마이그레이션 전략

### 1단계: 기존 방식 유지
```python
# 기존 코드 그대로 유지
reviews = Review__Manager.get_list(
    shop_id=shop_id,
    filters={'is_deleted': False}
)
```

### 2단계: 새로운 방식 선택적 도입
```python
# 새로운 Manager 클래스 생성
class ReviewManager(BaseManager):
    model_class = Review
    
    @classmethod
    def get_by_shop(cls, shop_id: int):
        return cls.query().filter(shop_id=shop_id)

# 기존 방식과 병행 사용
reviews_old = Review__Manager.get_list(shop_id=shop_id)
reviews_new = ReviewManager.get_by_shop(shop_id).build()
```

### 3단계: 복잡한 쿼리에 체이닝 활용
```python
# 복잡한 쿼리만 새로운 방식 적용
def get_complex_reviews(shop_id: int):
    return (ReviewManager.get_by_shop(shop_id)
            .or_filter(
                Q(review_photo_set__isnull=False),
                Q(review_video_set__isnull=False)
            )
            .annotate(engagement=Count('review_badge'))
            .order_by('-engagement')
            .build())
```

### 4단계: 점진적으로 전체 적용
```python
# 모든 Manager를 새로운 방식으로 통일
class ReviewManager(BaseManager):
    model_class = Review
    
    # 기존 메서드 호환성 유지
    @classmethod
    def get_list(cls, shop_id: int, **kwargs):
        return super().get_list(shop_id=shop_id, **kwargs)
    
    # 새로운 체이닝 메서드 추가
    @classmethod
    def get_by_shop(cls, shop_id: int):
        return cls.query().filter(shop_id=shop_id)
```

## 마이그레이션 체크리스트

### ✅ 준비 단계
- [ ] QueryBuilder 클래스 추가
- [ ] BaseManager 클래스 추가
- [ ] 테스트 환경에서 검증

### ✅ 적용 단계
- [ ] 새로운 Manager 클래스 생성
- [ ] 기존 메서드 호환성 확인
- [ ] 단위 테스트 작성

### ✅ 검증 단계
- [ ] 성능 테스트 수행
- [ ] 기존 기능 정상 동작 확인
- [ ] 코드 리뷰 완료

## 주의사항

### 1. 성능 고려사항
```python
# 주의: N+1 문제 방지
reviews = (ReviewManager.get_by_shop(shop_id)
           .select_related('product_fk')  # 필수
           .prefetch_related('review_badge')  # 필수
           .build())
```

### 2. 트랜잭션 처리
```python
from django.db import transaction

@transaction.atomic
def complex_operation(shop_id: int):
    # 트랜잭션 내에서 여러 작업 수행
    reviews = ReviewManager.get_by_shop(shop_id).build()
    # ... 추가 작업
```

### 3. 기존 코드 호환성
```python
class ReviewManager(BaseManager):
    # 기존 메서드명 유지
    @classmethod
    def get_list(cls, **kwargs):
        return super().get_list(**kwargs)
    
    # 새로운 메서드 추가
    @classmethod
    def get_by_shop(cls, shop_id: int):
        return cls.query().filter(shop_id=shop_id)
```

## 예상 문제점 및 해결방안

### 문제 1: 기존 코드 호환성
**해결**: 기존 메서드명과 시그니처 유지

### 문제 2: 성능 저하
**해결**: select_related, prefetch_related 적극 활용

### 문제 3: 복잡성 증가
**해결**: 단순한 쿼리는 기존 방식 유지, 복잡한 쿼리만 체이닝 적용
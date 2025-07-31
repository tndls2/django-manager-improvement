# Django Manager 개선 방안

Django ORM을 활용한 Manager 패턴 개선 및 QueryBuilder를 통한 체이닝 지원

## 🎯 목표

- **체이닝 방식**의 직관적인 쿼리 작성
- **Q 객체, annotate** 등 복잡한 ORM 기능 자유로운 사용
- **Manager와 Feature 역할 분리** 명확화

## 🚀 주요 특징

### 1. 체이닝 방식 쿼리 작성

**기존 방식**:
```python
Review__Manager.get_list(
    shop_id=shop_id,
    filters={'ratings__gte': 4},
    embed=['product_fk', 'review_badge']
)
```

**개선된 방식**:
```python
(ReviewManager.get_by_shop(shop_id)
 .filter(ratings__gte=4)
 .select_related('product_fk')
 .prefetch_related('review_badge')
 .annotate(badge_count=Count('review_badge'))
 .order_by('-ratings')
 .build())
```

### 2. 복잡한 쿼리 지원

```python
# OR 조건과 annotate를 활용한 복잡한 쿼리
(ReviewManager.get_by_shop(shop_id)
 .or_filter(
     Q(review_photo_set__isnull=False),
     Q(review_video_set__isnull=False)
 )
 .annotate(
     engagement_score=Count('review_badge') + Count('review_photo_set')
 )
 .filter(engagement_score__gt=0)
 .distinct()
 .build())
```

## 📖 사용법

### 기본 사용법

```python
# 단순한 조회
reviews = ReviewManager.get_by_shop(shop_id).build()

# 필터링
reviews = (ReviewManager.get_by_shop(shop_id)
           .filter(is_deleted=False)
           .order_by('-created_at')
           .build())

# 개수 조회
count = ReviewManager.get_by_shop(shop_id).filter(ratings__gte=4).count()
```

### 고급 사용법

```python
# 복잡한 검색 조건
def search_reviews_advanced(shop_id: int, search_params: dict):
    builder = ReviewManager.get_by_shop(shop_id)
    
    if search_params.get('keyword'):
        builder = builder.or_filter(
            Q(content__icontains=search_params['keyword']),
            Q(product_fk__name__icontains=search_params['keyword'])
        )
    
    if search_params.get('has_media'):
        builder = builder.or_filter(
            Q(review_photo_set__isnull=False),
            Q(review_video_set__isnull=False)
        )
    
    return (builder
            .select_related('product_fk')
            .prefetch_related('review_badge')
            .annotate(media_count=Count('review_photo_set'))
            .distinct()
            .build())
```

## 🏗️ 아키텍처

```
View → Feature → Manager → QueryBuilder → ORM → Database
```

- **View**: HTTP 요청/응답 처리
- **Feature**: 비즈니스 로직 (단순/복잡 모두)
- **Manager**: ORM 쿼리 구성
- **QueryBuilder**: 체이닝 쿼리 빌드

## 💡 장점

1. **가독성 향상**: SQL과 유사한 직관적인 구조
2. **유연성**: Q 객체, annotate 등 자유로운 사용
3. **재사용성**: QueryBuilder를 통한 쿼리 로직 재사용
4. **일관성**: 모든 Manager가 동일한 인터페이스 제공
5. **호환성**: 기존 코드와 완전 호환

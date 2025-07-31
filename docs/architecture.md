# 아키텍처 설명

## 전체 구조

```
View → Feature → Manager → QueryBuilder → ORM → Database
```

## 각 계층의 역할

### 1. View Layer
- HTTP 요청/응답 처리
- 데이터 직렬화/역직렬화
- 권한 검증

```python
class ReviewListView(APIView):
    def get(self, request, shop_id):
        reviews = ReviewFeature.get_published_reviews(shop_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
```

### 2. Feature Layer
- **비즈니스 로직** 구현
- **여러 Manager 조합** 사용
- **트랜잭션 관리**
- **외부 API 호출**

```python
class ReviewFeature:
    @staticmethod
    def get_trending_reviews(shop_id: int):
        # 복잡한 비즈니스 로직
        return (ReviewManager.get_by_shop(shop_id)
                .filter(ratings__gte=4)
                .annotate(engagement=Count('review_badge'))
                .order_by('-engagement')
                .build()[:10])
```

### 3. Manager Layer
- **ORM 쿼리 구성**
- **데이터 접근 로직**
- **QueryBuilder 활용**

```python
class ReviewManager(BaseManager):
    @classmethod
    def get_by_shop(cls, shop_id: int):
        return cls.query().filter(shop_id=shop_id)
```

### 4. QueryBuilder Layer
- **체이닝 방식** 쿼리 작성
- **Q 객체, annotate** 등 지원
- **메서드 체이닝** 구현

```python
class QueryBuilder:
    def filter(self, **kwargs):
        self._queryset = self._queryset.filter(**kwargs)
        return self
    
    def or_filter(self, *q_objs):
        # OR 조건 처리
        return self
```

## 데이터 흐름

1. **View**에서 요청 받음
2. **Feature**에서 비즈니스 로직 처리
3. **Manager**에서 데이터 조회 로직 구성
4. **QueryBuilder**에서 체이닝 쿼리 빌드
5. **ORM**을 통해 데이터베이스 접근
6. 결과를 역순으로 반환

## 장점

### 1. 관심사 분리
- 각 계층이 명확한 역할 담당
- 코드 유지보수성 향상

### 2. 재사용성
- Manager 메서드 재사용
- QueryBuilder 패턴 재사용

### 3. 테스트 용이성
- 각 계층별 독립적 테스트 가능
- Mock 객체 활용 용이

### 4. 확장성
- 새로운 기능 추가 시 해당 계층에만 영향
- 기존 코드 변경 최소화
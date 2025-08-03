# Django Manager 개선 방안

Django ORM을 활용한 Manager 패턴 개선

## 🎯 목표

- Manager와 Feature 역할 분리 명확화

## 📁 프로젝트 구조

```
django-manager-improvement/
├── README.md
├── core/
│   └── base_manager.py       # BaseManager 클래스
├── examples/
│   ├── models.py             # Django 모델 정의
│   ├── review_manager.py     # ReviewManager 구현
│   ├── review_feature.py     # ReviewFeature 구현
│   └── test_review_feature.py # 전체 테스트
└── requirements.txt
```

## 🏗️ 아키텍처

```
View → Feature → Manager → ORM → Database
```

- **View**: HTTP 요청/응답 처리
- **Feature**: 비즈니스 로직 처리
- **Manager**: ORM 쿼리 구성 및 데이터 접근
- **ORM**: Django ORM을 통한 데이터베이스 접근

## 💡 설계 원칙 및 장점

### 🏛️ 계층 분리 설계

#### BaseManager (기본 CRUD)
```python
class BaseManager:
    @classmethod
    def get_by_id(cls, pk) -> Optional[Model]:
        """ID로 단일 객체 조회"""
        return cls.model_class.objects.filter(pk=pk).first()
    
    @classmethod
    def create(cls, **data) -> Model:
        """단일 객체 생성"""
        instance = cls.model_class(**data)
        instance.save()
        return instance
    
    @classmethod
    def update_all(cls, filters: Dict, **data) -> int:
        """조건에 맞는 모든 객체 업데이트"""
        return cls.model_class.objects.filter(**filters).update(**data)
```

#### ReviewManager (도메인 특화)
```python
class ReviewManager(BaseManager):
    model_class = Review
    
    @classmethod
    def find_high_rating_reviews(cls, shop_id: int, min_rating: int = 4):
        """높은 평점 리뷰 조회"""
        return Review.objects.filter(
            shop_id=shop_id, 
            ratings__gte=min_rating,
            posting_status="게시됨"
        ).order_by("-ratings", "-created_at")
    
    @classmethod
    def get_shop_review_stats(cls, shop_id: int):
        """샵 리뷰 통계 조회"""
        return Review.objects.filter(
            shop_id=shop_id, 
            posting_status="게시됨"
        ).aggregate(
            total_count=Count("id"),
            avg_rating=Avg("ratings"),
            total_points=Sum("total_point")
        )
```

#### ReviewFeature (비즈니스 로직)
```python
class ReviewFeature:
    def get_high_ratings_reviews(self, shop_id: int):
        """평점 높은 리뷰 조회"""
        return ReviewManager.find_high_rating_reviews(shop_id, min_rating=4)
    
    def get_review_detail(self, review_id: int):
        """리뷰 상세 조회 - BaseManager 기본 메서드 사용"""
        return ReviewManager.get_by_id(review_id)
    
    def get_monthly_reviews(self, shop_id: int, year: int, month: int):
        """날짜 범위 조회"""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        return ReviewManager.find_by_date_range(shop_id, start_date, end_date)
```

### 🎯 핵심 장점

1. **명확한 책임 분리**
   - **Manager**: 모델 관련 코드만 담당 (ORM 쿼리, 데이터 접근)
   - **Feature**: 비즈니스 로직만 담당 (업무 규칙, 복합 처리)

2. **코드 재사용성**
   - BaseManager의 공통 메서드를 모든 도메인에서 활용
   - 도메인별 Manager는 특화된 쿼리만 구현

3. **유지보수성**
   - 쿼리 변경 시 Manager만 수정
   - 비즈니스 로직 변경 시 Feature만 수정
   - 변경 영향 범위 최소화

4. **확장성**
   - 새로운 도메인 추가 시 BaseManager 상속으로 빠른 구현
   - 복잡한 비즈니스 로직도 Feature에서 체계적 관리

## 🚀 실행 방법

### 1. 환경 설정

```bash
# 프로젝트 클론
git clone <repository-url>
cd django-manager-improvement

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 테스트 실행

```bash
# examples 디렉토리로 이동
cd examples

# ReviewFeature 전체 테스트
python test_review_feature.py
```

### 3. 예상 출력

```
=== ReviewFeature 메서드 테스트 ===
1. 게시된 리뷰: 2개
2. 높은 평점 리뷰: 2개
3. 미디어 포함 리뷰: 2개
4. 검색 결과: 1개
5. 월별 리뷰: 0개
6. 샵 통계: 총 2개, 평균 평점 4.5
7. 대량 게시: 2개 업데이트
8. 리뷰 숨김: 성공
9. 리뷰 삭제: 성공
10. 리뷰 상세: 좋은 상품입니다

=== 모든 테스트 완료 ===
```
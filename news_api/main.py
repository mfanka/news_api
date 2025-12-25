from datetime import datetime
from typing import Annotated, Literal

from fastapi import FastAPI, Depends, HTTPException, Query, Header, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc, asc

from database import Base, engine, SessionLocal
from models import News, Category
from schemas import (
    CategoryCreate, CategoryOut,
    NewsCreate, NewsUpdate, NewsOut, NewsListOut,
    CategoryStatsOut
)

from fastapi.middleware.cors import CORSMiddleware



# --- Инициализация БД ---
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="News Portal API",
    description="ЛР: REST API новостного портала (CRUD, фильтр, поиск, сортировка, пагинация, валидация, агрегация, Swagger/ReDoc)",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Зависимости ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Простая авторизация через API Key (для POST/PUT/DELETE)
API_KEY = "SECRET123"  # в реальном проекте хранить в env

def require_api_key(x_api_key: Annotated[str | None, Header()] = None):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key",
        )


# --- Категории ---

@app.post("/categories", response_model=CategoryOut, status_code=201, dependencies=[Depends(require_api_key)])
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(Category).where(Category.name == payload.name))
    if existing:
        raise HTTPException(status_code=409, detail="Category already exists")

    cat = Category(name=payload.name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@app.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    cats = db.scalars(select(Category).order_by(asc(Category.name))).all()
    return cats


@app.get("/categories/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@app.get("/stats/categories", response_model=list[CategoryStatsOut])
def category_stats(db: Session = Depends(get_db)):
    # агрегация: количество новостей в каждой категории
    stmt = (
        select(
            Category.id,
            Category.name,
            func.count(News.id).label("news_count"),
        )
        .join(News, News.category_id == Category.id, isouter=True)
        .group_by(Category.id)
        .order_by(desc("news_count"))
    )
    rows = db.execute(stmt).all()
    return [
        CategoryStatsOut(category_id=r[0], category_name=r[1], news_count=r[2])
        for r in rows
    ]


# --- Новости (CRUD + фильтр/поиск/сортировка/пагинация) ---

@app.post("/news", response_model=NewsOut, status_code=201, dependencies=[Depends(require_api_key)])
def create_news(payload: NewsCreate, db: Session = Depends(get_db)):
    cat = db.get(Category, payload.category_id)
    if not cat:
        raise HTTPException(status_code=400, detail="category_id does not exist")

    now = datetime.utcnow()
    news = News(
        title=payload.title,
        content=payload.content,
        author=payload.author,
        category_id=payload.category_id,
        is_published=payload.is_published,
        created_at=now,
        updated_at=now,
    )
    db.add(news)
    db.commit()
    db.refresh(news)
    return news


@app.get("/news", response_model=NewsListOut)
def list_news(
    db: Session = Depends(get_db),
    category_id: int | None = Query(default=None, gt=0, description="Фильтр по категории"),
    q: str | None = Query(default=None, min_length=2, max_length=100, description="Поиск по ключевому слову (title/content)"),
    author: str | None = Query(default=None, min_length=2, max_length=80, description="Фильтр по автору"),
    is_published: bool | None = Query(default=None, description="Фильтр по опубликованности"),
    sort_by: Literal["created_at", "title"] = Query(default="created_at", description="Поле сортировки"),
    order: Literal["asc", "desc"] = Query(default="desc", description="Порядок сортировки"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
):
    stmt = select(News).join(Category)

    if category_id is not None:
        stmt = stmt.where(News.category_id == category_id)
    if author is not None:
        stmt = stmt.where(News.author == author)
    if is_published is not None:
        stmt = stmt.where(News.is_published == is_published)
    if q is not None:
        like = f"%{q.strip()}%"
        stmt = stmt.where((News.title.ilike(like)) | (News.content.ilike(like)))

    # total
    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.scalar(total_stmt) or 0

    # sorting
    sort_col = News.created_at if sort_by == "created_at" else News.title
    stmt = stmt.order_by(desc(sort_col) if order == "desc" else asc(sort_col))

    # pagination
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    items = db.scalars(stmt).all()
    return NewsListOut(items=items, total=total, page=page, page_size=page_size)


@app.get("/news/{news_id}", response_model=NewsOut)
def get_news(news_id: int, db: Session = Depends(get_db)):
    news = db.get(News, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news


@app.put("/news/{news_id}", response_model=NewsOut, dependencies=[Depends(require_api_key)])
def update_news(news_id: int, payload: NewsUpdate, db: Session = Depends(get_db)):
    news = db.get(News, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    if payload.category_id is not None:
        cat = db.get(Category, payload.category_id)
        if not cat:
            raise HTTPException(status_code=400, detail="category_id does not exist")
        news.category_id = payload.category_id

    if payload.title is not None:
        news.title = payload.title
    if payload.content is not None:
        news.content = payload.content
    if payload.author is not None:
        news.author = payload.author
    if payload.is_published is not None:
        news.is_published = payload.is_published

    news.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(news)
    return news


@app.delete("/news/{news_id}", status_code=204, dependencies=[Depends(require_api_key)])
def delete_news(news_id: int, db: Session = Depends(get_db)):
    news = db.get(News, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    db.delete(news)
    db.commit()
    return None


@app.get("/news/latest", response_model=list[NewsOut])
def latest_news(
    db: Session = Depends(get_db),
    limit: int = Query(default=5, ge=1, le=20),
    only_published: bool = Query(default=True),
):
    stmt = select(News).order_by(desc(News.created_at)).limit(limit)
    if only_published:
        stmt = stmt.where(News.is_published == True)  # noqa: E712
    return db.scalars(stmt).all()

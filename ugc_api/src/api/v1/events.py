from fastapi import APIRouter, Depends
from pydantic import BaseModel

from services.event_service import EventService, get_event_service

router = APIRouter()


class MovieRating(BaseModel):
    movie_id: str
    user_id: str
    rating: float


class MovieHistory(BaseModel):
    movie_id: str
    user_id: str
    viewed: int


class MovieBookmark(BaseModel):
    movie_id: str
    user_id: str


class MovieLastViewTime(BaseModel):
    movie_id: str
    user_id: str
    paused_sec: int


@router.post('/send_rating/', summary='Отправить рейтинг фильма от пользователя')
async def send_rating(movie_rating: MovieRating,
                      event_service: EventService = Depends(get_event_service)):
    """В теле запроса отправляются данные пользовательского рейтинга для фильма."""
    event_service.send_rating(movie_rating.user_id, movie_rating.movie_id, movie_rating.rating)
    return 'ok'


@router.post('/send_history/', summary='Добавить в историю просмотров пользователя фильм')
async def send_history(movie_history: MovieHistory,
                      event_service: EventService = Depends(get_event_service)):
    """В теле запроса отправляются timestamp данные последнего просмотра пользователем фильма."""
    event_service.send_history(movie_history.user_id, movie_history.movie_id, movie_history.viewed)
    return 'ok'


@router.post('/send_bookmark/', summary='Добавить фильма в закладки')
async def send_bookmark(movie_bookmark: MovieBookmark,
                      event_service: EventService = Depends(get_event_service)):
    event_service.send_bookmark(movie_bookmark.user_id, movie_bookmark.movie_id)
    return 'ok'


@router.post('/send_last_view_time/',
             summary='Добавить метку времени в секундах на котором пользователь остановил просмотр фильма.')
async def send_last_view_time(movie_last_view_time: MovieLastViewTime,
                      event_service: EventService = Depends(get_event_service)):
    event_service.send_last_view_time(movie_last_view_time.user_id,
                                      movie_last_view_time.movie_id,
                                      movie_last_view_time.paused_sec)
    return 'ok'

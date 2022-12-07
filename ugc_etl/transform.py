from typing import Optional


class Transform:
    @staticmethod
    def get_bookmark_data(key: str, value: str) -> dict:
        return {
            'movie_id': key,
            'user_id': value,
        }

    @staticmethod
    def get_rating_data(key: str, value: str) -> Optional[dict]:
        parts = value.split('+')
        if len(parts) != 2:
            return None

        try:
            result = float(parts[1])
        except ValueError:
            return None

        return {
            'movie_id': key,
            'user_id': parts[0],
            'rating': result,
        }

    @staticmethod
    def get_history_data(key: str, value: str) -> Optional[dict]:
        parts = value.split('+')
        if len(parts) != 2:
            return None

        try:
            result = int(parts[1])
        except ValueError:
            return None

        return {
            'movie_id': key,
            'user_id': parts[0],
            'viewed': result,
        }

    @staticmethod
    def get_last_view_time_data(key: str, value: str) -> Optional[dict]:
        parts = value.split('+')
        if len(parts) != 2:
            return None

        try:
            result = int(parts[1])
        except ValueError:
            return None

        return {
            'movie_id': key,
            'user_id': parts[0],
            'paused_sec': result,
        }

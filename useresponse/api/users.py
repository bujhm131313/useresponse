from enum import Enum
from typing import Dict, Iterable, Optional


class SortCriteria(Enum):
    roles = 'roles'
    department = 'department'
    top_rated = 'top_rated'
    created_most = 'created_most'
    commented_most = 'commented_most'


class UserService(object):
    def __init__(self, transport):
        self._transport = transport

    def get(self, id_: int) -> dict:
        return self._transport.get(f'/users/{id_}.json', {})

    def get_by_email(self, email: str) -> Dict:
        request_params = {'email': email}
        result = self._transport.get('/users/search.json', request_params)
        return result['success'] if result['success'] else None

    def search(
        self,
        sort: Optional[SortCriteria] = None,
        role: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        count: int = 20,
    ) -> Dict:
        if page < 1:
            raise ValueError(f'Page number must be a positive int, got {page}')
        if count < 1 or count > 50:
            raise ValueError(f'Count must be between 1 and 50, got {count}')
        request_params = {
            'page': page,
            'count': count,
        }
        if sort is not None:
            request_params['sort'] = sort.value
        if role is not None:
            request_params['role'] = role
        if search is not None:
            request_params['search'] = search
        return self._transport.get('/users/search.json', request_params)

    def search_iter(
        self,
        sort: Optional[SortCriteria] = None,
        role: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Iterable[Dict]:
        page: int = 1
        total_pages: int = 0
        while True:
            results = self.search(sort, role, search, page=page)
            total_pages = results['totalPages']
            page += 1
            for value in results['data']:
                yield value
            if page > total_pages:
                break

    def edit(
        self,
        id_: int,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> Optional[Dict]:
        request_params = {}
        if email is not None:
            request_params['email'] = email
        if full_name is not None:
            request_params['full_name'] = full_name
        if not request_params:
            raise ValueError('Either email or full_name must be provided')
        result = self._transport.post(f'/users/{id_}.json', request_params)
        return result['success'] if result['success'] else None

    def change_password(self, id_: int, new_password: str) -> Optional[Dict]:
        request_params = {'password': new_password}
        result = self._transport.post(f'/users/{id_}/change-password.json',
                                      request_params)
        return result['success'] if result['success'] else None

    def create(
        self,
        email: str,
        full_name: str,
        password: Optional[str] = None,
    ) -> Optional[Dict]:
        request_params = {'email': email, 'full_name': full_name}
        if password is not None:
            request_params['password'] = password
        result = self._transport.post('/users.json', request_params)
        return result['success'] if result['success'] else None

    def delete(self, id_: int) -> Optional[Dict]:
        result = self._transport.delete(f'/users/{id_}.json')
        return result['success'] if result['success'] else None

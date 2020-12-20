from typing_extensions import Literal, TypedDict

Photo = TypedDict('Photo', {'url': str, 'local_file': str, 'title': str, 'taken': str})
PhotoKey = Literal['url', 'local_file', 'title', 'taken']
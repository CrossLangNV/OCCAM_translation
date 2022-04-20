import os
import tempfile
from pathlib import Path
from typing import List, Union
from urllib.parse import urljoin

import requests

BASE_URL = os.environ['ETRANSLATION']


# class ETranslationConnector:
#     url_info = urljoin(BASE_URL + '/', 'info')
#     url_trans_snippet = urljoin(BASE_URL + '/', 'translate/snippet')
#     url_trans_snippet_id = urljoin(url_trans_snippet + '/', '{id}')
#     url_trans_snippet_blocking = urljoin(url_trans_snippet + '/', 'blocking')
#     url_trans_doc = urljoin(BASE_URL + '/', 'translate/document')
#     url_trans_doc_id = urljoin(url_trans_doc + '/', '{id}')
#     url_trans_doc_blocking = urljoin(url_trans_doc + '/', 'blocking')
#
#     def __init__(self, username: str=None, password: str=None):
#         self._username = username
#         self._password = password
#
#     def info(self):
#         r = requests.get(self.url_info)
#
#         return r.json()
#
#     def trans_snippet(self,
#                       source: str,
#                       target: str,
#                       snippet: str):
#         """
#
#         Args:
#             source:
#             target:
#             snippet:
#
#         Returns:
#             the request id
#         """
#         data = {'source': str(source),
#                 'target': str(target),
#                 'snippet': str(snippet)}
#
#         r = requests.post(self.url_trans_snippet, data=data)
#
#         return r.json()
#
#     def trans_snippet_id(self, request_id):
#         r = requests.get(self.url_trans_snippet_id.format(id=request_id))
#
#         return r.json().get('content')
#
#     def trans_snippet_blocking(self, source: str,
#                                target: str,
#                                snippet: str):
#         data = {'source': str(source),
#                 'target': str(target),
#                 'snippet': str(snippet)}
#
#         r = requests.post(self.url_trans_snippet_blocking, data=data)
#
#         return r.json()
#
#     def trans_doc(self, source: str,
#                   target: str,
#                   filename: Path):
#         with open(filename, 'rb') as f:
#             data = {'source': str(source),
#                     'target': str(target),
#                     # 'file': f
#                     }
#
#             files = {'file': f}
#
#             r = requests.post(self.url_trans_doc,
#                               data=data,
#                               files=files)
#
#         return r.json()
#
#     def trans_doc_id(self, request_id):
#         """
#
#         Args:
#             request_id:
#
#         Returns:
#             raw bytestring
#         """
#
#         with requests.get(self.url_trans_doc_id.format(id=request_id)) as r:
#             # Magic filename
#
#             if r.status_code > 200:
#                 return None
#
#             filename = r.headers.get('Content-Disposition').split('filename=')[1]
#
#             return {'content': r.content,
#                     'filename': filename}
#
#     def trans_doc_blocking(self, source: str,
#                            target: str,
#                            filename: Path):
#         with open(filename, 'rb') as f:
#             data = {'source': str(source),
#                     'target': str(target),
#                     }
#
#             files = {'file': f}
#
#             r = requests.post(self.url_trans_doc_blocking,
#                               data=data,
#                               files=files)
#
#             if r.status_code > 300:
#                 raise Exception(f'{r}\n{r.text}')
#
#             # Magic filename
#             filename_trans = r.headers.get('Content-Disposition').split('filename=')[1]
#
#             return {'content': r.content,
#                     'filename': filename_trans}


class ETranslationConnector:
    url_info = urljoin(BASE_URL + '/', 'info')
    url_trans_snippet = urljoin(BASE_URL + '/', 'translate/snippet')
    url_trans_snippet_id = urljoin(url_trans_snippet + '/', '{id}')
    url_trans_snippet_blocking = urljoin(url_trans_snippet + '/', 'blocking')
    url_trans_doc = urljoin(BASE_URL + '/', 'translate/document')
    url_trans_doc_id = urljoin(url_trans_doc + '/', '{id}')
    url_trans_doc_blocking = urljoin(url_trans_doc + '/', 'blocking')

    url_docs = urljoin(url_trans_doc, "docs")

    def __init__(self, username: str = None, password: str = None):

        self._username = username
        self._password = password

    def info(self):
        r = self._get(self.url_info)
        return r.json()

    def trans_snippet(self,
                      source: str,
                      target: str,
                      snippet: str):
        """
        Args:
            source:
            target:
            snippet:
        Returns:
            the request id
        """
        data = {'source': str(source),
                'target': str(target),
                'snippet': str(snippet)}

        r = self._post(self.url_trans_snippet,
                       data=data)

        return r.json()

    def trans_snippet_id(self, request_id) -> Union[str, None]:
        r = self._get(self.url_trans_snippet_id.format(id=request_id))

        snippet_trans = r.json().get('content')
        return snippet_trans

    def trans_snippet_blocking(self, source: str,
                               target: str,
                               snippet: str) -> str:
        # Catch empty snippets
        if not bool(snippet):
            return snippet

        data = {'source': str(source),
                'target': str(target),
                'snippet': str(snippet)}

        r = self._post(self.url_trans_snippet_blocking,
                       data=data)

        r.raise_for_status()

        snippet_trans = r.json().strip()

        return snippet_trans

    def trans_doc(self, source: str,
                  target: str,
                  filename: Path):
        with open(filename, 'rb') as f:
            data = {'source': str(source),
                    'target': str(target),
                    # 'file': f
                    }

            files = {'file': f}

            r = self._post(self.url_trans_doc,
                           data=data,
                           files=files)
        if r:
            return r.json()
        else:
            return None

    def trans_doc_id(self, request_id):
        """
        Args:
            request_id:
        Returns:
            raw bytestring
        """

        with self._get(self.url_trans_doc_id.format(id=request_id)) as r:
            # Magic filename

            if r.status_code > 200:
                return None

            print(r.headers.get('Content-Disposition'))
            filename = r.headers.get('Content-Disposition').split('filename=')[1]

            return {'content': r.content,
                    'filename': filename}

    def trans_doc_blocking(self, source: str,
                           target: str,
                           filename: Path):
        with open(filename, 'rb') as f:
            data = {'source': str(source),
                    'target': str(target),
                    }

            files = {'file': f}

            r = self._post(self.url_trans_doc_blocking,
                           data=data,
                           files=files,
                           )

            if r.status_code > 300:
                raise Exception(f'{r}\n{r.text}')

            # Magic filename
            filename_trans = r.headers.get('Content-Disposition').split('filename=')[1]

            return {'content': r.content,
                    'filename': filename_trans}

    def trans_list_blocking(self,
                            l_text: List[str],
                            target: str,
                            source: str,
                            ) -> List[str]:
        """

        Args:
            l_text: List of sentences. May contain newlines.
            target: Target langauge
            source: Source langauge

        Returns:
            List with translated text segments.
        """

        l_n = []
        l_text_split: List[str] = []
        for text in l_text:
            text_split = text.splitlines()

            l_n.append(len(text_split))
            l_text_split.extend(text_split)

        s_tmp = ''.join(text_i + '\n' for text_i in l_text_split)

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_file = os.path.join(tmp_dir, 'tmp_text_lines.txt')
            with open(tmp_file, 'w') as f:
                f.write(s_tmp)
            # send to MT
            j = self.trans_doc_blocking(source, target, Path(tmp_file))

            l_trans_text_split = list(map(str.strip, j['content'].decode('UTF-8').splitlines()))

        # In case some sentences had newlines in them.
        l_text_trans = []
        it = iter(l_trans_text_split)
        for size in l_n:
            text_split_translated = [next(it) for _ in range(size)]

            text_translated = "\n".join(text_split_translated)

            l_text_trans.append(text_translated)

        return l_text_trans

    def _get(self, url, auth=None, *args, **kwargs) -> requests.Response:
        if auth is None:
            auth = (self._username, self._password)
        r = requests.get(url=url, auth=auth, *args, **kwargs)

        return r

    def _post(self, url, auth=None, *args, **kwargs) -> requests.Response:
        if auth is None:
            auth = (self._username, self._password)
        r = requests.post(url=url, auth=auth, *args, **kwargs)

        return r

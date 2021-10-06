# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.
#
# Modifications Copyright OpenSearch Contributors. See
# GitHub history for details.

from .connections import get_connection
from .query import Bool, Q
from .response import UpdateByQueryResponse
from .search import ProxyDescriptor, QueryProxy, Request
from .utils import recursive_to_dict


class UpdateByQuery(Request):

    query = ProxyDescriptor("query")

    def __init__(self, **kwargs):
        """
        Update by query request to opensearch.

        :arg using: `OpenSearch` instance to use
        :arg index: limit the search to index
        :arg doc_type: only query this type.

        All the parameters supplied (or omitted) at creation type can be later
        overridden by methods (`using`, `index` and `doc_type` respectively).

        """
        super(UpdateByQuery, self).__init__(**kwargs)
        self._response_class = UpdateByQueryResponse
        self._script = {}
        self._query_proxy = QueryProxy(self, "query")

    def filter(self, *args, **kwargs):
        return self.query(Bool(filter=[Q(*args, **kwargs)]))

    def exclude(self, *args, **kwargs):
        return self.query(Bool(filter=[~Q(*args, **kwargs)]))

    @classmethod
    def from_dict(cls, d):
        """
        Construct a new `UpdateByQuery` instance from a raw dict containing the search
        body. Useful when migrating from raw dictionaries.

        Example::

            ubq = UpdateByQuery.from_dict({
                "query": {
                    "bool": {
                        "must": [...]
                    }
                },
                "script": {...}
            })
            ubq = ubq.filter('term', published=True)
        """
        u = cls()
        u.update_from_dict(d)
        return u

    def _clone(self):
        """
        Return a clone of the current search request. Performs a shallow copy
        of all the underlying objects. Used internally by most state modifying
        APIs.
        """
        ubq = super(UpdateByQuery, self)._clone()

        ubq._response_class = self._response_class
        ubq._script = self._script.copy()
        ubq.query._proxied = self.query._proxied
        return ubq

    def response_class(self, cls):
        """
        Override the default wrapper used for the response.
        """
        ubq = self._clone()
        ubq._response_class = cls
        return ubq

    def update_from_dict(self, d):
        """
        Apply options from a serialized body to the current instance. Modifies
        the object in-place. Used mostly by ``from_dict``.
        """
        d = d.copy()
        if "query" in d:
            self.query._proxied = Q(d.pop("query"))
        if "script" in d:
            self._script = d.pop("script")
        self._extra.update(d)
        return self

    def script(self, **kwargs):
        """
        Define update action to take:

        Note: the API only accepts a single script, so
        calling the script multiple times will overwrite.

        Example::

            ubq = Search()
            ubq = ubq.script(source="ctx._source.likes++"")
            ubq = ubq.script(source="ctx._source.likes += params.f"",
                         lang="expression",
                         params={'f': 3})
        """
        ubq = self._clone()
        if ubq._script:
            ubq._script = {}
        ubq._script.update(kwargs)
        return ubq

    def to_dict(self, **kwargs):
        """
        Serialize the search into the dictionary that will be sent over as the
        request'ubq body.

        All additional keyword arguments will be included into the dictionary.
        """
        d = {}
        if self.query:
            d["query"] = self.query.to_dict()

        if self._script:
            d["script"] = self._script

        d.update(recursive_to_dict(self._extra))
        d.update(recursive_to_dict(kwargs))
        return d

    def execute(self):
        """
        Execute the search and return an instance of ``Response`` wrapping all
        the data.
        """
        opensearch = get_connection(self._using)

        self._response = self._response_class(
            self,
            opensearch.update_by_query(
                index=self._index, body=self.to_dict(), **self._params
            ),
        )
        return self._response

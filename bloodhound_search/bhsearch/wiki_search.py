#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.

r"""Wiki specifics for Bloodhound Search plugin."""
from bhsearch.api import ISearchParticipant, BloodhoundSearchApi, \
    IIndexParticipant, IndexFields
from bhsearch.base import BaseIndexer
from trac.core import implements, Component
from trac.config import ListOption
from trac.wiki import IWikiChangeListener, WikiSystem, WikiPage

WIKI_TYPE = u"wiki"

class WikiIndexer(BaseIndexer):
    implements(IWikiChangeListener, IIndexParticipant)

    #IWikiChangeListener methods
    def wiki_page_added(self, page):
        """Index a recently created ticket."""
        self._index_wiki(page)

    def wiki_page_changed(self, page, version, t, comment, author, ipnr):
        """Reindex a recently modified ticket."""
        self._index_wiki(page)

    def wiki_page_deleted(self, page):
        """Called when a ticket is deleted."""
        try:
            search_api = BloodhoundSearchApi(self.env)
            search_api.delete_doc(WIKI_TYPE, page.name)
        except Exception, e:
            if self.silence_on_error.lower() == "true":
                self.log.error("Error occurs during wiki indexing. \
                    The error will not be propagated. Exception: %s", e)
            else:
                raise

    def wiki_page_version_deleted(self, page):
        """Called when a version of a page has been deleted."""
        self._index_wiki(page)

    def wiki_page_renamed(self, page, old_name):
        """Called when a page has been renamed."""
        try:
            doc = self.build_doc(page)
            search_api = BloodhoundSearchApi(self.env)
            search_api.change_doc_id(doc, old_name)
        except Exception, e:
            if self.silence_on_error:
                self.log.error("Error occurs during renaming wiki from %s \
                    to %s. The error will not be propagated. Exception: %s",
                old_name, page.name, e)
            else:
                raise

    def _index_wiki(self, page):
        try:
            doc = self.build_doc(page)
            search_api = BloodhoundSearchApi(self.env)
            search_api.add_doc(doc)
        except Exception, e:
            page_name = None
            if page is not None:
                page_name = page.name
            if self.silence_on_error:
                self.log.error("Error occurs during wiki indexing: %s. \
                    The error will not be propagated. Exception: %s",
                    page_name, e)
            else:
                raise

    #IIndexParticipant members
    def build_doc(self, trac_doc):
        page = trac_doc
        #This is very naive prototype implementation
        #TODO: a lot of improvements must be added here!!!
        doc = {
            IndexFields.ID: page.name,
            IndexFields.TYPE: WIKI_TYPE,
            IndexFields.TIME: page.time,
            IndexFields.AUTHOR: page.author,
            IndexFields.CONTENT: page.text,
        }
        return doc

    def get_entries_for_index(self):
        page_names = WikiSystem(self.env).get_pages()
        for page_name in page_names:
            page = WikiPage(self.env, page_name)
            yield self.build_doc(page)

class WikiSearchParticipant(Component):
    implements(ISearchParticipant)

    default_facets = ListOption('bhsearch', 'default_facets_wiki',
        doc="""Default facets applied to search through wiki pages""")

    #ISearchParticipant members
    def get_search_filters(self, req=None):
        if not req or 'WIKI_VIEW' in req.perm:
            return WIKI_TYPE

    def get_title(self):
        return "Wiki"

    def get_default_facets(self):
        return self.default_facets

    def format_search_results(self, res):
        return u'%s: %s...' % (res['id'], res['content'][:50])




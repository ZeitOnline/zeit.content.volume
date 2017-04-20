# -*- coding: utf-8 -*-
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import IPublish
import itertools
import zeit.cms.admin.browser.admin
import zeit.cms.interfaces
import zeit.content.article.article
import zeit.content.infobox.infobox
import zeit.solr.query
import zope.formlib.form


class VolumeAdminForm(zeit.cms.admin.browser.admin.EditFormCI):

    """
    Add an additional Action to the Admin view, which publishes the content
    of a volume.
    """

    extra_actions = zope.formlib.form.Actions()
    assets_to_publish = [zeit.content.portraitbox.interfaces.IPortraitbox,
                         zeit.content.infobox.interfaces.IInfobox
                         ]

    @property
    def actions(self):
        return list(super(VolumeAdminForm, self).actions) + \
               list(self.extra_actions)

    @zope.formlib.form.action(_("Publish content of this volume"),
                              extra_actions)
    def publish_all(self, action, data):
        """
        Publish articles marked as urgent and their boxes.
        """
        Q = zeit.solr.query
        additional_constraints = [
            Q.field('published', 'not-published'),
            Q.and_(
                Q.bool_field('urgent', True),
                Q.field_raw(
                    'type',
                    zeit.content.article.article.ArticleType.type)),
        ]
        articles_to_publish = self.context.all_content_via_solr(
            additional_query_contstraints=additional_constraints)
        # Flatten the list of lists and remove duplicates
        all_content_to_publish = list(set(itertools.chain.from_iterable(
                [self._with_dependencies(article) for article in
                    articles_to_publish])))
        IPublish(self.context).publish_multiple(all_content_to_publish)

    def _with_dependencies(self, content):
        """
        :param content: CMSContent which dependencies are looked up.
        :return: [dep1, dep2,..., content]
        """
        with_dependencies = [
            content
            for content in zeit.cms.interfaces.ICMSContentIterable(
                content)
            if self._needs_publishing(content)
            ]
        with_dependencies.append(content)
        return with_dependencies

    def _needs_publishing(self, content):
        # Dont publish content which is already published
        if zeit.cms.workflow.interfaces.IPublishInfo(content).published:
            return False
        # content has to provide one of interfaces defined above
        return any([interface.providedBy(content) for interface
                    in self.assets_to_publish])

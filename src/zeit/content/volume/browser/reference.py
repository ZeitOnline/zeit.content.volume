from zeit.cms.i18n import MessageFactory as _
from zope.browserpage import ViewPageTemplateFile
import pkg_resources
import zeit.cms.browser.objectdetails
import zeit.cms.browser.view
import zeit.cms.repository.interfaces
import zeit.content.volume.interfaces
import zeit.edit.browser.form
import zope.component
import zope.formlib.form
import zope.formlib.interfaces


class EditReference(zeit.edit.browser.form.InlineForm):

    legend = ''
    undo_description = _('edit volume teaser text')

    form_fields = zope.formlib.form.FormFields(
        zeit.content.volume.interfaces.IVolumeReference,
        # support read-only mode, see
        # zeit.content.article.edit.browser.form.FormFields
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
        'teaserText')

    @property
    def prefix(self):
        return 'reference-details-%s' % self.context.target.uniqueId


class ReferenceDetailsHeading(zeit.cms.browser.objectdetails.Details):

    template = ViewPageTemplateFile(pkg_resources.resource_filename(
        'zeit.cms.browser', 'object-details-heading.pt'))

    def __init__(self, context, request):
        super(ReferenceDetailsHeading, self).__init__(context.target, request)

    def __call__(self):
        return self.template()


class Display(zeit.cms.browser.view.Base):

    def description(self):
        volume = self.context.target
        return "{}, Jahrgang: {}, Ausgabe {}".format(
            volume.product.title,
            volume.year,
            volume.volume,
        )

    def cover_image(self):
        height = 300

        if not self.context.target.covers['printcover']:
            return ''
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        cover_url = '{}{}/@@raw'.format(
            self.url(repository),
            self.context.target.covers['printcover'].variant_url(
                'original', thumbnail=True)
        )
        return '<img src="{}" alt="" height="{}" border="0" />'.format(
            cover_url, height)

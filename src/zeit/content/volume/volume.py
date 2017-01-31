from zeit.cms.i18n import MessageFactory as _
import UserDict
import grokcore.component as grok
import lxml.objectify
import zeit.cms.content.dav
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.cp.interfaces
import zeit.content.volume.interfaces
import zeit.workflow.interfaces
import zope.interface
import zope.schema
import zope.security.proxy


class Volume(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(
        zeit.content.volume.interfaces.IVolume,
        zeit.cms.interfaces.IAsset)

    default_template = u"""\
        <volume xmlns:py="http://codespeak.net/lxml/objectify/pytype">
            <head/>
            <body/>
            <covers/>
        </volume>
    """

    zeit.cms.content.dav.mapProperties(
        zeit.content.volume.interfaces.IVolume,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('date_digital_published', 'year', 'volume', 'teaserText'))

    _product_id = zeit.cms.content.dav.DAVProperty(
        zope.schema.TextLine(),
        zeit.workflow.interfaces.WORKFLOW_NS,
        'product-id')

    @property
    def product(self):
        source = zeit.content.volume.interfaces.IVolume['product'].source(self)
        for value in source:
            if value.id == self._product_id:
                return value

    @product.setter
    def product(self, value):
        if self._product_id == value.id:
            return
        self._product_id = value.id if value is not None else None

    def fill_template(self, text):
        return self._fill_template(self, text)

    @staticmethod
    def _fill_template(context, text):
        return text.format(
            year=context.year,
            name=str(context.volume).rjust(2, '0'))

    @property
    def previous(self):
        return self._find_in_order(None, self.date_digital_published, 'desc')

    @property
    def next(self):
        return self._find_in_order(self.date_digital_published, None, 'asc')

    def _find_in_order(self, start, end, sort):
        if len(filter(None, [start, end])) != 1:
            return None
        # Inspired by zeit.web.core.view.Content.lineage.
        Q = zeit.solr.query
        query = Q.and_(
            Q.field_raw('type', VolumeType.type),
            Q.field('product_id', self.product.id),
            Q.datetime_range('date_digital_published', start, end),
            Q.not_(Q.field('uniqueId', self.uniqueId))
        )
        solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
        result = solr.search(query, sort='date_digital_published ' + sort,
                             fl='uniqueId', rows=1)
        if not result:
            return None
        # Since `sort` is passed in accordingly, and we exclude ourselves,
        # the first result (if any) is always the one we want.
        return zeit.cms.interfaces.ICMSContent(
            iter(result).next()['uniqueId'], None)

    def get_cover(self, cover_id, product_id=None):
        path = '//covers/cover[@id="{}" and @product_id="{}"]' \
            .format(cover_id, product_id)
        node = self.xml.xpath(path)
        uniqueId = node[0].get('href') if node else None
        if uniqueId:
            return zeit.cms.interfaces.ICMSContent(uniqueId, None)
        # Fallback: try to find product for main product
        # Save recursion :)
        elif product_id is not self.product.id:
            return self.get_cover(cover_id, self.product.id)

    def set_cover(self, cover_id, product_id, imagegroup):
        # Check if this cover is defined in VolumeCoverSource and
        # product is part of this volume and set it in xml
        if self._is_valid_cover_id_and_product_id(cover_id, product_id):
            path = '//covers/cover[@id="{}" and @product_id="{}"]' \
                .format(cover_id, product_id)
            node = self.xml.xpath(path)
            if node:
                self.xml.covers.remove(node[0])
            if imagegroup:
                node = lxml.objectify.E.cover(id=cover_id,
                                              product_id=product_id,
                                              href=imagegroup.uniqueId)
                lxml.objectify.deannotate(node[0], cleanup_namespaces=True)
                self.xml.covers.append(node)
            # Is it neccassary or does the persistent module keep track of this
            # stuff?
            super(Volume, self).__setattr__('_p_changed', True)

    def _is_valid_cover_id_and_product_id(self, cover_id, product_id):
        cover_ids = list(zeit.content.volume.interfaces.VOLUME_COVER_SOURCE(
            self))
        product_ids = [self.product.id] + [val.id for val in
                                           self.product.dependent_products]
        return cover_id in cover_ids and product_id in product_ids


class VolumeType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Volume
    interface = zeit.content.volume.interfaces.IVolume
    title = _('Volume')
    type = 'volume'


# XXX copied & adjusted from `zeit.content.author.author.BiographyQuestions
#  Can be deleted with the new Implmentation
# class VolumeCovers(
#         grok.Adapter,
#         UserDict.DictMixin,
#         zeit.cms.content.xmlsupport.Persistent):
#     """Adapter to store `IImageGroup` references inside XML of `Volume`.
#
#     The adapter interferes with the zope.formlib by overwriting setattr/getattr
#     and storing/retrieving the values on the XML of `Volume` (context).
#
#     """
#
#     grok.context(zeit.content.volume.interfaces.IVolume)
#     grok.implements(zeit.content.volume.interfaces.IVolumeCovers)
#
#     def __init__(self, context):
#         """Set attributes using `object.__setattr__`, since we overwrite it."""
#         object.__setattr__(self, 'context', context)
#         object.__setattr__(self, 'xml', zope.security.proxy.getObject(
#             context.xml))
#         object.__setattr__(self, '__parent__', context)
#
#     def __getitem__(self, key):
#         node = self.xml.xpath('//covers/cover[@id="%s"]' % key)
#         uniqueId = node[0].get('href') if node else None
#         return zeit.cms.interfaces.ICMSContent(uniqueId, None)
#
#     def __setitem__(self, key, value):
#         node = self.xml.xpath('//covers/cover[@id="%s"]' % key)
#         if node:
#             self.xml.covers.remove(node[0])
#         if value:
#             node = lxml.objectify.E.cover(id=key, href=value.uniqueId)
#             lxml.objectify.deannotate(node[0], cleanup_namespaces=True)
#             self.xml.covers.append(node)
#         super(VolumeCovers, self).__setattr__('_p_changed', True)
#
#     def keys(self):
#         return list(zeit.content.volume.interfaces.VOLUME_COVER_SOURCE(self))
#
#     def title(self, key):
#         return zeit.content.volume.interfaces.VOLUME_COVER_SOURCE(
#             self).title(key)
#
#     # XXX Why does the formlib work without an explicit security declaration?
#
#     def __getattr__(self, key):
#         """Interfere with zope.formlib and retrieve content via getitem.
#
#         Since the formlib only accesses fields from VOLUME_COVER_SOURCE, i.e.
#         ``self.keys()``, we forward other calls to the "normal" implementation
#         of ``__getattr__``.
#
#         """
#         if key in self.keys():
#             return self.get(key)
#         return super(VolumeCovers, self).__getattr__(key)
#
#     def __setattr__(self, key, value):
#         """Interfere with zope.formlib and store content via setitem.
#
#         Since the formlib only accesses fields from VOLUME_COVER_SOURCE, i.e.
#         ``self.keys()``, we forward other calls to the "normal" implementation
#         of ``__setattr__``.
#
#         """
#         if key in self.keys():
#             self[key] = value
#         return super(VolumeCovers, self).__setattr__(key, value)


@grok.adapter(zeit.cms.content.interfaces.ICommonMetadata)
@grok.implementer(zeit.content.volume.interfaces.IVolume)
def retrieve_volume_using_info_from_metadata(context):
    unique_id = None
    if (context.year is None or context.volume is None or
            context.product is None):
        pass
    elif context.product.volume and context.product.location:
        unique_id = Volume._fill_template(context, context.product.location)
    else:
        for product in zeit.content.volume.interfaces.PRODUCT_SOURCE(None):
            if context.product in product.dependent_products:
                unique_id = Volume._fill_template(context, product.location)
    return zeit.cms.interfaces.ICMSContent(unique_id, None)


@grok.adapter(zeit.content.volume.interfaces.IVolume)
@grok.implementer(zeit.content.cp.interfaces.ICenterPage)
def retrieve_corresponding_centerpage(context):
    if context.product is None or context.product.centerpage is None:
        return None
    unique_id = context.fill_template(context.product.centerpage)
    cp = zeit.cms.interfaces.ICMSContent(unique_id, None)
    if not zeit.content.cp.interfaces.ICenterPage.providedBy(cp):
        return None
    return cp

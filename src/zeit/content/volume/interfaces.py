# coding: utf8
from collections import defaultdict
from zeit.cms.i18n import MessageFactory as _
import zc.sourcefactory.source
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zope.interface
import zope.interface.common.mapping
import zope.schema


class ProductSource(zeit.cms.content.sources.ProductSource):
    """
    Filtered XML source that only includes products with `volume="true"`.
    Every product also has dependent Products which are defined in the
    product.xml.
    """

    def getValues(self, context):
        values = super(ProductSource, self).getValues(context)
        products = []
        dependent_products = defaultdict(list)
        for value in values:
            if value.volume:
                products.append(value)
            if value.relates_to:
                dependent_products[value.relates_to] += [value]
        for product in products:
            product.dependent_products = dependent_products[product.id]
        return products

PRODUCT_SOURCE = ProductSource()


class IVolume(zeit.cms.content.interfaces.IXMLContent):

    product = zope.schema.Choice(
        title=_("Product id"),
        # XXX kludgy, we expect a product with this ID to be present in the XML
        # file. We only need to set an ID here, since to read the product we'll
        # ask the source anyway.
        default=zeit.cms.content.sources.Product(u'ZEI'),
        source=PRODUCT_SOURCE)

    year = zope.schema.Int(
        title=_("Year"),
        min=1900,
        max=2100)

    volume = zope.schema.Int(
        title=_("Volume"),
        min=1,
        max=53)

    teaserText = zope.schema.Text(
        title=_("Teaser text"),
        required=False,
        max_length=170)

    date_digital_published = zope.schema.Datetime(
        title=_('Date of digital publication'),
        required=False)

    # covers = zope.interface.Attribute(
    #     'Convenience method to adapt to IVolumeCovers')

    previous = zope.interface.Attribute(
        'The previous IVolume object (by date_digital_published) or None')

    next = zope.interface.Attribute(
        'The next IVolume object (by date_digital_published) or None')

    def fill_template(text):
        """Fill in a string template with the placeholders year=self.year
        and name=self.volume (zero-padded to two digits), e.g.
        ``http://xml.zeit.de/{year}/{name}/ausgabe``.
        """

    def get_cover(cover_id, product_id):
        """
        Get a cover of product.
        For example volume.get_cover('printcover','ZEI') returns the
        printcover of DIE ZEIT of this specific volume.
        :return: zeit.content.image.interfaces.IImageGroup or None
        """


class VolumeSource(zeit.cms.content.contentsource.CMSContentSource):

    check_interfaces = (IVolume,)
    name = 'volume'

VOLUME_SOURCE = VolumeSource()


class IVolumeCovers(zope.interface.common.mapping.IMapping):
    """Mapping from uniqueId to IImageGroup to save several covers on a volume.

    This interface is used to define the available covers via an XML source and
    to store the chosen cover images as references on the IVolume.

    """


class VolumeCoverSource(zeit.cms.content.sources.XMLSource):

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        def title(self, id):
            """Expose the `getTitle` function directly on the source class."""
            return self.factory.getTitle(self.context, id)

    product_configuration = 'zeit.content.volume'
    config_url = 'volume-cover-source'
    attribute = 'id'


VOLUME_COVER_SOURCE = VolumeCoverSource()


class ProductNameMapper():

    def __init__(self):
        self.mapping = None

    def __getitem__(self, key):
        if not self.mapping:
            products = list(zeit.cms.content.sources.PRODUCT_SOURCE(self))
            self.mapping = dict([(product.id, product.title) for product in
                                 products])
        return self.mapping.get(key)

    def get(self, key, default):
        try:
            return self[key]
        except KeyError:
            return default

PRODUCT_MAPPING = ProductNameMapper()


class IVolumeReference(zeit.cms.content.interfaces.IReference):

    teaserText = zope.schema.Text(
        title=_("Teaser text"),
        required=False,
        max_length=170)


class ITocConnector(zope.interface.Interface):
    """
    Marker Interface for a the Connector to get the Tocdata from
    /cms/wf-archiv/archiv
    """

import zeit.content.volume.testing
import zeit.content.volume.interfaces


class TestProductSource(zeit.content.volume.testing.FunctionalTestCase):

    def setUp(self):
        self.source = zeit.content.volume.interfaces.PRODUCT_SOURCE

    def test_source_is_filtered_by_volume_attribute(self):
        values = list(self.source(None))
        self.assertEqual(1, len(values))
        self.assertEqual('Die Zeit', values[0].title)

    def test_zeit_has_zeit_magazin_as_dependent_products(self):
        values = list(self.source(None))
        self.assertEqual('Zeit Magazin', values[0].dependent_products[0].title)

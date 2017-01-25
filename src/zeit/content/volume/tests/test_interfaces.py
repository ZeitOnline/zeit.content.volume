import zeit.content.volume.testing
import zeit.content.volume.interfaces


class TestProductSource(zeit.content.volume.testing.FunctionalTestCase):

    def setUp(self):
        source = zeit.content.volume.interfaces.PRODUCT_SOURCE
        self.values = list(source(None))

    def test_source_is_filtered_by_volume_attribute(self):
        self.assertEqual(2, len(self.values))
        self.assertEqual('Die Zeit', self.values[0].title)

    def test_zeit_has_zeit_magazin_as_dependent_products(self):
        self.assertEqual('Zeit Magazin', self.values[0].dependent_products[
            0].title)

    def test_source_without_dependencies_has_empty_list_as_dependent_products(
            self):
        self.assertEqual([], self.values[1].dependent_products)

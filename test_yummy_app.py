import unittest
from unittest.mock import patch

import gps_service
from yummy_app import YummyApp


# ================================================================
# CAP DO 1: Bo test co ban cho san
# ================================================================
class TestEasyLevel(unittest.TestCase):
    """Kiem thu chuc nang co ban tinh tien don hang."""

    def setUp(self):
        self.app = YummyApp()

    def test_calculate_total_for_single_item(self):
        cart = {"pho": 2}
        self.assertEqual(self.app.calculate_order_total(cart), 100000)

    def test_calculate_total_for_multiple_items(self):
        cart = {"pho": 1, "bun": 1}
        self.assertEqual(self.app.calculate_order_total(cart), 95000)

    def test_calculate_total_for_empty_cart(self):
        self.assertEqual(self.app.calculate_order_total({}), 0.0)

    def test_calculate_total_with_zero_quantity(self):
        cart = {"pho": 0}
        self.assertEqual(self.app.calculate_order_total(cart), 0.0)


# ================================================================
# CAP DO 2 (TIET 3): Bo sung test sau khi thiet ke test case tren giay
# ================================================================

class TestMediumLevel(unittest.TestCase):
    """Kiem thu ma khuyen mai theo ket noi mang va phien ban HDH."""

    def setUp(self):
        self.app = YummyApp(network_status="online", os_version=15)

    def test_apply_valid_promo_code_online(self):
        self.assertAlmostEqual(
            self.app.apply_promo_code(100000, "GIAM10"), 90000
        )

    def test_apply_promo_code_offline_raises_connection_error(self):
        app = YummyApp(network_status="offline")
        with self.assertRaisesRegex(ConnectionError, "Khong co ket noi mang"):
            app.apply_promo_code(100000, "GIAM10")

    def test_apply_special_promo_code_on_os_15(self):
        self.assertAlmostEqual(
            self.app.apply_promo_code(100000, "NEW_OS_ONLY"), 80000
        )

    def test_apply_special_promo_code_on_os_14_raises_value_error(self):
        app = YummyApp(os_version=14)
        with self.assertRaisesRegex(ValueError, "HDH phien ban 15"):
            app.apply_promo_code(100000, "NEW_OS_ONLY")

    def test_apply_invalid_promo_code_raises_value_error(self):
        with self.assertRaisesRegex(ValueError, "Ma khuyen mai khong hop le"):
            self.app.apply_promo_code(100000, "INVALID")


class TestHardLevel(unittest.TestCase):
    """Mock dich vu GPS de kiem thu de xuat nha hang."""

    def setUp(self):
        self.app = YummyApp()

    @patch(
        'yummy_app.gps_service.get_current_location',
        return_value=(10.0, 105.0),
    )
    def test_get_nearby_restaurants_inside_service_area(self, mock_gps):
        self.assertEqual(
            self.app.get_nearby_restaurants(),
            ["Nha hang Pho Ly Quoc Su", "Bun cha Huong Lien"],
        )
        mock_gps.assert_called_once_with()

    @patch(
        'yummy_app.gps_service.get_current_location',
        return_value=(20.0, 110.0),
    )
    def test_get_nearby_restaurants_outside_service_area(self, mock_gps):
        self.assertEqual(self.app.get_nearby_restaurants(), [])
        mock_gps.assert_called_once_with()

    @patch(
        'yummy_app.gps_service.get_current_location',
        side_effect=gps_service.GPSSignalLostError,
    )
    def test_get_nearby_restaurants_when_gps_signal_is_lost(self, mock_gps):
        self.assertEqual(
            self.app.get_nearby_restaurants(), "Khong the xac dinh vi tri."
        )
        mock_gps.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()

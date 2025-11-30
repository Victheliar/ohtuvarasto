import unittest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app, varastot, get_next_id


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        # Clear warehouses before each test
        varastot.clear()

    def tearDown(self):
        varastot.clear()

    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Varastojen hallinta', response.data)

    def test_luo_varasto_get(self):
        response = self.client.get('/luo')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Luo uusi varasto', response.data)

    def test_luo_varasto_post(self):
        response = self.client.post('/luo', data={
            'nimi': 'Testivarasto',
            'tilavuus': '100',
            'alku_saldo': '50'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Testivarasto', response.data)

    def test_nayta_varasto(self):
        # Create a warehouse first
        self.client.post('/luo', data={
            'nimi': 'Testivarasto',
            'tilavuus': '100',
            'alku_saldo': '50'
        })
        # Get the id of the created warehouse
        varasto_id = list(varastot.keys())[0]
        response = self.client.get(f'/varasto/{varasto_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Testivarasto', response.data)

    def test_nayta_varasto_not_found(self):
        response = self.client.get('/varasto/999', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Should redirect to index
        self.assertIn(b'Varastojen hallinta', response.data)

    def test_muokkaa_varasto_get(self):
        # Create a warehouse first
        self.client.post('/luo', data={
            'nimi': 'Testivarasto',
            'tilavuus': '100',
            'alku_saldo': '50'
        })
        varasto_id = list(varastot.keys())[0]
        response = self.client.get(f'/varasto/{varasto_id}/muokkaa')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Muokkaa', response.data)

    def test_muokkaa_varasto_post(self):
        # Create a warehouse first
        self.client.post('/luo', data={
            'nimi': 'Testivarasto',
            'tilavuus': '100',
            'alku_saldo': '50'
        })
        varasto_id = list(varastot.keys())[0]
        response = self.client.post(f'/varasto/{varasto_id}/muokkaa', data={
            'nimi': 'Uusi nimi'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Uusi nimi', response.data)

    def test_muokkaa_varasto_not_found(self):
        response = self.client.get('/varasto/999/muokkaa', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_lisaa_varastoon(self):
        # Create a warehouse first
        self.client.post('/luo', data={
            'nimi': 'Testivarasto',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        varasto_id = list(varastot.keys())[0]
        response = self.client.post(f'/varasto/{varasto_id}/lisaa', data={
            'maara': '25'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(varastot[varasto_id]['varasto'].saldo, 25)

    def test_lisaa_varastoon_not_found(self):
        response = self.client.post('/varasto/999/lisaa', data={
            'maara': '25'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_ota_varastosta(self):
        # Create a warehouse with some initial balance
        self.client.post('/luo', data={
            'nimi': 'Testivarasto',
            'tilavuus': '100',
            'alku_saldo': '50'
        })
        varasto_id = list(varastot.keys())[0]
        response = self.client.post(f'/varasto/{varasto_id}/ota', data={
            'maara': '20'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(varastot[varasto_id]['varasto'].saldo, 30)

    def test_ota_varastosta_not_found(self):
        response = self.client.post('/varasto/999/ota', data={
            'maara': '20'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_poista_varasto(self):
        # Create a warehouse first
        self.client.post('/luo', data={
            'nimi': 'Testivarasto',
            'tilavuus': '100',
            'alku_saldo': '50'
        })
        varasto_id = list(varastot.keys())[0]
        response = self.client.post(f'/varasto/{varasto_id}/poista',
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(varasto_id, varastot)

    def test_poista_varasto_not_found(self):
        response = self.client.post('/varasto/999/poista', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_empty_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Ei viel', response.data)  # "Ei vielä luotuja varastoja"

    def test_luo_varasto_invalid_tilavuus(self):
        response = self.client.post('/luo', data={
            'nimi': 'Testivarasto',
            'tilavuus': 'invalid',
            'alku_saldo': '50'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Should use default value of 100
        varasto_id = list(varastot.keys())[0]
        self.assertEqual(varastot[varasto_id]['varasto'].tilavuus, 100)

    def test_lisaa_varastoon_invalid_maara(self):
        self.client.post('/luo', data={
            'nimi': 'Testivarasto',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        varasto_id = list(varastot.keys())[0]
        response = self.client.post(f'/varasto/{varasto_id}/lisaa', data={
            'maara': 'invalid'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Should use default value of 0
        self.assertEqual(varastot[varasto_id]['varasto'].saldo, 0)

from funkload.FunkLoadTestCase import FunkLoadTestCase
import client

class TestLauncelot(FunkLoadTestCase):
    def test_dialog(self):
        for success in client.client('localhost', 2000):
            self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()
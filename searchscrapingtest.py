import unittest
import searcher as scr

class Test_Part1(unittest.TestCase):
    def setUp(self):
        self.state_url = scr.get_youtube_video_url('Hofner')

    def test_1_return(self):
        self.assertEqual(self.finalreturns, 'https://www.youtube.com/watch?v=lLdoW45vGe4')


if __name__ == '__main__':
    unittest.main()
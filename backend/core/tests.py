from django.test import TestCase
from .services import calculate_metrics, calculate_readability
from .badges import get_badges


class MetricsTests(TestCase):
    def test_efficiency(self):
        m = calculate_metrics(word_count=200, time_seconds=60, correct=4, total=5)
        self.assertEqual(m['wpm'], 200.0)
        self.assertEqual(m['quality_percent'], 80.0)
        self.assertEqual(m['efficiency'], 160.0)


class ReadabilityTests(TestCase):
    def test_easy_text(self):
        r = calculate_readability("Мама мыла раму. Кот спит на печи. Дом стоит у реки.")
        self.assertEqual(r['difficulty'], 'easy')

    def test_empty(self):
        self.assertEqual(calculate_readability("")['difficulty'], '')


class BadgesTests(TestCase):
    def test_rushing(self):
        self.assertEqual(get_badges(250, 20)[0].code, 'rushing')

    def test_golden(self):
        self.assertEqual(get_badges(190, 80)[0].code, 'golden')

    def test_thoughtful_and_accuracy(self):
        main, extras = get_badges(90, 100)
        self.assertEqual(main.code, 'thoughtful')
        self.assertEqual(extras[0].code, 'accuracy')

    def test_no_focus(self):
        self.assertEqual(get_badges(150, 0)[0].code, 'no_focus')

    def test_every_combination_has_badge(self):
        for v in range(0, 400, 10):
            for q in (0, 20, 40, 60, 80, 100):
                self.assertIsNotNone(get_badges(v, q)[0])
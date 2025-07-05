from django.core.management.base import BaseCommand
from results.models import WordResult

class Command(BaseCommand):
    help = "Обновляет поле current_result для всех записей WordResult на основе known_count и unknown_count"

    def handle(self, *args, **options):
        all_results = WordResult.objects.all()
        total = all_results.count()
        self.stdout.write(f"Обработка {total} записей WordResult...")

        for i, result in enumerate(all_results, start=1):
            value = result.known_count - result.unknown_count

            # Ограничение от 0 до 10
            if value < 0:
                value = 0
            elif value > 10:
                value = 10

            result.current_result = value
            result.save(update_fields=['current_result'])

            if i % 100 == 0 or i == total:
                self.stdout.write(f"Обработано {i}/{total}...")

        self.stdout.write(self.style.SUCCESS("Обновление current_result завершено!"))

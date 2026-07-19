import random

from django.core.management.base import BaseCommand
from faker import Faker

from Receptions.models import News, Insurances

fake = Faker()


class Command(BaseCommand):
    help = "Seed database with test Insurance & News"

    def handle(self, *args, **kwargs):

        insurance_names = [
            "تامین اجتماعی",
            "خدمات درمانی",
            "نیرو مسلح",
            "دانا",
            "البرز",
            "نوین",
            "کوثر",
            "فولاد خوزستان",
            "نفت",
            "برق آبی",
            "سردفتران",
            "دی",
            "آتیه سازان",
        ]

        insurances = []
        for name in insurance_names:
            insurance, created = Insurances.objects.get_or_create(
                name=name, type=random.choice(["Supplementary"]), status="Enable"
            )
            insurances.append(insurance)

        self.stdout.write(self.style.SUCCESS("insurances created ✅"))

        for _ in range(30):
            News.objects.create(
                title=random.choice(
                    [
                        "خبر فوری 1",
                        "خبر فوری 2",
                        "خبر فوری 3",
                        "خبر فوری 4",
                        "خبر فوری 5",
                        "خبر فوری 6",
                    ]
                ),
                text="لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ، و با استفاده از طراحان گرافیک است، چاپگرها و متون بلکه روزنامه و مجله در ستون و سطرآنچنان که لازم است، و برای شرایط فعلی تکنولوژی مورد نیاز، و کاربردهای متنوع با هدف بهبود ابزارهای کاربردی می باشد، کتابهای زیادی در شصت و سه درصد گذشته حال و آینده، شناخت فراوان جامعه و متخصصان را می طلبد، تا با نرم افزارها شناخت بیشتری را برای طراحان رایانه ای علی الخصوص طراحان خلاقی، و فرهنگ پیشرو در زبان فارسی ایجاد کرد، در این صورت می توان امید داشت که تمام و دشواری موجود در ارائه راهکارها، و شرایط سخت تایپ به پایان رسد و زمان مورد نیاز شامل حروفچینی دستاوردهای اصلی، و جوابگوی سوالات پیوسته اهل دنیای موجود طراحی اساسا مورد استفاده قرار گیرد.",
                status="Enable",
            )

        self.stdout.write(self.style.SUCCESS("News created ✅"))

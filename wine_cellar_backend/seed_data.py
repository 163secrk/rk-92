import os
import django
from django.utils import timezone
from datetime import timedelta, date
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wine_cellar.settings')
django.setup()

from monitoring.models import WineCellar, SensorReading, Alert
from collection.models import Wine, ValuationHistory
from mortgage.models import MortgageApplication, MortgageCollateral
from django.contrib.auth.models import User

def create_superuser():
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@winecellar.com', 'admin123')
        print("创建超级用户: admin / admin123")

def create_cellars():
    cellars_data = [
        {
            'name': '主酒窖A区',
            'location': '地下一层A区',
            'capacity': 500,
            'optimal_temp_min': 12.0,
            'optimal_temp_max': 14.0,
            'optimal_humidity_min': 65.0,
            'optimal_humidity_max': 75.0,
        },
        {
            'name': '主酒窖B区',
            'location': '地下一层B区',
            'capacity': 300,
            'optimal_temp_min': 10.0,
            'optimal_temp_max': 12.0,
            'optimal_humidity_min': 70.0,
            'optimal_humidity_max': 80.0,
        },
        {
            'name': '珍藏酒窖',
            'location': '地下二层VIP区',
            'capacity': 100,
            'optimal_temp_min': 13.0,
            'optimal_temp_max': 15.0,
            'optimal_humidity_min': 68.0,
            'optimal_humidity_max': 78.0,
        },
    ]

    cellars = []
    for data in cellars_data:
        cellar, created = WineCellar.objects.get_or_create(**data)
        cellars.append(cellar)
        if created:
            print(f"创建酒窖: {cellar.name}")

    return cellars

def create_sensor_readings(cellars):
    for cellar in cellars:
        base_temp = (cellar.optimal_temp_min + cellar.optimal_temp_max) / 2
        base_humidity = (cellar.optimal_humidity_min + cellar.optimal_humidity_max) / 2

        for days_ago in range(30):
            for hour in range(0, 24, 2):
                timestamp = timezone.now() - timedelta(days=days_ago, hours=hour)
                temp_variation = random.uniform(-1.5, 1.5)
                humidity_variation = random.uniform(-3, 3)

                if days_ago == 0 and hour > 12:
                    continue

                reading = SensorReading.objects.create(
                    cellar=cellar,
                    temperature=round(base_temp + temp_variation, 1),
                    humidity=round(base_humidity + humidity_variation, 1),
                    timestamp=timestamp,
                )

                if reading.temperature > cellar.optimal_temp_max + 0.5:
                    Alert.objects.get_or_create(
                        cellar=cellar,
                        reading=reading,
                        defaults={
                            'alert_type': 'temp_high',
                            'severity': 'warning' if reading.temperature < cellar.optimal_temp_max + 2 else 'critical',
                            'value': reading.temperature,
                            'message': f'温度过高: {reading.temperature}°C',
                            'status': 'resolved' if days_ago > 1 else 'active',
                        }
                    )
                elif reading.temperature < cellar.optimal_temp_min - 0.5:
                    Alert.objects.get_or_create(
                        cellar=cellar,
                        reading=reading,
                        defaults={
                            'alert_type': 'temp_low',
                            'severity': 'warning' if reading.temperature > cellar.optimal_temp_min - 2 else 'critical',
                            'value': reading.temperature,
                            'message': f'温度过低: {reading.temperature}°C',
                            'status': 'resolved' if days_ago > 1 else 'active',
                        }
                    )

    print(f"创建传感器读数完成")

def create_wines():
    wines_data = [
        {
            'name': 'Château Lafite Rothschild',
            'chateau': 'Château Lafite Rothschild',
            'region': 'Bordeaux, Pauillac',
            'country': '法国',
            'vintage': 2018,
            'category': 'red',
            'grape_variety': 'Cabernet Sauvignon, Merlot',
            'alcohol_content': 13.5,
            'bottle_size': 0.75,
            'quantity': 12,
            'purchase_date': date(2020, 5, 15),
            'purchase_price': Decimal('28000.00'),
            'current_value': Decimal('42000.00'),
            'cellar_location': 'A-01-01',
            'status': 'cellared',
            'drinking_window_start': 2028,
            'drinking_window_end': 2050,
            'tasting_notes': '黑加仑、雪松、烟草香气，单宁细腻，余韵悠长',
        },
        {
            'name': 'Château Margaux',
            'chateau': 'Château Margaux',
            'region': 'Bordeaux, Margaux',
            'country': '法国',
            'vintage': 2016,
            'category': 'red',
            'grape_variety': 'Cabernet Sauvignon, Merlot, Cabernet Franc',
            'alcohol_content': 13.0,
            'bottle_size': 0.75,
            'quantity': 6,
            'purchase_date': date(2019, 8, 20),
            'purchase_price': Decimal('18000.00'),
            'current_value': Decimal('28500.00'),
            'cellar_location': 'A-02-03',
            'status': 'cellared',
            'drinking_window_start': 2025,
            'drinking_window_end': 2045,
            'tasting_notes': '紫罗兰、黑醋栗、松露香气，结构优雅',
        },
        {
            'name': 'Domaine de la Romanée-Conti',
            'chateau': 'Domaine de la Romanée-Conti',
            'region': 'Burgundy, Côte de Nuits',
            'country': '法国',
            'vintage': 2019,
            'category': 'red',
            'grape_variety': 'Pinot Noir',
            'alcohol_content': 13.0,
            'bottle_size': 0.75,
            'quantity': 3,
            'purchase_date': date(2021, 3, 10),
            'purchase_price': Decimal('128000.00'),
            'current_value': Decimal('185000.00'),
            'cellar_location': 'VIP-01-01',
            'status': 'cellared',
            'drinking_window_start': 2030,
            'drinking_window_end': 2055,
            'tasting_notes': '玫瑰、红莓、森林地表香气，层次极为复杂',
        },
        {
            'name': 'Château d\'Yquem',
            'chateau': 'Château d\'Yquem',
            'region': 'Bordeaux, Sauternes',
            'country': '法国',
            'vintage': 2015,
            'category': 'dessert',
            'grape_variety': 'Sémillon, Sauvignon Blanc',
            'alcohol_content': 14.0,
            'bottle_size': 0.75,
            'quantity': 6,
            'purchase_date': date(2018, 11, 5),
            'purchase_price': Decimal('15000.00'),
            'current_value': Decimal('24000.00'),
            'cellar_location': 'B-01-02',
            'status': 'cellared',
            'drinking_window_start': 2025,
            'drinking_window_end': 2060,
            'tasting_notes': '蜂蜜、杏桃、贵腐香气，酸甜平衡极佳',
        },
        {
            'name': 'Dom Pérignon',
            'chateau': 'Moët & Chandon',
            'region': 'Champagne',
            'country': '法国',
            'vintage': 2012,
            'category': 'sparkling',
            'grape_variety': 'Chardonnay, Pinot Noir',
            'alcohol_content': 12.5,
            'bottle_size': 0.75,
            'quantity': 12,
            'purchase_date': date(2020, 12, 20),
            'purchase_price': Decimal('2200.00'),
            'current_value': Decimal('3500.00'),
            'cellar_location': 'B-02-05',
            'status': 'drinking',
            'drinking_window_start': 2020,
            'drinking_window_end': 2030,
            'tasting_notes': '烤面包、苹果、矿物香气，气泡细腻持久',
        },
        {
            'name': 'Château Latour',
            'chateau': 'Château Latour',
            'region': 'Bordeaux, Pauillac',
            'country': '法国',
            'vintage': 2010,
            'category': 'red',
            'grape_variety': 'Cabernet Sauvignon, Merlot',
            'alcohol_content': 13.5,
            'bottle_size': 0.75,
            'quantity': 6,
            'purchase_date': date(2015, 6, 18),
            'purchase_price': Decimal('18000.00'),
            'current_value': Decimal('38000.00'),
            'cellar_location': 'A-03-02',
            'status': 'peak',
            'drinking_window_start': 2022,
            'drinking_window_end': 2040,
            'tasting_notes': '黑currant、石墨、烟草香气，结构宏大',
        },
        {
            'name': 'Opus One',
            'chateau': 'Opus One',
            'region': 'Napa Valley, Oakville',
            'country': '美国',
            'vintage': 2018,
            'category': 'red',
            'grape_variety': 'Bordeaux Blend',
            'alcohol_content': 14.0,
            'bottle_size': 0.75,
            'quantity': 12,
            'purchase_date': date(2021, 1, 15),
            'purchase_price': Decimal('4500.00'),
            'current_value': Decimal('7200.00'),
            'cellar_location': 'A-04-01',
            'status': 'cellared',
            'drinking_window_start': 2028,
            'drinking_window_end': 2045,
            'tasting_notes': '黑樱桃、摩卡、香料香气，口感圆润',
        },
        {
            'name': 'Penfolds Grange',
            'chateau': 'Penfolds',
            'region': 'South Australia, Barossa Valley',
            'country': '澳大利亚',
            'vintage': 2016,
            'category': 'red',
            'grape_variety': 'Shiraz',
            'alcohol_content': 14.5,
            'bottle_size': 0.75,
            'quantity': 6,
            'purchase_date': date(2019, 9, 10),
            'purchase_price': Decimal('5500.00'),
            'current_value': Decimal('8800.00'),
            'cellar_location': 'A-05-03',
            'status': 'cellared',
            'drinking_window_start': 2026,
            'drinking_window_end': 2040,
            'tasting_notes': '黑莓、巧克力、薄荷香气，单宁强劲',
        },
        {
            'name': 'Château Cheval Blanc',
            'chateau': 'Château Cheval Blanc',
            'region': 'Bordeaux, Saint-Émilion',
            'country': '法国',
            'vintage': 2015,
            'category': 'red',
            'grape_variety': 'Cabernet Franc, Merlot',
            'alcohol_content': 13.5,
            'bottle_size': 0.75,
            'quantity': 3,
            'purchase_date': date(2018, 4, 22),
            'purchase_price': Decimal('22000.00'),
            'current_value': Decimal('36000.00'),
            'cellar_location': 'VIP-01-02',
            'status': 'peak',
            'drinking_window_start': 2023,
            'drinking_window_end': 2040,
            'tasting_notes': '红莓、紫罗兰、石墨香气，优雅细腻',
        },
        {
            'name': 'Krug Grande Cuvée',
            'chateau': 'Krug',
            'region': 'Champagne',
            'country': '法国',
            'vintage': 2008,
            'category': 'sparkling',
            'grape_variety': 'Chardonnay, Pinot Noir, Pinot Meunier',
            'alcohol_content': 12.0,
            'bottle_size': 0.75,
            'quantity': 6,
            'purchase_date': date(2017, 8, 15),
            'purchase_price': Decimal('3500.00'),
            'current_value': Decimal('5800.00'),
            'cellar_location': 'B-03-01',
            'status': 'drinking',
            'drinking_window_start': 2018,
            'drinking_window_end': 2028,
            'tasting_notes': '烤杏仁、蜂蜜、柑橘香气，复杂度极高',
        },
        {
            'name': 'Château Haut-Brion',
            'chateau': 'Château Haut-Brion',
            'region': 'Bordeaux, Pessac-Léognan',
            'country': '法国',
            'vintage': 2005,
            'category': 'red',
            'grape_variety': 'Cabernet Sauvignon, Merlot',
            'alcohol_content': 13.5,
            'bottle_size': 0.75,
            'quantity': 3,
            'purchase_date': date(2010, 5, 20),
            'purchase_price': Decimal('12000.00'),
            'current_value': Decimal('28000.00'),
            'cellar_location': 'A-06-01',
            'status': 'declining',
            'drinking_window_start': 2015,
            'drinking_window_end': 2025,
            'tasting_notes': '黑加仑、石墨、雪松香气，已进入衰退期',
        },
        {
            'name': 'Château Mouton Rothschild',
            'chateau': 'Château Mouton Rothschild',
            'region': 'Bordeaux, Pauillac',
            'country': '法国',
            'vintage': 2000,
            'category': 'red',
            'grape_variety': 'Cabernet Sauvignon, Merlot',
            'alcohol_content': 13.0,
            'bottle_size': 0.75,
            'quantity': 2,
            'purchase_date': date(2008, 3, 15),
            'purchase_price': Decimal('15000.00'),
            'current_value': Decimal('35000.00'),
            'cellar_location': 'A-06-02',
            'status': 'declining',
            'drinking_window_start': 2010,
            'drinking_window_end': 2020,
            'tasting_notes': '黑醋栗、烟草、松露香气，已过最佳适饮期',
        },
        {
            'name': 'Veuve Clicquot La Grande Dame',
            'chateau': 'Veuve Clicquot',
            'region': 'Champagne',
            'country': '法国',
            'vintage': 2012,
            'category': 'sparkling',
            'grape_variety': 'Chardonnay, Pinot Noir',
            'alcohol_content': 12.5,
            'bottle_size': 0.75,
            'quantity': 4,
            'purchase_date': date(2018, 10, 10),
            'purchase_price': Decimal('2800.00'),
            'current_value': Decimal('4200.00'),
            'cellar_location': 'B-03-02',
            'status': 'peak',
            'drinking_window_start': 2020,
            'drinking_window_end': 2027,
            'tasting_notes': '烤面包、白色花朵、矿物香气，巅峰状态',
        },
    ]

    wines = []
    for data in wines_data:
        wine, created = Wine.objects.get_or_create(
            name=data['name'],
            vintage=data['vintage'],
            defaults=data
        )
        wines.append(wine)
        if created:
            print(f"创建酒品: {wine.name} {wine.vintage}")
            ValuationHistory.objects.create(
                wine=wine,
                value=wine.current_value,
                change_percent=0,
                reason='初始录入'
            )

    return wines

def create_mortgage_applications(wines):
    user = User.objects.first()

    apps_data = [
        {
            'applicant_name': '张先生',
            'applicant_id': '110101198001011234',
            'applicant_phone': '13800138001',
            'applicant_email': 'zhang@example.com',
            'loan_amount': Decimal('500000.00'),
            'loan_term_months': 12,
            'interest_rate': 4.8,
            'purpose': '企业流动资金周转',
            'status': 'active',
            'approved_amount': Decimal('450000.00'),
            'collateral_value': Decimal('900000.00'),
        },
        {
            'applicant_name': '李女士',
            'applicant_id': '310101198505155678',
            'applicant_phone': '13900139002',
            'applicant_email': 'li@example.com',
            'loan_amount': Decimal('800000.00'),
            'loan_term_months': 24,
            'interest_rate': 5.2,
            'purpose': '房产投资',
            'status': 'approved',
        },
        {
            'applicant_name': '王先生',
            'applicant_id': '440101197812129012',
            'applicant_phone': '13700137003',
            'applicant_email': 'wang@example.com',
            'loan_amount': Decimal('300000.00'),
            'loan_term_months': 6,
            'interest_rate': 4.5,
            'purpose': '短期资金周转',
            'status': 'reviewing',
        },
    ]

    for i, data in enumerate(apps_data):
        app, created = MortgageApplication.objects.get_or_create(
            applicant_name=data['applicant_name'],
            defaults=data
        )
        if created:
            print(f"创建抵押申请: {app.applicant_name}")

            selected_wines = wines[i*3:(i+1)*3] if (i+1)*3 <= len(wines) else wines[-3:]
            for wine in selected_wines:
                MortgageCollateral.objects.get_or_create(
                    application=app,
                    wine=wine,
                    defaults={
                        'quantity': 2,
                        'unit_value': wine.current_value,
                        'total_value': wine.current_value * 2,
                        'storage_location': wine.cellar_location,
                    }
                )

def main():
    print("开始初始化数据...")
    create_superuser()
    cellars = create_cellars()
    create_sensor_readings(cellars)
    wines = create_wines()
    create_mortgage_applications(wines)
    print("数据初始化完成!")

if __name__ == '__main__':
    main()

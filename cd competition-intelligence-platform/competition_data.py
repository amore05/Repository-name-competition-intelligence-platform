import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class CompetitionDataGenerator:
    def __init__(self):
        self.products = ['سكر', 'أرز', 'زيت طهي', 'دقيق', 'قهوة', 'شاي', 'حليب', 'خبز']
        self.regions = ['الرياض', 'جدة', 'الدمام', 'مكة', 'المدينة', 'القصيم', 'عسير', 'حائل']
        self.companies = [
            'شركة الأغذية الوطنية', 'مؤسسة التسويق الحديث', 'شركة التوزيع المتكامل',
            'مجموعة الأسواق المركزية', 'شركة المستهلك المتحدة', 'مؤسسة التجارة المتطورة',
            'شركة التجزئة الكبرى', 'مجموعة التموين الشامل'
        ]
        
    def generate_comprehensive_data(self):
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        
        data = []
        for date in dates:
            for product in self.products:
                for region in self.regions:
                    for company in self.companies:
                        base_prices = {
                            'سكر': 3.5, 'أرز': 8.0, 'زيت طهي': 15.0, 'دقيق': 2.5, 
                            'قهوة': 25.0, 'شاي': 12.0, 'حليب': 4.0, 'خبز': 1.0
                        }
                        base_price = base_prices[product]
                        price = self.apply_scenarios(date, product, region, company, base_price)
                        complaint_count = self.generate_complaints(date, product, region, company)
                        market_share = self.generate_market_share(product, region, company)
                        
                        data.append({
                            'date': date, 'product': product, 'region': region, 'company': company,
                            'price': round(price, 2), 'complaint_count': complaint_count,
                            'market_share': round(market_share, 2),
                            'scenario_type': self.get_scenario_type(date, product, region, company)
                        })
        
        return pd.DataFrame(data)
    
    def apply_scenarios(self, date, product, region, company, base_price):
        price = base_price
        
        if (region == 'الرياض' and company == 'شركة الأغذية الوطنية' 
            and date >= datetime(2024, 6, 1) and date <= datetime(2024, 8, 31)):
            price *= 1.4
        elif (region == 'جدة' and company == 'مؤسسة التسويق الحديث' 
              and date >= datetime(2024, 3, 1) and date <= datetime(2024, 5, 31)):
            price *= 0.6
        elif (product in ['سكر', 'دقيق'] and date >= datetime(2024, 9, 1) 
              and company in ['شركة التوزيع المتكامل', 'مجموعة الأسواق المركزية', 'شركة المستهلك المتحدة']):
            price *= 1.25
        elif region == 'حائل' and product == 'زيت طهي':
            price *= 1.3
        elif company == 'مجموعة التموين الشامل' and product == 'قهوة':
            daily_variation = np.random.normal(0, 0.2)
            price *= (1 + daily_variation)
        else:
            normal_variation = np.random.normal(0, 0.05)
            price *= (1 + normal_variation)
        
        return max(price, base_price * 0.5)
    
    def generate_complaints(self, date, product, region, company):
        base_complaints = np.random.poisson(2)
        if (region == 'الرياض' and company == 'شركة الأغذية الوطنية' 
            and date >= datetime(2024, 6, 1)):
            base_complaints += np.random.poisson(5)
        elif (company == 'مؤسسة التسويق الحديث' and product in ['حليب', 'خبز']):
            base_complaints += np.random.poisson(3)
        return max(base_complaints, 0)
    
    def generate_market_share(self, product, region, company):
        base_share = np.random.normal(12.5, 3)
        if (company == 'شركة الأغذية الوطنية' and region == 'الرياض' 
            and product in ['سكر', 'دقيق']):
            base_share = np.random.normal(35, 5)
        elif region == 'جدة' and product == 'قهوة':
            base_share = np.random.normal(8, 2)
        return max(min(base_share, 50), 1)
    
    def get_scenario_type(self, date, product, region, company):
        if (region == 'الرياض' and company == 'شركة الأغذية الوطنية' 
            and date >= datetime(2024, 6, 1)):
            return "ارتفاع أسعار غير مبرر"
        elif (region == 'جدة' and company == 'مؤسسة التسويق الحديث' 
              and date >= datetime(2024, 3, 1)):
            return "انخفاض أسعار مشبوه (إغراق)"
        elif (product in ['سكر', 'دقيق'] and date >= datetime(2024, 9, 1) 
              and company in ['شركة التوزيع المتكامل', 'مجموعة الأسواق المركزية', 'شركة المستهلك المتحدة']):
            return "تغير أسعار متزامن (تكتل)"
        elif region == 'حائل' and product == 'زيت طهي':
            return "تفاوت أسعار جغرافي"
        elif company == 'مجموعة التموين الشامل' and product == 'قهوة':
            return "تقلبات أسعار شديدة"
        else:
            return "طبيعي"

def get_analysis_insights(df):
    insights = []
    high_price_data = df[
        (df['scenario_type'] == "ارتفاع أسعار غير مبرر") &
        (df['price'] > df[df['scenario_type'] == "طبيعي"]["price"].mean() * 1.3)
    ]
    if not high_price_data.empty:
        insights.append({
            "type": "تحذير", "title": "ارتفاع أسعار غير مبرر",
            "description": f"تم رصد ارتفاع غير طبيعي في الأسعار لـ {len(high_price_data)} سجل",
            "companies": high_price_data['company'].unique().tolist(),
            "products": high_price_data['product'].unique().tolist(),
            "regions": high_price_data['region'].unique().tolist()
        })
    return insights

def get_statistical_summary(df):
    return {
        "total_records": len(df),
        "date_range": {"start": df['date'].min().strftime('%Y-%m-%d'), "end": df['date'].max().strftime('%Y-%m-%d')},
        "products_count": df['product'].nunique(), "regions_count": df['region'].nunique(), 
        "companies_count": df['company'].nunique(), "total_complaints": df['complaint_count'].sum(),
        "avg_price_by_product": df.groupby('product')['price'].mean().to_dict(),
        "scenario_distribution": df['scenario_type'].value_counts().to_dict()
    }

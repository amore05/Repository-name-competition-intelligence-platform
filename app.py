import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# توليد البيانات مباشرة في التطبيق
class CompetitionDataGenerator:
    def __init__(self):
        self.products = ['سكر', 'أرز', 'زيت طهي', 'دقيق', 'قهوة']
        self.regions = ['الرياض', 'جدة', 'الدمام', 'مكة', 'المدينة']
        self.companies = [
            'شركة الأغذية الوطنية', 'مؤسسة التسويق الحديث', 
            'شركة التوزيع المتكامل', 'مجموعة الأسواق المركزية'
        ]
        
    def generate_data(self):
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
        
        data = []
        for date in dates:
            for product in self.products:
                for region in self.regions:
                    for company in self.companies:
                        base_prices = {'سكر': 3.5, 'أرز': 8.0, 'زيت طهي': 15.0, 'دقيق': 2.5, 'قهوة': 25.0}
                        base_price = base_prices[product]
                        
                        # تطبيق سيناريوهات
                        price = base_price
                        if region == 'الرياض' and company == 'شركة الأغذية الوطنية':
                            price *= 1.3
                        elif region == 'جدة' and company == 'مؤسسة التسويق الحديث':
                            price *= 0.7
                        
                        # تباين طبيعي
                        price *= (1 + np.random.normal(0, 0.05))
                        price = max(price, base_price * 0.8)
                        
                        complaint_count = np.random.poisson(2)
                        market_share = np.random.normal(15, 5)
                        market_share = max(min(market_share, 40), 5)
                        
                        data.append({
                            'date': date, 'product': product, 'region': region, 
                            'company': company, 'price': round(price, 2),
                            'complaint_count': complaint_count,
                            'market_share': round(market_share, 2)
                        })
        
        return pd.DataFrame(data)

@st.cache_data
def load_data():
    generator = CompetitionDataGenerator()
    return generator.generate_data()

# كشف الشذوذ بدون scikit-learn
def detect_anomalies_simple(df):
    """كشف شذوذ مبسط باستخدام القيم المتطرفة الإحصائية"""
    price_mean = df['price'].mean()
    price_std = df['price'].std()
    threshold = price_mean + 2 * price_std
    
    df['is_anomaly'] = df['price'] > threshold
    return df

# إعداد صفحة Streamlit
st.set_page_config(page_title="منصة ذكاء المنافسة", page_icon="📊", layout="wide")

# تنسيق CSS
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #1f77b4; text-align: center; margin-bottom: 2rem; font-weight: bold;}
    .section-header {font-size: 1.5rem; color: #2e86ab; margin: 1rem 0; border-right: 5px solid #2e86ab; padding-right: 10px;}
    .metric-card {background-color: #f0f2f6; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-right: 4px solid #2e86ab;}
    .warning-box {background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 10px; margin: 10px 0;}
    .danger-box {background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 10px; margin: 10px 0;}
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<div class="main-header">🏢 منصة ذكاء المنافسة - الهيئة العامة للمنافسة</div>', unsafe_allow_html=True)
    
    # تحميل البيانات
    data = load_data()
    
    # الشريط الجانبي
    with st.sidebar:
        st.markdown("### إعدادات التحليل")
        analysis_type = st.selectbox(
            "نوع التحليل:",
            ["نظرة عامة", "تحليل الأسعار", "كشف الشذوذ", "التقارير"]
        )
        selected_product = st.selectbox("اختر المنتج:", data['product'].unique())
        selected_region = st.selectbox("اختر المنطقة:", data['region'].unique())
    
    # تصفية البيانات
    filtered_data = data[
        (data['product'] == selected_product) & 
        (data['region'] == selected_region)
    ]
    
    if analysis_type == "نظرة عامة":
        display_overview(filtered_data)
    elif analysis_type == "تحليل الأسعار":
        display_price_analysis(filtered_data)
    elif analysis_type == "كشف الشذوذ":
        display_anomaly_detection(filtered_data)
    else:
        display_reports(filtered_data)

def display_overview(df):
    st.markdown('<div class="section-header">📈 النظرة العامة</div>', unsafe_allow_html=True)
    
    # مؤشرات الأداء
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("متوسط السعر", f"{df['price'].mean():.2f} ريال")
    with col2:
        st.metric("إجمالي الشكاوى", df['complaint_count'].sum())
    with col3:
        st.metric("عدد الشركات", df['company'].nunique())
    with col4:
        st.metric("أعلى سعر", f"{df['price'].max():.2f} ريال")
    
    # الرسوم البيانية
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**تطور الأسعار**")
        price_trend = df.groupby('date')['price'].mean().reset_index()
        fig = px.line(price_trend, x='date', y='price', title='متوسط الأسعار اليومية')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**مقارنة الشركات**")
        company_prices = df.groupby('company')['price'].mean().reset_index()
        fig = px.bar(company_prices, x='company', y='price', title='متوسط الأسعار حسب الشركة')
        st.plotly_chart(fig, use_container_width=True)
    
    # تحليل إضافي
    st.markdown("**تحليل الشكاوى**")
    complaints_by_company = df.groupby('company')['complaint_count'].sum().reset_index()
    fig = px.pie(complaints_by_company, values='complaint_count', names='company', 
                 title='توزيع الشكاوى بين الشركات')
    st.plotly_chart(fig, use_container_width=True)

def display_price_analysis(df):
    st.markdown('<div class="section-header">💰 تحليل الأسعار</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**توزيع الأسعار**")
        fig = px.box(df, x='company', y='price', title='توزيع الأسعار لكل شركة')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**مقارنة المناطق**")
        # استخدام بيانات كاملة للمقارنة الإقليمية
        region_comparison = df.groupby('region')['price'].mean().reset_index()
        fig = px.bar(region_comparison, x='region', y='price', title='متوسط الأسعار حسب المنطقة')
        st.plotly_chart(fig, use_container_width=True)
    
    # تحليل الانحراف المعياري
    st.markdown("**تحليل استقرار الأسعار**")
    price_stability = df.groupby('company')['price'].std().reset_index()
    price_stability = price_stability.sort_values('price', ascending=False)
    
    fig = px.bar(price_stability, x='company', y='price', 
                 title='الانحراف المعياري للأسعار (مؤشر عدم الاستقرار)')
    st.plotly_chart(fig, use_container_width=True)

def display_anomaly_detection(df):
    st.markdown('<div class="section-header">🔍 كشف الشذوذ</div>', unsafe_allow_html=True)
    
    # كشف الشذوذ المبسط
    anomaly_data = detect_anomalies_simple(df)
    anomalies = anomaly_data[anomaly_data['is_anomaly'] == True]
    
    if not anomalies.empty:
        st.markdown(f'<div class="danger-box">🚨 تم كشف {len(anomalies)} حالة شاذة</div>', unsafe_allow_html=True)
        
        for _, anomaly in anomalies.iterrows():
            st.markdown(f"""
            <div class="warning-box">
                <strong>تنبيه:</strong> {anomaly['company']} - {anomaly['product']}<br>
                <strong>السعر:</strong> {anomaly['price']} ريال | 
                <strong>التاريخ:</strong> {anomaly['date'].strftime('%Y-%m-%d')}
            </div>
            """, unsafe_allow_html=True)
        
        # رسم بياني للشذوذ
        fig = px.scatter(anomaly_data, x='date', y='price', color='is_anomaly',
                        title='كشف الشذوذ في الأسعار (النقاط الحمراء تمثل شذوذ)',
                        color_discrete_map={True: 'red', False: 'blue'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown('<div class="warning-box">✅ لا توجد حالات شذوذ في الفترة المحددة</div>', unsafe_allow_html=True)
    
    # إحصائيات الشذوذ
    st.markdown("**إحصائيات الشذوذ**")
    if not anomalies.empty:
        anomaly_stats = anomalies.groupby('company').size().reset_index(name='anomaly_count')
        fig = px.bar(anomaly_stats, x='company', y='anomaly_count', 
                     title='عدد حالات الشذوذ لكل شركة')
        st.plotly_chart(fig, use_container_width=True)

def display_reports(df):
    st.markdown('<div class="section-header">📋 التقارير</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**تقرير أداء الشركات**")
        company_report = df.groupby('company').agg({
            'price': ['mean', 'std', 'min', 'max'],
            'complaint_count': 'sum',
            'market_share': 'mean'
        }).round(2)
        
        # تبسيط الأعمدة المتعددة المستويات
        company_report.columns = ['_'.join(col).strip() for col in company_report.columns.values]
        st.dataframe(company_report)
    
    with col2:
        st.markdown("**مؤشرات الأداء**")
        
        metrics = {
            'إجمالي الحركات': len(df),
            'نطاق الأسعار': f"{df['price'].min():.2f} - {df['price'].max():.2f} ريال",
            'متوسط الشكاوى': f"{df['complaint_count'].mean():.1f}",
            'أعلى حصة سوق': f"{df['market_share'].max():.1f}%",
            'أدنى حصة سوق': f"{df['market_share'].min():.1f}%"
        }
        
        for metric, value in metrics.items():
            st.metric(metric, value)
    
    # تقرير تفاعلي
    st.markdown("**تقرير تحليلي تفاعلي**")
    
    selected_metric = st.selectbox("اختر المقياس:", ['price', 'complaint_count', 'market_share'])
    
    fig = px.scatter(df, x='date', y=selected_metric, color='company',
                    title=f'تطور {selected_metric} مع الزمن',
                    hover_data=['price', 'complaint_count'])
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()

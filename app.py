import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from sklearn.ensemble import IsolationForest
from competition_data import CompetitionDataGenerator, get_analysis_insights, get_statistical_summary

# إعداد صفحة Streamlit
st.set_page_config(page_title="منصة ذكاء المنافسة", page_icon="📊", layout="wide")

# تنسيق CSS
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #1f77b4; text-align: center; margin-bottom: 2rem; font-weight: bold;}
    .section-header {font-size: 1.5rem; color: #2e86ab; margin: 1rem 0; border-right: 5px solid #2e86ab; padding-right: 10px;}
    .metric-card {background-color: #f0f2f6; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-right: 4px solid #2e86ab;}
    .warning-card {background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 10px; margin: 10px 0;}
    .danger-card {background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 10px; margin: 10px 0;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    generator = CompetitionDataGenerator()
    return generator.generate_comprehensive_data()

class CompetitionPlatform:
    def __init__(self):
        self.data = load_data()
        self.insights = get_analysis_insights(self.data)
        self.summary = get_statistical_summary(self.data)
    
    def detect_anomalies(self, df):
        try:
            prices = df['price'].values.reshape(-1, 1)
            model = IsolationForest(contamination=0.1, random_state=42)
            df['anomaly_score'] = model.fit_predict(prices)
            df['is_anomaly'] = df['anomaly_score'] == -1
            return df
        except Exception as e:
            st.error(f"خطأ في كشف الشذوذ: {e}")
            return df
    
    def calculate_hhi_index(self, df):
        try:
            market_shares = df.groupby('company')['market_share'].mean()
            hhi = (market_shares ** 2).sum()
            return hhi
        except:
            return 0

def main():
    st.markdown('<div class="main-header">🏢 منصة ذكاء المنافسة - الهيئة العامة للمنافسة</div>', unsafe_allow_html=True)
    
    platform = CompetitionPlatform()
    
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3063/3063812.png", width=100)
        st.markdown("### إعدادات التحليل")
        analysis_type = st.selectbox("نوع التحليل:", ["نظرة عامة", "الرؤى التحليلية", "تحليل السيناريوهات", "كشف الشذوذ", "تقارير متقدمة"])
        selected_product = st.selectbox("اختر المنتج:", platform.data['product'].unique())
        selected_region = st.selectbox("اختر المنطقة:", platform.data['region'].unique())
    
    filtered_data = platform.data[(platform.data['product'] == selected_product) & (platform.data['region'] == selected_region)]
    
    if analysis_type == "نظرة عامة":
        display_overview(platform, filtered_data)
    elif analysis_type == "الرؤى التحليلية":
        display_insights(platform)
    elif analysis_type == "تحليل السيناريوهات":
        display_scenario_analysis(platform)
    elif analysis_type == "كشف الشذوذ":
        display_anomaly_detection(platform, filtered_data)
    else:
        display_advanced_reports(platform, filtered_data)

def display_overview(platform, filtered_data):
    st.markdown('<div class="section-header">📈 النظرة العامة الشاملة</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("متوسط السعر", f"{filtered_data['price'].mean():.2f} ريال")
    with col2: st.metric("إجمالي الشكاوى", filtered_data['complaint_count'].sum())
    with col3: st.metric("مؤشر تركيز السوق", f"{platform.calculate_hhi_index(filtered_data):.0f}")
    with col4: st.metric("عدد السيناريوهات", filtered_data['scenario_type'].nunique())
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.scatter(filtered_data, x='date', y='price', color='scenario_type', title='تطور الأسعار مع أنواع السيناريوهات')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        scenario_counts = filtered_data['scenario_type'].value_counts()
        fig = px.pie(values=scenario_counts.values, names=scenario_counts.index, title='توزيع أنواع السيناريوهات')
        st.plotly_chart(fig, use_container_width=True)

def display_insights(platform):
    st.markdown('<div class="section-header">🔍 الرؤى والتنبيهات التحليلية</div>', unsafe_allow_html=True)
    for insight in platform.insights:
        if insight['type'] == 'تحذير':
            st.markdown(f'<div class="danger-card">🚨 {insight["title"]}: {insight["description"]}</div>', unsafe_allow_html=True)

def display_scenario_analysis(platform):
    st.markdown('<div class="section-header">🎭 تحليل السيناريوهات</div>', unsafe_allow_html=True)
    scenario_data = platform.data
    st.dataframe(scenario_data.groupby('scenario_type').agg({'price': ['mean', 'count']}).round(2))

def display_anomaly_detection(platform, filtered_data):
    st.markdown('<div class="section-header">🔎 كشف الشذوذ والمخالفات</div>', unsafe_allow_html=True)
    anomaly_data = platform.detect_anomalies(filtered_data)
    anomalies = anomaly_data[anomaly_data['is_anomaly'] == True]
    if not anomalies.empty:
        st.markdown(f"### 🚨 تم كشف {len(anomalies)} حالة شاذة")
        for _, anomaly in anomalies.head(5).iterrows():
            st.markdown(f'<div class="danger-card">تنبيه: {anomaly["company"]} - {anomaly["product"]} بسعر {anomaly["price"]} ريال</div>', unsafe_allow_html=True)

def display_advanced_reports(platform, filtered_data):
    st.markdown('<div class="section-header">📋 التقارير المتقدمة</div>', unsafe_allow_html=True)
    st.dataframe(filtered_data.groupby('company').agg({'price': 'mean', 'complaint_count': 'sum', 'market_share': 'mean'}).round(2))

if __name__ == "__main__":
    main()

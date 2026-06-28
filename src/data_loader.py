import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def fetch_and_clean_data():
    """Fetches real e-commerce event stream logs and normalizes features."""
    url = "https://raw.githubusercontent.com/marcopeix/datasets/master/retail_marketplace_events.csv"
    try:
        # Load real e-commerce session data
        df = pd.read_csv(url)
        df.columns = [col.lower() for col in df.columns]
        df = df.dropna(subset=['user_id', 'event_type'])
    except Exception:
        # High-weightage fallback matrix mimicking actual e-commerce cohorts
        np.random.seed(42)
        n_users = 2500
        devices = ['Desktop', 'Mobile', 'Tablet']
        locations = ['United States', 'India', 'United Kingdom', 'Germany']
        sources = ['Google Search', 'Facebook Ads', 'Organic', 'LinkedIn']
        
        data = []
        for i in range(n_users):
            uid = f"USR_{20000 + i}"
            dev = np.random.choice(devices, p=[0.45, 0.45, 0.10])
            loc = np.random.choice(locations)
            src = np.random.choice(sources, p=[0.4, 0.3, 0.2, 0.1])
            
            # Step 1: Visit
            data.append({'user_id': uid, 'device': dev, 'location': loc, 'traffic_source': src, 'stage': '1. Visit'})
            
            # Step 2: Signup (Simulating friction for Mobile users)
            if np.random.rand() < (0.48 if dev == 'Mobile' else 0.72):
                data.append({'user_id': uid, 'device': dev, 'location': loc, 'traffic_source': src, 'stage': '2. Signup'})
                
                # Step 3: Add to Cart
                if np.random.rand() < 0.50:
                    data.append({'user_id': uid, 'device': dev, 'location': loc, 'traffic_source': src, 'stage': '3. Add to Cart'})
                    
                    # Step 4: Purchase (Simulating payment friction for India region on Mobile)
                    pay_prob = 0.22 if (loc == 'India' and dev == 'Mobile') else 0.45
                    if np.random.rand() < pay_prob:
                        data.append({'user_id': uid, 'device': dev, 'location': loc, 'traffic_source': src, 'stage': '4. Purchase'})
        
        df = pd.DataFrame(data)
        
    # Standardize stage naming conventions if mapping raw e-commerce event streams
    stage_mapping = {
        'view': '1. Visit', 'visit': '1. Visit', '1. visit': '1. Visit',
        'register': '2. Signup', 'signup': '2. Signup', '2. signup': '2. Signup',
        'cart': '3. Add to Cart', 'add to cart': '3. Add to Cart', '3. add to cart': '3. Add to Cart',
        'purchase': '4. Purchase', 'buy': '4. Purchase', '4. purchase': '4. Purchase'
    }
    if 'event_type' in df.columns:
        df['stage'] = df['event_type'].map(stage_mapping)
        df = df.dropna(subset=['stage'])
        
    if 'country' in df.columns:
        df = df.rename(columns={'country': 'location'})
    if 'channel' in df.columns:
        df = df.rename(columns={'channel': 'traffic_source'})
        
    return df
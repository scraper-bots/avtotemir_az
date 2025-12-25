#!/usr/bin/env python3
"""
Business Analytics Dashboard for Avtotemir Masters Dataset
Generates actionable business insights through data visualizations
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
import re

warnings.filterwarnings('ignore')

# Set professional style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Create output directory
import os
OUTPUT_DIR = 'charts'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load data
print("Loading dataset...")
df = pd.read_csv('avtotemir_masters.csv')
print(f"Loaded {len(df)} service provider records\n")

# Data preprocessing
print("Preprocessing data...")

# Parse experience (extract years)
def extract_years(exp_str):
    if pd.isna(exp_str):
        return None
    match = re.search(r'(\d+)', str(exp_str))
    return int(match.group(1)) if match else None

df['experience_years'] = df['experience'].apply(extract_years)

# Parse location to extract district
df['district'] = df['location'].str.split(',').str[-1].str.strip()

# Parse added_date
df['added_date'] = pd.to_datetime(df['added_date'], errors='coerce')
df['year_joined'] = df['added_date'].dt.year
df['month_joined'] = df['added_date'].dt.to_period('M')

# Create rating categories
df['rating_category'] = pd.cut(df['rating'],
                                bins=[0, 3.5, 4.0, 4.5, 5.0],
                                labels=['Below Average', 'Average', 'Good', 'Excellent'])

# Experience categories
df['experience_category'] = pd.cut(df['experience_years'],
                                     bins=[0, 5, 10, 20, 50],
                                     labels=['Entry (0-5 yrs)', 'Mid (6-10 yrs)',
                                            'Senior (11-20 yrs)', 'Expert (20+ yrs)'])

# Views categories
df['visibility_level'] = pd.cut(df['views'],
                                 bins=[0, 1000, 5000, 20000, 100000],
                                 labels=['Low', 'Medium', 'High', 'Very High'])

print("Data preprocessing complete\n")


# ============================================================================
# CHART 1: Geographic Market Distribution
# ============================================================================
print("Generating Chart 1: Geographic Market Distribution...")

fig, ax = plt.subplots(figsize=(14, 8))

district_counts = df['district'].value_counts().head(15)

bars = ax.barh(range(len(district_counts)), district_counts.values, color='#2E86AB')
ax.set_yticks(range(len(district_counts)))
ax.set_yticklabels(district_counts.index, fontsize=11)
ax.set_xlabel('Number of Service Providers', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Districts by Service Provider Concentration\nWhere is the market most competitive?',
             fontsize=14, fontweight='bold', pad=20)

# Add value labels
for i, (idx, value) in enumerate(district_counts.items()):
    ax.text(value + 10, i, f'{value:,}', va='center', fontsize=10, fontweight='bold')

ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/01_geographic_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 1 saved\n")


# ============================================================================
# CHART 2: Service Specialization Mix
# ============================================================================
print("Generating Chart 2: Service Specialization Analysis...")

fig, ax = plt.subplots(figsize=(14, 10))

position_counts = df['position'].value_counts().head(20)

bars = ax.barh(range(len(position_counts)), position_counts.values,
               color=sns.color_palette("viridis", len(position_counts)))
ax.set_yticks(range(len(position_counts)))
ax.set_yticklabels(position_counts.index, fontsize=10)
ax.set_xlabel('Number of Specialists', fontsize=12, fontweight='bold')
ax.set_title('Top 20 Service Specializations\nWhich skills are most represented in the market?',
             fontsize=14, fontweight='bold', pad=20)

# Add value labels
for i, (idx, value) in enumerate(position_counts.items()):
    ax.text(value + 2, i, f'{value}', va='center', fontsize=9)

ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/02_service_specializations.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 2 saved\n")


# ============================================================================
# CHART 3: Car Brand Coverage Analysis
# ============================================================================
print("Generating Chart 3: Car Brand Support Coverage...")

# Count how many providers support "Bütün markalar" vs specific brands
brand_type = df['car_brands'].apply(lambda x: 'All Brands' if 'Bütün markalar' in str(x) else 'Specific Brands')
brand_distribution = brand_type.value_counts()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Bar chart
colors = ['#06D6A0', '#118AB2']
bars = ax1.bar(brand_distribution.index, brand_distribution.values, color=colors, width=0.6)
ax1.set_ylabel('Number of Service Providers', fontsize=12, fontweight='bold')
ax1.set_title('Market Coverage Strategy\nGeneralists vs Specialists',
              fontsize=13, fontweight='bold', pad=15)
ax1.grid(axis='y', alpha=0.3)

for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}\n({height/len(df)*100:.1f}%)',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

# Specific brand analysis (for those who specify)
specific_brands_df = df[df['car_brands'].str.contains('Mercedes|BMW|Toyota|Lexus|Nissan|Hyundai|Kia',
                                                       case=False, na=False)]

brand_mentions = {}
for brands in specific_brands_df['car_brands'].dropna():
    for brand in ['Mercedes', 'BMW', 'Toyota', 'Lexus', 'Nissan', 'Hyundai', 'Kia', 'Audi', 'Volkswagen', 'Honda']:
        if brand.lower() in brands.lower():
            brand_mentions[brand] = brand_mentions.get(brand, 0) + 1

if brand_mentions:
    top_brands = pd.Series(brand_mentions).sort_values(ascending=False).head(10)

    bars2 = ax2.barh(range(len(top_brands)), top_brands.values,
                     color=sns.color_palette("rocket", len(top_brands)))
    ax2.set_yticks(range(len(top_brands)))
    ax2.set_yticklabels(top_brands.index, fontsize=11)
    ax2.set_xlabel('Number of Specialists', fontsize=12, fontweight='bold')
    ax2.set_title('Top 10 Brands with Dedicated Specialists\nWhich brands have focused expertise?',
                  fontsize=13, fontweight='bold', pad=15)

    for i, (idx, value) in enumerate(top_brands.items()):
        ax2.text(value + 1, i, f'{value}', va='center', fontsize=10)

    ax2.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/03_brand_coverage.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 3 saved\n")


# ============================================================================
# CHART 4: Experience Distribution Analysis
# ============================================================================
print("Generating Chart 4: Experience Distribution...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Experience category distribution
exp_cat_counts = df['experience_category'].value_counts().sort_index()
colors = ['#FFC857', '#E9724C', '#C5283D', '#481D24']

bars = ax1.bar(range(len(exp_cat_counts)), exp_cat_counts.values, color=colors, width=0.6)
ax1.set_xticks(range(len(exp_cat_counts)))
ax1.set_xticklabels(exp_cat_counts.index, fontsize=11, rotation=15, ha='right')
ax1.set_ylabel('Number of Providers', fontsize=12, fontweight='bold')
ax1.set_title('Workforce Experience Distribution\nHow experienced is our service network?',
              fontsize=13, fontweight='bold', pad=15)
ax1.grid(axis='y', alpha=0.3)

for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}\n({height/len(df[df["experience_category"].notna()])*100:.1f}%)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

# Experience histogram
experience_data = df['experience_years'].dropna()
ax2.hist(experience_data, bins=20, color='#6A4C93', alpha=0.7, edgecolor='black')
ax2.axvline(experience_data.median(), color='red', linestyle='--', linewidth=2,
           label=f'Median: {experience_data.median():.0f} years')
ax2.axvline(experience_data.mean(), color='orange', linestyle='--', linewidth=2,
           label=f'Average: {experience_data.mean():.1f} years')
ax2.set_xlabel('Years of Experience', fontsize=12, fontweight='bold')
ax2.set_ylabel('Number of Providers', fontsize=12, fontweight='bold')
ax2.set_title('Detailed Experience Distribution\nWhat is the typical experience level?',
              fontsize=13, fontweight='bold', pad=15)
ax2.legend(fontsize=11)
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/04_experience_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 4 saved\n")


# ============================================================================
# CHART 5: Quality Ratings Analysis
# ============================================================================
print("Generating Chart 5: Service Quality Analysis...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Rating category distribution
rating_cat_counts = df['rating_category'].value_counts().sort_index()
colors_rating = ['#C1121F', '#FCA311', '#4EA8DE', '#06D6A0']

bars = ax1.bar(range(len(rating_cat_counts)), rating_cat_counts.values,
              color=colors_rating, width=0.6)
ax1.set_xticks(range(len(rating_cat_counts)))
ax1.set_xticklabels(rating_cat_counts.index, fontsize=11, rotation=15, ha='right')
ax1.set_ylabel('Number of Providers', fontsize=12, fontweight='bold')
ax1.set_title('Service Provider Quality Distribution\nHow do our providers rate overall?',
              fontsize=13, fontweight='bold', pad=15)
ax1.grid(axis='y', alpha=0.3)

for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}\n({height/len(df[df["rating_category"].notna()])*100:.1f}%)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

# Votes distribution (top providers by votes)
top_voted = df.nlargest(15, 'votes')[['name', 'votes', 'rating']].sort_values('votes')

bars2 = ax2.barh(range(len(top_voted)), top_voted['votes'].values,
                color=sns.color_palette("coolwarm", len(top_voted)))
ax2.set_yticks(range(len(top_voted)))
ax2.set_yticklabels([name[:30] + '...' if len(name) > 30 else name
                     for name in top_voted['name'].values], fontsize=9)
ax2.set_xlabel('Number of Customer Reviews', fontsize=12, fontweight='bold')
ax2.set_title('Top 15 Most Reviewed Providers\nWho has the strongest customer engagement?',
              fontsize=13, fontweight='bold', pad=15)

for i, (idx, row) in enumerate(top_voted.iterrows()):
    ax2.text(row['votes'] + 20, i, f"{row['votes']} (★{row['rating']})",
            va='center', fontsize=9)

ax2.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/05_quality_ratings.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 5 saved\n")


# ============================================================================
# CHART 6: Market Visibility Analysis
# ============================================================================
print("Generating Chart 6: Provider Visibility Analysis...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Visibility level distribution
visibility_counts = df['visibility_level'].value_counts().sort_index()
colors_vis = ['#D62828', '#F77F00', '#FCBF49', '#06D6A0']

bars = ax1.bar(range(len(visibility_counts)), visibility_counts.values,
              color=colors_vis, width=0.6)
ax1.set_xticks(range(len(visibility_counts)))
ax1.set_xticklabels(visibility_counts.index, fontsize=11)
ax1.set_ylabel('Number of Providers', fontsize=12, fontweight='bold')
ax1.set_title('Provider Visibility Levels\nHow visible are providers to customers?',
              fontsize=13, fontweight='bold', pad=15)
ax1.grid(axis='y', alpha=0.3)

for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}\n({height/len(df[df["visibility_level"].notna()])*100:.1f}%)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

# Top viewed providers
top_viewed = df.nlargest(15, 'views')[['name', 'views', 'rating', 'votes']].sort_values('views')

bars2 = ax2.barh(range(len(top_viewed)), top_viewed['views'].values,
                color=sns.color_palette("mako", len(top_viewed)))
ax2.set_yticks(range(len(top_viewed)))
ax2.set_yticklabels([name[:30] + '...' if len(name) > 30 else name
                     for name in top_viewed['name'].values], fontsize=9)
ax2.set_xlabel('Profile Views', fontsize=12, fontweight='bold')
ax2.set_title('Top 15 Most Viewed Provider Profiles\nWho attracts the most customer attention?',
              fontsize=13, fontweight='bold', pad=15)

for i, (idx, row) in enumerate(top_viewed.iterrows()):
    ax2.text(row['views'] + 500, i, f"{row['views']:,}", va='center', fontsize=9)

ax2.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/06_market_visibility.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 6 saved\n")


# ============================================================================
# CHART 7: Platform Growth Trends
# ============================================================================
print("Generating Chart 7: Platform Growth Over Time...")

fig, ax = plt.subplots(figsize=(16, 6))

# Filter valid years and aggregate
year_counts = df[df['year_joined'].notna() & (df['year_joined'] >= 2015) & (df['year_joined'] <= 2025)]['year_joined'].value_counts().sort_index()

if len(year_counts) > 0:
    ax.plot(year_counts.index, year_counts.values, marker='o', linewidth=3,
           markersize=10, color='#2A9D8F')
    ax.fill_between(year_counts.index, year_counts.values, alpha=0.3, color='#2A9D8F')

    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('New Providers Joined', fontsize=12, fontweight='bold')
    ax.set_title('Platform Growth Trajectory\nHow is the provider network expanding over time?',
                fontsize=14, fontweight='bold', pad=20)

    # Add value labels
    for year, count in year_counts.items():
        ax.text(year, count + 5, f'{count}', ha='center', fontsize=10, fontweight='bold')

    ax.grid(alpha=0.3)
    ax.set_xticks(year_counts.index)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/07_platform_growth.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Chart 7 saved\n")
else:
    print("⚠ Insufficient date data for Chart 7\n")


# ============================================================================
# CHART 8: Experience vs Performance Correlation
# ============================================================================
print("Generating Chart 8: Experience vs Service Quality...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Average rating by experience category
exp_rating = df.groupby('experience_category')['rating'].agg(['mean', 'count']).sort_index()

bars = ax1.bar(range(len(exp_rating)), exp_rating['mean'].values,
              color=['#FFC857', '#E9724C', '#C5283D', '#481D24'], width=0.6)
ax1.set_xticks(range(len(exp_rating)))
ax1.set_xticklabels(exp_rating.index, fontsize=11, rotation=15, ha='right')
ax1.set_ylabel('Average Rating', fontsize=12, fontweight='bold')
ax1.set_ylim(0, 5)
ax1.axhline(y=df['rating'].mean(), color='red', linestyle='--', linewidth=2,
           label=f'Overall Average: {df["rating"].mean():.2f}')
ax1.set_title('Average Rating by Experience Level\nDoes experience correlate with quality?',
              fontsize=13, fontweight='bold', pad=15)
ax1.legend(fontsize=10)
ax1.grid(axis='y', alpha=0.3)

for bar, (idx, row) in zip(bars, exp_rating.iterrows()):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.05,
            f'{height:.2f}\n(n={int(row["count"])})',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

# Scatter plot: Experience vs Votes (engagement)
scatter_data = df[df['experience_years'].notna() & (df['votes'] > 0)]
scatter = ax2.scatter(scatter_data['experience_years'], scatter_data['votes'],
                     c=scatter_data['rating'], cmap='RdYlGn',
                     s=100, alpha=0.6, edgecolors='black', linewidth=0.5)

ax2.set_xlabel('Years of Experience', fontsize=12, fontweight='bold')
ax2.set_ylabel('Number of Customer Reviews', fontsize=12, fontweight='bold')
ax2.set_title('Experience vs Customer Engagement\nDo experienced providers get more reviews?',
              fontsize=13, fontweight='bold', pad=15)

cbar = plt.colorbar(scatter, ax=ax2)
cbar.set_label('Rating', fontsize=11, fontweight='bold')
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/08_experience_performance.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 8 saved\n")


# ============================================================================
# CHART 9: Engagement Metrics Analysis
# ============================================================================
print("Generating Chart 9: Customer Engagement Analysis...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Views vs Votes correlation
engagement_data = df[(df['views'] > 0) & (df['votes'] > 0)]
engagement_sample = engagement_data.sample(min(500, len(engagement_data)))

scatter1 = ax1.scatter(engagement_sample['views'], engagement_sample['votes'],
                      c=engagement_sample['rating'], cmap='viridis',
                      s=80, alpha=0.6, edgecolors='black', linewidth=0.5)

ax1.set_xlabel('Profile Views', fontsize=12, fontweight='bold')
ax1.set_ylabel('Customer Reviews', fontsize=12, fontweight='bold')
ax1.set_title('Profile Views vs Customer Reviews\nDoes visibility drive engagement?',
              fontsize=13, fontweight='bold', pad=15)
ax1.set_xscale('log')
ax1.set_yscale('log')
cbar1 = plt.colorbar(scatter1, ax=ax1)
cbar1.set_label('Rating', fontsize=11, fontweight='bold')
ax1.grid(alpha=0.3)

# Review conversion rate by visibility level
conversion_by_visibility = df.groupby('visibility_level').agg({
    'votes': 'sum',
    'views': 'sum'
}).dropna()

conversion_by_visibility['conversion_rate'] = (conversion_by_visibility['votes'] /
                                                conversion_by_visibility['views'] * 100)

bars2 = ax2.bar(range(len(conversion_by_visibility)),
               conversion_by_visibility['conversion_rate'].values,
               color=['#D62828', '#F77F00', '#FCBF49', '#06D6A0'], width=0.6)
ax2.set_xticks(range(len(conversion_by_visibility)))
ax2.set_xticklabels(conversion_by_visibility.index, fontsize=11)
ax2.set_ylabel('Review Conversion Rate (%)', fontsize=12, fontweight='bold')
ax2.set_title('Review Conversion by Visibility Level\nWhich visibility level drives best engagement?',
              fontsize=13, fontweight='bold', pad=15)
ax2.grid(axis='y', alpha=0.3)

for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.2f}%',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/09_engagement_metrics.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 9 saved\n")


# ============================================================================
# CHART 10: District Performance Comparison
# ============================================================================
print("Generating Chart 10: District-Level Performance Analysis...")

fig, ax = plt.subplots(figsize=(14, 8))

# Get top 12 districts and their metrics
top_districts = df['district'].value_counts().head(12).index
district_metrics = df[df['district'].isin(top_districts)].groupby('district').agg({
    'rating': 'mean',
    'votes': 'sum',
    'views': 'sum',
    'id': 'count'
}).rename(columns={'id': 'provider_count'})

district_metrics = district_metrics.sort_values('rating', ascending=True)

# Create horizontal bar chart
bars = ax.barh(range(len(district_metrics)), district_metrics['rating'].values,
              color=sns.color_palette("RdYlGn", len(district_metrics)))
ax.set_yticks(range(len(district_metrics)))
ax.set_yticklabels(district_metrics.index, fontsize=11)
ax.set_xlabel('Average Rating', fontsize=12, fontweight='bold')
ax.set_xlim(0, 5)
ax.axvline(x=df['rating'].mean(), color='red', linestyle='--', linewidth=2,
          label=f'Platform Average: {df["rating"].mean():.2f}')
ax.set_title('Average Service Quality by Top Districts\nWhich districts deliver the best service?',
             fontsize=14, fontweight='bold', pad=20)
ax.legend(fontsize=10)
ax.grid(axis='x', alpha=0.3)

for i, (district, row) in enumerate(district_metrics.iterrows()):
    ax.text(row['rating'] + 0.05, i,
           f"{row['rating']:.2f} ({int(row['provider_count'])} providers)",
           va='center', fontsize=9)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/10_district_performance.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 10 saved\n")


# ============================================================================
# Summary Statistics
# ============================================================================
print("\n" + "="*70)
print("BUSINESS INSIGHTS SUMMARY")
print("="*70)

print(f"\nTotal Service Providers: {len(df):,}")
print(f"Average Rating: {df['rating'].mean():.2f} / 5.0")
print(f"Median Experience: {df['experience_years'].median():.0f} years")
print(f"Total Customer Reviews: {df['votes'].sum():,}")
print(f"Total Profile Views: {df['views'].sum():,}")
print(f"\nTop District: {df['district'].value_counts().index[0]} ({df['district'].value_counts().values[0]} providers)")
print(f"Most Common Specialty: {df['position'].value_counts().index[0]} ({df['position'].value_counts().values[0]} specialists)")
print(f"Providers Supporting All Brands: {len(df[df['car_brands'].str.contains('Bütün markalar', na=False)]):,} ({len(df[df['car_brands'].str.contains('Bütün markalar', na=False)])/len(df)*100:.1f}%)")

print("\n" + "="*70)
print("All charts have been generated successfully in the 'charts/' directory")
print("="*70)

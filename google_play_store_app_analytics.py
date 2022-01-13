import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

pd.options.display.float_format = '{:,.2f}'.format

df_apps = pd.read_csv('apps.csv')

df_apps = df_apps.drop(columns=['Last_Updated', 'Android_Ver'])
df_apps_clean = df_apps.dropna()
duplicated_rows = df_apps_clean[df_apps_clean.duplicated(subset=['App', 'Type', 'Price'])]
df_apps_clean = df_apps_clean.drop_duplicates(subset=['App', 'Type', 'Price'])

# Content Ratings

ratings = df_apps_clean.Content_Rating.value_counts()
fig = px.pie(labels=ratings.index, values=ratings.values, names=ratings.index, hole=0.6)
fig.update_traces(textposition='inside', textinfo='percent')
fig.show()
# plt.bar(ratings.index, ratings.values)

# Number of Installs

df_apps_clean.Installs = df_apps_clean.Installs.astype(str).str.replace(',', "")
df_apps_clean.Installs = pd.to_numeric(df_apps_clean.Installs)

df_apps_clean.Price = df_apps_clean.Price.astype(str).str.lstrip('$')
df_apps_clean.Price = pd.to_numeric(df_apps_clean.Price)

# Most Expensive Apps

df_apps_clean = df_apps_clean[df_apps_clean.Price < 250]
df_value = df_apps_clean
d = df_value.Installs.mul(df_value.Price)
df_value.insert(1, 'Income', d)

# Analysing App Categories

best = df_value
c = df_value.groupby(["Category"]).sum()
best = best.Category.value_counts()
best = pd.DataFrame({'Category': best.index, 'count': best.values})

merged_df = pd.merge(c, best, on='Category')
merged_df = merged_df[['Category', 'Installs', 'count']]
merged_df['Rate']=merged_df.Installs/merged_df['count']
merged_df = merged_df.sort_values('Rate', ascending=True)

h_bar = px.bar(y=merged_df['Category'], x=merged_df['Rate'], orientation='h')
h_bar.update_layout(xaxis_title='Number of Downloads', yaxis_title='Category')
h_bar.show()


# Downloads vs. Competition

scat = px.scatter(x=merged_df['count'], y=merged_df['Installs'], color=merged_df['Installs'], title='Category Concentration', hover_name=merged_df['Category'], log_y=True, size=merged_df['count'])
scat.update_layout(xaxis_title='Number of Apps', yaxis_title='Installs')
scat.show()

# Genres

stack = df_value.Genres.str.split(';', expand=True).stack()
num_genres = stack.value_counts()

# Competition in Genres

bar = px.bar(x=num_genres.index[:15], y=num_genres.values[:15], title='Top Genres', hover_name=num_genres.index[:15], color=num_genres.values[:15], color_continuous_scale='Agsunset')
bar.update_layout(xaxis_title='Genre', yaxis_title='Number of Apps', coloraxis_showscale=False)
bar.show()

# Free vs. Paid Apps per Category

df_free_vs_paid = df_apps_clean.groupby(["Category", "Type"], as_index=False).agg({'App': pd.Series.count})

g_bar = px.bar(df_free_vs_paid, x='Category', y='App', title='Free vs Paid Apps by Category', color='Type', barmode='group')
g_bar.update_layout(xaxis_title='Category', yaxis_title='Number of Apps', xaxis={'categoryorder':'total descending'}, yaxis=dict(type='log'))
g_bar.show()

# Lost Downloads for Paid Apps

df_free_vs_paid_2 = df_apps_clean.groupby("Type", as_index=False).agg({'Installs': pd.Series.count})
fig = px.box(df_apps_clean, x="Type", y="Installs", color='Type', points="all", notched=True, title='How Many Downloads are Paid Apps Giving Up?')
fig.update_yaxes(type='log')
fig.show()

# Revenue by App Category

df_apps_clean['Income']=df_apps_clean['Installs']*df_apps_clean['Price']
df_apps_clean.Type.value_counts()
df_paid_apps = df_apps_clean[df_apps_clean['Type']=='Paid']
fig = px.box(df_paid_apps, x="Category", y="Income", title='How Much Can Paid Apps Earn?')
fig.update_layout(xaxis_title='Category', yaxis_title='Paid App Revenue', xaxis={'categoryorder':'min ascending'}, yaxis=dict(type='log'))
fig.show()

# Paid App Pricing Strategies by Category

fig = px.box(df_paid_apps, x="Category", y="Price", title='Price per Category')
fig.update_layout(xaxis_title='Category', yaxis_title='Paid App Price', xaxis={'categoryorder':'max descending'}, yaxis=dict(type='log'))
fig.show()

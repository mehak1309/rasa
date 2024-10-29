import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px
import math

data_file = '/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngram/scripts/lang_bigrams/bigram_count.csv'

df = pd.read_csv(data_file)


fig = go.Figure(data=[
    go.Bar(name='Indic Voices', x=df['languages'], y=df['indic_voices'], marker_color='#FFA15A'),
    go.Bar(name='IndicTTS', x=df['languages'], y=df['indic_tts'], marker_color='#AB63FA')
])

# Calculate tick values and labels automatically
max_y_value = max(df['indic_voices'].max(), df['indic_tts'].max())
tick_interval = max_y_value / 5  # You can adjust the number of ticks
print(tick_interval)
tick_values = [i for i in range(0, math.ceil(max_y_value + tick_interval), math.ceil(tick_interval))]

# Function to format tick labels
def format_tick_label(value):
    if value % 1000 != 0:
        return f'{value / 1000:.1f}k' 
    else:
         f'{value // 1000}k'
    if value==0:
        return '0'
    # return str(value)

tick_labels = [format_tick_label(value) for value in tick_values]

fig.update_layout(
    barmode='group',
    template='plotly_white',
    showlegend=True,
    font=dict(family="Times New Roman", size=32),
    xaxis=dict(title='Language →', titlefont=dict(size=32), showgrid=True, minor_griddash='solid'),
    yaxis=dict(
        title='Unique Bigram →',
        titlefont=dict(size=32),
        tickvals=tick_values,
        ticktext=tick_labels
    ),
    legend=dict(
        x=0.85,
        y=1,
        bgcolor='rgba(255, 255, 255, 0)',
    ),
    margin=dict(l=50, r=40, t=40, b=40),
    bargap=0.4)

file_path = "/nlsasfs/home/ai4bharat/praveens/ttsteam/repos/ngram/scripts/lang_bigrams/bigrams_barplot.png"
os.makedirs(os.path.dirname(file_path), exist_ok=True)
fig.write_image(file_path, width=1900, height=800)

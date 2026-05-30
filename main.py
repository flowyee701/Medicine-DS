from fastapi import FastAPI
import pandas as pd
import json
import plotly.express as px

data = pd.read_csv("data/processed/cleaned_ecg_dataset.csv")

app = FastAPI()


@app.get("/")
def read_root():
    return 'Hello'


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

@app.get("/heart/{heart_rate_min}_{heart_rate_max}")
def filter_hr(heart_rate_min : int, heart_rate_max : int | None = None):
    res = data[data['heart_rate'].between(heart_rate_min, heart_rate_max)].to_json(force_ascii=False)
    return json.dumps(json.loads(res), indent=4)

@app.get("/elaxis")
def qrs_to_axis():
    sample = data.dropna(subset=['qrs_axis', 'qrs_duration']).sample(4000, random_state=42)
    fig = px.scatter_polar(
        sample,
        r='qrs_duration',
        theta='qrs_axis',
        color='axis_deviation',
        category_orders={'axis_deviation' : ['normal', 'left_deviation', 'right_deviation']},
        color_discrete_map={
            'normal':          '#2ca02c',
            'left_deviation':  '#d62728',
            'right_deviation': '#1f77b4',
        },
        opacity=0.45,
        hover_data={'age': True, 'heart_rate': True, 'abnormal_flag': True,
                'qrs_axis': ':.0f', 'qrs_duration': ':.0f'},
        title=('Электрическая ось сердца vs длительность QRS<br>'
           '<sup>угол = ось (°), радиус = QRS (мс), цвет = тип девиации оси</sup>'),
    )
    fig.update_traces(marker=dict(size=4))
    fig.update_layout(
        polar=dict(
            angularaxis=dict(
                direction='clockwise',
                rotation=0,
                tickmode='array',
                tickvals=[-180, -150, -120, -90, -60, -30, 0, 30, 60, 90, 120, 150],
                ticktext=['±180°','-150°','-120°','-90°','-60°','-30°',
                      '0°','+30°','+60°','+90°','+120°','+150°'],
            ),
            radialaxis=dict(title='QRS Duration (мс)', range=[50, 200]),
        ),
        legend_title_text='Axis deviation',
        width=800, height=700,
    )
    return json.loads(fig.to_json())
from fastapi import FastAPI
import pandas as pd
import json
import plotly.express as px

data = pd.read_csv("data/processed/cleaned_ecg_dataset.csv")

app = FastAPI()


@app.get("/")
def read_root():
    return 'Hello'

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
            'normal':          "#279727",
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

@app.get("/hypo3")
def hypo3():
    samp = data.sample(5000, random_state=42)

    def qt_status(x):
        b = x['qtc_bazett'] > 450
        f = x['qtc_fridericia'] > 450
        if b and f: return "Оба"
        if b: return "Bazett"
        if f: return "Fridericia"
        return "Ни один"

    samp['qt_status'] = samp.apply(qt_status, axis=1)

    fig = px.scatter(
        samp, x='qtc_fridericia', y='qtc_bazett',
        color='heart_rate', color_continuous_scale='RdYlBu_r', opacity=0.7,
        symbol="qt_status",
        symbol_map={
            "Оба" : "circle",
            "Bazett" : "square",
            "Fridericia" : "x",
            "Ни один" : "diamond"
        },
        labels={"qtc_fridericia": "QTc Fridericia (мс)",
                "qtc_bazett": "QTc Bazett (мс)", "heart_rate": "ЧСС"},
        title=("Bazett против Fridericia: одна ЭКГ — разный QTc"),
    )
    fig.add_shape(type="line", x0=300, y0=300, x1=600, y1=600,
                line=dict(dash="dash", color="black"))
    fig.add_hline(y=450, line_dash="dot", line_color="grey")
    fig.add_vline(x=450, line_dash="dot", line_color="grey")
    fig.update_layout(width=800, height=750)
    return json.loads(fig.to_json())


@app.get("/ageheart/{item1}_{item2}_{item3}_{item4}")
def age_heart_distr(item1 : int,item2 : int,item3 : int,item4 : int | None=None):
    filtered_data = data[
        (data["age"] >= item1) & (data["age"] <= item2) &
        (data["heart_rate"] >= item3) & (data["heart_rate"] <= item4)
    ]

    fig = px.scatter(
        filtered_data,
        x="age",
        y="heart_rate",
        title="",
        labels={
            "age": "Age",
            "heart_rate": "Heart rate"
        },
        hover_data=filtered_data.columns
    )

    return json.loads(fig.to_json())
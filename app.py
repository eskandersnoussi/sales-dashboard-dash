"""Sales performance dashboard built with Dash and Plotly.

Run:  pip install -r requirements.txt
      python app.py
Then open http://127.0.0.1:8050 in your browser.

All data is fictional (see make_data.py).
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, ctx, dash_table, dcc, html
from dash.dash_table.Format import Format, Group, Scheme, Sign, Symbol

# ---------- data ----------
DATA = Path(__file__).parent / "data" / "sales.csv"
df = pd.read_csv(DATA, parse_dates=["month"])
df["year"] = df["month"].dt.year
YEARS = sorted(df["year"].unique())
REGIONS = sorted(df["region"].unique())
CATEGORIES = sorted(df["category"].unique())

# ---------- style ----------
ACCENT = "#1F8A7A"
ACCENT_LIGHT = "#9FD3C9"
NAVY = "#16323F"
MUTED = "#5B6770"
GRID = "#E3E8EB"
GREY = "#B8C2C9"
FONT = "Inter, Segoe UI, Arial, sans-serif"


def nok(v):
    return f"{v:,.0f}".replace(",", " ")


def nok_short(v):
    if abs(v) >= 1e6:
        return f"NOK {v/1e6:.1f}M"
    if abs(v) >= 1e3:
        return f"NOK {v/1e3:.0f}k"
    return f"NOK {v:.0f}"


def base_layout(fig, height=320):
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family=FONT, size=12, color=NAVY),
        hoverlabel=dict(bgcolor="white", font_family=FONT, bordercolor=GRID),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0),
        bargap=0.35,
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, ticks="")
    fig.update_yaxes(gridcolor=GRID, zeroline=False, ticks="")
    return fig


def filtered(year, regions, categories):
    d = df[df["region"].isin(regions or REGIONS) & df["category"].isin(categories or CATEGORIES)]
    return d[d["year"] == year], d[d["year"] == year - 1]


# ---------- layout ----------
def kpi_card(kpi_id, label):
    return html.Div(className="card kpi", children=[
        html.Div(label, className="kpi-label"),
        html.Div("–", id=f"{kpi_id}-value", className="kpi-value"),
        html.Div("", id=f"{kpi_id}-change", className="kpi-change"),
    ])


def chart_card(title, note, graph_id, extra_class=""):
    return html.Div(className=f"card {extra_class}", children=[
        html.Div(title, className="card-title"),
        html.Div(note, className="card-note"),
        dcc.Graph(id=graph_id, config={"displayModeBar": False}),
    ])


app = Dash(__name__, title="Sales performance",
           external_stylesheets=["https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"])

server = app.server  # used by gunicorn when the app is deployed

app.layout = html.Div(className="page", children=[
    html.Div(className="header", children=[
        html.Div([
            html.H1("Sales performance"),
            html.Div("Fjord Outdoor AS  ·  built with Python, Dash and Plotly  ·  fictional sample data", className="subtitle"),
        ]),
        html.Div(className="filters", children=[
            html.Div([html.Label("Year"), dcc.Dropdown(YEARS, YEARS[-1], id="year", clearable=False, className="dd dd-year")]),
            html.Div([html.Label("Region"), dcc.Dropdown(REGIONS, [], id="region", multi=True, placeholder="All regions", className="dd")]),
            html.Div([html.Label("Category"), dcc.Dropdown(CATEGORIES, [], id="category", multi=True, placeholder="All categories", className="dd")]),
            html.Button("Reset", id="reset", className="reset"),
        ]),
    ]),
    html.Div(className="kpis", children=[
        kpi_card("rev", "Revenue"),
        kpi_card("units", "Units sold"),
        kpi_card("gp", "Gross profit"),
        kpi_card("gm", "Gross margin"),
    ]),
    html.Div(className="row row-wide", children=[
        chart_card("Revenue by month", "Selected year as bars, previous year as line", "monthly"),
        chart_card("Revenue by category", "Share of total and change vs last year · click a bar to filter", "by-category"),
    ]),
    html.Div(className="row row-split", children=[
        chart_card("Revenue by region", "Selected year", "by-region"),
        html.Div(className="card", children=[
            html.Div("Top products", className="card-title"),
            html.Div("Sorted by revenue · click a column header to sort", className="card-note"),
            dash_table.DataTable(
                id="products", sort_action="native", page_size=8,
                columns=[
                    {"name": "Product", "id": "product"},
                    {"name": "Category", "id": "category"},
                    {"name": "Revenue (NOK)", "id": "revenue", "type": "numeric",
                     "format": Format(precision=0, scheme=Scheme.fixed, group=Group.yes, group_delimiter=" ")},
                    {"name": "Units", "id": "units", "type": "numeric",
                     "format": Format(precision=0, scheme=Scheme.fixed, group=Group.yes, group_delimiter=" ")},
                    {"name": "Margin", "id": "margin", "type": "numeric",
                     "format": Format(precision=1, scheme=Scheme.fixed, symbol=Symbol.yes, symbol_suffix="%")},
                    {"name": "vs last year", "id": "change", "type": "numeric",
                     "format": Format(precision=1, scheme=Scheme.fixed, sign=Sign.positive, symbol=Symbol.yes, symbol_suffix="%")},
                ],
                style_as_list_view=True,
                style_header={"fontWeight": 500, "color": MUTED, "backgroundColor": "white", "border": "none",
                              "borderBottom": f"1px solid {GRID}", "fontFamily": FONT, "fontSize": 12},
                style_cell={"fontFamily": FONT, "fontSize": 13, "color": NAVY, "padding": "9px 8px",
                            "border": "none", "borderBottom": "1px solid #EEF2F4", "textAlign": "right"},
                style_cell_conditional=[{"if": {"column_id": c}, "textAlign": "left"} for c in ("product", "category")],
                style_data_conditional=[
                    {"if": {"filter_query": "{change} > 0", "column_id": "change"}, "color": "#1E8E4E"},
                    {"if": {"filter_query": "{change} < 0", "column_id": "change"}, "color": "#C0392B"},
                ],
            ),
        ]),
    ]),
    html.Div("All numbers are fictional and generated for demonstration.", className="footer"),
])


# ---------- callbacks ----------
@app.callback(
    Output("category", "value"), Output("region", "value"), Output("year", "value"),
    Input("by-category", "clickData"), Input("reset", "n_clicks"),
    State("category", "value"), prevent_initial_call=True,
)
def click_or_reset(click, _n, current):
    if ctx.triggered_id == "reset":
        return [], [], YEARS[-1]
    cat = click["points"][0]["y"]
    return [cat], dash_no_update(), dash_no_update()


def dash_no_update():
    from dash import no_update
    return no_update


@app.callback(
    [Output(f"{k}-{p}", "children") for k in ("rev", "units", "gp", "gm") for p in ("value", "change")]
    + [Output(f"{k}-change", "className") for k in ("rev", "units", "gp", "gm")]
    + [Output("monthly", "figure"), Output("by-category", "figure"), Output("by-region", "figure"), Output("products", "data")],
    Input("year", "value"), Input("region", "value"), Input("category", "value"),
)
def update(year, regions, categories):
    cur, prev = filtered(year, regions, categories)
    has_prev = not prev.empty

    def change(a, b, pts=False):
        if not has_prev or b == 0:
            return "No data for previous year", "kpi-change"
        v = (a - b) * 100 if pts else (a / b - 1) * 100
        unit = " pts" if pts else "%"
        if abs(v) < 0.05:
            return f"Unchanged vs {year - 1}", "kpi-change"
        arrow = "▲" if v >= 0 else "▼"
        return f"{arrow} {abs(v):.1f}{unit} vs {year - 1}", "kpi-change up" if v >= 0 else "kpi-change down"

    rev, prev_rev = cur.revenue.sum(), prev.revenue.sum()
    units, prev_units = cur.units.sum(), prev.units.sum()
    gp, prev_gp = cur.gross_profit.sum(), prev.gross_profit.sum()
    gm = gp / rev if rev else 0
    prev_gm = prev_gp / prev_rev if prev_rev else 0
    c_rev, c_units, c_gp, c_gm = change(rev, prev_rev), change(units, prev_units), change(gp, prev_gp), change(gm, prev_gm, pts=True)

    # monthly
    m_cur = cur.groupby(cur.month.dt.month).revenue.sum().reindex(range(1, 13), fill_value=0)
    m_prev = prev.groupby(prev.month.dt.month).revenue.sum().reindex(range(1, 13), fill_value=0)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    f1 = go.Figure()
    f1.add_bar(x=months, y=m_cur / 1e6, name=str(year), marker_color=ACCENT,
               hovertemplate="%{x} " + str(year) + "<br>NOK %{y:.2f}M<extra></extra>")
    if has_prev:
        f1.add_scatter(x=months, y=m_prev / 1e6, name=str(year - 1), mode="lines+markers",
                       line=dict(color=NAVY, width=2), marker=dict(size=5),
                       hovertemplate="%{x} " + str(year - 1) + "<br>NOK %{y:.2f}M<extra></extra>")
    base_layout(f1).update_yaxes(ticksuffix="M", tickprefix="")

    # by category: always shows every category (year and region filters apply); selected ones are highlighted
    all_cur, all_prev = filtered(year, regions, None)
    cat_cur = all_cur.groupby("category").revenue.sum().sort_values()
    cat_prev = all_prev.groupby("category").revenue.sum()
    total_all = cat_cur.sum()
    labels = []
    for c, v in cat_cur.items():
        share = v / total_all * 100 if total_all else 0
        if has_prev and cat_prev.get(c, 0):
            labels.append(f"{share:.0f}%  ·  {(v / cat_prev[c] - 1) * 100:+.0f}%")
        else:
            labels.append(f"{share:.0f}%")
    selected = set(categories or [])
    bar_colors = [ACCENT if (not selected or c in selected) else GREY for c in cat_cur.index]
    f2 = go.Figure(go.Bar(x=cat_cur / 1e6, y=cat_cur.index, orientation="h", marker_color=bar_colors,
                          text=labels, textposition="outside", cliponaxis=False,
                          hovertemplate="%{y}<br>NOK %{x:.2f}M<extra></extra>"))
    base_layout(f2).update_xaxes(ticksuffix="M", gridcolor=GRID, showgrid=True,
                                 range=[0, (cat_cur.max() / 1e6 * 1.45) if len(cat_cur) else 1])
    f2.update_yaxes(showgrid=False, ticksuffix="  ")
    f2.update_layout(margin=dict(l=10, r=30, t=10, b=10))

    # by region
    reg = cur.groupby("region").revenue.sum().sort_values()
    colors = [GREY] * (len(reg) - 1) + [ACCENT] if len(reg) else []
    f3 = go.Figure(go.Bar(x=reg / 1e6, y=reg.index, orientation="h", marker_color=colors,
                          text=[f"{v/1e6:.1f}M" for v in reg], textposition="outside", cliponaxis=False,
                          hovertemplate="%{y}<br>NOK %{x:.2f}M<extra></extra>"))
    base_layout(f3, height=300).update_xaxes(ticksuffix="M", gridcolor=GRID, showgrid=True,
                                             range=[0, (reg.max() / 1e6 * 1.2) if len(reg) else 1])
    f3.update_yaxes(showgrid=False, ticksuffix="  ")

    # products
    p = cur.groupby(["product", "category"]).agg(revenue=("revenue", "sum"), units=("units", "sum"), gp=("gross_profit", "sum")).reset_index()
    pp = prev.groupby("product").revenue.sum()
    p["margin"] = (p.gp / p.revenue * 100).round(1)
    p["change"] = [round((r / pp[n] - 1) * 100, 1) if has_prev and pp.get(n, 0) else None for n, r in zip(p["product"], p.revenue)]
    p = p.sort_values("revenue", ascending=False)
    p["revenue"] = p.revenue.round(0)
    table = p[["product", "category", "revenue", "units", "margin", "change"]].to_dict("records")

    return (nok_short(rev), c_rev[0], nok(units), c_units[0], nok_short(gp), c_gp[0], f"{gm*100:.1f}%", c_gm[0],
            c_rev[1], c_units[1], c_gp[1], c_gm[1], f1, f2, f3, table)


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)

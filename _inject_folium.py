import json, uuid, sys

path = r'c:\Users\jacop\Desktop\DTU\Social data analysis and visualization\socialdata2026-project\HappinessRealorNot.ipynb'
nb = json.load(open(path, encoding='utf-8'))
print('Before injection:', len(nb['cells']), 'cells')  # v2 fixed

# Check if already injected
already = any('happiness_change_map' in ''.join(c.get('source', [])) for c in nb['cells'])
if already:
    print('Folium change map cell already present — skipping.')
    sys.exit(0)

md_src = [
    "### Chart 5 \u2014 Who Got Happier? Folium Map of Happiness Change 2015\u21922020\n",
    "\n",
    "While the choropleth above shows *average* scores, this map asks: **did things actually improve?**  \n",
    "Each circle represents one country: **green** if happiness rose, **red** if it fell.  \n",
    "Circle size reflects the magnitude of change. Click any marker for full details."
]

code_lines = [
    "import folium\n",
    "\n",
    "# -- Compute happiness change 2015 -> 2020\n",
    "hap_2015 = (\n",
    "    df_t[df_t['Year'] == 2015][['Country', 'Happiness']]\n",
    "    .dropna().set_index('Country')['Happiness']\n",
    ")\n",
    "hap_2020 = (\n",
    "    df_t[df_t['Year'] == 2020][['Country', 'Happiness']]\n",
    "    .dropna().set_index('Country')['Happiness']\n",
    ")\n",
    "common   = hap_2015.index.intersection(hap_2020.index)\n",
    "df_delta = pd.DataFrame({\n",
    "    'Country':        common,\n",
    "    'Happiness_2015': hap_2015[common].values,\n",
    "    'Happiness_2020': hap_2020[common].values,\n",
    "    'Delta':          (hap_2020[common] - hap_2015[common]).values,\n",
    "})\n",

    "\n",
    "# Approximate lat/lon for the retained countries\n",
    "CHANGE_COORDS = {\n",
    "    'Australia':               (-25.3,  133.8),\n",
    "    'Austria':                 ( 47.5,   14.6),\n",
    "    'Belgium':                 ( 50.5,    4.5),\n",
    "    'Canada':                  ( 56.1, -106.3),\n",
    "    'Czechia':                 ( 49.8,   15.5),\n",
    "    'Denmark':                 ( 56.3,    9.5),\n",
    "    'Estonia':                 ( 58.6,   25.0),\n",
    "    'Finland':                 ( 61.9,   25.7),\n",
    "    'France':                  ( 46.2,    2.2),\n",
    "    'Germany':                 ( 51.2,   10.5),\n",
    "    'Greece':                  ( 39.1,   21.8),\n",
    "    'Hungary':                 ( 47.2,   19.5),\n",
    "    'Iceland':                 ( 64.9,  -19.0),\n",
    "    'Ireland':                 ( 53.4,   -8.2),\n",
    "    'Israel':                  ( 31.0,   35.0),\n",
    "    'Italy':                   ( 41.9,   12.6),\n",
    "    'Japan':                   ( 36.2,  138.3),\n",
    "    'Korea, Republic of':      ( 36.5,  127.9),\n",
    "    'Latvia':                  ( 56.9,   24.6),\n",
    "    'Lithuania':               ( 55.2,   23.9),\n",
    "    'Luxembourg':              ( 49.8,    6.1),\n",
    "    'Netherlands':             ( 52.3,    5.3),\n",
    "    'New Zealand':             (-40.9,  174.9),\n",
    "    'Norway':                  ( 60.5,    8.5),\n",
    "    'Poland':                  ( 51.9,   19.1),\n",
    "    'Portugal':                ( 39.4,   -8.2),\n",
    "    'Slovakia':                ( 48.7,   19.7),\n",
    "    'Slovenia':                ( 46.2,   15.0),\n",
    "    'Spain':                   ( 40.5,   -3.7),\n",
    "    'Sweden':                  ( 60.1,   18.6),\n",
    "    'Switzerland':             ( 46.8,    8.2),\n",
    "    'United Kingdom':          ( 55.4,   -3.4),\n",
    "    'United States':           ( 37.1,  -95.7),\n",
    "    'Turkiye':                 ( 38.9,   35.2),\n",
    "    'T\\u00fcrkiye':             ( 38.9,   35.2),\n",
    "}\n",

    "\n",
    "max_abs = df_delta['Delta'].abs().max()\n",
    "m_change = folium.Map(location=[50, 15], zoom_start=3, tiles='CartoDB positron')\n",
    "\n",
    "for _, row in df_delta.iterrows():\n",
    "    coords = CHANGE_COORDS.get(row['Country'])\n",
    "    if coords is None:\n",
    "        continue\n",
    "    delta  = row['Delta']\n",
    "    color  = '#27AE60' if delta >= 0 else '#E74C3C'\n",
    "    radius = max(6, abs(delta) / max_abs * 28)\n",
    "    sign   = '+' if delta >= 0 else ''\n",
    "    popup_html = (\n",
    "        f\"<b style='font-size:13px'>{row['Country']}</b><br>\"\n",
    "        f\"2015: {row['Happiness_2015']:.2f}<br>\"\n",
    "        f\"2020: {row['Happiness_2020']:.2f}<br>\"\n",
    "        f\"<span style='color:{color};font-weight:bold'>Change: {sign}{delta:.2f}</span>\"\n",
    "    )\n",
    "    folium.CircleMarker(\n",
    "        location=coords,\n",
    "        radius=radius,\n",
    "        color='white', weight=1.5,\n",
    "        fill=True, fill_color=color, fill_opacity=0.88,\n",
    "        popup=folium.Popup(popup_html, max_width=200),\n",
    "        tooltip=f\"{row['Country']}: {sign}{delta:.2f}\",\n",
    "    ).add_to(m_change)\n",
    "\n",
    "legend_html = (\n",
    "    '<div style=\"position:fixed;bottom:30px;left:30px;z-index:9999;'\n",
    "    'background:white;padding:12px 16px;border-radius:8px;'\n",
    "    'border:1px solid #ccc;font-family:sans-serif;font-size:12px;\">'\n",
    "    '<b>Happiness Change 2015&#8594;2020</b><br>'\n",
    "    '<span style=\"color:#27AE60;font-size:16px;\">&#9679;</span> Increased &nbsp;'\n",
    "    '<span style=\"color:#E74C3C;font-size:16px;\">&#9679;</span> Decreased<br>'\n",
    "    '<span style=\"color:#888\">Circle size = magnitude of change</span></div>'\n",
    ")\n",
    "m_change.get_root().html.add_child(folium.Element(legend_html))\n",
    "\n",
    "import os; os.makedirs('./docs/visualizations', exist_ok=True)\n",
    "change_path = './docs/visualizations/happiness_change_map.html'\n",
    "m_change.save(change_path)\n",
    "print(f'Saved -> {change_path}')\n",
    "m_change\n",
]

new_md = {
    'cell_type': 'markdown',
    'id': str(uuid.uuid4())[:8],
    'metadata': {},
    'source': md_src
}
new_code = {
    'cell_type': 'code',
    'id': str(uuid.uuid4())[:8],
    'execution_count': None,
    'metadata': {},
    'outputs': [],
    'source': code_lines
}

choropleth_idx = next(
    i for i, c in enumerate(nb['cells'])
    if 'happiness_geo.html' in ''.join(c.get('source', []))
)
print('Inserting after choropleth cell index:', choropleth_idx)

nb['cells'].insert(choropleth_idx + 1, new_md)
nb['cells'].insert(choropleth_idx + 2, new_code)

with open(path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=True)

print('After injection:', len(nb['cells']), 'cells')
print('Done!')

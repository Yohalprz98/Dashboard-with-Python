import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

#setting title and icon
st.set_page_config(page_title="My Dashboard", page_icon=":bar_chart:", layout="wide")

st.title(":bar_chart: My Dashboard")
st.markdown('<style>div.block-container{padding-top:2.5rem;}</style>',unsafe_allow_html=True)

#File uploader
fl = st.file_uploader(":file_folder: Upload a file", type=(["csv", "xlsx", "xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)

    if filename.endswith('.csv'):
        df = pd.read_csv(fl, encoding = "ISO-8859-1")
    elif fl.name.endswith('.xlsx'):
        df = pd.read_excel(fl, engine = "openpyxl")  #For.xlsx files
    elif fl.name.endswith('.xls'):
        df = pd.read_excel(fl, engine = "xlrd")  # For.xls files
    else:
        st.error("Unsupported file type.")
        df = None
else:
    default_file = r"C:\Users\yohal\OneDrive\Programación\Python\proyectos\dashboard\Sample.xls"
    df = pd.read_excel(default_file, engine="xlrd")

#Date filter
col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] >= date2)].copy() 

#Side filters
st.sidebar.header("Filters")

#Region filter
region = st.sidebar.multiselect("Region", df["Region"].unique())
if not region:
    df2 = df.copy() #if no region is selected, no filter would be applied and all regions will show in df2
else:
    df2 = df[df["Region"].isin(region)] #if a region is selected, only data with the 'region' selected
                                        #will be saved to df2

#State filter
state = st.sidebar.multiselect("State", df2["State"].unique()) #df2 used so we will work only with
                                                                        #the data previously filtered in region 
if not state: 
    df3 = df2.copy() #if no state is selected, no filter would be applied and all states will show in df3
else:
    df3 = df2[df2["State"].isin(state)] #if a stae is selected, only data with the 'state' selected
                                        #will be saved to df3

#City filter
city = st.sidebar.multiselect("City", df3["City"].unique())

if not city:
    df4 = df3.copy() #same usage as previous cases
else:
    df4 = df3[df3["City"].isin(city)]

category_df = df4.groupby(by = ["Category"], as_index = False)["Sales"].sum()

#Setting charts
with col1:
    st.subheader("Sales by category")
    fig = px.bar(
        category_df, 
        x = "Category", 
        y = "Sales", 
        text = ['${:,.2f}'.format(x) #setting bar chart
        for x in category_df["Sales"]], template = "seaborn")

    st.plotly_chart(fig, use_container_width = True, height = 200)

with col2:
    st.subheader("Sales by region")
    fig = px.pie(
        df4, values = "Sales", 
        names = "Region", 
        hole = 0.5) #setting pie chart

    fig.update_traces(text = df4["Region"], textposition = "outside") #Setting labels
    st.plotly_chart(fig, use_container_width = True)


#Downloading data based on chart created

col1, col2 = st.columns(2)

with col1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap = "Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv", 
        help = 'Click here to download the data as a CSV file')

with col2:
    with st.expander("Region_ViewData"):
        region = df4.groupby(by = ["Region"], as_index = False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap = "Oranges"))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv", 
        help = 'Click here to download the data as a CSV file')




#Treemap based on Region, Category and sub-category

st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(
    df4, 
    path = ["Region", "Category", "Sub-Category"], 
    values = "Sales", 
    hover_data = ["Sales"], 
    color = "Sub-Category")

fig.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width = True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Sales by Segment')
    fig = px.pie(
        df,
        values = "Sales",
        names = "Segment",
        template = "plotly_dark"
    )
    fig.update_traces(text = df["Segment"], textposition = "inside")
    st.plotly_chart(fig, use_container_width = True)

with chart2:
    st.subheader('Sales by category')
    fig = px.pie(
        df,
        values ="Sales",
        names = "Category",
        template = "gridon"
    )
    fig.update_traces(text = df["Category"], textposition = "inside")
    st.plotly_chart(fig, use_container_width = True)

import plotly.figure_factory as ff
st.subheader(":point_right: Sub-category Sales Summary by Month")
with st.expander("Summary table"):
    df_sample = df[0:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale = "Cividis")
    st.plotly_chart(fig, use_container_width = True)

    st.markdown("Monthly sub-category table")
    df4["month"] = df4["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data = df4, values = "Sales", index = ["Sub-Category"], columns = "month")
    st.write(sub_category_Year.style.background_gradient(cmap = "Blues"))

#Scatter plot

data1 = px.scatter(df4, x = "Sales", y = "Profit", size = "Quantity")
data1['layout'].update(title = "Sales and Profits - Scatter Plot", titlefont = dict(size = 20),
                       xaxis = dict(title = "Sales", titlefont = dict(size=19)),
                       yaxis = dict(title = "Profit", titlefont = dict(size=19)))
st.plotly_chart(data1, use_container_width = True)

with st.expander("View Data"):
    st.write(df4.iloc[:500,1:20:2].style.background_gradient(cmap = "Oranges"))

#Download original data

csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download data', data = csv, file_name = "Data.csv", mime = "text/csv")
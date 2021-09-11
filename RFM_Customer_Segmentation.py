
            # RFM_Customer_Segmentation #
#######################################################
#######################################################

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
# Show all rows
pd.set_option('display.max_rows', None)
# Show all columns
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df = pd.read_excel(r"C:\Users\hp\PycharmProjects\VBO\WEEK_03\online_retail_II.xlsx",
                   sheet_name="Year 2010-2011")
df_ = df.copy()

#######################################################
                # Data Understanding #
#######################################################

df.head()
df.shape
df.describe().T

# What is the unique product?
df["Description"].nunique()

# How many of each product are there?
df["Description"].value_counts().head()

# How many orders came from which country?
df["Country"].value_counts()

# Rank the 5 most ordered products from most to least.
df.groupby("Description").agg({"Quantity": "sum"}).\
    sort_values("Quantity", ascending=False).head()

#######################################################
                # Data Preparation #
#######################################################

df.isnull().sum()
df.dropna(inplace=True)

# Removal from dataset of canceled transactions 'C' in invoices
df = df[~df["Invoice"].str.contains("C", na=False)]
df = df[(df['Quantity'] > 0)]
df = df[(df['Price'] > 0)]
df.head()
df.describe().T

df["TotalPrice"] = df["Quantity"] * df["Price"]
df.head()

#######################################################
              # Customer Segmentation #
#######################################################

# Last date in dataset
df["InvoiceDate"].max()

# Received 2 days after the deadline
today_date = dt.datetime(2011, 12, 11)

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

rfm.head()

rfm.columns = ['recency', 'frequency', 'monetary']

#######################################################
           # Calculating RFM Scores #
#######################################################

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])


rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])


rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

rfm.head()

rfm.describe().T

rfm[rfm["RFM_SCORE"] == "25"].head()
# can't loose them

rfm[rfm["RFM_SCORE"] == "41"].head()
# promising

#######################################################
       # Creating & Analysing RFM Segments #
#######################################################

# Classes are assigned based on RFM scores. The following grades are given for their scores.
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

rfm.head()

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

rfm[rfm["segment"] == "need_attention"].head()

rfm[rfm["segment"] == "new_customers"].index

new_df = pd.DataFrame()
new_df["loyal_customers_id"] = rfm[rfm["segment"] == "loyal_customers"].index
new_df.head()
new_df.to_csv("new_loyal_customers.csv")

#######################################################
     # Functionalization of the Whole Process #
#######################################################
# The function was written using all the above operations.
# This function was written with the aim of targeting specific customer clusters and
# thus generating much higher response rates as well as increased loyalty and customer lifetime value.

def create_rfm(dataframe):

    # PREPARING THE DATA
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    dataframe = dataframe[(dataframe['Quantity'] > 0)]
    dataframe = dataframe[(dataframe['Price'] > 0)]
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]

    # CALCULATION OF RFM METRICS
    today_date = dt.datetime(2011, 12, 11)
    rfm = dataframe.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                                'Invoice': lambda num: num.nunique(),
                                                "TotalPrice": lambda price: price.sum()})
    rfm.columns = ['recency', 'frequency', "monetary"]
    rfm = rfm[(rfm['monetary'] > 0)]

    # CALCULATION OF RFM SCORES
    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

    # VARIABLES CONVERTED TO STR AND CONCATENATED
    rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                        rfm['frequency_score'].astype(str))

    # NAMING OF SEGMENTS
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
    rfm = rfm[["recency", "frequency", "monetary", "segment"]]
    return rfm

df = df_.copy()
rfm_new = create_rfm(df)
rfm_new.head()


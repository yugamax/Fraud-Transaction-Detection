import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

df = pd.read_csv(r"dataset\transaction_recs.csv")

x = df.iloc[:,2:20]
y= df.iloc[:,1]

y = y.replace({'Fraud': 1, 'Non - Fraud': 0})

balancingf = y.value_counts()[0]/y.value_counts()[1]

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)

model = XGBClassifier(scale_pos_weight=balancingf)
model.fit(x_train, y_train)
y_pred = model.predict(x_test)
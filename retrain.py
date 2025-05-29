import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from xgboost import XGBClassifier
import joblib
import warnings

warnings.filterwarnings("ignore")

df = pd.read_csv(r"dataset\cleaned_dataset.csv")

df['ERC20 most sent token type'] = df['ERC20 most sent token type'].fillna('missing')
enc1 = LabelEncoder()
df['ERC20 most sent token type'] = enc1.fit_transform(df['ERC20 most sent token type'])

df['ERC20_most_rec_token_type'] = df['ERC20_most_rec_token_type'].fillna('missing')
enc2 = LabelEncoder()
df['ERC20_most_rec_token_type'] = enc2.fit_transform(df['ERC20_most_rec_token_type'])

df = df.fillna(df.median())

# print(df.isnull().sum())

x = df.iloc[:,2:20]
y= df.iloc[:,1]

balancingf = y.value_counts()[0]/y.value_counts()[1]

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.30, shuffle=True , random_state=42, stratify=y)

model = XGBClassifier(scale_pos_weight=balancingf)
model.fit(x_train, y_train)

y_pred = model.predict(x_test)

print("\t\tClassification Report:\n")
print(classification_report(y_test, y_pred))
print(f"\nAccuracy of model : {model.score(x_test, y_test)*100:.2f} %")

bundle = {
    'model': model,
    'enc1': enc1,
    'enc2': enc2
}

joblib.dump(bundle , r"model/models.joblib")
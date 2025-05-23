!pip install lazypredict

from google.colab import auth
from google.colab import drive
import re
import os
import numpy as np
import zipfile
import pandas as pd
import io
from googleapiclient.http import MediaIoBaseDownload
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn import metrics
from lazypredict.Supervised import LazyRegressor
pd.reset_option

# Авторизуемся в Colab
auth.authenticate_user()

# Используем учетные данные Colab
drive.mount('/content/drive')
zip_file='/content/drive/MyDrive/Milk task/milk_data.zip'
#распаковывем зипку
milk_data = zipfile.ZipFile(zip_file)
milk_data.extractall()
#переходим в нужную директорию
zip_directory = '/content/milk_data'
file_list_antibiotics = os.listdir(zip_directory)
#просто проверяем, что все сохранилось и у нас есть доступ
len(file_list_antibiotics)

#разбиваем названия файлов на информацию, название антибиотика и концентрацию
antibiotic=[]
concentration=[]
file_name=[]
pd.reset_option('all')
dfs = [[]*len(file_list_antibiotics)]
#читаем файлы
for file_title in file_list_antibiotics:
    file_name=file_title.split('_')
    antibiotic.append(file_name[0])
    concentration.append(float(file_name[1]))
    full_file_path = os.path.join(zip_directory, file_title)
    #считываем столбцы с амперами
    dfs.append([pd.read_csv(full_file_path)['Current, A']])
    file_name=[]
#Создаем массив данных (наша будущая таблица)
big_frame = pd.concat([df[0] for df in dfs[1:]], axis=1)
#переворачиваем таблицу
big_frame_1 = big_frame.transpose()
#сохраняем вольтажи, потом называем столбиками
list_V = pd.read_csv('/content/milk_data/cefazoline_1e-06_1157.csv')['Voltage, V']
#присваиваем столбцам вольты, при которых были проведены измерения
big_frame_1.columns=list_V
#добавляем наши столбцы с названием антибиотика и концентрацией
big_frame_1['antibiotic']=antibiotic
big_frame_1['concentration']=concentration
big_frame_1.sort_values(by='concentration', ascending=False, axis=0)
#сохраняем файл
big_frame_1.to_csv('milk_data.csv', index=False)
big_frame_1

#находим диапазон концентраций для каждого из антибиотиков
#оставляем только уникальные названия
antibio_unique = set(antibiotic)
for antibio in antibio_unique:
    min_concentraion = big_frame_1[big_frame_1["antibiotic"].str.contains(antibio, flags=re.I)]['concentration'].min()
    max_concentraion = big_frame_1[big_frame_1["antibiotic"].str.contains(antibio, flags=re.I)]['concentration'].max()
    #ура, френдли вывод :)
    print('for', antibio, 'concentration from', min_concentraion, 'to', max_concentraion, sep=' ')
print('number of unique antibiotics:', len(antibio_unique), sep=' ')

#распределение измерений каждого антибиотика
big_frame_1['antibiotic'].value_counts().plot.bar(legend=True)
plt.xlabel('Антибиотик')
plt.ylabel('Число измерений')
plt.tight_layout()
plt.show()
#распределение для измерений концентрации у каждого антибиотика
for antibio in antibio_unique:
    big_frame_1[big_frame_1["antibiotic"].str.contains(antibio, flags=re.I)]['concentration'].value_counts().plot.bar(legend=True)
    plt.title(f'Число измерений концентраций для {antibio}')
    plt.xlabel('Концентрация')
    plt.ylabel('Число измерений')
    plt.tight_layout()
    plt.show()

#построим ВАХ для любого из файлов в каждом антибиотике
    voltamp = ['/content/milk_data/cefazoline_1e-06_1157.csv', '/content/milk_data/ceftiofur_1e-07_839.csv', '/content/milk_data/penicillin_1e-07_44.csv', '/content/milk_data/streptomycin_1e-05_1055.csv', '/content/milk_data/tetracycline_1e-07_668.csv']
    for voltamp in voltamp:
       name = voltamp.split('/')[3]
       cols = pd.read_csv(voltamp).columns.tolist()
       pd.read_csv(voltamp).plot.scatter(cols[1],cols[2])
       plt.grid()
       plt.title(f'ВАХ {name}')

zip_file='/content/drive/MyDrive/milk_data_all.zip'
#распаковывем зипку
milk_data = zipfile.ZipFile(zip_file)
milk_data.extractall()
#переходим в нужную директорию
zip_directory = '/content/milk_data_all'
file_list_antibiotics = os.listdir(zip_directory)
#просто проверяем, что все сохранилось и у нас есть доступ
len(file_list_antibiotics)

file_name=[]
presence=[]
dfs = [[]*len(file_list_antibiotics)]
#читаем файлы
for file_title in file_list_antibiotics:
    file_name=file_title.split('_')
    if file_name[0]=='milk':
        presence.append(0)
    else:
      presence.append(1)
    full_file_path = os.path.join(zip_directory, file_title)
    #считываем столбцы с амперами
    dfs.append([pd.read_csv(full_file_path)['Current, A']])
    file_name=[]
#Создаем массив данных (наша будущая таблица)
big_frame_all = pd.concat([df[0] for df in dfs[1:]], axis=1)
#переворачиваем таблицу
big_frame_all = big_frame_all.transpose()
#сохраняем вольтажи, потом называем столбиками
list_V = pd.read_csv('/content/milk_data/cefazoline_1e-06_1157.csv')['Voltage, V']
#присваиваем столбцам вольты, при которых были проведены измерения
big_frame_all.columns=list_V
#добавляем наши столбцы с названием антибиотика и концентрацией
big_frame_all['presence']=presence
#сохраняем файл
big_frame_all

d = preprocessing.normalize(big_frame_all, axis=0)
scaled_big_frame_all = pd.DataFrame(d, columns=big_frame_all.columns, index=big_frame_all.index)
del scaled_big_frame_all['presence']
scaled_big_frame_all['presence'] = big_frame_all['presence']
scaled_big_frame_all

X = scaled_big_frame_all.drop(['presence'], axis=1)
y= scaled_big_frame_all['presence']

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.datasets import make_classification
from sklearn.metrics import roc_curve, auc
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
log_reg = LogisticRegression(random_state=42)
log_reg.fit(X_train, y_train)
y_pred_log = log_reg.predict(X_test)
cm = confusion_matrix(y_test, y_pred_log)
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', annot_kws={'fontsize': 14})
plt.ylabel('Истинные значения')
plt.xlabel('Предсказанные значения')
plt.title('Матрица ошибок', pad=15)
plt.show()

report = classification_report(y_test, log_reg.predict(X_test))
print(report)

y_pred_proba = log_reg.predict_proba(X_test)[:,1]
fpr, tpr, _ = metrics.roc_curve(y_test,  y_pred_proba)

# построение ROC кривой
plt.plot(fpr, tpr)
plt.ylabel('Истинно позитивный исход')
plt.xlabel('Ложно положительный исход')
auc = metrics.roc_auc_score(y_test, y_pred_proba)
print("AUC: %.3f" % auc)
plt.show()

knn = KNeighborsClassifier(n_neighbors=10)
knn.fit(X_train, y_train)
y_pred_knn = knn.predict(X_test)
log_reg.fit(X_train, y_train)
y_pred_knn = knn.predict(X_test)
cm = confusion_matrix(y_test, y_pred_knn)
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', annot_kws={'fontsize': 14})
plt.ylabel('Истинные значения')
plt.xlabel('Предсказанные значения')
plt.title('Матрица ошибок', pad=15)
plt.show()

report = classification_report(y_test, knn.predict(X_test))
print(report)

y_pred_proba = knn.predict_proba(X_test)[:,1]
fpr, tpr, _ = metrics.roc_curve(y_test,  y_pred_proba)

# построение ROC кривой
plt.plot(fpr, tpr)
plt.ylabel('Истинно позитивный исход')
plt.xlabel('Ложно положительный исход')
auc = metrics.roc_auc_score(y_test, y_pred_proba)
print("AUC: %.3f" % auc)
plt.show()

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

classifer = RandomForestClassifier(random_state=42)
classifer.fit(X_train, y_train)
y_pred_classifer =  classifer.predict(X_test)
classifer.fit(X_train, y_train)
y_pred_classifer = classifer.predict(X_test)
cm = confusion_matrix(y_test, y_pred_classifer)
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', annot_kws={'fontsize': 14})
plt.ylabel('Истинные значения')
plt.xlabel('Предсказанные значения')
plt.title('Матрица ошибок', pad=15)
plt.show()

report = classification_report(y_test, classifer.predict(X_test))
print(report)

y_pred_proba = classifer.predict_proba(X_test)[:,1]
fpr, tpr, _ = metrics.roc_curve(y_test,  y_pred_proba)

# построение ROC кривой
plt.plot(fpr, tpr)
plt.ylabel('Истинно позитивный исход')
plt.xlabel('Ложно положительный исход')
auc = metrics.roc_auc_score(y_test, y_pred_proba)
print("AUC: %.3f" % auc)
plt.show()

from mlxtend.plotting import plot_decision_regions
from sklearn.utils import check_random_state, check_array
from sklearn.svm import LinearSVC, LinearSVR, SVC, SVR, _libsvm
from sklearn.datasets import load_iris, load_diabetes, load_wine, load_breast_cancer
linear_svm = SVC(random_state=42, probability=True)
linear_svm.fit(X_train, y_train)
y_pred_linear_svm =  linear_svm.predict(X_test)
linear_svm.fit(X_train, y_train)
y_pred_linear_svm = linear_svm.predict(X_test)
cm = confusion_matrix(y_test, y_pred_linear_svm)
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', annot_kws={'fontsize': 14})
plt.ylabel('Истинные значения')
plt.xlabel('Предсказанные значения')
plt.title('Матрица ошибок', pad=15)
plt.show()

report = classification_report(y_test, linear_svm.predict(X_test))
print(report)

y_pred_proba = linear_svm.predict_proba(X_test)[:,1]
fpr, tpr, _ = metrics.roc_curve(y_test,  y_pred_proba)

# построение ROC кривой
plt.plot(fpr, tpr)
plt.ylabel('Истинно позитивный исход')
plt.xlabel('Ложно положительный исход')
auc = metrics.roc_auc_score(y_test, y_pred_proba)
print("AUC: %.3f" % auc)
plt.show()

import xgboost as xgb
model = xgb.XGBClassifier()
model.fit(X_train.values, y_train.values)
y_pred_model = model.predict(X_test.values)
cm = confusion_matrix(y_test, y_pred_model)
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', annot_kws={'fontsize': 14})
plt.ylabel('Истинные значения')
plt.xlabel('Предсказанные значения')
plt.title('Матрица ошибок', pad=15)
plt.show()

report = classification_report(y_test, model.predict(X_test.values))
print(report)

y_pred_proba = model.predict_proba(X_test.values)[:,1]
fpr, tpr, _ = metrics.roc_curve(y_test,  y_pred_proba)

# построение ROC кривой
plt.plot(fpr, tpr)
plt.ylabel('Истинно позитивный исход')
plt.xlabel('Ложно положительный исход')
auc = metrics.roc_auc_score(y_test, y_pred_proba)
print("AUC: %.3f" % auc)
plt.show()

antibiotic=[]
concentration=[]
file_name=[]
pd.reset_option('all')
dfs = [[]*len(file_list_antibiotics)]
#читаем файлы
for file_title in file_list_antibiotics:
    file_name=file_title.split('_')
    antibiotic.append(file_name[0])
    full_file_path = os.path.join(zip_directory, file_title)
    #считываем столбцы с амперами
    dfs.append([pd.read_csv(full_file_path)['Current, A']])
    file_name=[]
#Создаем массив данных (наша будущая таблица)
frame = pd.concat([df[0] for df in dfs[1:]], axis=1)
#переворачиваем таблицу
frame = frame.transpose()
#сохраняем вольтажи, потом называем столбиками
list_V = pd.read_csv('/content/milk_data/cefazoline_1e-06_1157.csv')['Voltage, V']
#присваиваем столбцам вольты, при которых были проведены измерения
frame.columns=list_V
#добавляем наши столбцы с названием антибиотика и концентрацией
frame['antibiotic']=antibiotic
frame

frame['antibiotic'].replace({'penicillin': 0, 'tetracycline': 1, 'cefazoline': 2, 'streptomycin': 3, 'ceftiofur' : 4, 'milk' : 5}, inplace=True)
frame

frame_new = preprocessing.normalize(frame, axis=0)
scaled_big_frame_all = pd.DataFrame(frame_new, columns=frame.columns, index=frame.index)
# Convert frame_new to DataFrame before deleting the column
frame_new = scaled_big_frame_all.copy()  # Create a DataFrame copy
del frame_new['antibiotic']
frame_new['antibiotic'] = frame['antibiotic']
frame_new

X = frame_new.drop(['antibiotic'], axis=1)
y= frame_new['antibiotic']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

log_reg = LogisticRegression(random_state=42, multi_class='multinomial')
log_reg.fit(X_train, y_train)
y_pred_log = log_reg.predict(X_test)
cm = confusion_matrix(y_test, y_pred_log)
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', annot_kws={'fontsize': 14})
plt.ylabel('Истинные значения')
plt.xlabel('Предсказанные значения')
plt.title('Матрица ошибок', pad=15)
plt.show()

report = classification_report(y_test, log_reg.predict(X_test))
print(report)

knn = KNeighborsClassifier(n_neighbors=10)
knn.fit(X_train, y_train)
y_pred_knn = knn.predict(X_test)
log_reg.fit(X_train, y_train)
y_pred_knn = knn.predict(X_test)
cm = confusion_matrix(y_test, y_pred_knn)
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', annot_kws={'fontsize': 14})
plt.ylabel('Истинные значения')
plt.xlabel('Предсказанные значения')
plt.title('Матрица ошибок', pad=15)
plt.show()

report = classification_report(y_test, knn.predict(X_test))
print(report)

classifer = RandomForestClassifier(random_state=42)
classifer.fit(X_train, y_train)
y_pred_classifer = classifer.predict(X_test)
cm = confusion_matrix(y_test, y_pred_classifer)
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', annot_kws={'fontsize': 14})
plt.ylabel('Истинные значения')
plt.xlabel('Предсказанные значения')
plt.title('Матрица ошибок', pad=15)
plt.show()

report = classification_report(y_test, classifer.predict(X_test))
print(report)

from mlxtend.plotting import plot_decision_regions
from sklearn.utils import check_random_state, check_array
from sklearn.svm import LinearSVC, LinearSVR, SVC, SVR, _libsvm
from sklearn.datasets import load_iris, load_diabetes, load_wine, load_breast_cancer
linear_svm = SVC(random_state=42, probability=True)
linear_svm.fit(X_train, y_train)
y_pred_linear_svm =  linear_svm.predict(X_test)
linear_svm.fit(X_train, y_train)
y_pred_linear_svm = linear_svm.predict(X_test)
cm = confusion_matrix(y_test, y_pred_linear_svm)
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', annot_kws={'fontsize': 14})
plt.ylabel('Истинные значения')
plt.xlabel('Предсказанные значения')
plt.title('Матрица ошибок', pad=15)
plt.show()

report = classification_report(y_test, linear_svm.predict(X_test))
print(report)

import xgboost as xgb
model = xgb.XGBClassifier()
model.fit(X_train.values, y_train.values)
y_pred_model = model.predict(X_test.values)
cm = confusion_matrix(y_test, y_pred_model)
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', annot_kws={'fontsize': 14})
plt.ylabel('Истинные значения')
plt.xlabel('Предсказанные значения')
plt.title('Матрица ошибок', pad=15)
plt.show()

report = classification_report(y_test, model.predict(X_test.values))
print(report)


# итого наилучшая точность у Random forest и KNN

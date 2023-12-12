import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

data = pd.read_csv("mtcnn_unpruned.csv")
data["mse"] = np.sqrt(data["mse"])

# 1. Boxplot to see the distribution of time for each combination of illum and occ
plt.figure(figsize=(12, 6))
sns.boxplot(x='illum', y='mse', hue='occ', data=data, palette="Set2")
plt.title("Distribution of RMSE by Illumination and Occlusion")
plt.xlabel("Illumination Level")
plt.ylabel("RMSE")
plt.legend(title='Occlusion Level')
plt.grid()
plt.savefig("boxplot_mtcnn_acc.png", dpi=200)

# # 2. Heatmap to visualize the average time for each combination of illum and occ
# plt.figure(figsize=(8, 6))
# sns.heatmap(pivot_data, annot=True, cmap="YlGnBu", fmt=".2f")
# plt.title("Heatmap of Average Time by Illumination and Occlusion")
# plt.xlabel("Occlusion Level")
# plt.ylabel("Illumination Level")
# plt.show()
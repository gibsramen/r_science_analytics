import matplotlib.pyplot as plt
import pandas as pd


plt.rcParams["font.sans-serif"] = "Alte Haas Grotesk"
plt.rcParams["figure.facecolor"] = "white"

df = pd.read_csv("data/submissions.tsv", sep="\t", index_col=0)
category_counts = df["link_flair_text"].value_counts()

fig, ax = plt.subplots(1, 1, figsize=(10, 6))
ax.barh(
    y=category_counts.index,
    width=category_counts,
)
ax.set_xlabel("Number of Submissions", fontsize=16)
ax.set_ylabel("Post Category", fontsize=16)
plt.tight_layout()
plt.savefig(
    "results/figures/category_distributions.png",
    dpi=300,
    bbox_inches="tight"
)

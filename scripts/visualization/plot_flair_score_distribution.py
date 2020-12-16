import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


plt.rcParams["font.sans-serif"] = "Alte Haas Grotesk"
plt.rcParams["figure.facecolor"] = "white"

df = pd.read_csv("data/submissions.tsv", sep="\t", index_col=0)
# remove the two flairs with only 1 entry
category_counts = df["link_flair_text"].value_counts()
categories_to_keep = category_counts[category_counts > 1].index
df = df[df["link_flair_text"].isin(categories_to_keep)]

flair_score_medians = df.groupby(["link_flair_text"]).median()["score"]
flair_score_medians = flair_score_medians.sort_values()
flair_score_labels = [
    f"{flair} (n = {df[df['link_flair_text'] == flair].shape[0]})"
    for flair in flair_score_medians.index
]

fig, ax = plt.subplots(1, 1, figsize=(10, 6))
sns.boxplot(
    data=df,
    y="link_flair_text",
    x="score",
    palette="Oranges",
    order=flair_score_medians.index,
    orient="horizontal",
    linewidth=1.5,
    ax=ax,
)
ax.tick_params("both", labelsize=12)
ax.set_xscale("log", base=10)
ax.set_xlabel("Score", fontsize=16)
ax.set_ylabel("Flair", fontsize=16)
ax.set_yticklabels(flair_score_labels)
n = df.shape[0]
ax.set_title(
    f"Score Distributions of {n} Recent /r/science Posts ≥ 50 Points",
    fontsize=18,
    loc="center",
)
plt.tight_layout()
plt.savefig(
    "results/figures/category_score_distributions.png",
    dpi=300,
    bbox_inches="tight",
)

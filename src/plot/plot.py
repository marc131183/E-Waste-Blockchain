import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns


def pieChart(labels, numbers):
    total = sum(numbers)
    fig, ax = plt.subplots(figsize=(8, 6))
    patches, texts, _ = ax.pie(
        numbers, autopct=lambda p: "{:.1f}% ({:.0f})".format(p, p * total / 100)
    )
    plt.legend(
        patches, labels, loc="center left", bbox_to_anchor=(0.92, 0.5), frameon=False
    )
    plt.show()


def stackedBarChart():
    # Define the data
    reasons = [
        "Afraid of data abuse",
        "No time yet",
        "Do not know where to submit devices",
        "Do not see the value of it",
        "Might need the device someday",
        "Do not know that these devices are recyclable",
        "Another reason",
    ]
    counts = [44, 29, 39, 8, 59, 10, 12]
    totalNumber = 96

    # sort them
    temp = [(x, y) for x, y in zip(reasons, counts)]
    temp.sort(key=lambda x: x[1], reverse=True)
    reasons = [elem[0] for elem in temp]
    counts = [elem[1] for elem in temp]

    # Create the bar chart
    plt.barh(reasons, counts)
    plt.yticks(fontsize=14)
    fig = plt.gcf()
    fig.set_figwidth(10)
    fig.set_figheight(6)

    # Add labels and legend
    plt.xlabel("Number of Respondents", fontsize=14)
    plt.ylabel("Reason", fontsize=14)
    plt.xlim(0, totalNumber)

    # Add number and percentage labels to the bars
    for i, count in enumerate(counts):
        plt.text(
            count + 0.5,
            i,
            str(count) + " (" + str(round(count / totalNumber * 100, 1)) + "%)",
            ha="left",
            va="center",
        )

    # Display the chart
    plt.tight_layout()
    plt.show()


def barChart(answers, counts, colors):
    # Create the bar chart
    plt.bar(answers, counts, color=colors, width=0.5)
    plt.yticks(fontsize=12)

    # Add labels and title
    plt.ylabel("Number of Respondents", fontsize=14)
    plt.xlabel("Answer", fontsize=14)

    # Add number and percentage labels to the bars
    for i, count in enumerate(counts):
        plt.text(
            i,
            count - 2,
            str(count) + " (" + str(round(count / sum(counts) * 100, 1)) + "%)",
            ha="center",
            va="center",
        )

    # Display the chart
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # plot number of devices at home
    labels = ["0", "1", "2-3", "4-6", "7+"]
    numbers = [8, 15, 56, 21, 14]
    pieChart(labels, numbers)

    # plot age of respondents
    labels = ["0-18", "19-29", "30-39", "40-49", "50-59", "60+"]
    numbers = [1, 31, 31, 20, 23, 8]
    pieChart(labels, numbers)

    # plot the reasons for not sending them for recycling
    stackedBarChart()

    # plot if respondents have ever sent items for recycling
    barChart(["Yes", "No"], [50, 64], ["green", "red"])

    # plot if tracking system would encourage sending of devices
    barChart(["Yes", "No"], [56, 45], ["green", "red"])

    df = pd.read_csv("survey.csv")
    # drop all rows, where reason is nan
    df = df[df[df.columns[5]].notna()]
    # get only rows for which respondents didn't list "I might use the device someday" as a reason for not sending it
    # columns: timestamp, gender, age, num devices at home, reason, encourage, anything else
    filtered_df = df[
        ~df[df.columns[5]].str.contains("I might need the device someday", na=False)
    ]
    reasons = [
        "I am afraid that my data on these devices may be abused",
        "I have not had the time yet to send them in",
        "I do not know where to submit these items for recycling",
        "I do not see the value of it",
        "I might need the device someday",
        "I do not know that these items are recyclable",
        "Another reason",
    ]
    for reason in reasons:
        print("Reason: {}".format(reason))
        temp = len(
            filtered_df[filtered_df[filtered_df.columns[5]].str.contains(reason)]
        )
        print("Count: {}, {}%".format(temp, np.round(temp / len(filtered_df) * 100, 3)))

    # check if different age groups have different reasons
    age_groups = ["0-18", "19-29", "30-39", "40-49", "50-59", "60+"]

    matrix = np.empty((len(age_groups), len(reasons)))
    for i, age in enumerate(age_groups):
        for j, reason in enumerate(reasons):
            matrix[i, j] = len(
                df[
                    (df[df.columns[2]] == age)
                    & (df[df.columns[5]].str.contains(reason))
                ]
            )

    num_respondents_per_age_group = np.array(
        [len(df[df[df.columns[2]] == age]) for age in age_groups]
    )
    print(matrix)
    matrix = matrix / num_respondents_per_age_group[:, np.newaxis]

    reasons = [
        "Afraid of data abuse",
        "No time yet",
        "Do not know where to submit devices",
        "Do not see the value of it",
        "Might need the device someday",
        "Do not know that these devices are recyclable",
        "Another reason",
    ]

    plt.figure(figsize=(10, 6))
    ax = sns.heatmap(matrix.T, linewidth=0.5, annot=True, fmt=".0%", cmap="Blues")
    plt.yticks(np.arange(len(reasons)) + 0.5, labels=reasons, rotation=0)
    plt.xticks(np.arange(len(age_groups)) + 0.5, labels=age_groups)
    plt.ylabel("Reason", fontsize=14)
    plt.xlabel("Age", fontsize=14)
    plt.tight_layout()
    plt.show()

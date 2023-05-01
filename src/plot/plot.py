import matplotlib.pyplot as plt


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
    counts = [38, 26, 35, 8, 55, 9, 12]
    totalNumber = 89

    # sort them
    temp = [(x, y) for x, y in zip(reasons, counts)]
    temp.sort(key=lambda x: x[1], reverse=True)
    reasons = [elem[0] for elem in temp]
    counts = [elem[1] for elem in temp]

    # Create the bar chart
    plt.barh(reasons, counts)
    fig = plt.gcf()
    fig.set_figwidth(10)
    fig.set_figheight(6)

    # Add labels and legend
    plt.xlabel("Number of Respondents")
    plt.ylabel("Reason")
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

    # Add labels and title
    plt.ylabel("Number of Respondents")

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
    numbers = [7, 13, 54, 17, 13]
    pieChart(labels, numbers)

    # plot age of respondents
    labels = ["0-18", "19-29", "30-39", "40-49", "50-59", "60+"]
    numbers = [1, 28, 29, 17, 22, 7]
    print(numbers)
    pieChart(labels, numbers)

    # plot the reasons for not sending them for recycling
    stackedBarChart()

    # plot if respondents have ever sent items for recycling
    barChart(["Yes", "No"], [44, 60], ["green", "red"])

    # plot if tracking system would encourage sending of devices
    barChart(["Yes", "No"], [50, 41], ["green", "red"])

import os
import sys

# --- FORCES INTERACTIVE POPUP (If running locally) ---
import matplotlib

#matplotlib.use("TkAgg")
# ----------------------------------------------------

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def main():
    # 1. Check if a filename was provided in the command line
    if len(sys.argv) < 2:
        print("Error: No CSV file provided.")
        print("Usage: python script_name.py <path_to_csv_file>")
        sys.exit(1)

    # 2. Get the input file path from the command line argument
    input_file = sys.argv[1]

    # 3. Verify the file exists
    if not os.path.exists(input_file):
        print(f"Error: The file '{input_file}' does not exist.")
        sys.exit(1)

    # 4. Generate the output PNG filename automatically
    # This splits off the extension (e.g., '.csv') and appends '.png'
    base_path, _ = os.path.splitext(input_file)
    output_png = base_path + ".png"

    # 5. Read the CSV data
    print(f"Reading data from: {input_file} ...")
    df = pd.read_csv(input_file)

    # 6. Set up the plotting style
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="whitegrid")

    # 7. Create the scatter plot, coloring by the 'part' column
    palette_colors = {"melody": "#1f77b4", "accompaniment": "#ff7f0e"}

    sns.scatterplot(
        data=df,
        x="start_beat",
        y="velocity",
        hue="part",
        style="part",
        palette=palette_colors,
        s=100,  # Size of the dots
    )

    # 8. Customize labels and axis bounds
    plt.title("Musical Part Distribution by Velocity and Beat", fontsize=14, pad=15)
    plt.xlabel("start_beat", fontsize=12)
    plt.ylabel("velocity", fontsize=12)
    plt.ylim(0, 130)

    # 9. Clean up the legend layout
    plt.legend(title="Musical Part", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()

    # 10. Save the plot to a PNG file dynamically
    print(f"Saving chart to:  {output_png} ...")
    plt.savefig(output_png, dpi=300)

    # 11. Display the popup window
    #plt.show()


if __name__ == "__main__":
    main()


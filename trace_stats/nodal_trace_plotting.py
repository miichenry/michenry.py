import pandas as pd
import matplotlib.pyplot as plt

# Load your dataframe (replace 'your_dataframe.csv' with the actual filename)
df = pd.read_csv('trace_stats_temp.csv')

# --- Data Visualization Section ---

# 1. Plot histogram of trace lengths
plt.figure(figsize=(10, 6))
plt.hist(df['length_seconds'], bins=50, color='blue', alpha=0.7)
plt.title('Distribution of Trace Lengths')
plt.xlabel('Trace Length (seconds)')
plt.ylabel('Number of Traces')
plt.grid(True)
plt.savefig('trace_length_distribution.png')  # Save the histogram
plt.close()  # Close the plot after saving
print("Histogram of trace lengths saved as 'trace_length_distribution.png'")

# 2. Scatter plot of start times and trace lengths
plt.figure(figsize=(10, 6))
plt.scatter(df['starttime'], df['length_seconds'], alpha=0.5, color='green')
plt.title('Trace Lengths over Time')
plt.xlabel('Start Time')
plt.ylabel('Trace Length (seconds)')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig('trace_lengths_over_time.png')  # Save the scatter plot
plt.close()
print("Scatter plot of trace lengths over time saved as 'trace_lengths_over_time.png'")

# 3. Bar plot of traces per station
station_counts = df['station'].value_counts()
plt.figure(figsize=(12, 6))
station_counts.plot(kind='bar', color='purple')
plt.title('Number of Traces per Station')
plt.xlabel('Station')
plt.ylabel('Number of Traces')
plt.grid(True)
plt.tight_layout()
plt.savefig('traces_per_station.png')  # Save the bar plot
plt.close()
print("Bar plot of traces per station saved as 'traces_per_station.png'")

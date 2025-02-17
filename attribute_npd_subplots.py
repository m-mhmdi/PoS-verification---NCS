import numpy as np
from scipy.stats import binom
import matplotlib.pyplot as plt
import map_npd

# map npd plays
df_npd = map_npd.map_npd(data)

# Global list of NPD names (regions)
npd_names = ['north sea', 'norwegian sea', 'barents sea']

def calculate_confidence_intervals(avg_prob, trials, confidence_level):
    """
    Calculate the confidence intervals for the binomial distribution.
    
    Parameters:
        avg_prob (float): Average probability of success.
        trials (int): Number of trials.
        confidence_level (float): Desired confidence level.
    
    Returns:
        tuple: Lower and upper bounds of the confidence interval.
    """
    lower_bound_cp, upper_bound_cp = binom.interval(confidence_level, trials, avg_prob, loc=0)
    lower_bound_cp /= trials
    upper_bound_cp /= trials
    return lower_bound_cp, upper_bound_cp

def attribute_diagram(df, years):
    """
    Generate attribute diagrams and Brier/Skill Score plots for multiple features over time.
    
    For each period a single 3×3 figure is created:
      - The rows (top to bottom) correspond to the features: Reservoir, Source, Trap.
      - The columns (left to right) correspond to the regions: north sea, norwegian sea, barents sea.
      
    Similarly, after processing all periods a single 3×3 figure is created showing the time series 
    of Brier/Skill Score (plus bias) for each region/feature pair.
    
    """
    # Define the feature parameters internally
    feature_p = ['Reservoir', 'Source', 'Trap']
    feature_obs = ['reservoir', 'source', 'trap']
    feature_title = [
        'Reservoir Probability',
        'Source Probability',
        'Trap Probability'
    ]
    
    # Dictionary to store verification metrics for each (region, feature) pair
    metrics = {(region, feat): {'brier': [], 'skill': [], 'bias': [], 'time_label': []} 
               for region in npd_names for feat in feature_p}
    
    # ----- 1. For each period, create a 3×3 figure for attribute diagrams -----
    for p in range(len(years) - 1):
        period_start = years[p]
        period_end = years[p+1]
        # Create a 3×3 subplot figure (rows: features, columns: regions)
        fig, axes = plt.subplots(3, 3, figsize=(16, 14))
        # Loop over regions (columns)
        for j, region in enumerate(npd_names):
            # Filter the dataframe for the current region.
            df_region = df[df['result NPD play'] == region]
            # Loop over features (rows)
            for i, feat in enumerate(feature_p):
                # Select data for the current period.
                df_y = df_region[(df_region['year'] >= period_start) & (df_region['year'] < period_end)]
                # Retrieve forecast probabilities and observations.
                probs = np.array(df_y[f'{feat} Probability'])
                discovs = np.array(df_y[f'{feature_obs[i]}?'])
                success_mean = np.mean(discovs)
                
                bins_num = 5
                width = 0.2
                
                # Initialize binning arrays.
                extra_bin = bins_num  # Extra bin for probability == 1
                succ_well_per_bin = [0] * (bins_num + 1)
                sum_probs_per_bin = [0] * (bins_num + 1)
                count_per_bin = [0] * (bins_num + 1)
                
                # Bin the forecast probabilities and count successes.
                for prob, discov in zip(probs, discovs):
                    if prob == 1.0:
                        bin_idx = extra_bin
                    elif 0.9 < prob < 1:
                        bin_idx = bins_num - 1
                    else:
                        bin_idx = min(int((prob - 0.001) / width), bins_num - 1)
                    sum_probs_per_bin[bin_idx] += prob
                    count_per_bin[bin_idx] += 1
                    if discov == 1:
                        succ_well_per_bin[bin_idx] += 1
                        
                avg_probs = [sum_probs_per_bin[i] / count_per_bin[i] if count_per_bin[i] > 0 else 0
                             for i in range(bins_num + 1)]
                succ_rate_bin = [succ_well_per_bin[i] / count_per_bin[i] if count_per_bin[i] > 0 else 0
                                 for i in range(bins_num + 1)]
                succ_bin = [succ_well_per_bin[i] if count_per_bin[i] > 0 else 0
                            for i in range(bins_num + 1)]
                bins_mid = [round((i + 0.5) * width, 2) for i in range(bins_num)] + [1.0]
                
                # Attribute measures.
                brier = np.mean((probs - discovs) ** 2)
                rel = np.sum([count_per_bin[i] * (avg_probs[i] - succ_rate_bin[i]) ** 2
                              for i in range(bins_num + 1) if count_per_bin[i] > 0]) / len(probs)
                res = np.sum([count_per_bin[i] * (succ_rate_bin[i] - success_mean) ** 2
                              for i in range(bins_num + 1) if count_per_bin[i] > 0]) / len(probs)
                variance = np.var(discovs, ddof=1)
                skill = (res - rel) / variance if variance > 0 else 0
                bias0 = np.mean(probs - discovs)
                sharp = np.sqrt(np.mean((probs - np.mean(probs)) ** 2))
                
                # Store metrics for the later Brier/Skill Score plot.
                metrics[(region, feat)]['brier'].append(brier)
                metrics[(region, feat)]['skill'].append(skill)
                metrics[(region, feat)]['bias'].append(bias0)
                metrics[(region, feat)]['time_label'].append(f"{period_start}-{period_end-1}")
                
                
                # --- Plot the attribute diagram on the corresponding subplot ---
                ax = axes[i, j]  # row: feature, column: region
                
                # Prepare empirical curve data.
                x_axis = [m for m, cnt in zip(bins_mid, count_per_bin) if cnt != 0]
                # Adjust first two bins as in original logic.
                if len(x_axis) >= 3:
                    x_axis = [0.2] + x_axis[2:]
                counts = [cnt for cnt in count_per_bin if cnt != 0]
                if len(counts) >= 2:
                    counts = [counts[0] + counts[1]] + counts[2:]
                y_axis = [val for val, cnt in zip(succ_rate_bin, count_per_bin) if cnt != 0]
                if len(y_axis) >= 2 and counts[0] != 0:
                    y_axis = [ (succ_bin[0] + succ_bin[1]) / counts[0] ] + y_axis[2:]
                
                # Plot the empirical curve and perfect reliability line.
                ax.plot(x_axis[:-1], y_axis[:-1], 'ro--', markersize=4, label='Empirical Curve')
                ax.plot([0, 1], [0, 1], 'k--', label='Perfect Reliability')
                
                # Confidence intervals.
                lower_bounds = [calculate_confidence_intervals(x_axis[i], counts[i], 0.8)[0]
                                for i in range(len(x_axis))]
                upper_bounds = [calculate_confidence_intervals(x_axis[i], counts[i], 0.8)[1]
                                for i in range(len(x_axis))]
                ax.fill_between(x_axis[:-1], lower_bounds[:-1], upper_bounds[:-1],
                                color='gray', alpha=0.2, label='80% Conf. Interval')
                
                # Additional lines and text.
                #if i == 0 and j == 'north sea':
                #    ax.text(0.83, 0.78, 'Perfect', color='blue', fontsize=9)
                #    ax.plot([0, 1.1], [success_mean, success_mean], 'orange', linestyle='--')
                #    ax.text(0.8, success_mean + 0.02, 'No Resolution', color='blue', fontsize=9)
                #    ax.text(0.84, (success_mean + 0.84) / 2, 'No Skill', color='blue', fontsize=12)
                ax.plot([0] + avg_probs + [1.1],
                        [success_mean / 2] + [0.5 * (a + success_mean) for a in avg_probs] + [(success_mean + 1.1) / 2],
                        'orange', linestyle='--')
                
                
                # Display metrics.
                ax.text(0.03, 1.03, f'Brier Score: {round(brier, 2)}', color='blue', fontsize=9)
                ax.text(0.39, 1.03, f'Skill Score: {round(skill, 2)}', color='blue', fontsize=9)
                ax.text(0.75, 1.03, f'Bias: {round(bias0, 2)}', color='blue', fontsize=9)
                
                # Annotate bin counts.
                for n in range(len(x_axis)):
                    if n < len(x_axis) - 1:
                        ax.text(x_axis[n], 0.05, f'{counts[n]}', color='blue', fontsize=9,
                                rotation=90, ha='center')
                ax.axhline(y=1.0, color='gray', linestyle='-', linewidth=1)
                
                # Titles and axis labels.
                # For the leftmost column add the region name to the title.
                if i == 0:
                    ax.set_title(f'{region.capitalize()}\n\n{feature_title[i]}', fontsize=10)
                else:
                    ax.set_title(f'{feature_title[i]}', fontsize=10)
                if i == 2:
                    ax.set_xlabel('Forecasted PoS (f)', fontsize=10)
                if j == 0:
                    ax.set_ylabel('Observed Rel. Frequency', fontsize=10)
                ax.set_ylim([0, 1.1])
                ax.set_xlim([0, 1])
                ax.tick_params(axis='both', labelsize=9)
                
                # Custom x-ticks.
                xticks = x_axis
                xticklabels = []
                for idx, m in enumerate(x_axis):
                    if idx == len(x_axis) - 1:
                        label = '1'
                    elif idx > 0 and idx < len(x_axis) - 2:
                        label = f'({round(m - width/2, 2)} - {round(m + width/2, 2)}]'
                    elif idx == 0:
                        label = f'({round(0, 2)} - {round(m + width, 2)}]'
                    else:
                        label = f'({round(m - width/2, 2)} - {round(m + width/2, 2)})'
                    xticklabels.append(label)
                ax.set_xticks(xticks[:-1])
                ax.set_xticklabels(xticklabels[:-1], fontsize=9, rotation=45)
                
                # Bar plot for probability assessment frequency.
                normalized_counts = [cnt / sum(counts) if sum(counts) != 0 else 0 for cnt in counts]
                ax.bar(x_axis[1:-1], normalized_counts[1:-1], width=width, align='center', alpha=0.3,
                       label='Probability Assessment Frequency')
                default_blue = plt.rcParams['axes.prop_cycle'].by_key()['color'][0]
                ax.bar(0.2, normalized_counts[0], width=0.4, align='center', alpha=0.3, color=default_blue)
                #if (i == 0 and j == 0):
                #    ax.legend(loc=(0.008, 0.71), fontsize=10)
        #fig.suptitle(f'Attribute Diagrams for period {period_start}-{period_end-1}', fontsize=12)
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(f"attribute_npd.pdf")
        plt.show()
    
    # ----- 2. Create a single 3×3 figure for Brier/Skill Score plots -----
    fig, axes = plt.subplots(3, 3, figsize=(16, 12))
    for j, region in enumerate(npd_names):
        for i, feat in enumerate(feature_p):
            ax = axes[i, j]
            key = (region, feat)
            time_labels = metrics[key]['time_label']
            ax.plot(time_labels, metrics[key]['brier'], marker='o', linestyle='-', color='brown',
                    markersize=4, label='Brier Score')
            ax.plot(time_labels, metrics[key]['skill'], marker='o', linestyle='-', color='r',
                    markersize=4, label='Skill Score')
            ax.set_title(feature_title[i] if i != 0 else f'{region.capitalize()}\n\n{feature_title[i]}',
                         fontsize=12)
            if i == 2:
                ax.set_xlabel('Year Range', fontsize=10)
            if j == 0:
                ax.set_ylabel('Brier and Skill Score', fontsize=10)
            ax.tick_params(axis='both', labelsize=10)
            ax.set_ylim([-.8, .7])
            if j == 0 and i == 0:
                ax.legend(fontsize=9, loc='upper left')
            ax.grid(True, which='both', axis='both', linestyle='-', color='red', alpha=0.2)
            ax2 = ax.twinx()
            ax2.plot(time_labels, metrics[key]['bias'], marker='s', linestyle='--', color='g',
                     markersize=4, label='Bias')
            if j == 2:
                ax2.set_ylabel('Bias', fontsize=10)
            ax2.tick_params(axis='y', labelsize=10)
            ax2.set_ylim([-.4, .4])
            if j == 0 and i == 0:
                ax2.legend(fontsize=9, loc='upper right')
            ax2.grid(True, which='both', axis='both', linestyle='-', color='green', alpha=0.2)
    plt.tight_layout()
    plt.savefig(f"measures_npd.pdf")
    plt.show()

# Example call:
#years = [1990, 2022]
#attribute_diagram(df_npd, years)

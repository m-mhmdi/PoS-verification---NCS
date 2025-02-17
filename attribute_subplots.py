import numpy as np
from scipy.stats import binom
import matplotlib.pyplot as plt

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
    Generate attribute diagrams and measure Score plots for multiple features over time.
    - For each period (years[i] to years[i+1]-1) a 2×2 figure is created showing the attribute diagrams for
      Technical, Reservoir, Source, and Trap.
    - After processing all periods, a single 2×2 figure is created where each subplot shows the Brier/Skill Score
      (plus bias) evolution over time for one feature.
      
    """
    # Define the feature parameters internally
    feature_p = ['Technical', 'Reservoir', 'Source', 'Trap']
    feature_obs = ['discovery', 'reservoir', 'source', 'trap']
    feature_title = [
        'Technical Probability',
        'Reservoir Probability',
        'Source Probability',
        'Trap Probability'
    ]
    
    # This dictionary will store the Brier/Skill/Bias metrics per feature over the periods.
    metrics = {fp: {'brier': [], 'skill': [], 'bias': [], 'time_label': []} for fp in feature_p}
    
    # ----- 1. For each period, create a 2x2 figure for attribute diagrams -----
    for period in range(len(years) - 1):
        period_start = years[period]
        period_end = years[period + 1]
        # Create a 2x2 subplot figure for the 4 features for this period.
        fig, axes = plt.subplots(2, 2, figsize=(16, 14))
        axes = axes.flatten()
        
        for ff in range(len(feature_p)):
            # Select data for the current period.
            df_y = df[(df['year'] >= period_start) & (df['year'] < period_end)]
            # Extract forecast probabilities and observations for current feature.
            probs = np.array(df_y[f'{feature_p[ff]} Probability'])
            discovs = np.array(df_y[f'{feature_obs[ff]}?'])
            # The mean observed success
            success_mean = np.mean(discovs)
            
            bins_num = 10
            width = 0.1
            
            # Initialize lists for bin calculations.
            extra_bin = bins_num  # extra bin for probability == 1
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
            
            avg_probs = [
                sum_probs_per_bin[i] / count_per_bin[i] if count_per_bin[i] > 0 else 0
                for i in range(bins_num + 1)
            ]
            succ_rate_bin = [
                succ_well_per_bin[i] / count_per_bin[i] if count_per_bin[i] > 0 else 0
                for i in range(bins_num + 1)
            ]
            bins_mid = [round((i + 0.5) * width, 2) for i in range(bins_num)] + [1.0]
            
            # --- Attribute measures ---
            brier = np.mean((probs - discovs) ** 2)
            rel = np.sum([
                (count_per_bin[i] * (avg_probs[i] - succ_rate_bin[i]) ** 2)
                for i in range(bins_num + 1) if count_per_bin[i] > 0
            ]) / len(probs)
            res = np.sum([
                (count_per_bin[i] * (succ_rate_bin[i] - success_mean) ** 2)
                for i in range(bins_num + 1) if count_per_bin[i] > 0
            ]) / len(probs)
            variance = np.var(discovs, ddof=1)
            skill = (res - rel) / variance if variance > 0 else 0
            bias0 = np.mean(probs - discovs)
            
            # Store metrics for the later Brier/Skill Score plot.
            metrics[feature_p[ff]]['brier'].append(brier)
            metrics[feature_p[ff]]['skill'].append(skill)
            metrics[feature_p[ff]]['bias'].append(bias0)
            metrics[feature_p[ff]]['time_label'].append(f"{period_start}-{period_end-1}")
            
            # --- Plotting the attribute diagram in the subplot ---
            ax = axes[ff]
            
            # Plot the empirical curve.
            # (Select only bins with nonzero counts.)
            valid_bins = [i for i, cnt in enumerate(count_per_bin) if cnt != 0]
            x_axis = [bins_mid[i] for i in valid_bins]
            y_axis = [succ_rate_bin[i] for i in valid_bins]
            if len(x_axis) > 1:
                ax.plot(x_axis[:-1], y_axis[:-1], 'ro--', markersize=10, label='Empirical Curve')
            ax.plot([0, 1], [0, 1], 'k--', label='Perfect Reliability')
            fig_num = ['(a)', '(b)', '(c)', '(d)']
            ax.text(0, 1.13, fig_num[ff], color='k', fontsize=12)
            
            # Confidence intervals.
            p_hat = [bins_mid[i] for i in valid_bins]
            counts = [count_per_bin[i] for i in valid_bins]
            lower_bounds = [
                calculate_confidence_intervals(p_hat[i_idx], counts[i_idx], 0.8)[0]
                for i_idx in range(len(p_hat))
            ]
            upper_bounds = [
                calculate_confidence_intervals(p_hat[i_idx], counts[i_idx], 0.8)[1]
                for i_idx in range(len(p_hat))
            ]
            if len(p_hat) > 1:
                ax.fill_between(p_hat[:-1], lower_bounds[:-1], upper_bounds[:-1],
                                color='gray', alpha=0.2, label='80% Conf. Interval')
            
            # Additional lines and texts (perfect reliability, no resolution, no skill).
            perfect = ['Perfect', '', '', '']
            no_res = ['No Resolution', '', '', '']
            no_skl = ['No Skill', '', '', '']
            ax.text(0.83, 0.78, perfect[ff], color='blue', fontsize=12)
            ax.plot([0, 1.1], [success_mean, success_mean], 'orange', linestyle='--')
            ax.text(0.8, success_mean + 0.02, no_res[ff], color='blue', fontsize=12)
            ax.plot([0] + avg_probs + [1.1],
                    [success_mean / 2] + [0.5 * (a + success_mean) for a in avg_probs] + [(success_mean + 1.1) / 2],
                    'orange', linestyle='--')
            ax.text(0.84, (success_mean + 0.84) / 2, no_skl[ff], color='blue', fontsize=12)
            
            # Display metrics.
            ax.text(0.03, 1.03, f'Brier Score: {round(brier, 2)}', color='blue', fontsize=12)
            ax.text(0.39, 1.03, f'Skill Score: {round(skill, 2)}', color='blue', fontsize=12)
            ax.text(0.75, 1.03, f'Bias: {round(bias0, 2)}', color='blue', fontsize=12)
            
            # Annotate bin counts.
            for n in range(len(bins_mid)):
                if n < len(bins_mid) - 1:
                    ax.text(bins_mid[n], 0.05, f'{count_per_bin[n]}', color='blue',
                            fontsize=12, rotation=90, ha='center')
            ax.axhline(y=1.0, color='gray', linestyle='-', linewidth=1)
            
            # Set titles and labels.
            ax.set_title(feature_title[ff], fontsize=14)
            x_lab = ['', '', 'Forecasted PoS (f)', 'Forecasted PoS (f)']
            y_lab = ['Observed Rel. Frequency', '', 'Observed Rel. Frequency', '']
            ax.set_xlabel(x_lab[ff], fontsize=12)
            ax.set_ylabel(y_lab[ff], fontsize=12)
            ax.set_ylim([0, 1.1])
            ax.set_xlim([0, 1])
            
            # Custom x-ticks.
            ax.set_xticks(bins_mid[:-1])
            xticklabels = []
            for i, m in enumerate(bins_mid):
                if i == bins_num:  # Special label for the last bin (1.0)
                    label = '1'
                elif 0 <= i < bins_num - 1:
                    label = f'({round(m - width / 2, 2)} - {round(m + width / 2, 2)}]'
                else:
                    label = f'({round(m - width / 2, 2)} - {round(m + width / 2, 2)})'
                xticklabels.append(label)
            ax.set_xticklabels(xticklabels[:-1], fontsize=10, rotation=45)
            
            # Bar plot for probability assessment frequency.
            normalized_counts = [cnt / sum(count_per_bin) for cnt in count_per_bin]
            ax.bar(bins_mid[:-1], normalized_counts[:-1], width=width, align='center',
                   alpha=0.3, label='Probability Assessment Frequency')
            if ff == 0:
                ax.legend(loc=(0.008, 0.73), fontsize=10)
        
        #fig.suptitle(f'Attribute Diagrams for period {period_start}-{period_end-1}', fontsize=24)
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(f"attribute_diagram.pdf")
        plt.show()
    
    # ----- 2. Create a single 2x2 figure for Brier/Skill Score plots -----
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    fig_num = ['(a)', '(b)', '(c)', '(d)']
    
    for ff in range(len(feature_p)):
        ax = axes[ff]
        # Retrieve stored metrics for the current feature.
        time_labels = metrics[feature_p[ff]]['time_label']
        ax.plot(time_labels, metrics[feature_p[ff]]['brier'], marker='o', linestyle='-',
                color='brown', markersize=8, label='Brier Score')
        ax.plot(time_labels, metrics[feature_p[ff]]['skill'], marker='o', linestyle='-',
                color='r', markersize=8, label='Skill Score')
        ax.text(-0.2, 0.72, fig_num[ff], color='k', fontsize=12)
        ax.set_title(feature_title[ff], fontsize=14)
        if ff == 2 or ff == 3:
            ax.set_xlabel('Year Range', fontsize=12)
        if ff == 0 or ff == 2:
            ax.set_ylabel('Brier and Skill Score', fontsize=12)
        ax.tick_params(axis='both', labelsize=10)
        ax.set_ylim([-.8, .7])
        if ff == 0:
            ax.legend(fontsize=10, loc='upper left')
        ax.grid(True, which='both', axis='both', linestyle='-', color='red', alpha=0.2)
        
        # Add bias using a secondary y-axis.
        ax2 = ax.twinx()
        ax2.plot(time_labels, metrics[feature_p[ff]]['bias'], marker='s', linestyle='--',
                 color='g', markersize=8, label='Bias')
        if ff == 1 or ff == 3:
            ax2.set_ylabel('Bias', fontsize=12)
        ax2.set_ylim([-.25, .25])
        ax2.tick_params(axis='y', labelsize=10)
        if ff == 0:
            ax2.legend(fontsize=10, loc='upper right')
        ax2.grid(True, which='both', axis='both', linestyle='-', color='green', alpha=0.2)
    
    plt.tight_layout()
    plt.savefig(f"measures.pdf")
    plt.show()

# Example call:
# (Make sure that "data" is defined as a DataFrame with columns such as
#  'year', 'Technical Probability', 'discovery?', etc.)
#years = [1990, 1996, 2002, 2011, 2016, 2022]
#years = [1990, 2022]
#attribute_diagram(data, years)

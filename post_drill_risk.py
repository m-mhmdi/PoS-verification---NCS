import numpy as np
import matplotlib.pyplot as plt

def risk_pie_chart(df_npd):
    """
    Analyzes and visualizes the post-drilling risks for different NPD play areas.
    
    Parameters:
    df_npd (DataFrame): Input data containing exploration results and probabilities.
    
    Returns:
    None (Displays a pie chart visualization of risks per play area).
    """
    feature_obs = ['discovery?', 'reservoir?', 'source?', 'trap?']
    #feature_prog = ['Technical Probability', 'Reservoir Probability', 'Source Probability', 'Trap Probability']
    feature_name = ['Reservoir', 'Source', 'Trap']
    npd_names = ['north sea', 'norwegian sea', 'barents sea']
    
    post_risk_all = []
    num = []
    
    for n in npd_names:
        succ_rate = []
        avg_prob = []
        df_play = df_npd[df_npd['result NPD play'] == n]
        
        for ff in range(4):
            disc = df_play[feature_obs[ff]]
            #probs = df_play[feature_prog[ff]].apply(np.mean)
            
            d_yes = (disc == 1).sum()
            d_no = (disc == 0).sum()
            
            #avg_p = np.mean(probs)
            succ_r = round(d_yes / (d_yes + d_no), 2) if (d_yes + d_no) > 0 else 0
            
            succ_rate.append(succ_r)
            #avg_prob.append(avg_p)
        
        #a, b, c = avg_prob[1], avg_prob[2], avg_prob[3]
        a2, b2, c2 = succ_rate[1], succ_rate[2], succ_rate[3]
        
        #pre_risk = [(1-a)/(3-a-b-c), (1-b)/(3-a-b-c), (1-c)/(3-a-b-c)]
        post_risk = [(1-a2)/(3-a2-b2-c2), (1-b2)/(3-a2-b2-c2), (1-c2)/(3-a2-b2-c2)]
        
        post_risk_all.append(post_risk)
        num.append(len(df_play))
    
    # Plot settings
    fig = plt.figure(figsize=(12, 8))
    ax1 = fig.add_axes([0.1, 0.55, 0.35, 0.35])  # Top-left for North Sea
    ax2 = fig.add_axes([0.55, 0.55, 0.35, 0.35])  # Top-right for Norwegian Sea
    ax3 = fig.add_axes([0.33, 0.1, 0.35, 0.35])  # Bottom center for Barents Sea
    
    fig.suptitle('Main Reason for Failure', fontsize=14, fontweight='normal', y=1.02)
    
    axes = [ax1, ax2, ax3]
    for i, ax in enumerate(axes):
        ax.pie(post_risk_all[i], labels=feature_name, autopct='%1.1f%%', radius=1.5, textprops={'fontsize': 10})
        ax.set_title(f'{npd_names[i].capitalize()}', fontsize=12, pad=40)
    
    plt.subplots_adjust(hspace=1, wspace=0.1)
    #plt.savefig(f"Figure_2.pdf")
    plt.show()
    
    
#risk_pie_chart(df_npd)
def create_plot(factors, weights, type):
    from io import BytesIO

    import matplotlib.pyplot as plt
    import matplotlib as mpl
    import numpy as np
    import base64
    
    mpl.use('agg')
    mpl.rcParams['font.size'] = '19'
    
    strengths, weaknesses = factors[0],factors[1]
    strength_weights, weakness_weights = weights[0],weights[1]

    if (type == "sw"):
      factor_dict = {f's{i+1}': (strengths[i], strength_weights[i]) for i in range(len(strengths))}
      factor_dict.update({f'w{i+1}': (weaknesses[i], weakness_weights[i]) for i in range(len(weaknesses))})
    else:
      factor_dict = {f'o{i+1}': (strengths[i], strength_weights[i]) for i in range(len(strengths))}
      factor_dict.update({f't{i+1}': (weaknesses[i], weakness_weights[i]) for i in range(len(weaknesses))})


    sw_factor_means_strings = strength_weights + weakness_weights
    sw_factor_means_values = [float(value) for value in sw_factor_means_strings]
    sw_factor_means_keys = factor_dict.keys()
    
    sw_factor_means = dict(zip(sw_factor_means_keys,  map(float, sw_factor_means_values)))
    sw_sorted_factor_means = dict(sorted(sw_factor_means.items(), key=lambda item: item[1], reverse=True))
    
    fig, ax = plt.subplots(layout='constrained', figsize=(14, 8))
    fig.set_facecolor('black')
    ax.set_facecolor('#131313')
    
    species = ("Adelie",)
    x = np.arange(len(species))
    width = 0.2
    multiplier = 0
    
    for attribute, measurement in sw_sorted_factor_means.items():
        offset = width * multiplier
        color = '#333333' if (attribute.startswith('s') or attribute.startswith('o')) else '#666666'
        rects = ax.bar(x + offset, measurement, width, label=attribute, color=color, edgecolor='white', linewidth=1.5)
        ax.bar_label(rects, labels=[attribute]*len(species), padding=3, color='white')
        multiplier += 1
    
    ax.set_ylabel('Веса факторов \n', color='white')
    if (type == "sw"):
      ax.set_title('\nФинальные оценки внутренних сторон\n', color='white')
    else:
      ax.set_title('\nФинальные оценки внешних сторон\n', color='white')
    ax.set_xticks(x)
    
    min_value = min(sw_factor_means_values)  
    max_value = max(sw_factor_means_values) + 1
    num_ticks = 10
    tick_positions = np.linspace(min_value, max_value, num_ticks)
    ax.set_yticks(tick_positions)
    ax.set_yticklabels([str(round(float(tick),2)) for tick in tick_positions], color='white')
    ax.tick_params(axis='y', labelsize=12)
    ax.set_ylim(min_value - 1, max_value)
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    buffer.seek(0)
    image_png = buffer.getvalue()
    plot_base64 = base64.b64encode(image_png).decode('utf-8')
    buffer.close()

    legend = ""
    for i in factor_dict.keys():
      legend = legend + i + ": " + factor_dict[i][0] + ";" + "\n"
    legend = legend[:-2] + "."

    return plot_base64, legend
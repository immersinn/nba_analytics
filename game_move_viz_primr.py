

from matplotlib.patches import Circle, Rectangle, Arc

# Function to draw the basketball court lines
def draw_court(ax=None, color="gray", lw=1, zorder=0):
    
    if ax is None:
        ax = plt.gca()

    # Creates the out of bounds lines around the court
    outer = Rectangle((0,-50), width=94, height=50, color=color,
                      zorder=zorder, fill=False, lw=lw)

    # The left and right basketball hoops
    l_hoop = Circle((5.35,-25), radius=.75, lw=lw, fill=False, 
                    color=color, zorder=zorder)
    r_hoop = Circle((88.65,-25), radius=.75, lw=lw, fill=False,
                    color=color, zorder=zorder)
    
    # Left and right backboards
    l_backboard = Rectangle((4,-28), 0, 6, lw=lw, color=color,
                            zorder=zorder)
    r_backboard = Rectangle((90, -28), 0, 6, lw=lw,color=color,
                            zorder=zorder)

    # Left and right paint areas
    l_outer_box = Rectangle((0, -33), 19, 16, lw=lw, fill=False,
                            color=color, zorder=zorder)    
    l_inner_box = Rectangle((0, -31), 19, 12, lw=lw, fill=False,
                            color=color, zorder=zorder)
    r_outer_box = Rectangle((75, -33), 19, 16, lw=lw, fill=False,
                            color=color, zorder=zorder)

    r_inner_box = Rectangle((75, -31), 19, 12, lw=lw, fill=False,
                            color=color, zorder=zorder)

    # Left and right free throw circles
    l_free_throw = Circle((19,-25), radius=6, lw=lw, fill=False,
                          color=color, zorder=zorder)
    r_free_throw = Circle((75, -25), radius=6, lw=lw, fill=False,
                          color=color, zorder=zorder)

    # Left and right corner 3-PT lines
    # a represents the top lines
    # b represents the bottom lines
    l_corner_a = Rectangle((0,-3), 14, 0, lw=lw, color=color,
                           zorder=zorder)
    l_corner_b = Rectangle((0,-47), 14, 0, lw=lw, color=color,
                           zorder=zorder)
    r_corner_a = Rectangle((80, -3), 14, 0, lw=lw, color=color,
                           zorder=zorder)
    r_corner_b = Rectangle((80, -47), 14, 0, lw=lw, color=color,
                           zorder=zorder)
    
    # Left and right 3-PT line arcs
    l_arc = Arc((5,-25), 47.5, 47.5, theta1=292, theta2=68, lw=lw,
                color=color, zorder=zorder)
    r_arc = Arc((89, -25), 47.5, 47.5, theta1=112, theta2=248, lw=lw,
                color=color, zorder=zorder)

    # half_court
    # ax.axvline(470)
    half_court = Rectangle((47,-50), 0, 50, lw=lw, color=color,
                           zorder=zorder)

    hc_big_circle = Circle((47, -25), radius=6, lw=lw, fill=False,
                           color=color, zorder=zorder)
    hc_sm_circle = Circle((47, -25), radius=2, lw=lw, fill=False,
                          color=color, zorder=zorder)

    court_elements = [l_hoop, l_backboard, l_outer_box, outer,
                      l_inner_box, l_free_throw, l_corner_a,
                      l_corner_b, l_arc, r_hoop, r_backboard, 
                      r_outer_box, r_inner_box, r_free_throw,
                      r_corner_a, r_corner_b, r_arc, half_court,
                      hc_big_circle, hc_sm_circle]

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax


def standardPosPlot(pos_df, draw_court=False):

    # Initialize figure
    plt.figure(figsize=(15, 11.5))
    # Plot the movemnts as scatter plot
    # using a colormap to show change in game clock
    plt.scatter(pos_df.x_loc, - pos_df.y_loc,
                c = pos_df.game_clock,
                cmap = plt.cm.Blues, zorder = 1)
    # Darker colors represent moments earlier on in the game
    cbar = plt.colorbar(orientation="horizontal")
    # invert the colorbar to have higher numbers on the left
    cbar.ax.invert_xaxis()
    # (Optional) Draw court image
    if draw_court:
        draw_court()
    # Set axis limits
    plt.xlim(0, 101)
    plt.ylim(-51, 0)
    # Dram plot
    plt.show()


def distancesPlot():

    # Create some lists that will help create our plot
    # Distance data
    distances = [ariza_barnes, ariza_paul, harden_jordan, howard_barnes]
    # Labels for each line that we will plopt
    labels = ["Ariza - Barnes", "Ariza - Paul", "Harden - Jordan", "Howard - Barnes"]
    # Colors for each line
    colors = sns.color_palette('colorblind', 4)

    plt.figure(figsize=(12,9))

    # Use enumerate to index the labels and colors and match
    # them with the proper distance data
    for i, dist in enumerate(distances):
        plt.plot(time_df.shot_clock.unique(), dist, color=colors[i])
        
        y_pos = dist[-1]
        
        plt.text(6.15, y_pos, labels[i], fontsize=14, color=colors[i])

    # Plot a line to indicate when Harden passes the ball
    plt.vlines(7.7, 0, 30, color='gray', lw=0.7)
    plt.annotate("Harden passes the ball", (7.7, 27), 
                 xytext=(8.725, 26.8), fontsize=12, 
                 arrowprops=dict(facecolor='lightgray', shrink=0.10))

    # Create horizontal grid lines
    plt.grid(axis='y',color='gray', linestyle='--', lw=0.5, alpha=0.5)

    plt.xlim(10.1, 6.2)

    plt.title("The Distance (in feet) Between Players \nFrom the Beginning"
              " of Harden's Drive up until Ariza Releases his Shot", size=16)
    plt.xlabel("Time Left on Shot Clock (seconds)", size=14)

    # Get rid of unneeded chart lines
    sns.despine(left=True, bottom=True) 

    plt.show()


def main():

    pass

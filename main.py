import pandas as pd
from tkinter import *
from tkinter import filedialog
import numpy as np
import os
import matplotlib.pyplot as plt

# opens window to select file.
master = Tk()
master.title('LISST File Selection')
master.filename = filedialog.askopenfilename(filetypes=(('csv files', '*.csv'), ('All Files', '*.*')))
master.filename2 = filedialog.askopenfilename(filetypes=(('Excel files', '*.xlsx'), ('All Files', '*.*')))

exp_name = master.filename
log_sheet = master.filename2

df = pd.read_csv(exp_name)  # LISST File
df2 = pd.read_excel(log_sheet)  # Log File
df2 = df2.set_index('Experiment Number')

exp_name = os.path.basename(exp_name)
file_name = exp_name
exp_name = exp_name.rstrip('2056.csv')
exp_name = exp_name.rstrip('2057.csv')
exp_name = exp_name.strip()
lisst_num = file_name.rstrip('.csv').lstrip(f'{exp_name}').strip()

start_time = df2.loc[f'{exp_name}']['Oil Release Time']

df.columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
              '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
              '21', '22', '23', '24', '25', '26', '27', '28', '29', '30',
              '31', '32', '33', '34', '35', '36',
              'LaserTransmissionSensor',
              'SupplyVoltage',
              'ExternalAnalogInput1',
              'LaserReferenceSensor',
              'Depth',
              'Temperature',
              'Year', 'Month', 'Day', 'Hour', 'Minute', 'Second',
              'ExternalAnalogInput2', 'MeanDiameter',
              'TotlVolumeConcentration',
              'RelativeHumidity',
              'AccelerometerX', 'AccelerometerY', 'AccelerometerZ',
              'RawPressure[most significant bit]', 'RawPressure[least significant 16 bits]',
              'AmbientLight',
              'NotUsed',
              'ComputedOpticalTransmissionOverPath',
              'Beam-attenuation']

# add DateTime column then split to date and time
time_col = pd.to_datetime(df[['Year', 'Month', 'Day', 'Hour', 'Minute', 'Second']])
df['DateTime'] = time_col
df['date'] = [d.date() for d in df['DateTime']]
df['time'] = [d.time() for d in df['DateTime']]

# splits start_time into hour,min, sec so i can clip data based on those inputs
_1 = str(start_time)
new = _1.split(':')
h = new[0]
m = new[1]
s = new[2]

# minimum and maximum times aka start and end times   ***** MAKE THE LENGTH OF THE EXPERIMENT A VARIABLE ******
df_min_time = df.loc[(df['Hour'] == int(h)) & (df['Minute'] >= int(m))]  # start time
df_max_time = df.loc[(df['Hour'] == (int(h) + 1)) & (df['Minute'] <= int(m))]  # end time

data = [df_min_time, df_max_time]
exp_window = pd.concat(data)

df = exp_window
# min elapsed column
time = df['DateTime']
time_delta = time - time.min()
time_delta = time_delta / np.timedelta64(1, 'm')
df['minElapsed'] = round(time_delta, 2)

df['TPC'] = df.iloc[:, 0:36].sum(axis=1)
# HOW TO GET THIS IN A COLUMN IN DF
# for x in df['minElapsed']:
#     mins = x
#     secs = (x * 60) % 60
#     print('%d:%02d' % (mins, secs))

# save exp_window as csv
new_dir = f'processed_data//{exp_name}'
dir_exist = os.path.exists(new_dir)
if not dir_exist:
    os.mkdir(new_dir)
exp_window.to_csv(f'processed_data//{exp_name}//clipped {file_name}', index=False, header=True)

# ##Contour Plot
# bin size median value taken from LISST-200x manual
bin_size = [1.21, 1.60, 1.89, 2.23, 2.63, 3.11, 3.67, 4.33, 5.11, 6.03,
            7.11, 8.39, 9.9, 11.7, 13.8, 16.3, 19.2, 22.7, 26.7, 31.6,
            37.2, 43.9, 51.9, 61.2, 72.2, 85.2, 101, 119, 140, 165,
            195, 230, 273, 324, 386, 459]

bin_size_label = [' ', ' ', ' ', 2.23, ' ', ' ', ' ', 4.33, ' ', ' ', ' ', 8.39,
                  ' ', ' ', ' ', 16.3, ' ', ' ', ' ', 31.6, ' ', ' ', ' ', 61.2,
                  ' ', ' ', ' ', 119, ' ', ' ', ' ', 230, ' ', ' ', ' ', 459]
y_pos = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
         28, 29, 30, 31, 32, 33, 34, 35]


################################
#########################

def cont_zcons_plot(plt_color, zcons=1):
    plt.clf()
    X = df['minElapsed']
    Y = bin_size
    y, x = np.meshgrid(Y, X)
    z = df.iloc[:, 0:36]
    z = z.rolling(400, min_periods=1).mean()
    z = np.clip(z, 0, zcons)

    plt.figure(1)

    plt.yscale('log')
    plt.tick_params(axis='y', length=5, which='major')
    plt.yticks(bin_size, bin_size_label)

    plt.contourf(x, y, z, 10, cmap=plt_color)
    # 'Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r', 'CMRmap',
    # 'CMRmap_r', 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Greens', 'Greens_r', 'Greys', 'Greys_r', 'OrRd', 'OrRd_r',
    # 'Oranges', 'Oranges_r', 'PRGn', 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r', 'Pastel2', 'Pastel2_r',
    # 'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r', 'PuRd', 'PuRd_r', 'Purples',
    # 'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r',
    # 'Reds', 'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 'Set3_r', 'Spectral', 'Spectral_r', 'Wistia',
    # 'Wistia_r', 'YlGn', 'YlGnBu', 'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'afmhot',
    # 'afmhot_r', 'autumn', 'autumn_r', 'binary', 'binary_r', 'bone', 'bone_r', 'brg', 'brg_r', 'bwr', 'bwr_r',
    # 'cividis', 'cividis_r', 'cool', 'cool_r', 'coolwarm', 'coolwarm_r', 'copper', 'copper_r', 'cubehelix',
    # 'cubehelix_r', 'flag', 'flag_r', 'gist_earth', 'gist_earth_r', 'gist_gray', 'gist_gray_r', 'gist_heat',
    # 'gist_heat_r', 'gist_ncar', 'gist_ncar_r', 'gist_rainbow', 'gist_rainbow_r', 'gist_stern', 'gist_stern_r',
    # 'gist_yarg', 'gist_yarg_r', 'gnuplot', 'gnuplot2', 'gnuplot2_r', 'gnuplot_r', 'gray', 'gray_r', 'hot',
    # 'hot_r', 'hsv', 'hsv_r', 'inferno', 'inferno_r', 'jet', 'jet_r', 'magma', 'magma_r', 'nipy_spectral',
    # 'nipy_spectral_r', 'ocean', 'ocean_r', 'pink', 'pink_r', 'plasma', 'plasma_r', 'prism', 'prism_r',
    # 'rainbow', 'rainbow_r', 'seismic', 'seismic_r', 'spring', 'spring_r', 'summer', 'summer_r', 'tab10',
    # 'tab10_r', 'tab20', 'tab20_r', 'tab20b', 'tab20b_r', 'tab20c', 'tab20c_r', 'terrain', 'terrain_r',
    # 'twilight', 'twilight_r', 'twilight_shifted', 'twilight_shifted_r', 'viridis', 'viridis_r', 'winter', 'winter_r'

    plt.colorbar()

    # Need to try and have this be more blended

    plt.title(f'{exp_name} Contour Plot Z Constrained {lisst_num}')
    plt.xlabel('time (minutes)')
    plt.ylabel('Particle Size (microns)')
    # plt.show()


# cont_zcons_plot()  # input number for z constraint. default 1


def tpc_plot():
    x = df['minElapsed']
    y = df['TPC']
    plt.figure(2)
    plt.scatter(x, y, marker='o', color='black', s=10)
    plt.title(f'{exp_name} Total Particle Concentration {lisst_num}')
    plt.ylabel(r'Particle Concentration ($\mu$L/L)')
    plt.xlabel('Time (minutes)')
    # plt.show()


def tpc_mean_plot(num_samp_roll=4):
    x = df['minElapsed']
    y = df['TPC']
    rolling_tpc = y.rolling(num_samp_roll, min_periods=1).mean()
    y = rolling_tpc
    plt.figure(3)
    plt.scatter(x, y, marker='o', color='black', s=10)

    if num_samp_roll == 1:
        plt.title(f'{exp_name} Total Particle Concentration {lisst_num}')
    else:
        plt.title(f'{exp_name} Mean Total Particle Concentration({num_samp_roll} samples) {lisst_num}')

    plt.ylabel(r'Particle Concentration ($\mu$L/L)')
    plt.xlabel('Time (minutes)')
    # plt.show()


x = bin_size
y = df[df.TPC == df.TPC.max()].iloc[:, 0:36]
y = y.values.tolist()
y = pd.DataFrame(y)
y = y.transpose()
x = pd.DataFrame(x)
df76 = x
df76.columns = ['binsize']
df76['psc'] = y


def psd_plot():
    yy = df76['psc']
    x_pos = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
             28, 29, 30, 31, 32, 33, 34, 35]

    plt.figure(4)
    plt.bar(x_pos, yy, color='black')

    plt.tick_params(axis='x', length=5, which='major')
    plt.xticks(x_pos, bin_size_label)

    plt.title(f'{exp_name} Particle Size Distribution {lisst_num}')
    plt.ylabel(r'Particle Concentration ($\mu$L/L)')
    plt.xlabel(r'LISST Particle Size Bins ($\mu$m)')
    # plt.show()


def plt_test():
    print(var1.get(), var2.get(), var3.get(), var4.get())
    if var1.get() == 1:
        plt.clf()
        cont_zcons_plot(entr3.get(), entr2.get())
    if var2.get() == 1:
        tpc_plot()
    if var3.get() == 1:
        tpc_mean_plot(entr1.get())
    if var4.get() == 1:
        psd_plot()
    plt.show()


def plt_save():  # make this actually save
    print(var1.get(), var2.get(), var3.get(), var4.get())
    if var1.get() == 1:
        plt.clf()
        cont_zcons_plot(entr3.get(), entr2.get())
        plt.savefig(f'{new_dir}//{exp_name} Contour Plot Z constrained {lisst_num}')
    if var2.get() == 1:
        tpc_plot()
        plt.savefig(f'{new_dir}//{exp_name} TPC Plot {lisst_num}')
    if var3.get() == 1:
        tpc_mean_plot(entr1.get())
        plt.savefig(f'{new_dir}//{exp_name} TPC Mean Plot {lisst_num}')
    if var4.get() == 1:
        psd_plot()
        plt.savefig(f'{new_dir}//{exp_name} PSD Plot {lisst_num}')
    


# ## GUI ###


entr1 = IntVar()  # value for tpc mean value number of samples
entr1.set(4)
entr2 = IntVar()  # value for z constraint
entr2.set(1)
entr3 = StringVar()  # value for z constraint
entr3.set('Blues')

Label(master, text='mean value, default 4').grid(row=1, sticky=W)
Entry(master, textvariable=entr1).grid(row=2, sticky=W)

Label(master, text='z limit, default 1').grid(row=3, sticky=W)
Entry(master, textvariable=entr2).grid(row=4, sticky=W)

Label(master, text='contour color, Blues/Greys').grid(row=5, sticky=W)
Entry(master, textvariable=entr3).grid(row=6, sticky=W)

var1 = IntVar()
var1.set(1)
cont_box = Checkbutton(master, variable=var1, text='contour').grid(row=7, sticky=W)

var2 = IntVar()
var2.set(1)
tpc_box = Checkbutton(master, variable=var2, text='tpc').grid(row=8, sticky=W)

var3 = IntVar()
var3.set(1)
mean_box = Checkbutton(master, variable=var3, text='tpc mean').grid(row=9, sticky=W)

var4 = IntVar()
var4.set(1)
psd_box = Checkbutton(master, variable=var4, text='psd').grid(row=10, sticky=W)

show_button = Button(master, text='show', command=plt_test).grid(row=11, sticky=W)
save_button = Button(master, text='save', command=plt_save).grid(row=11, sticky=E)
master.mainloop()
